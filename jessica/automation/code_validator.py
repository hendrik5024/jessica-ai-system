"""
Code Validator - Ensures generated code meets quality and safety standards
Validates syntax, imports, performance, and security
"""

import logging
import ast
import subprocess
import sys
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger("jessica.automation.code_validator")


class CodeValidator:
    """
    Validates code changes before deployment
    Checks:
    - Syntax validity
    - Import availability
    - Security issues
    - Performance impact
    - Backward compatibility
    """

    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
        
        # Dangerous operations that should trigger security warnings
        self.dangerous_operations = [
            'eval',
            'exec',
            'compile',
            '__import__',
            'globals()',
            'locals()',
            'vars()',
            'dir()',
            'getattr',
            'setattr',
            'delattr',
            'os.system',
            'subprocess.call',
            'subprocess.run',
            'open(',  # File operations
            'requests.post',  # Network operations
            'socket',
            'threading',
            'multiprocessing',
        ]
        
        logger.info("CodeValidator initialized")

    def validate_code(self, code: str) -> Dict:
        """
        Run all validation checks on code
        
        Returns:
            {
                'valid': bool,
                'syntax_valid': bool,
                'imports_valid': bool,
                'security': dict,
                'performance': dict,
                'errors': list,
                'warnings': list,
            }
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        result = {
            'valid': True,
            'syntax_valid': self.check_syntax(code),
            'imports_valid': self.check_imports(code),
            'security': self.check_security(code),
            'performance': self.check_performance(code),
            'complexity': self.check_complexity(code),
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
        }
        
        # Mark as invalid if any critical check failed
        if not result['syntax_valid'] or not result['imports_valid']:
            result['valid'] = False
        
        if result['security']['has_security_issues']:
            result['valid'] = False
        
        return result

    def check_syntax(self, code: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            logger.debug("Syntax validation passed")
            return True
        except SyntaxError as e:
            error_msg = f"Syntax error at line {e.lineno}: {e.msg}"
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Syntax check failed: {str(e)}"
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False

    def check_imports(self, code: str) -> bool:
        """Verify all imports are available"""
        try:
            tree = ast.parse(code)
            imports = []
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split('.')[0])
            
            # Check each import
            all_valid = True
            for imp in set(imports):
                try:
                    __import__(imp)
                except ImportError:
                    warning = f"Import not available: {imp}"
                    self.validation_warnings.append(warning)
                    logger.warning(warning)
                    all_valid = False
            
            if all_valid:
                logger.debug("Import validation passed")
            
            return all_valid
            
        except Exception as e:
            error_msg = f"Import check failed: {str(e)}"
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False

    def check_security(self, code: str) -> Dict:
        """Check for security issues"""
        security_issues = []
        
        # Check for dangerous operations
        for dangerous_op in self.dangerous_operations:
            if dangerous_op in code:
                security_issues.append(f"Potentially dangerous operation detected: {dangerous_op}")
        
        # Check for hardcoded secrets/passwords
        if re.search(r'(password|secret|token|api[_-]?key)\s*[=:]\s*["\']', code, re.IGNORECASE):
            security_issues.append("Possible hardcoded credentials detected")
        
        # Check for SQL injection patterns
        if 'SQL' in code and '%s' in code and 'format(' in code:
            security_issues.append("Potential SQL injection vulnerability detected")
        
        result = {
            'has_security_issues': len(security_issues) > 0,
            'issues': security_issues,
            'severity': 'high' if len(security_issues) > 0 else 'none',
        }
        
        if security_issues:
            for issue in security_issues:
                self.validation_warnings.append(issue)
                logger.warning(issue)
        else:
            logger.debug("Security check passed")
        
        return result

    def check_performance(self, code: str) -> Dict:
        """Check for potential performance issues"""
        performance_issues = []
        
        try:
            tree = ast.parse(code)
            
            # Check for nested loops
            loop_depth = 0
            max_loop_depth = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    loop_depth += 1
                    max_loop_depth = max(max_loop_depth, loop_depth)
            
            if max_loop_depth > 3:
                performance_issues.append(f"Deeply nested loops detected (depth: {max_loop_depth})")
            
            # Check for list comprehensions that might be inefficient
            if code.count('[') > 5 and code.count(']') > 5:
                performance_issues.append("Possible inefficient list operations")
            
            # Check for recursive calls without limits
            if 'def ' in code and 'recursion' in code.lower():
                performance_issues.append("Recursive function detected - ensure recursion limit")
            
            # Check function complexity (number of conditions)
            condition_count = code.count('if ') + code.count('elif ') + code.count('else:')
            if condition_count > 10:
                performance_issues.append(f"High cyclomatic complexity ({condition_count} conditions)")
            
        except Exception as e:
            logger.warning(f"Performance check partial failure: {e}")
        
        result = {
            'has_performance_issues': len(performance_issues) > 0,
            'issues': performance_issues,
        }
        
        if performance_issues:
            for issue in performance_issues:
                self.validation_warnings.append(issue)
                logger.warning(issue)
        else:
            logger.debug("Performance check passed")
        
        return result

    def check_complexity(self, code: str) -> Dict:
        """Check code complexity metrics"""
        try:
            tree = ast.parse(code)
            
            # Count functions
            function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            
            # Count classes
            class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            # Count lines
            lines = code.split('\n')
            code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            
            # Estimate complexity (McCabe)
            decision_points = (
                code.count('if ') + 
                code.count('elif ') + 
                code.count('except ') +
                code.count('for ') +
                code.count('while ') +
                code.count(' and ') +
                code.count(' or ')
            )
            
            complexity_score = decision_points + 1  # Base complexity is 1
            
            result = {
                'functions': function_count,
                'classes': class_count,
                'code_lines': code_lines,
                'decision_points': decision_points,
                'complexity_score': complexity_score,
                'complexity_level': self._rate_complexity(complexity_score),
            }
            
            if complexity_score > 20:
                self.validation_warnings.append(f"High complexity score: {complexity_score}")
            
            logger.debug(f"Complexity: {result}")
            return result
            
        except Exception as e:
            logger.warning(f"Complexity check failed: {e}")
            return {'error': str(e)}

    def check_backward_compatibility(self, old_code: str, new_code: str) -> Dict:
        """Check if new code maintains backward compatibility"""
        compatibility_issues = []
        
        try:
            old_tree = ast.parse(old_code)
            new_tree = ast.parse(new_code)
            
            # Extract function signatures from old code
            old_functions = {}
            for node in ast.walk(old_tree):
                if isinstance(node, ast.FunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    old_functions[node.name] = set(args)
            
            # Check new code maintains same function signatures
            new_functions = {}
            for node in ast.walk(new_tree):
                if isinstance(node, ast.FunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    new_functions[node.name] = set(args)
            
            # Check for removed functions
            for func_name in old_functions:
                if func_name not in new_functions:
                    compatibility_issues.append(f"Function removed: {func_name}")
            
            # Check for changed signatures
            for func_name in old_functions:
                if func_name in new_functions:
                    old_args = old_functions[func_name]
                    new_args = new_functions[func_name]
                    if old_args != new_args:
                        compatibility_issues.append(f"Function signature changed: {func_name}")
            
        except Exception as e:
            logger.warning(f"Compatibility check failed: {e}")
        
        return {
            'compatible': len(compatibility_issues) == 0,
            'issues': compatibility_issues,
        }

    def validate_file(self, file_path: str) -> Dict:
        """Validate a Python file"""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            return self.validate_code(code)
        except Exception as e:
            logger.error(f"Failed to validate file {file_path}: {e}")
            return {
                'valid': False,
                'error': str(e),
            }

    def _rate_complexity(self, score: int) -> str:
        """Rate complexity based on score"""
        if score <= 5:
            return 'low'
        elif score <= 10:
            return 'moderate'
        elif score <= 20:
            return 'high'
        else:
            return 'very_high'

    def get_validation_report(self) -> str:
        """Generate human-readable validation report"""
        report = "VALIDATION REPORT\n"
        report += "=" * 50 + "\n\n"
        
        if self.validation_errors:
            report += "ERRORS:\n"
            for error in self.validation_errors:
                report += f"  ✗ {error}\n"
            report += "\n"
        
        if self.validation_warnings:
            report += "WARNINGS:\n"
            for warning in self.validation_warnings:
                report += f"  ⚠ {warning}\n"
            report += "\n"
        
        if not self.validation_errors and not self.validation_warnings:
            report += "✓ All validations passed!\n"
        
        return report
