#!/usr/bin/env python3
"""
Cross-Platform Testing Script for PersonalAgent
Tests compatibility across different platforms and Python versions
"""

import os
import sys
import json
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

class CrossPlatformTester:
    """Tests PersonalAgent compatibility across platforms"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.test_results = []
        self.platform_info = self._get_platform_info()
    
    def _get_platform_info(self) -> Dict:
        """Gather current platform information"""
        return {
            'system': platform.system(),
            'platform': platform.platform(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'architecture': platform.architecture(),
        }
    
    def run_compatibility_tests(self) -> Dict:
        """Run comprehensive cross-platform compatibility tests"""
        print("🌍 PersonalAgent Cross-Platform Testing")
        print("=" * 45)
        print(f"Platform: {self.platform_info['system']} {self.platform_info['machine']}")
        print(f"Python: {self.platform_info['python_version']}")
        print()
        
        # Core compatibility tests
        self.test_python_version()
        self.test_shell_compatibility()
        self.test_path_handling()
        self.test_file_permissions()
        self.test_dependency_installation()
        self.test_core_functionality()
        self.test_calendar_integration()
        self.test_alias_system()
        
        return self.generate_report()
    
    def test_python_version(self):
        """Test Python version compatibility"""
        print("🐍 Testing Python version compatibility...")
        
        current_version = tuple(map(int, platform.python_version().split('.')))
        required_version = (3, 8)
        
        if current_version >= required_version:
            self.test_results.append({
                'test': 'python_version',
                'status': 'pass',
                'message': f"Python {platform.python_version()} ✅"
            })
        else:
            self.test_results.append({
                'test': 'python_version',
                'status': 'fail',
                'message': f"Python {platform.python_version()} < 3.8 ❌"
            })
        
        # Test specific Python features we use
        features_to_test = [
            ('pathlib.Path', lambda: Path('.').exists()),
            ('subprocess.run', lambda: subprocess.run(['echo', 'test'], capture_output=True)),
            ('json.loads', lambda: json.loads('{\"test\": true}')),
            ('f-strings', lambda: eval('f\"test {1+1}\"')),
        ]
        
        for feature_name, test_func in features_to_test:
            try:
                test_func()
                self.test_results.append({
                    'test': f'python_feature_{feature_name}',
                    'status': 'pass',
                    'message': f"{feature_name} available ✅"
                })
            except Exception as e:
                self.test_results.append({
                    'test': f'python_feature_{feature_name}',
                    'status': 'fail',
                    'message': f"{feature_name} failed: {e} ❌"
                })
    
    def test_shell_compatibility(self):
        """Test shell compatibility and alias support"""
        print("💻 Testing shell compatibility...")
        
        # Detect current shell
        shell_path = os.environ.get('SHELL', '')
        shell_name = Path(shell_path).name if shell_path else 'unknown'
        
        self.test_results.append({
            'test': 'shell_detection',
            'status': 'info',
            'message': f"Detected shell: {shell_name}"
        })
        
        # Test shell-specific features
        shell_tests = {
            'zsh': self._test_zsh_features,
            'bash': self._test_bash_features,
            'fish': self._test_fish_features,
        }
        
        if shell_name in shell_tests:
            shell_tests[shell_name]()
        else:
            self.test_results.append({
                'test': 'shell_support',
                'status': 'warning',
                'message': f"Untested shell: {shell_name} ⚠️"
            })
        
        # Test environment variable handling
        test_var = 'PERSONALAGENT_TEST_VAR'
        test_value = 'test_value_12345'
        
        try:
            os.environ[test_var] = test_value
            if os.environ.get(test_var) == test_value:
                self.test_results.append({
                    'test': 'env_variables',
                    'status': 'pass',
                    'message': "Environment variables working ✅"
                })
            del os.environ[test_var]
        except Exception as e:
            self.test_results.append({
                'test': 'env_variables',
                'status': 'fail',
                'message': f"Environment variables failed: {e} ❌"
            })
    
    def _test_zsh_features(self):
        """Test zsh-specific features"""
        try:
            # Test alias creation
            result = subprocess.run(['zsh', '-c', 'alias test_alias=\"echo test\"'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.test_results.append({
                    'test': 'zsh_aliases',
                    'status': 'pass',
                    'message': "ZSH alias support ✅"
                })
            else:
                self.test_results.append({
                    'test': 'zsh_aliases',
                    'status': 'fail',
                    'message': "ZSH alias support failed ❌"
                })
        except Exception as e:
            self.test_results.append({
                'test': 'zsh_features',
                'status': 'warning',
                'message': f"ZSH testing limited: {e} ⚠️"
            })
    
    def _test_bash_features(self):
        """Test bash-specific features"""
        try:
            result = subprocess.run(['bash', '-c', 'alias test_alias=\"echo test\"'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.test_results.append({
                    'test': 'bash_aliases',
                    'status': 'pass',
                    'message': "Bash alias support ✅"
                })
        except Exception as e:
            self.test_results.append({
                'test': 'bash_features',
                'status': 'warning',
                'message': f"Bash testing limited: {e} ⚠️"
            })
    
    def _test_fish_features(self):
        """Test fish shell features"""
        try:
            result = subprocess.run(['fish', '-c', 'function test_func; echo test; end'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.test_results.append({
                    'test': 'fish_functions',
                    'status': 'pass',
                    'message': "Fish function support ✅"
                })
        except Exception as e:
            self.test_results.append({
                'test': 'fish_features',
                'status': 'warning',
                'message': f"Fish testing limited: {e} ⚠️"
            })
    
    def test_path_handling(self):
        """Test cross-platform path handling"""
        print("📁 Testing path handling...")
        
        # Test path separators
        test_path = Path("config") / "test_file.json"
        expected_separator = '\\\\' if platform.system() == 'Windows' else '/'
        
        if str(test_path).replace('\\\\', '/').replace('\\', '/') == "config/test_file.json":
            self.test_results.append({
                'test': 'path_handling',
                'status': 'pass',
                'message': "Path handling working ✅"
            })
        else:
            self.test_results.append({
                'test': 'path_handling',
                'status': 'fail',
                'message': f"Path handling issue: {test_path} ❌"
            })
        
        # Test home directory expansion
        try:
            home_path = Path.home()
            if home_path.exists():
                self.test_results.append({
                    'test': 'home_directory',
                    'status': 'pass',
                    'message': f"Home directory: {home_path} ✅"
                })
        except Exception as e:
            self.test_results.append({
                'test': 'home_directory',
                'status': 'fail',
                'message': f"Home directory failed: {e} ❌"
            })
    
    def test_file_permissions(self):
        """Test file permission handling"""
        print("🔒 Testing file permissions...")
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            # Test basic file operations
            tmp_path.write_text("test content")
            content = tmp_path.read_text()
            
            if content == "test content":
                self.test_results.append({
                    'test': 'file_operations',
                    'status': 'pass',
                    'message': "File operations working ✅"
                })
            
            # Test permission changes (Unix-like systems only)
            if platform.system() != 'Windows':
                try:
                    os.chmod(tmp_path, 0o600)
                    stat_info = tmp_path.stat()
                    if oct(stat_info.st_mode)[-3:] == '600':
                        self.test_results.append({
                            'test': 'file_permissions',
                            'status': 'pass',
                            'message': "File permissions working ✅"
                        })
                except Exception as e:
                    self.test_results.append({
                        'test': 'file_permissions',
                        'status': 'fail',
                        'message': f"Permission setting failed: {e} ❌"
                    })
            else:
                self.test_results.append({
                    'test': 'file_permissions',
                    'status': 'info',
                    'message': "Windows: Permission testing skipped"
                })
        
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_dependency_installation(self):
        """Test if all dependencies can be imported"""
        print("📦 Testing dependency imports...")
        
        required_packages = [
            'google.oauth2',
            'googleapiclient',
            'requests',
            'dateutil',
            'dotenv',
        ]
        
        optional_packages = [
            'openai',
            'anthropic',
            'google.generativeai',
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.test_results.append({
                    'test': f'import_{package}',
                    'status': 'pass',
                    'message': f"✅ {package} imported successfully"
                })
            except ImportError as e:
                self.test_results.append({
                    'test': f'import_{package}',
                    'status': 'fail',
                    'message': f"❌ {package} failed: {e}"
                })
        
        for package in optional_packages:
            try:
                __import__(package)
                self.test_results.append({
                    'test': f'import_optional_{package}',
                    'status': 'pass',
                    'message': f"✅ {package} (optional) available"
                })
            except ImportError:
                self.test_results.append({
                    'test': f'import_optional_{package}',
                    'status': 'info',
                    'message': f"ℹ️ {package} (optional) not available"
                })
    
    def test_core_functionality(self):
        """Test core PersonalAgent functionality"""
        print("⚙️ Testing core functionality...")
        
        # Test profile manager import
        try:
            sys.path.insert(0, str(self.project_root / "src"))
            # Use explicit import to avoid conflict with Python's calendar module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "profileManager", 
                self.project_root / "src" / "calendar" / "profileManager.py"
            )
            profileManager = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(profileManager)
            
            self.test_results.append({
                'test': 'profile_manager_import',
                'status': 'pass',
                'message': "Profile manager import ✅"
            })
            
            # Test basic profile operations
            try:
                manager = profileManager.CalendarProfileManager()
                profiles = manager.list_profiles()
                
                self.test_results.append({
                    'test': 'profile_manager_basic',
                    'status': 'pass',
                    'message': f"Profile manager basic ops ✅ ({len(profiles)} profiles)"
                })
            except Exception as e:
                self.test_results.append({
                    'test': 'profile_manager_basic',
                    'status': 'warning',
                    'message': f"Profile manager limited: {e} ⚠️"
                })
                
        except Exception as e:
            self.test_results.append({
                'test': 'profile_manager_import',
                'status': 'fail',
                'message': f"Profile manager import failed: {e} ❌"
            })
    
    def test_calendar_integration(self):
        """Test Google Calendar integration basics"""
        print("📅 Testing calendar integration...")
        
        credentials_file = self.project_root / "config" / "credentials.json"
        
        if credentials_file.exists():
            self.test_results.append({
                'test': 'calendar_credentials',
                'status': 'pass',
                'message': "Calendar credentials found ✅"
            })
            
            # Test basic calendar service initialization
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
                
                self.test_results.append({
                    'test': 'calendar_api_import',
                    'status': 'pass',
                    'message': "Calendar API imports ✅"
                })
            except ImportError as e:
                self.test_results.append({
                    'test': 'calendar_api_import',
                    'status': 'fail',
                    'message': f"Calendar API import failed: {e} ❌"
                })
        else:
            self.test_results.append({
                'test': 'calendar_credentials',
                'status': 'info',
                'message': "No calendar credentials (setup required) ℹ️"
            })
    
    def test_alias_system(self):
        """Test the alias system compatibility"""
        print("🔗 Testing alias system...")
        
        aliases_file = self.project_root / "zshrc_aliases.txt"
        
        if aliases_file.exists():
            try:
                content = aliases_file.read_text()
                
                # Count aliases
                alias_count = content.count('alias ')
                
                self.test_results.append({
                    'test': 'alias_file',
                    'status': 'pass',
                    'message': f"Alias file found ({alias_count} aliases) ✅"
                })
                
                # Test for platform-specific issues
                if platform.system() == 'Windows' and 'python3' in content:
                    self.test_results.append({
                        'test': 'alias_windows_compat',
                        'status': 'warning',
                        'message': "Windows: python3 may need to be 'python' ⚠️"
                    })
                
            except Exception as e:
                self.test_results.append({
                    'test': 'alias_file',
                    'status': 'fail',
                    'message': f"Alias file read failed: {e} ❌"
                })
        else:
            self.test_results.append({
                'test': 'alias_file',
                'status': 'fail',
                'message': "Alias file not found ❌"
            })
    
    def generate_report(self) -> Dict:
        """Generate comprehensive compatibility report"""
        print("\n" + "=" * 45)
        print("📊 CROSS-PLATFORM COMPATIBILITY REPORT")
        print("=" * 45)
        
        # Categorize results
        passed = [r for r in self.test_results if r['status'] == 'pass']
        failed = [r for r in self.test_results if r['status'] == 'fail']
        warnings = [r for r in self.test_results if r['status'] == 'warning']
        info = [r for r in self.test_results if r['status'] == 'info']
        
        print(f"\n🌍 Platform: {self.platform_info['platform']}")
        print(f"🐍 Python: {self.platform_info['python_version']}")
        
        print(f"\n✅ PASSED ({len(passed)}):")
        for result in passed:
            print(f"  {result['message']}")
        
        print(f"\n⚠️ WARNINGS ({len(warnings)}):")
        for result in warnings:
            print(f"  {result['message']}")
        
        print(f"\nℹ️ INFO ({len(info)}):")
        for result in info:
            print(f"  {result['message']}")
        
        print(f"\n❌ FAILED ({len(failed)}):")
        for result in failed:
            print(f"  {result['message']}")
        
        # Calculate compatibility score
        total_critical = len(passed) + len(failed)
        if total_critical > 0:
            score = len(passed) / total_critical * 100
        else:
            score = 100
        
        print(f"\n🎯 COMPATIBILITY SCORE: {score:.1f}/100")
        
        compatible = len(failed) == 0
        if compatible:
            print("✅ PLATFORM COMPATIBLE")
        else:
            print("❌ COMPATIBILITY ISSUES FOUND")
        
        return {
            'platform': self.platform_info,
            'score': score,
            'compatible': compatible,
            'results': {
                'passed': len(passed),
                'failed': len(failed),
                'warnings': len(warnings),
                'info': len(info)
            },
            'details': self.test_results
        }


def main():
    """Run cross-platform testing from command line"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PersonalAgent Cross-Platform Testing")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--output", type=Path,
                       help="Save report to JSON file")
    
    args = parser.parse_args()
    
    tester = CrossPlatformTester(args.project_root)
    report = tester.run_compatibility_tests()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report['compatible'] else 1)


if __name__ == "__main__":
    main()
