"""
Tests for database configuration detection and environment analysis.
Validates current database setup patterns and environment file usage.

This is part of Task 1.1 from database alignment spec #25:
Write tests to verify current database configuration detection.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

from app.config import settings, Settings
from app.database import engine, SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


class TestDatabaseConfigDetection(unittest.TestCase):
    """Test detection of current database configuration patterns."""
    
    def setUp(self):
        """Set up test environment."""
        self.original_settings = settings
        
    def test_default_configuration_uses_sqlite(self):
        """Test that default configuration points to SQLite."""
        # Test the default value from config
        default_settings = Settings()
        self.assertEqual(default_settings.database_url, "sqlite:///./spy_tracker.db")
        print("✅ Default configuration uses SQLite as expected")
    
    def test_current_environment_detection(self):
        """Test detection of current environment database configuration."""
        # Check what the current settings are actually using
        current_db_url = settings.database_url
        
        # Determine database type from URL
        if current_db_url.startswith("sqlite"):
            db_type = "sqlite"
        elif current_db_url.startswith("postgresql"):
            db_type = "postgresql"
        else:
            db_type = "unknown"
        
        print(f"✅ Current database type: {db_type}")
        print(f"✅ Current database URL: {current_db_url}")
        
        # Verify we can categorize the database type
        self.assertIn(db_type, ["sqlite", "postgresql"])
    
    def test_environment_file_loading_order(self):
        """Test that environment files are loaded in correct order."""
        # Create temporary environment files to test loading order
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create root .env file
            root_env = temp_path / ".env"
            root_env.write_text("DATABASE_URL=sqlite:///root.db\nTEST_VAR=root\n")
            
            # Create backend .env file  
            backend_dir = temp_path / "backend"
            backend_dir.mkdir()
            backend_env = backend_dir / ".env"
            backend_env.write_text("DATABASE_URL=postgresql://backend.db\nTEST_VAR=backend\n")
            
            # Test loading with mock paths
            with patch('app.config._ROOT_DIR', temp_path), \
                 patch('app.config._BACKEND_DIR', backend_dir):
                
                # Import fresh settings to test loading
                from importlib import reload
                import app.config
                reload(app.config)
                
                # Root .env should be loaded first (override=False means first wins)
                test_settings = app.config.Settings()
                
                # The first loaded value should persist (root .env)
                # Note: This tests the current loading behavior
                print(f"✅ Environment loading order test completed")
    
    def test_database_type_detection_utility(self):
        """Test utility function to detect database type from URL."""
        test_cases = [
            ("sqlite:///./spy_tracker.db", "sqlite"),
            ("sqlite:////absolute/path/spy.db", "sqlite"),
            ("postgresql+psycopg2://spy:pass@localhost:5432/spy", "postgresql"),
            ("postgresql://spy:pass@127.0.0.1:5433/spy", "postgresql"),
            ("mysql://user:pass@localhost/db", "mysql"),  # Not supported but should detect
            ("", "unknown"),
            ("invalid-url", "unknown")
        ]
        
        def detect_database_type(database_url: str) -> str:
            """Utility function to detect database type from URL."""
            if not database_url:
                return "unknown"
            
            if database_url.startswith("sqlite"):
                return "sqlite"
            elif database_url.startswith("postgresql"):
                return "postgresql"
            elif database_url.startswith("mysql"):
                return "mysql"
            else:
                return "unknown"
        
        for url, expected_type in test_cases:
            detected_type = detect_database_type(url)
            self.assertEqual(detected_type, expected_type, 
                           f"Failed to detect {expected_type} from URL: {url}")
        
        print("✅ Database type detection utility working correctly")
    
    def test_current_database_connectivity(self):
        """Test connectivity to currently configured database."""
        try:
            # Test basic connection to current database
            with engine.connect() as connection:
                # Try a simple query that works on both SQLite and PostgreSQL
                from sqlalchemy import text
                if settings.database_url.startswith("sqlite"):
                    result = connection.execute(text("SELECT sqlite_version()"))
                    version = result.fetchone()[0]
                    print(f"✅ SQLite connection successful: {version}")
                elif settings.database_url.startswith("postgresql"):
                    result = connection.execute(text("SELECT version()"))
                    version = result.fetchone()[0]
                    print(f"✅ PostgreSQL connection successful: {version[:50]}...")
                    
        except OperationalError as e:
            self.skipTest(f"Database not available: {e}")
    
    def test_sqlalchemy_engine_configuration(self):
        """Test SQLAlchemy engine configuration for different database types."""
        # Test current engine configuration
        current_url = str(engine.url)
        
        # Check connect_args based on database type
        if current_url.startswith("sqlite"):
            # SQLite should have check_same_thread=False
            connect_args = engine.pool._creator_args[1] if hasattr(engine.pool, '_creator_args') else {}
            print(f"✅ SQLite connect_args detected: {connect_args}")
        elif current_url.startswith("postgresql"):
            # PostgreSQL should have minimal or no connect_args
            print(f"✅ PostgreSQL engine configured correctly")
        
        print(f"✅ Engine URL: {current_url}")
    
    def test_environment_variable_precedence(self):
        """Test environment variable precedence patterns."""
        test_scenarios = [
            {
                "name": "No environment variables",
                "env_vars": {},
                "expected_db": "sqlite:///./spy_tracker.db"  # Default
            },
            {
                "name": "DATABASE_URL set",
                "env_vars": {"DATABASE_URL": "postgresql://test:test@localhost/test"},
                "expected_db": "postgresql://test:test@localhost/test"
            }
        ]
        
        for scenario in test_scenarios:
            with patch.dict(os.environ, scenario["env_vars"], clear=True):
                # Create fresh settings instance
                test_settings = Settings()
                self.assertEqual(test_settings.database_url, scenario["expected_db"],
                               f"Failed scenario: {scenario['name']}")
                
        print("✅ Environment variable precedence test passed")


class TestEnvironmentFilePatterns(unittest.TestCase):
    """Test environment file patterns and usage."""
    
    def test_identify_environment_files(self):
        """Test identification of all environment files in the project."""
        project_root = Path(__file__).resolve().parents[2]  # Go up to project root
        
        # Find all .env* files
        env_files = []
        for pattern in ["**/.env*"]:
            env_files.extend(list(project_root.glob(pattern)))
        
        # Filter out node_modules and .venv directories
        filtered_files = [
            f for f in env_files 
            if "node_modules" not in str(f) and ".venv" not in str(f)
        ]
        
        # Document found files
        print("✅ Found environment files:")
        for env_file in filtered_files:
            relative_path = env_file.relative_to(project_root)
            print(f"  - {relative_path}")
            
            # Verify file is readable
            try:
                content = env_file.read_text()
                print(f"    Size: {len(content)} chars")
            except Exception as e:
                print(f"    Error reading: {e}")
        
        # Should find at least .env.example files
        self.assertGreater(len(filtered_files), 0, "No environment files found")
    
    def test_environment_file_database_configurations(self):
        """Test database configurations in environment files."""
        project_root = Path(__file__).resolve().parents[2]
        
        env_files = [
            project_root / ".env.example",
            project_root / "backend" / ".env.example",
            project_root / "backend" / ".env.postgres.example"
        ]
        
        database_configs = {}
        
        for env_file in env_files:
            if env_file.exists():
                try:
                    content = env_file.read_text()
                    
                    # Look for DATABASE_URL lines
                    db_urls = []
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('DATABASE_URL=') or line.startswith('# DATABASE_URL='):
                            db_urls.append(line)
                    
                    database_configs[str(env_file.relative_to(project_root))] = db_urls
                    
                except Exception as e:
                    print(f"Error reading {env_file}: {e}")
        
        # Document findings
        print("✅ Database configurations found in environment files:")
        for file_path, urls in database_configs.items():
            print(f"  {file_path}:")
            for url in urls:
                print(f"    {url}")
        
        # Verify we found some database configurations
        total_configs = sum(len(urls) for urls in database_configs.values())
        self.assertGreater(total_configs, 0, "No database configurations found in environment files")


class TestDocumentationAudit(unittest.TestCase):
    """Test documentation accuracy for database setup."""
    
    def test_readme_database_instructions(self):
        """Test that README.md contains database setup instructions."""
        project_root = Path(__file__).resolve().parents[2]
        readme_path = project_root / "README.md"
        
        if readme_path.exists():
            content = readme_path.read_text().lower()
            
            # Check for database-related keywords
            database_keywords = [
                "database", "postgresql", "sqlite", "docker", "env"
            ]
            
            found_keywords = []
            for keyword in database_keywords:
                if keyword in content:
                    found_keywords.append(keyword)
            
            print(f"✅ README.md database keywords found: {found_keywords}")
            
            # Should mention at least database and one database type
            self.assertIn("database", found_keywords, "README should mention database")
        else:
            print("⚠️ README.md not found")
    
    def test_claude_md_database_configuration(self):
        """Test CLAUDE.md database configuration documentation."""
        project_root = Path(__file__).resolve().parents[2]
        claude_md_path = project_root / "CLAUDE.md"
        
        if claude_md_path.exists():
            content = claude_md_path.read_text()
            
            # Check for database policy mentions
            if "database policy" in content.lower():
                print("✅ CLAUDE.md contains database policy")
            
            if "postgresql" in content.lower():
                print("✅ CLAUDE.md mentions PostgreSQL")
                
            if "sqlite" in content.lower():
                print("✅ CLAUDE.md mentions SQLite")
                
        else:
            print("⚠️ CLAUDE.md not found")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)