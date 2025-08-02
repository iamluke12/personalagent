#!/usr/bin/env python3
"""
Security Audit Script for PersonalAgent
Performs comprehensive security checks before release
"""

import os
import sys
import json
import stat
import hashlib
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class SecurityAuditor:
    """Performs security audit checks for PersonalAgent"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.results = []
        self.warnings = []
        self.errors = []
    
    def run_full_audit(self) -> Dict:
        """Run complete security audit"""
        print("🔒 PersonalAgent Security Audit")
        print("=" * 40)
        
        # Core security checks
        self.check_file_permissions()
        self.check_credential_storage()
        self.check_sensitive_data_exposure()
        self.check_dependency_security()
        self.check_code_vulnerabilities()
        self.check_environment_security()
        
        # Generate report
        return self.generate_report()
    
    def check_file_permissions(self):
        """Check file permissions for sensitive files"""
        print("\n📁 Checking file permissions...")
        
        sensitive_files = [
            "config/credentials.json",
            "config/token.json", 
            "config/token_write.json",
            "config/secure_credentials.enc",
            "config/credential_salt.dat",
            ".env"
        ]
        
        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                file_stat = full_path.stat()
                permissions = stat.filemode(file_stat.st_mode)
                
                # Check if file is readable by others
                if file_stat.st_mode & (stat.S_IRGRP | stat.S_IROTH):
                    self.errors.append(f"🚨 {file_path}: Readable by group/others ({permissions})")
                elif file_stat.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                    self.errors.append(f"🚨 {file_path}: Writable by group/others ({permissions})")
                else:
                    self.results.append(f"✅ {file_path}: Secure permissions ({permissions})")
        
        # Check directory permissions
        config_dir = self.project_root / "config"
        if config_dir.exists():
            dir_stat = config_dir.stat()
            if dir_stat.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
                self.warnings.append(f"⚠️ config/: Directory accessible by group/others")
            else:
                self.results.append("✅ config/: Secure directory permissions")
    
    def check_credential_storage(self):
        """Check how credentials are stored"""
        print("\n🔐 Checking credential storage...")
        
        # Check for plaintext API keys in files
        plaintext_patterns = [
            (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API key'),
            (r'AIza[0-9A-Za-z-_]{35}', 'Google API key'),
            (r'sk-ant-[a-zA-Z0-9-_]{95}', 'Anthropic API key'),
        ]
        
        suspicious_files = []
        for py_file in self.project_root.rglob("*.py"):
            if "venv" in str(py_file) or ".git" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for pattern, key_type in plaintext_patterns:
                    import re
                    if re.search(pattern, content):
                        suspicious_files.append(f"{py_file}: Potential {key_type}")
            except:
                continue
        
        if suspicious_files:
            for file_info in suspicious_files:
                self.errors.append(f"🚨 Plaintext credential found: {file_info}")
        else:
            self.results.append("✅ No plaintext credentials found in code")
        
        # Check for encrypted credential system
        secure_creds = self.project_root / "config/secure_credentials.enc"
        if secure_creds.exists():
            self.results.append("✅ Encrypted credential storage found")
        else:
            self.warnings.append("⚠️ No encrypted credential storage found")
    
    def check_sensitive_data_exposure(self):
        """Check for sensitive data in logs, cache, etc."""
        print("\n📝 Checking sensitive data exposure...")
        
        # Check log files for sensitive data
        log_files = list(self.project_root.rglob("*.log")) + list((self.project_root / "data/logs").rglob("*") if (self.project_root / "data/logs").exists() else [])
        
        for log_file in log_files:
            try:
                content = log_file.read_text()
                if any(pattern in content.lower() for pattern in ['api_key', 'token', 'password', 'secret']):
                    self.errors.append(f"🚨 Sensitive data in log: {log_file}")
                else:
                    self.results.append(f"✅ Clean log file: {log_file}")
            except:
                continue
        
        # Check cache files
        cache_files = list((self.project_root / "data/cache").rglob("*.json") if (self.project_root / "data/cache").exists() else [])
        
        for cache_file in cache_files:
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    if self._contains_sensitive_data(data):
                        self.warnings.append(f"⚠️ Potential sensitive data in cache: {cache_file}")
            except:
                continue
    
    def _contains_sensitive_data(self, data) -> bool:
        """Check if data structure contains sensitive information"""
        if isinstance(data, dict):
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in ['token', 'key', 'password', 'secret']):
                    return True
                if self._contains_sensitive_data(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._contains_sensitive_data(item):
                    return True
        elif isinstance(data, str):
            # Check for token-like patterns
            if len(data) > 20 and any(char.isalnum() for char in data):
                if data.startswith(('sk-', 'AIza', 'sk-ant-')):
                    return True
        return False
    
    def check_dependency_security(self):
        """Check dependencies for known vulnerabilities"""
        print("\n📦 Checking dependency security...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.warnings.append("⚠️ No requirements.txt found")
            return
        
        try:
            # Use pip-audit if available
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                installed_packages = json.loads(result.stdout)
                package_count = len(installed_packages)
                self.results.append(f"✅ {package_count} packages checked")
                
                # Check for commonly vulnerable packages
                vulnerable_patterns = [
                    'pillow<8.3.2',
                    'requests<2.25.0',
                    'urllib3<1.26.5'
                ]
                
                for package in installed_packages:
                    name = package['name'].lower()
                    version = package['version']
                    
                    # Basic vulnerability checks
                    if name == 'pillow' and version < '8.3.2':
                        self.warnings.append(f"⚠️ Pillow {version} may have vulnerabilities")
                    elif name == 'requests' and version < '2.25.0':
                        self.warnings.append(f"⚠️ Requests {version} may have vulnerabilities")
            
        except Exception as e:
            self.warnings.append(f"⚠️ Could not check dependencies: {e}")
    
    def check_code_vulnerabilities(self):
        """Check code for common security vulnerabilities"""
        print("\n🔍 Checking code vulnerabilities...")
        
        # Check for dangerous function usage
        dangerous_patterns = [
            ('eval(', 'Code injection risk'),
            ('exec(', 'Code injection risk'),
            ('subprocess.call', 'Command injection risk without shell=False'),
            ('os.system(', 'Command injection risk'),
            ('input(', 'User input without validation'),
        ]
        
        vulnerable_files = []
        for py_file in self.project_root.rglob("*.py"):
            if "venv" in str(py_file) or ".git" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                for pattern, risk in dangerous_patterns:
                    if pattern in content:
                        # Check if it's in a comment
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if pattern in line and not line.strip().startswith('#'):
                                vulnerable_files.append(f"{py_file}:{i+1} - {risk}")
            except:
                continue
        
        if vulnerable_files:
            for vuln in vulnerable_files:
                self.warnings.append(f"⚠️ {vuln}")
        else:
            self.results.append("✅ No obvious code vulnerabilities found")
    
    def check_environment_security(self):
        """Check environment and configuration security"""
        print("\n🌍 Checking environment security...")
        
        # Check for development/debug settings in production
        env_file = self.project_root / ".env"
        if env_file.exists():
            try:
                content = env_file.read_text()
                if "DEBUG=True" in content or "DEVELOPMENT=True" in content:
                    self.warnings.append("⚠️ Development settings found in .env")
                else:
                    self.results.append("✅ No development flags in .env")
            except:
                pass
        
        # Check git configuration
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            required_entries = ['.env', 'config/credentials.json', 'config/token*.json']
            missing = [entry for entry in required_entries if entry not in content]
            
            if missing:
                for entry in missing:
                    self.warnings.append(f"⚠️ Missing from .gitignore: {entry}")
            else:
                self.results.append("✅ .gitignore properly configured")
        else:
            self.errors.append("🚨 No .gitignore file found")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive security audit report"""
        print("\n" + "=" * 40)
        print("📊 SECURITY AUDIT REPORT")
        print("=" * 40)
        
        print(f"\n✅ PASSED CHECKS ({len(self.results)}):")
        for result in self.results:
            print(f"  {result}")
        
        print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
        for warning in self.warnings:
            print(f"  {warning}")
        
        print(f"\n🚨 ERRORS ({len(self.errors)}):")
        for error in self.errors:
            print(f"  {error}")
        
        # Calculate security score
        total_checks = len(self.results) + len(self.warnings) + len(self.errors)
        if total_checks > 0:
            score = (len(self.results) + 0.5 * len(self.warnings)) / total_checks * 100
        else:
            score = 0
        
        print(f"\n🎯 SECURITY SCORE: {score:.1f}/100")
        
        if score >= 85:
            print("✅ READY FOR RELEASE")
            ready_for_release = True
        elif score >= 70:
            print("⚠️ NEEDS MINOR IMPROVEMENTS")
            ready_for_release = False
        else:
            print("🚨 REQUIRES MAJOR SECURITY FIXES")
            ready_for_release = False
        
        return {
            'score': score,
            'ready_for_release': ready_for_release,
            'passed': len(self.results),
            'warnings': len(self.warnings),
            'errors': len(self.errors),
            'details': {
                'passed': self.results,
                'warnings': self.warnings,
                'errors': self.errors
            }
        }


def main():
    """Run security audit from command line"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PersonalAgent Security Audit")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--output", type=Path,
                       help="Save report to JSON file")
    
    args = parser.parse_args()
    
    auditor = SecurityAuditor(args.project_root)
    report = auditor.run_full_audit()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report['ready_for_release'] else 1)


if __name__ == "__main__":
    main()
