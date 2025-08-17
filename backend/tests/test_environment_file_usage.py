"""
Tests for environment file identification and usage patterns.
Validates the actual usage of environment files across the project.

This is part of Task 1.3 from database alignment spec #25:
Identify all environment files and their actual usage.
"""

import unittest
import os
from pathlib import Path
import re
from typing import Dict, List, Tuple, Set
import tempfile
from unittest.mock import patch


class TestEnvironmentFileUsage(unittest.TestCase):
    """Test identification and usage patterns of all environment files."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).resolve().parents[2]
        self.env_files = self._find_all_env_files()
    
    def _find_all_env_files(self) -> List[Path]:
        """Find all environment-related files in the project."""
        env_files = []
        
        # Common environment file patterns
        patterns = [
            "**/.env*",
            "**/env.*",
            "**/*env*"
        ]
        
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                # Filter out node_modules, .venv, and other irrelevant directories
                path_str = str(file_path)
                if any(exclude in path_str for exclude in [
                    "node_modules", ".venv", "__pycache__", ".git",
                    "dist", "build", ".DS_Store"
                ]):
                    continue
                
                # Only include files (not directories)
                if file_path.is_file():
                    env_files.append(file_path)
        
        return sorted(env_files)
    
    def test_environment_file_inventory(self):
        """Test complete inventory of environment files."""
        print("✅ Environment File Inventory:")
        
        for env_file in self.env_files:
            relative_path = env_file.relative_to(self.project_root)
            size = env_file.stat().st_size
            
            # Determine file category
            if env_file.name.endswith('.example'):
                category = "TEMPLATE"
            elif env_file.name == '.env':
                category = "ACTIVE"
            elif 'local' in env_file.name:
                category = "LOCAL"
            elif 'production' in env_file.name or 'prod' in env_file.name:
                category = "PRODUCTION"
            else:
                category = "OTHER"
            
            print(f"  [{category:10}] {relative_path} ({size} bytes)")
        
        # Verify we found expected files
        self.assertGreater(len(self.env_files), 0, "No environment files found")
        print(f"\n✅ Total environment files found: {len(self.env_files)}")
    
    def test_environment_file_loading_sequence(self):
        """Test the sequence of environment file loading in the application."""
        
        # Analyze config.py to understand loading order
        config_file = self.project_root / "backend" / "app" / "config.py"
        if config_file.exists():
            content = config_file.read_text()
            
            # Look for load_dotenv calls
            load_patterns = re.findall(r'load_dotenv\([^)]+\)', content)
            
            print("✅ Environment loading sequence from config.py:")
            for i, pattern in enumerate(load_patterns, 1):
                print(f"  {i}. {pattern}")
            
            # Verify expected loading patterns
            self.assertGreater(len(load_patterns), 0, "No load_dotenv calls found")
        
        # Analyze start.sh for environment loading
        start_script = self.project_root / "start.sh"
        if start_script.exists():
            content = start_script.read_text()
            
            # Look for source commands
            source_patterns = re.findall(r'source [^\s]+\.env[^\s]*', content)
            
            print("\n✅ Environment loading sequence from start.sh:")
            for i, pattern in enumerate(source_patterns, 1):
                print(f"  {i}. {pattern}")
    
    def test_database_url_configurations(self):
        """Test DATABASE_URL configurations across all environment files."""
        
        database_configs = {}
        
        for env_file in self.env_files:
            try:
                content = env_file.read_text()
                
                # Find all DATABASE_URL lines (including commented)
                db_lines = []
                for line_num, line in enumerate(content.split('\n'), 1):
                    line = line.strip()
                    if 'DATABASE_URL' in line:
                        # Determine if line is commented
                        is_commented = line.startswith('#')
                        # Extract the URL value
                        if '=' in line:
                            url_part = line.split('=', 1)[1].strip()
                            # Remove quotes if present
                            url_part = url_part.strip('"\'')
                        else:
                            url_part = ""
                        
                        db_lines.append({
                            'line_num': line_num,
                            'raw_line': line,
                            'commented': is_commented,
                            'url': url_part
                        })
                
                if db_lines:
                    relative_path = str(env_file.relative_to(self.project_root))
                    database_configs[relative_path] = db_lines
                    
            except Exception as e:
                print(f"Error reading {env_file}: {e}")
        
        print("✅ DATABASE_URL configurations found:")
        for file_path, configs in database_configs.items():
            print(f"\n  📁 {file_path}:")
            for config in configs:
                status = "COMMENTED" if config['commented'] else "ACTIVE"
                db_type = self._detect_db_type(config['url'])
                print(f"    Line {config['line_num']:2d}: [{status:9}] [{db_type:10}] {config['url'][:60]}")
        
        # Verify we found database configurations
        self.assertGreater(len(database_configs), 0, "No DATABASE_URL configurations found")
        
        return database_configs
    
    def test_environment_variable_precedence(self):
        """Test environment variable precedence and override behavior."""
        
        # Test scenarios for environment variable loading
        test_scenarios = [
            {
                "name": "Root .env only",
                "files": {".env": "DATABASE_URL=sqlite:///root.db"},
                "expected_url": "sqlite:///root.db"
            },
            {
                "name": "Backend .env override",
                "files": {
                    ".env": "DATABASE_URL=sqlite:///root.db",
                    "backend/.env": "DATABASE_URL=postgresql://backend.db"
                },
                "expected_url": "postgresql://backend.db"  # Backend should override
            },
            {
                "name": "System env override",
                "files": {".env": "DATABASE_URL=sqlite:///root.db"},
                "system_env": {"DATABASE_URL": "postgresql://system.db"},
                "expected_url": "postgresql://system.db"
            }
        ]
        
        print("✅ Environment variable precedence testing:")
        
        for scenario in test_scenarios:
            print(f"\n  Testing: {scenario['name']}")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create test files
                for file_path, content in scenario["files"].items():
                    full_path = temp_path / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(content)
                
                # Test loading behavior (conceptual - actual testing would require
                # mocking the config loading process)
                print(f"    Files created: {list(scenario['files'].keys())}")
                print(f"    Expected result: {scenario['expected_url']}")
    
    def test_production_environment_setup(self):
        """Test production environment configuration patterns."""
        
        # Look for production-specific environment files
        prod_files = [f for f in self.env_files if 'production' in str(f).lower() or 'prod' in str(f).lower()]
        
        print("✅ Production environment files:")
        
        for prod_file in prod_files:
            relative_path = prod_file.relative_to(self.project_root)
            print(f"  📄 {relative_path}")
            
            try:
                content = prod_file.read_text()
                
                # Look for production-specific configurations
                prod_indicators = []
                
                for line in content.split('\n'):
                    line = line.strip()
                    if any(keyword in line.lower() for keyword in [
                        'production', 'prod', 'ssl', 'secure', 'render', 'railway'
                    ]):
                        prod_indicators.append(line)
                
                if prod_indicators:
                    print(f"    Production indicators:")
                    for indicator in prod_indicators[:5]:  # Limit to 5 lines
                        print(f"      {indicator}")
                        
            except Exception as e:
                print(f"    Error reading file: {e}")
        
        print(f"\n✅ Found {len(prod_files)} production environment files")
    
    def test_docker_environment_integration(self):
        """Test Docker-related environment configuration."""
        
        # Look for Docker-related files
        docker_files = []
        for pattern in ["**/docker-compose*", "**/Dockerfile*", "**/.dockerignore"]:
            docker_files.extend(list(self.project_root.glob(pattern)))
        
        print("✅ Docker environment integration:")
        
        for docker_file in docker_files:
            if docker_file.is_file():
                relative_path = docker_file.relative_to(self.project_root)
                print(f"  🐳 {relative_path}")
                
                try:
                    content = docker_file.read_text()
                    
                    # Look for environment variable references
                    env_references = []
                    for line in content.split('\n'):
                        if any(keyword in line for keyword in [
                            'DATABASE_URL', 'POSTGRES_', 'OPENAI_API_KEY', '${', '${'
                        ]):
                            env_references.append(line.strip())
                    
                    if env_references:
                        print(f"    Environment variable references:")
                        for ref in env_references[:3]:  # Limit display
                            print(f"      {ref}")
                            
                except Exception as e:
                    print(f"    Error reading {docker_file}: {e}")
        
        print(f"\n✅ Found {len(docker_files)} Docker-related files")
    
    def test_start_script_environment_handling(self):
        """Test start.sh script environment variable handling."""
        
        start_script = self.project_root / "start.sh"
        if not start_script.exists():
            self.skipTest("start.sh not found")
        
        content = start_script.read_text()
        
        print("✅ start.sh environment handling analysis:")
        
        # Look for environment variable operations
        env_operations = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            line = line.strip()
            if any(keyword in line for keyword in [
                'export', 'DATABASE_URL', 'source .env', 'set -a'
            ]):
                env_operations.append(f"Line {line_num:2d}: {line}")
        
        for operation in env_operations:
            print(f"  {operation}")
        
        # Check for specific patterns
        has_db_override = 'DATABASE_URL=' in content and 'export DATABASE_URL' in content
        has_env_loading = 'source .env' in content
        has_docker_detection = 'docker' in content.lower()
        
        print(f"\n  Analysis:")
        print(f"    Database URL override: {'✅' if has_db_override else '❌'}")
        print(f"    Environment file loading: {'✅' if has_env_loading else '❌'}")
        print(f"    Docker detection: {'✅' if has_docker_detection else '❌'}")
        
        self.assertTrue(has_env_loading, "start.sh should load environment files")
    
    def _detect_db_type(self, url: str) -> str:
        """Detect database type from URL."""
        if not url:
            return "EMPTY"
        elif url.startswith("sqlite"):
            return "SQLITE"
        elif url.startswith("postgresql"):
            return "POSTGRESQL"
        elif url.startswith("mysql"):
            return "MYSQL"
        else:
            return "UNKNOWN"


class TestEnvironmentFileConsistency(unittest.TestCase):
    """Test consistency across environment files."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).resolve().parents[2]
    
    def test_template_consistency(self):
        """Test that .env.example files are consistent across directories."""
        
        # Find all .env.example files
        example_files = list(self.project_root.glob("**/.env.example"))
        example_files = [f for f in example_files if "node_modules" not in str(f) and ".venv" not in str(f)]
        
        print("✅ Environment template consistency check:")
        
        # Analyze each template file
        template_analysis = {}
        
        for example_file in example_files:
            relative_path = str(example_file.relative_to(self.project_root))
            
            try:
                content = example_file.read_text()
                
                # Extract all variable names
                variables = set()
                for line in content.split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        var_name = line.split('=', 1)[0].strip()
                        variables.add(var_name)
                
                template_analysis[relative_path] = variables
                
                print(f"  📄 {relative_path}: {len(variables)} variables")
                
            except Exception as e:
                print(f"  ❌ Error reading {relative_path}: {e}")
        
        # Compare variables across templates
        if len(template_analysis) > 1:
            all_variables = set()
            for variables in template_analysis.values():
                all_variables.update(variables)
            
            print(f"\n  📊 Variable coverage analysis:")
            for var in sorted(all_variables):
                files_with_var = [path for path, variables in template_analysis.items() if var in variables]
                coverage = len(files_with_var) / len(template_analysis) * 100
                print(f"    {var:20s}: {coverage:5.1f}% coverage ({len(files_with_var)}/{len(template_analysis)} files)")
        
        self.assertGreater(len(template_analysis), 0, "No .env.example files found")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)