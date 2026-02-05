"""
Unit Tests for p1person
Tests core functionality of the application
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from attribute_manager import AttributeManager
from config_manager import ConfigManager
from pingone_client import PingOneClient


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / 'test_p1person.properties'
        self.key_path = Path(self.test_dir) / '.p1person.key'
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.config_path.exists():
            self.config_path.unlink()
        if self.key_path.exists():
            self.key_path.unlink()
        os.rmdir(self.test_dir)
    
    def test_config_exists_false(self):
        """Test config_exists returns False when file doesn't exist."""
        config_manager = ConfigManager(self.config_path)
        self.assertFalse(config_manager.config_exists())
    
    def test_encrypt_decrypt_secret(self):
        """Test encryption and decryption of secrets."""
        config_manager = ConfigManager(self.config_path)
        secret = "test_secret_12345"
        
        encrypted = config_manager._encrypt_secret(secret)
        decrypted = config_manager._decrypt_secret(encrypted)
        
        self.assertEqual(secret, decrypted)
        self.assertNotEqual(secret, encrypted)
    
    @patch('config_manager.input')
    @patch('config_manager._getpass_with_asterisks')
    def test_create_new_connection(self, mock_getpass, mock_input):
        """Test creating new connection configuration."""
        mock_input.side_effect = ['Test Env', 'env-id-123', 'client-id-456']
        mock_getpass.return_value = 'secret-789'
        
        config_manager = ConfigManager(self.config_path)
        config_manager.create_new_connection()
        
        self.assertTrue(config_manager.config_exists())
        
        config = config_manager.load_config()
        self.assertEqual(config['friendly_name'], 'Test Env')
        self.assertEqual(config['environment_id'], 'env-id-123')
        self.assertEqual(config['client_id'], 'client-id-456')
        self.assertEqual(config['client_secret'], 'secret-789')
    
    def test_load_config_not_found(self):
        """Test load_config raises error when file doesn't exist."""
        config_manager = ConfigManager(self.config_path)
        
        with self.assertRaises(FileNotFoundError):
            config_manager.load_config()
    
    def test_additional_attributes(self):
        """Test adding and retrieving additional attributes."""
        # Create initial config
        config_manager = ConfigManager(self.config_path)
        config = {
            'friendly_name': 'Test',
            'environment_id': 'env-123',
            'client_id': 'client-123',
            'client_secret_encrypted': config_manager._encrypt_secret('secret'),
            'additional_attributes': {}
        }
        config_manager._save_config(config)
        
        # Add attribute
        config_manager.add_additional_attribute('customAttr', 'Custom attribute description')
        
        # Retrieve attributes
        attrs = config_manager.get_additional_attributes()
        self.assertIn('customAttr', attrs)
        self.assertEqual(attrs['customAttr'], 'Custom attribute description')
    
    @patch('config_manager.input')
    @patch('config_manager._getpass_with_asterisks')
    def test_prompt_to_fix_config_missing_fields(self, mock_getpass, mock_input):
        """Test prompting for missing configuration fields."""
        # Create incomplete config
        config_manager = ConfigManager(self.config_path)
        config = {
            'friendly_name': 'Test',
            'additional_attributes': {}
        }
        config_manager._save_config(config)
        
        # Mock user input to fill missing fields
        mock_input.side_effect = ['y', 'env-id-123', 'client-id-456']
        mock_getpass.return_value = 'secret-789'
        
        # Load config with prompt_for_missing=True
        loaded_config = config_manager.load_config(prompt_for_missing=True)
        
        self.assertEqual(loaded_config['environment_id'], 'env-id-123')
        self.assertEqual(loaded_config['client_id'], 'client-id-456')
        self.assertEqual(loaded_config['client_secret'], 'secret-789')
    
    @patch('config_manager.input')
    @patch('config_manager._getpass_with_asterisks')
    def test_prompt_for_client_secret_only(self, mock_getpass, mock_input):
        """Test updating only the client secret."""
        # Create config with invalid encrypted secret
        config_manager = ConfigManager(self.config_path)
        config = {
            'friendly_name': 'Test',
            'environment_id': 'env-123',
            'client_id': 'client-123',
            'client_secret_encrypted': 'invalid_encrypted_data',
            'additional_attributes': {}
        }
        config_manager._save_config(config)
        
        # Mock user choosing to update secret
        mock_input.return_value = 'y'
        mock_getpass.return_value = 'new-secret-123'
        
        # Load config with prompt_for_missing=True (should handle decrypt failure)
        loaded_config = config_manager.load_config(prompt_for_missing=True)
        
        self.assertEqual(loaded_config['client_secret'], 'new-secret-123')


class TestPingOneClient(unittest.TestCase):
    """Test cases for PingOneClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'friendly_name': 'Test Environment',
            'environment_id': 'test-env-id',
            'client_id': 'test-client-id',
            'client_secret': 'test-secret'
        }
        self.mock_logger = Mock()
    
    def test_client_initialization(self):
        """Test PingOneClient initialization."""
        client = PingOneClient(self.config, self.mock_logger)
        
        self.assertEqual(client.environment_id, 'test-env-id')
        self.assertEqual(client.client_id, 'test-client-id')
        self.assertEqual(client.client_secret, 'test-secret')
    
    @patch('pingone_client.requests.post')
    def test_get_access_token_success(self, mock_post):
        """Test successful token acquisition."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test-token-123',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        client = PingOneClient(self.config, self.mock_logger)
        token = client._get_access_token()
        
        self.assertEqual(token, 'test-token-123')
    
    @patch('pingone_client.requests.post')
    def test_get_access_token_failure(self, mock_post):
        """Test token acquisition failure."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'error': 'invalid_client',
            'error_description': 'Invalid credentials'
        }
        mock_post.return_value = mock_response
        
        client = PingOneClient(self.config, self.mock_logger)
        
        with self.assertRaises(Exception) as context:
            client._get_access_token()
        
        self.assertIn('Authentication failed', str(context.exception))
    
    @patch('pingone_client.requests.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection test."""
        # Mock token request
        with patch.object(PingOneClient, '_get_access_token', return_value='test-token'):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'name': 'Test Environment'}
            mock_get.return_value = mock_response
            
            client = PingOneClient(self.config, self.mock_logger)
            success, message = client.test_connection()
            
            self.assertTrue(success)
            self.assertIn('Test Environment', message)
    
    def test_get_attribute_by_name(self):
        """Test retrieving attribute by name."""
        client = PingOneClient(self.config, self.mock_logger)
        
        mock_schema_data = {
            '_embedded': {
                'attributes': [
                    {'name': 'title', 'id': 'attr-1', 'type': 'STRING'},
                    {'name': 'employeeNumber', 'id': 'attr-2', 'type': 'STRING'}
                ]
            }
        }
        
        with patch.object(client, 'get_schema_attributes', return_value=(True, mock_schema_data, None)):
            success, attr, error = client.get_attribute_by_name('title')
            
            self.assertTrue(success)
            self.assertIsNotNone(attr)
            self.assertEqual(attr['name'], 'title')
            self.assertEqual(attr['id'], 'attr-1')
    
    def test_get_attribute_by_name_not_found(self):
        """Test retrieving non-existent attribute."""
        client = PingOneClient(self.config, self.mock_logger)
        
        mock_schema_data = {
            '_embedded': {
                'attributes': [
                    {'name': 'title', 'id': 'attr-1', 'type': 'STRING'}
                ]
            }
        }
        
        with patch.object(client, 'get_schema_attributes', return_value=(True, mock_schema_data, None)):
            success, attr, error = client.get_attribute_by_name('nonexistent')
            
            self.assertTrue(success)
            self.assertIsNone(attr)
            self.assertIsNone(error)


class TestAttributeManager(unittest.TestCase):
    """Test cases for AttributeManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.attributes = {
            'title': 'Job title',
            'employeeNumber': 'Employee ID'
        }
    
    def test_create_attributes_success(self):
        """Test successful attribute creation."""
        # Mock get_attribute_by_name to return None (not exists)
        self.mock_client.get_attribute_by_name.return_value = (True, None, None)
        # Mock create_attribute to return success
        self.mock_client.create_attribute.return_value = (True, {'id': 'new-attr-id'}, None)
        
        manager = AttributeManager(self.mock_client, self.attributes)
        manager.create_attributes()
        
        # Verify create was called for each attribute
        self.assertEqual(self.mock_client.create_attribute.call_count, 2)
    
    def test_create_attributes_skip_existing(self):
        """Test skipping existing attributes."""
        # Mock get_attribute_by_name to return existing attribute
        self.mock_client.get_attribute_by_name.return_value = (
            True, 
            {'name': 'title', 'id': 'existing-id'}, 
            None
        )
        
        manager = AttributeManager(self.mock_client, self.attributes)
        manager.create_attributes()
        
        # Verify create was NOT called since attribute exists
        self.mock_client.create_attribute.assert_not_called()
    
    def test_remove_attributes_success(self):
        """Test successful attribute removal."""
        # Mock get_attribute_by_name to return existing attribute
        self.mock_client.get_attribute_by_name.return_value = (
            True,
            {'name': 'title', 'id': 'attr-to-delete'},
            None
        )
        # Mock delete_attribute to return success
        self.mock_client.delete_attribute.return_value = (True, None, None)
        
        manager = AttributeManager(self.mock_client, self.attributes)
        manager.remove_attributes()
        
        # Verify delete was called for each attribute
        self.assertEqual(self.mock_client.delete_attribute.call_count, 2)
    
    def test_clear_attributes_success(self):
        """Test successful attribute clearing."""
        # Mock get_attribute_by_name to return enabled attribute
        self.mock_client.get_attribute_by_name.return_value = (
            True,
            {'name': 'title', 'id': 'attr-id', 'enabled': True},
            None
        )
        # Mock update_attribute to return success
        self.mock_client.update_attribute.return_value = (True, None, None)
        
        manager = AttributeManager(self.mock_client, self.attributes)
        manager.clear_attributes()
        
        # Verify update was called for each attribute
        self.assertEqual(self.mock_client.update_attribute.call_count, 2)
    
    def test_dry_run_mode(self):
        """Test dry run mode doesn't make actual changes."""
        # Mock methods
        self.mock_client.get_attribute_by_name.return_value = (True, None, None)
        
        manager = AttributeManager(self.mock_client, self.attributes, dry_run=True)
        manager.create_attributes()
        
        # Verify create was NOT called in dry run mode
        self.mock_client.create_attribute.assert_not_called()


def run_tests():
    """Run all unit tests."""
    print("=" * 70)
    print("Starting p1person Unit Tests")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPingOneClient))
    suite.addTests(loader.loadTestsFromTestCase(TestAttributeManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log summary
    print("=" * 70)
    print("Test Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    # Log failures and errors
    if result.failures:
        print("Failures:")
        for test, traceback in result.failures:
            print(f"{test}: {traceback}")
    
    if result.errors:
        print("Errors:")
        for test, traceback in result.errors:
            print(f"{test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
