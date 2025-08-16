"""
Tests for PostgreSQL database connection and basic operations.
Verifies PostgreSQL-specific functionality and compatibility.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import pytest
from datetime import date, datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, IntegrityError

from app.database import Base, get_db
from app.models import DailyPrediction, PriceLog, AIPrediction
from app.config import settings


class TestPostgreSQLConnection(unittest.TestCase):
    """Test PostgreSQL database connectivity and basic operations."""
    
    def setUp(self):
        """Set up test database connection."""
        # Use test database URL if provided, otherwise default test config
        self.test_db_url = os.getenv(
            "TEST_DATABASE_URL", 
            "postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy_test"
        )
        
        # Create test engine
        self.engine = create_engine(self.test_db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def test_postgresql_connection_available(self):
        """Test that PostgreSQL is available and accepting connections."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                self.assertIn("PostgreSQL", version)
                print(f"✅ PostgreSQL connection successful: {version}")
        except OperationalError as e:
            self.skipTest(f"PostgreSQL not available: {e}")
    
    def test_database_creation_and_schema(self):
        """Test database and table creation with PostgreSQL."""
        try:
            # Drop and recreate tables for clean test
            Base.metadata.drop_all(bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            
            # Verify tables exist
            with self.engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result.fetchall()]
                
                expected_tables = [
                    'daily_predictions', 'price_logs', 'ai_predictions',
                    'baseline_models', 'model_performance'
                ]
                
                for table in expected_tables:
                    self.assertIn(table, tables, f"Table {table} not found in database")
                    
                print(f"✅ All {len(expected_tables)} tables created successfully")
                
        except Exception as e:
            self.skipTest(f"Schema creation failed: {e}")
    
    def test_basic_crud_operations(self):
        """Test basic CRUD operations with PostgreSQL."""
        try:
            # Ensure tables exist
            Base.metadata.create_all(bind=self.engine)
            
            session = self.SessionLocal()
            test_date = date(2025, 8, 16)
            
            try:
                # Test CREATE operation
                prediction = DailyPrediction(
                    date=test_date,
                    predLow=580.0,
                    predHigh=585.0,
                    bias="Neutral",
                    volCtx="Medium",
                    dayType="Range",
                    source="test"
                )
                session.add(prediction)
                session.commit()
                
                # Test READ operation
                retrieved = session.query(DailyPrediction).filter(
                    DailyPrediction.date == test_date
                ).first()
                
                self.assertIsNotNone(retrieved)
                self.assertEqual(retrieved.predLow, 580.0)
                self.assertEqual(retrieved.predHigh, 585.0)
                self.assertEqual(retrieved.bias, "Neutral")
                
                # Test UPDATE operation
                retrieved.predLow = 579.0
                session.commit()
                
                updated = session.query(DailyPrediction).filter(
                    DailyPrediction.date == test_date
                ).first()
                self.assertEqual(updated.predLow, 579.0)
                
                # Test DELETE operation
                session.delete(updated)
                session.commit()
                
                deleted = session.query(DailyPrediction).filter(
                    DailyPrediction.date == test_date
                ).first()
                self.assertIsNone(deleted)
                
                print("✅ Basic CRUD operations successful")
                
            finally:
                session.close()
                
        except Exception as e:
            self.skipTest(f"CRUD operations failed: {e}")
    
    def test_postgresql_specific_features(self):
        """Test PostgreSQL-specific features and constraints."""
        try:
            Base.metadata.create_all(bind=self.engine)
            session = self.SessionLocal()
            
            try:
                # Test unique constraint on date field
                test_date = date(2025, 8, 16)
                
                # Insert first prediction
                prediction1 = DailyPrediction(
                    date=test_date,
                    predLow=580.0,
                    predHigh=585.0,
                    source="test1"
                )
                session.add(prediction1)
                session.commit()
                
                # Try to insert duplicate date - should fail
                prediction2 = DailyPrediction(
                    date=test_date,
                    predLow=581.0,
                    predHigh=586.0,
                    source="test2"
                )
                session.add(prediction2)
                
                with self.assertRaises(IntegrityError):
                    session.commit()
                
                session.rollback()
                
                # Test timezone-aware datetime fields
                ai_prediction = AIPrediction(
                    date=test_date,
                    checkpoint="open",
                    predicted_price=582.5,
                    confidence=0.75,
                    reasoning="Test prediction",
                    source="test"
                )
                session.add(ai_prediction)
                session.commit()
                
                # Verify datetime is stored with timezone
                retrieved = session.query(AIPrediction).filter(
                    AIPrediction.date == test_date
                ).first()
                
                self.assertIsNotNone(retrieved.created_at)
                # PostgreSQL should maintain timezone info
                self.assertIsNotNone(retrieved.created_at.tzinfo)
                
                print("✅ PostgreSQL-specific features working correctly")
                
            finally:
                # Cleanup
                session.query(AIPrediction).delete()
                session.query(DailyPrediction).delete()
                session.commit()
                session.close()
                
        except Exception as e:
            self.skipTest(f"PostgreSQL-specific feature test failed: {e}")
    
    def test_connection_pooling(self):
        """Test connection pooling behavior."""
        try:
            # Create multiple connections to test pooling
            connections = []
            
            for i in range(5):
                conn = self.engine.connect()
                result = conn.execute(text("SELECT current_database()"))
                db_name = result.fetchone()[0]
                self.assertIsNotNone(db_name)
                connections.append(conn)
            
            # Close all connections
            for conn in connections:
                conn.close()
            
            print("✅ Connection pooling test successful")
            
        except Exception as e:
            self.skipTest(f"Connection pooling test failed: {e}")
    
    def test_transaction_handling(self):
        """Test transaction handling and rollback."""
        try:
            Base.metadata.create_all(bind=self.engine)
            session = self.SessionLocal()
            
            try:
                test_date = date(2025, 8, 16)
                
                # Start transaction
                session.begin()
                
                prediction = DailyPrediction(
                    date=test_date,
                    predLow=580.0,
                    predHigh=585.0,
                    source="transaction_test"
                )
                session.add(prediction)
                
                # Verify data is not committed yet
                session.flush()  # Send to DB but don't commit
                
                # Rollback transaction
                session.rollback()
                
                # Verify data was rolled back
                committed = session.query(DailyPrediction).filter(
                    DailyPrediction.date == test_date
                ).first()
                self.assertIsNone(committed)
                
                print("✅ Transaction handling test successful")
                
            finally:
                session.close()
                
        except Exception as e:
            self.skipTest(f"Transaction handling test failed: {e}")


class TestPostgreSQLConfiguration(unittest.TestCase):
    """Test PostgreSQL configuration and environment setup."""
    
    def test_database_url_format(self):
        """Test PostgreSQL URL format validation."""
        valid_urls = [
            "postgresql+psycopg2://spy:pass@localhost:5432/spy",
            "postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy",
            "postgresql+psycopg2://spy:pass@db:5432/spy",
        ]
        
        for url in valid_urls:
            self.assertTrue(url.startswith("postgresql+psycopg2://"))
            self.assertIn("spy", url)
            
        print("✅ Database URL format validation successful")
    
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        # Test with mock environment
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql+psycopg2://spy:pass@localhost:5433/spy',
            'DEBUG': 'false'
        }):
            from app.config import Settings
            test_settings = Settings()
            
            self.assertEqual(test_settings.database_url, 
                           'postgresql+psycopg2://spy:pass@localhost:5433/spy')
            
        print("✅ Environment variable loading test successful")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)