"""
Configuration Manager for p1person
Handles loading, saving, and encrypting connection properties using standard .properties file format
"""

import base64
import getpass
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Constants
SEPARATOR_LINE = '=' * 70
CONFIG_FILE_NAME = 'p1person.properties'
KEY_FILE_NAME = '.p1person.key'

# Platform-specific imports for password masking
try:
    import termios
    import tty
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False


def _getpass_with_asterisks(prompt='Password: '):
    """
    Get password input with asterisk masking.
    Falls back to standard getpass if terminal manipulation not available.
    
    Args:
        prompt: Prompt to display
        
    Returns:
        str: The entered password
    """
    if not HAS_TERMIOS or not sys.stdin.isatty():
        # Fallback to standard getpass for non-Unix or non-TTY environments
        return getpass.getpass(prompt)
    
    print(prompt, end='', flush=True)
    password = []
    
    try:
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            # Set terminal to raw mode
            tty.setraw(fd)
            
            while True:
                char = sys.stdin.read(1)
                
                # Enter or newline
                if char in ('\n', '\r'):
                    print()  # New line after password entry
                    break
                # Backspace or delete
                elif char in ('\x7f', '\x08'):
                    if password:
                        password.pop()
                        # Erase the last asterisk
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                # Ctrl+C
                elif char == '\x03':
                    print()
                    raise KeyboardInterrupt
                # Ctrl+D (EOF)
                elif char == '\x04':
                    if not password:
                        print()
                        raise EOFError
                # Printable characters
                elif ord(char) >= 32:
                    password.append(char)
                    sys.stdout.write('*')
                    sys.stdout.flush()
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    except Exception:
        # If anything goes wrong, restore settings and fall back
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            pass
        print("\nFalling back to hidden input...")
        return getpass.getpass(prompt)
    
    return ''.join(password)


class ConfigManager:
    """Manages p1person.properties configuration file."""
    
    CONFIG_FILE = 'p1person.properties'
    
    def __init__(self, config_path=None):
        """
        Initialize ConfigManager.
        
        Args:
            config_path: Optional custom path to config file
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path(__file__).parent / self.CONFIG_FILE
        
        # Generate or load encryption key
        self._key = self._get_or_create_key()
    
    def _get_or_create_key(self):
        """
        Get or create encryption key for securing client secret.
        Uses machine-specific data for key derivation.
        
        Returns:
            bytes: Encryption key
        """
        key_file = Path(__file__).parent / '.p1person.key'
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        
        # Generate new key using machine-specific salt
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        # Use a combination of username and hostname for key derivation
        key_material = f"{os.getlogin()}{os.uname().nodename}".encode()
        key = base64.urlsafe_b64encode(kdf.derive(key_material))
        
        # Save key and salt
        with open(key_file, 'wb') as f:
            f.write(key)
            f.write(salt)
        
        # Make key file read-only for owner
        os.chmod(key_file, 0o600)
        
        return key
    
    def _encrypt_secret(self, secret):
        """
        Encrypt client secret.
        
        Args:
            secret: Plain text secret
            
        Returns:
            str: Base64 encoded encrypted secret
        """
        try:
            fernet = Fernet(self._key)
            encrypted = fernet.encrypt(secret.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            raise Exception(f"Failed to encrypt secret: {str(e)}")
    
    def _decrypt_secret(self, encrypted_secret):
        """
        Decrypt client secret.
        
        Args:
            encrypted_secret: Base64 encoded encrypted secret
            
        Returns:
            str: Plain text secret
        """
        try:
            fernet = Fernet(self._key)
            decoded = base64.b64decode(encrypted_secret.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise Exception(f"Failed to decrypt secret: {str(e)}")
    
    def config_exists(self):
        """
        Check if configuration file exists.
        
        Returns:
            bool: True if config file exists
        """
        return self.config_path.exists()
    
    def create_new_connection(self):
        """
        Interactive dialog to create new connection configuration.
        Securely stores client secret.
        """
        print("\n=== PingOne Connection Setup ===\n")
        
        # Gather connection details
        friendly_name = input("Friendly Name: ").strip()
        environment_id = input("Environment ID: ").strip()
        client_id = input("Client ID: ").strip()
        client_secret = _getpass_with_asterisks("Client Secret: ").strip()
        
        # Validate inputs
        if not all([friendly_name, environment_id, client_id, client_secret]):
            raise ValueError("All fields are required")
        
        # Encrypt client secret
        encrypted_secret = self._encrypt_secret(client_secret)
        
        # Create configuration dictionary
        config = {
            'friendly_name': friendly_name,
            'environment_id': environment_id,
            'client_id': client_id,
            'client_secret_encrypted': encrypted_secret
        }
        
        # Save configuration
        self._save_config(config)
        
        print(f"\nConfiguration saved to {self.config_path}")
    
    def load_config(self, prompt_for_missing=False):
        """
        Load and decrypt configuration from .properties file.
        
        Args:
            prompt_for_missing: If True, prompt user for missing fields instead of raising error
        
        Returns:
            dict: Configuration with decrypted client secret
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                "Run with -n/--newconnection to create configuration."
            )
        
        try:
            config = {}
            with open(self.config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Handle additional_attributes section
                        if key.startswith('additional_attribute.'):
                            attr_name = key.replace('additional_attribute.', '')
                            if 'additional_attributes' not in config:
                                config['additional_attributes'] = {}
                            config['additional_attributes'][attr_name] = value
                        elif key in ['api_log_level', 'connection_log_level']:
                            # Store log level settings
                            config[key] = value
                        else:
                            config[key] = value
            
            # Ensure additional_attributes exists
            if 'additional_attributes' not in config:
                config['additional_attributes'] = {}
            
            # Check for missing fields
            required_fields = ['friendly_name', 'environment_id', 'client_id', 'client_secret_encrypted']
            missing = [field for field in required_fields if field not in config or not config[field]]
            
            if missing:
                if prompt_for_missing:
                    print(f"\n⚠ Warning: Configuration is incomplete. Missing: {', '.join(missing)}")
                    if self._prompt_to_fix_config(config, missing):
                        # Reload the saved config
                        return self.load_config(prompt_for_missing=False)
                    else:
                        raise ValueError(f"Missing required fields in config: {', '.join(missing)}")
                else:
                    raise ValueError(f"Missing required fields in config: {', '.join(missing)}")
            
            # Decrypt client secret
            try:
                config['client_secret'] = self._decrypt_secret(config['client_secret_encrypted'])
            except Exception as e:
                if prompt_for_missing:
                    print(f"\n⚠ Warning: Failed to decrypt client secret: {str(e)}")
                    if self._prompt_for_client_secret_only(config):
                        return self.load_config(prompt_for_missing=False)
                    else:
                        raise
                else:
                    raise
            
            return config
            
        except ValueError:
            raise
        except Exception as e:
            if "Missing required fields" not in str(e) and "Failed to decrypt" not in str(e):
                raise Exception(f"Failed to load configuration: {str(e)}")
            raise
    
    def _save_config(self, config):
        """
        Save configuration to .properties file.
        
        Args:
            config: Configuration dictionary
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                # Write header comment
                f.write("# PingOne Connection Configuration\n")
                f.write("# This file is automatically managed by p1person\n")
                f.write("# Client secret is encrypted for security\n\n")
                
                # Write main properties
                f.write(f"friendly_name={config.get('friendly_name', '')}\n")
                f.write(f"environment_id={config.get('environment_id', '')}\n")
                f.write(f"client_id={config.get('client_id', '')}\n")
                f.write(f"client_secret_encrypted={config.get('client_secret_encrypted', '')}\n")
                
                # Add optional log level settings
                if 'api_log_level' in config:
                    f.write(f"\n# Logging Configuration (Optional)\n")
                    f.write(f"# Valid levels: DEBUG, INFO, WARNING, ERROR, CRITICAL\n")
                    f.write(f"api_log_level={config['api_log_level']}\n")
                    f.write(f"connection_log_level={config.get('connection_log_level', 'INFO')}\n")
                
                # Write additional attributes if any
                additional_attrs = config.get('additional_attributes', {})
                if additional_attrs:
                    f.write("\n# Additional Custom Attributes\n")
                    for attr_name, attr_desc in additional_attrs.items():
                        f.write(f"additional_attribute.{attr_name}={attr_desc}\n")
                else:
                    # Add logging configuration template if not already present
                    if 'api_log_level' not in config:
                        f.write("\n# Logging Configuration (Optional)\n")
                        f.write("# Valid levels: DEBUG, INFO, WARNING, ERROR, CRITICAL\n")
                        f.write("# api_log_level=INFO\n")
                        f.write("# connection_log_level=INFO\n")
                    
                    # Add template section for additional attributes
                    f.write("\n# Additional Custom Attributes\n")
                    f.write("# Add your custom attributes using the format: badgeNumber=Badge Number\n")
                    f.write("# These can be used with the -a flag\n")
                    f.write("# Examples:\n")
                    f.write("# badgeNumber=Employee badge number\n")
                    f.write("# costCenter=Department cost center code\n")
            
            # Make config file read-only for owner
            os.chmod(self.config_path, 0o600)
            
        except Exception as e:
            raise Exception(f"Failed to save configuration: {str(e)}")
    
    def get_additional_attributes(self):
        """
        Get additional custom attributes from configuration.
        
        Returns:
            dict: Additional attributes {name: description}
        """
        try:
            config = self.load_config()
            return config.get('additional_attributes', {})
        except Exception as e:
            raise Exception(f"Failed to load additional attributes: {str(e)}")
    
    def add_additional_attribute(self, name, description):
        """
        Add a custom attribute to configuration.
        
        Args:
            name: Attribute name
            description: Attribute description
        """
        try:
            config = self.load_config()
            
            # Ensure additional_attributes exists
            if 'additional_attributes' not in config:
                config['additional_attributes'] = {}
            
            config['additional_attributes'][name] = description
            
            # Remove decrypted secret before saving
            if 'client_secret' in config:
                del config['client_secret']
            
            self._save_config(config)
            
        except Exception as e:
            raise Exception(f"Failed to add additional attribute: {str(e)}")
    
    def _prompt_to_fix_config(self, config, missing_fields):
        """
        Prompt user to fill in missing configuration fields.
        
        Args:
            config: Existing config dictionary
            missing_fields: List of missing field names
            
        Returns:
            bool: True if config was updated, False if user declined
        """
        response = input("\nWould you like to enter the missing values now? (y/n): ").strip().lower()
        if response != 'y':
            return False
        
        print("\n=== Complete Configuration ===\n")
        
        # Prompt for each missing field
        if 'friendly_name' in missing_fields:
            config['friendly_name'] = input("Friendly Name: ").strip()
        
        if 'environment_id' in missing_fields:
            config['environment_id'] = input("Environment ID: ").strip()
        
        if 'client_id' in missing_fields:
            config['client_id'] = input("Client ID: ").strip()
        
        if 'client_secret_encrypted' in missing_fields:
            client_secret = _getpass_with_asterisks("Client Secret: ").strip()
            if client_secret:
                config['client_secret_encrypted'] = self._encrypt_secret(client_secret)
        
        # Validate all required fields are now present
        if not all([config.get('friendly_name'), config.get('environment_id'), 
                   config.get('client_id'), config.get('client_secret_encrypted')]):
            print("\n✗ Error: All fields are required")
            return False
        
        # Ensure additional_attributes exists
        if 'additional_attributes' not in config:
            config['additional_attributes'] = {}
        
        # Save updated config
        self._save_config(config)
        print(f"\n✓ Configuration updated and saved")
        return True
    
    def _prompt_for_client_secret_only(self, config):
        """
        Prompt user to enter only the client secret.
        
        Args:
            config: Existing config dictionary
            
        Returns:
            bool: True if secret was updated, False if user declined
        """
        response = input("\nWould you like to enter the client secret? (y/n): ").strip().lower()
        if response != 'y':
            return False
        
        print("\n=== Update Client Secret ===\n")
        client_secret = _getpass_with_asterisks("Client Secret: ").strip()
        
        if not client_secret:
            print("\n✗ Error: Client secret cannot be empty")
            return False
        
        # Encrypt and save
        config['client_secret_encrypted'] = self._encrypt_secret(client_secret)
        self._save_config(config)
        print(f"\n✓ Client secret updated and saved")
        return True
    
    def prompt_to_reconfigure(self):
        """
        Ask user if they want to reconfigure connection after a connection failure.
        
        Returns:
            bool: True if user wants to reconfigure
        """
        print(f"\n{SEPARATOR_LINE}")
        print("CONNECTION FAILED")
        print(SEPARATOR_LINE)
        response = input("\nWould you like to re-enter your connection details? (y/n): ").strip().lower()
        
        if response == 'y':
            self.create_new_connection()
            return True
        return False
    
    def offer_connection_test(self, api_logger, connection_logger):
        """
        Offer to test connection after configuration is saved.
        Loops until connection succeeds or user declines.
        
        Args:
            api_logger: Logger for API calls
            connection_logger: Logger for connections
        """
        from pingone_client import PingOneClient
        from logger import log_connection
        
        while True:
            response = input("\nWould you like to test the connection now? (y/n): ").strip().lower()
            
            if response != 'y':
                print("Skipping connection test.")
                break
            
            # Load the saved config and test
            try:
                config = self.load_config()
                print(f"\nTesting connection to PingOne environment: {config['friendly_name']}...")
                
                client = PingOneClient(config, api_logger)
                success, message = client.test_connection()
                
                if success:
                    print(f"✓ Connection successful: {message}")
                    log_connection(connection_logger, config['friendly_name'])
                    break
                else:
                    print(f"\n{SEPARATOR_LINE}")
                    print(f"✗ CONNECTION FAILED: {message}")
                    print(SEPARATOR_LINE)
                    
                    # Ask if they want to try again or update config
                    retry = input("\nWould you like to (r)etry, (u)pdate configuration, or (q)uit? (r/u/q): ").strip().lower()
                    
                    if retry == 'u':
                        self.create_new_connection()
                        print("Configuration updated.")
                    elif retry == 'q':
                        print("Exiting connection test.")
                        break
                    # If 'r' or anything else, loop continues to test again
                    
            except Exception as e:
                print(f"✗ Error during connection test: {str(e)}")
                break
    
    def prompt_to_reconfigure_and_test(self, api_logger, connection_logger):
        """
        Ask user if they want to reconfigure connection and test it in a loop.
        Continues testing until successful or user declines.
        
        Args:
            api_logger: Logger for API calls
            connection_logger: Logger for connections
            
        Returns:
            bool: True if connection eventually succeeds
        """
        from pingone_client import PingOneClient
        from logger import log_connection
        
        print(f"\n{SEPARATOR_LINE}")
        print("CONNECTION FAILED")
        print(SEPARATOR_LINE)
        
        while True:
            response = input("\nWould you like to re-enter your connection details? (y/n): ").strip().lower()
            
            if response != 'y':
                return False
            
            # Update configuration
            self.create_new_connection()
            print("\nConfiguration saved. Testing connection...")
            
            # Test the new configuration
            try:
                config = self.load_config()
                client = PingOneClient(config, api_logger)
                success, message = client.test_connection()
                
                if success:
                    print(f"✓ Connection successful: {message}")
                    log_connection(connection_logger, config['friendly_name'])
                    return True
                else:
                    print(f"\n{SEPARATOR_LINE}")
                    print(f"✗ CONNECTION FAILED: {message}")
                    print(SEPARATOR_LINE)
                    
                    # Ask if they want to try updating again
                    retry = input("\nWould you like to update the configuration again? (y/n): ").strip().lower()
                    if retry != 'y':
                        return False
                    # Loop continues to update and test again
                    
            except Exception as e:
                print(f"✗ Error during connection test: {str(e)}")
                return False
