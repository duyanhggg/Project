#!/usr/bin/env python3
"""
Unit tests for code_generator.py
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Import the module to test
sys.path.insert(0, os.path.dirname(__file__))
import code_generator


class TestCodeGenerator(unittest.TestCase):
    """Test cases for code generator tool"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment after each test"""
        # Remove the temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_get_current_date(self):
        """Test date formatting function"""
        date = code_generator.get_current_date()
        self.assertIsInstance(date, str)
        self.assertRegex(date, r'\d{4}-\d{2}-\d{2}')
    
    def test_get_classname_from_filename(self):
        """Test Java class name generation"""
        # Test with PascalCase
        self.assertEqual(code_generator.get_classname_from_filename('HelloWorld'), 'HelloWorld')
        
        # Test with snake_case
        self.assertEqual(code_generator.get_classname_from_filename('hello_world'), 'HelloWorld')
        
        # Test with kebab-case
        self.assertEqual(code_generator.get_classname_from_filename('hello-world'), 'HelloWorld')
        
        # Test with .java extension
        self.assertEqual(code_generator.get_classname_from_filename('HelloWorld.java'), 'HelloWorld')
    
    def test_create_python_file(self):
        """Test Python file generation"""
        success, message = code_generator.create_file('python', 'test_script', self.test_dir)
        
        self.assertTrue(success)
        self.assertIn('Success', message)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'test_script.py')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('#!/usr/bin/env python3', content)
            self.assertIn('def main():', content)
            self.assertIn('if __name__ == "__main__":', content)
    
    def test_create_javascript_file(self):
        """Test JavaScript file generation"""
        success, message = code_generator.create_file('javascript', 'app', self.test_dir)
        
        self.assertTrue(success)
        self.assertIn('Success', message)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'app.js')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('function main()', content)
            self.assertIn('console.log', content)
    
    def test_create_java_file(self):
        """Test Java file generation"""
        success, message = code_generator.create_file('java', 'HelloWorld', self.test_dir)
        
        self.assertTrue(success)
        self.assertIn('Success', message)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'HelloWorld.java')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('public class HelloWorld', content)
            self.assertIn('public static void main', content)
    
    def test_create_typescript_file(self):
        """Test TypeScript file generation"""
        success, message = code_generator.create_file('typescript', 'index', self.test_dir)
        
        self.assertTrue(success)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'index.ts')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('function main(): void', content)
    
    def test_create_cpp_file(self):
        """Test C++ file generation"""
        success, message = code_generator.create_file('cpp', 'main', self.test_dir)
        
        self.assertTrue(success)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'main.cpp')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('#include <iostream>', content)
            self.assertIn('int main()', content)
    
    def test_create_go_file(self):
        """Test Go file generation"""
        success, message = code_generator.create_file('go', 'server', self.test_dir)
        
        self.assertTrue(success)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'server.go')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('package main', content)
            self.assertIn('func main()', content)
    
    def test_create_rust_file(self):
        """Test Rust file generation"""
        success, message = code_generator.create_file('rust', 'main', self.test_dir)
        
        self.assertTrue(success)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'main.rs')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('fn main()', content)
            self.assertIn('println!', content)
    
    def test_create_php_file(self):
        """Test PHP file generation"""
        success, message = code_generator.create_file('php', 'index', self.test_dir)
        
        self.assertTrue(success)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'index.php')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('<?php', content)
            self.assertIn('function main()', content)
    
    def test_create_ruby_file(self):
        """Test Ruby file generation"""
        success, message = code_generator.create_file('ruby', 'script', self.test_dir)
        
        self.assertTrue(success)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'script.rb')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('#!/usr/bin/env ruby', content)
            self.assertIn('def main', content)
    
    def test_create_swift_file(self):
        """Test Swift file generation"""
        success, message = code_generator.create_file('swift', 'main', self.test_dir)
        
        self.assertTrue(success)
        
        # Check file exists
        filepath = os.path.join(self.test_dir, 'main.swift')
        self.assertTrue(os.path.exists(filepath))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('func main()', content)
            self.assertIn('print(', content)
    
    def test_unsupported_language(self):
        """Test error handling for unsupported language"""
        success, message = code_generator.create_file('cobol', 'test', self.test_dir)
        
        self.assertFalse(success)
        self.assertIn('Unsupported language', message)
    
    def test_file_already_exists(self):
        """Test error handling when file already exists"""
        # Create a file first
        code_generator.create_file('python', 'test', self.test_dir)
        
        # Try to create it again
        success, message = code_generator.create_file('python', 'test', self.test_dir)
        
        self.assertFalse(success)
        self.assertIn('already exists', message)
    
    def test_automatic_directory_creation(self):
        """Test automatic directory creation"""
        nested_dir = os.path.join(self.test_dir, 'src', 'utils')
        success, message = code_generator.create_file('python', 'helper', nested_dir)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.exists(os.path.join(nested_dir, 'helper.py')))
    
    def test_filename_with_extension(self):
        """Test that extension is not duplicated if provided"""
        success, message = code_generator.create_file('python', 'test.py', self.test_dir)
        
        self.assertTrue(success)
        
        # Should create test.py, not test.py.py
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'test.py')))
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, 'test.py.py')))
    
    def test_all_templates_have_required_fields(self):
        """Test that all templates have required structure"""
        for lang, template_info in code_generator.TEMPLATES.items():
            # Check extension exists
            self.assertIn('extension', template_info)
            self.assertIn('template', template_info)
            
            # Check extension format
            self.assertTrue(template_info['extension'].startswith('.'))
            
            # Check template has placeholders
            template = template_info['template']
            self.assertIn('{filename}', template)
            self.assertIn('{date}', template)


class TestTemplateQuality(unittest.TestCase):
    """Test cases for template code quality"""
    
    def test_all_languages_supported(self):
        """Test that all required languages are supported"""
        required_languages = [
            'python', 'javascript', 'typescript', 'java', 
            'cpp', 'go', 'rust', 'php', 'ruby', 'swift'
        ]
        
        for lang in required_languages:
            self.assertIn(lang, code_generator.TEMPLATES, 
                         f"Language {lang} is not supported")
    
    def test_extensions_are_correct(self):
        """Test that file extensions are correct"""
        expected_extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'go': '.go',
            'rust': '.rs',
            'php': '.php',
            'ruby': '.rb',
            'swift': '.swift'
        }
        
        for lang, expected_ext in expected_extensions.items():
            actual_ext = code_generator.TEMPLATES[lang]['extension']
            self.assertEqual(actual_ext, expected_ext,
                           f"Extension for {lang} should be {expected_ext}, got {actual_ext}")


if __name__ == '__main__':
    unittest.main()
