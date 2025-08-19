#!/usr/bin/env python3
"""
EMERGENCY DATABASE RECOVERY SCRIPT
Fixes stuck transactions and restores database connectivity
"""

import os
import sys
import logging
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, InvalidRequestError
import time
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """Get database URL from environment or config."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Try loading from .env
        try:
            from dotenv import load_dotenv
            load_dotenv("backend/.env")
            database_url = os.getenv("DATABASE_URL")
        except:
            pass
    
    if not database_url:
        logger.error("DATABASE_URL not found in environment")
        sys.exit(1)
    
    # Handle Render.com's postgres:// URLs
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    return database_url

def reset_database_connections(engine):
    """Force reset all database connections."""
    logger.info("Resetting all database connections...")
    try:
        # Dispose of the connection pool
        engine.dispose()
        logger.info("✅ Connection pool disposed")
        
        # Create new connection to test
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"✅ New connection test successful: {result.scalar()}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to reset connections: {e}")
        return False

def rollback_stuck_transactions(engine):
    """Rollback any stuck transactions."""
    logger.info("Rolling back stuck transactions...")
    try:
        with engine.connect() as conn:
            # Get all active transactions
            result = conn.execute(text("""
                SELECT pid, state, query, state_change
                FROM pg_stat_activity
                WHERE state IN ('idle in transaction', 'idle in transaction (aborted)')
                AND pid <> pg_backend_pid()
            """))
            
            stuck_transactions = result.fetchall()
            
            if stuck_transactions:
                logger.warning(f"Found {len(stuck_transactions)} stuck transactions")
                
                for tx in stuck_transactions:
                    pid, state, query, state_change = tx
                    logger.info(f"  - PID {pid}: {state} since {state_change}")
                    logger.info(f"    Last query: {query[:100]}...")
                    
                    # Terminate the stuck connection
                    try:
                        conn.execute(text(f"SELECT pg_terminate_backend({pid})"))
                        logger.info(f"  ✅ Terminated PID {pid}")
                    except Exception as e:
                        logger.error(f"  ❌ Failed to terminate PID {pid}: {e}")
            else:
                logger.info("✅ No stuck transactions found")
            
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"❌ Failed to rollback transactions: {e}")
        return False

def verify_database_health(engine) -> bool:
    """Verify database is healthy and can perform operations."""
    logger.info("Verifying database health...")
    
    try:
        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT NOW()"))
            current_time = result.scalar()
            logger.info(f"✅ Database time: {current_time}")
            
            # Test table access
            result = conn.execute(text("""
                SELECT COUNT(*) FROM daily_predictions
            """))
            count = result.scalar()
            logger.info(f"✅ Daily predictions count: {count}")
            
            # Test transaction
            trans = conn.begin()
            conn.execute(text("SELECT 1"))
            trans.commit()
            logger.info("✅ Transaction test successful")
            
            return True
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return False

def create_recovery_engine():
    """Create a fresh database engine with recovery settings."""
    database_url = get_database_url()
    
    # Create engine with specific recovery settings
    engine = create_engine(
        database_url,
        poolclass=pool.NullPool,  # No connection pooling for recovery
        echo=False,
        connect_args={
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"  # 30 second statement timeout
        }
    )
    
    return engine

def generate_missing_predictions(engine, target_dates: list):
    """Generate predictions for missing dates."""
    logger.info(f"Generating predictions for dates: {target_dates}")
    
    try:
        # Import here to avoid circular imports
        from database import SessionLocal
        from ai_predictor import ai_predictor
        from models import DailyPrediction, AIPrediction
        from providers import default_provider
        
        db = SessionLocal()
        
        for target_date in target_dates:
            logger.info(f"Processing {target_date}...")
            
            # Check if prediction already exists
            existing = db.query(DailyPrediction).filter(
                DailyPrediction.date == target_date
            ).first()
            
            if existing and existing.predLow and existing.predHigh:
                logger.info(f"  ⚠️ Prediction already exists for {target_date}")
                continue
            
            try:
                # Get pre-market price
                pre_market = default_provider.get_price("SPY")
                
                # Generate AI predictions
                ai_result = ai_predictor.generate_predictions(target_date)
                
                # Create or update daily prediction
                if not existing:
                    existing = DailyPrediction(date=target_date)
                    db.add(existing)
                
                # Set baseline prediction values
                existing.preMarket = pre_market
                existing.source = "ai_recovery"
                
                # Extract predicted ranges from AI predictions
                for pred in ai_result.predictions:
                    if pred.checkpoint == "open":
                        existing.predLow = pred.predicted_price * 0.995  # -0.5%
                        existing.predHigh = pred.predicted_price * 1.005  # +0.5%
                        existing.open = pred.predicted_price
                    elif pred.checkpoint == "close":
                        existing.close = pred.predicted_price
                
                # Store AI predictions
                for pred in ai_result.predictions:
                    ai_pred = AIPrediction(
                        date=target_date,
                        checkpoint=pred.checkpoint,
                        predicted_price=pred.predicted_price,
                        confidence=pred.confidence,
                        reasoning=pred.reasoning,
                        interval_low=pred.interval_low,
                        interval_high=pred.interval_high,
                        source=pred.source,
                        model=pred.model
                    )
                    db.add(ai_pred)
                
                db.commit()
                logger.info(f"  ✅ Generated predictions for {target_date}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to generate predictions for {target_date}: {e}")
                db.rollback()
                
                # Try baseline prediction as fallback
                try:
                    if not existing:
                        existing = DailyPrediction(date=target_date)
                        db.add(existing)
                    
                    # Simple baseline
                    base_price = pre_market if pre_market else 580.0
                    existing.predLow = base_price * 0.99
                    existing.predHigh = base_price * 1.01
                    existing.preMarket = pre_market
                    existing.source = "baseline_recovery"
                    
                    db.commit()
                    logger.info(f"  ✅ Generated baseline predictions for {target_date}")
                except Exception as e2:
                    logger.error(f"  ❌ Baseline generation also failed: {e2}")
                    db.rollback()
        
        db.close()
        logger.info("✅ Prediction generation complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to generate predictions: {e}")
        return False

def main():
    """Main recovery process."""
    logger.info("=" * 60)
    logger.info("DATABASE RECOVERY SCRIPT STARTED")
    logger.info("=" * 60)
    
    # Create recovery engine
    engine = create_recovery_engine()
    
    # Step 1: Reset connections
    if not reset_database_connections(engine):
        logger.error("Failed to reset connections, trying rollback...")
    
    # Step 2: Rollback stuck transactions
    if not rollback_stuck_transactions(engine):
        logger.error("Failed to rollback transactions, continuing...")
    
    # Step 3: Reset connections again after rollback
    reset_database_connections(engine)
    
    # Step 4: Verify health
    if not verify_database_health(engine):
        logger.error("Database still unhealthy after recovery attempt!")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("✅ DATABASE RECOVERY SUCCESSFUL")
    logger.info("=" * 60)
    
    # Step 5: Generate missing predictions
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-predictions":
        # Generate for Monday and Tuesday
        target_dates = [
            date(2025, 8, 18),  # Monday
            date(2025, 8, 19),  # Tuesday
        ]
        
        logger.info("Generating missing predictions...")
        if generate_missing_predictions(engine, target_dates):
            logger.info("✅ Missing predictions generated")
        else:
            logger.error("❌ Failed to generate some predictions")
    
    engine.dispose()
    logger.info("Recovery script complete")

if __name__ == "__main__":
    main()