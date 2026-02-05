#!/usr/bin/env python3
"""
p1person - PingOne Custom Attribute Management Tool
Version: 0.2
"""

import argparse
import sys
from config_manager import ConfigManager
from pingone_client import PingOneClient
from attribute_manager import AttributeManager
from logger import setup_logging, log_connection, log_api_call

VERSION = "0.2"

# Default inetOrgPerson attributes to create
# Note: 'title' and 'preferredLanguage' are excluded - these are never added or removed
DEFAULT_ATTRIBUTES = {
    'businessCategory': 'The type of business performed by the organization.',
    'carLicense': 'Vehicle license plate or registration.',
    'department': 'The organizational department name.',
    'departmentNumber': 'Identifies a specific department.',
    'employeeNumber': 'A numeric or alphanumeric ID assigned by the organization.',
    'employeeType': 'The nature of employment (e.g., Contractor, Intern, Temp).',
    'homePhone': 'The user\'s home telephone number.',
    'homePostalAddress': 'The user\'s home address.',
    'manager': 'The name of the user\'s manager. (This does not update as LDAP Manager does)',
    'o': 'The organization name.',
    'roomNumber': 'The user\'s office or room number.',
    'secretary': 'The name of the user\'s administrative assistant. (This does not update as LDAP Manager does)'
}


def validate_arguments(args):
    """
    Validate command-line argument combinations.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # -t/--testconnection cannot be used with other arguments
    if args.testconnection:
        other_args = [args.prefix, args.clear, args.remove, args.display, 
                     args.dryrun, args.newconnection, args.additionalattributes]
        if any(other_args):
            return False, "ERROR: -t/--testconnection cannot be used with other arguments"
    
    # -c/--clear cannot be used with -r/--remove
    if args.clear and args.remove:
        return False, "ERROR: -c/--clear cannot be used with -r/--remove"
    
    # -d/--display cannot be used with -r/--remove
    if args.display and args.remove:
        return False, "ERROR: -d/--display cannot be used with -r/--remove"
    
    return True, None


def main():
    """Main entry point for p1person application."""
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description='p1person - PingOne Custom Attribute Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Default inetOrgPerson Attributes (12 total):
  businessCategory       - The type of business performed by the organization
  carLicense            - Vehicle license plate or registration
  department            - The organizational department name
  departmentNumber      - Identifies a specific department
  employeeNumber        - A numeric or alphanumeric ID assigned by the organization
  employeeType          - The nature of employment (e.g., Contractor, Intern, Temp)
  homePhone             - The user's home telephone number
  homePostalAddress     - The user's home address
  manager               - The name of the user's manager
  o                     - The organization name
  roomNumber            - The user's office or room number
  secretary             - The name of the user's administrative assistant

Note: The 'title' and 'preferredLanguage' attributes are intentionally excluded
and will never be added or removed by this application.

Examples:
  p1person                          Create default attributes
  p1person -p MyPrefix              Create attributes with prefix
  p1person -d                       Display existing default attributes
  p1person -d -a                    Display existing additional attributes
  p1person -r                       Remove attributes (with confirmation)
  p1person -r -y                    Remove attributes without confirmation
  p1person -c -a                    Clear additional attribute values
  p1person -t                       Test connection
  p1person -n                       Configure new connection
  p1person -a                       Create additional custom attributes
        """
    )
    
    parser.add_argument('-p', '--prefix', type=str, metavar='PREFIX',
                       help='Prepend a unique string to attribute names (can be used with -r to remove prefixed attributes)')
    parser.add_argument('-c', '--clear', action='store_true',
                       help='Clear any assigned values for existing attributes (cannot be used with -r)')
    parser.add_argument('-r', '--remove', action='store_true',
                       help='Remove the set of attributes (use with -p to remove prefixed attributes)')
    parser.add_argument('-d', '--display', action='store_true',
                       help='Show the attributes defined in the system (cannot be used with -r)')
    parser.add_argument('-t', '--testconnection', action='store_true',
                       help='Test connection properties from p1person.properties (standalone only)')
    parser.add_argument('--dryrun', action='store_true',
                       help='Test operations without making changes, display errors or info from PingOne')
    parser.add_argument('-n', '--newconnection', action='store_true',
                       help='Initiate dialog to update connection information in p1person.properties')
    parser.add_argument('-a', '--additionalattributes', action='store_true',
                       help='Read custom list of attributes from p1person.properties')
    parser.add_argument('-y', '--yes', action='store_true',
                       help='Automatically accept all confirmations (use with -r or -c)')
    parser.add_argument('-v', '--version', action='version', version=f'p1person {VERSION}')
    parser.add_argument('--Skynet', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--Cyberdyne', action='store_true', help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    # Validate argument combinations
    is_valid, error_msg = validate_arguments(args)
    if not is_valid:
        print(error_msg)
        sys.exit(1)
    
    # Setup logging (before try block so it's available in exception handler)
    try:
        api_logger, connection_logger = setup_logging()
    except Exception as e:
        print(f"ERROR: Failed to setup logging: {str(e)}")
        sys.exit(1)
    
    try:
        # Handle new connection setup
        if args.newconnection:
            config_manager = ConfigManager()
            config_manager.create_new_connection()
            print("Connection configuration saved successfully.")
            # Offer to test connection after setup
            config_manager.offer_connection_test(api_logger, connection_logger)
            return 0
        
        # Load configuration
        config_manager = ConfigManager()
        if not config_manager.config_exists():
            print("No configuration file found. Starting connection setup...")
            config_manager.create_new_connection()
            # Offer to test connection after initial setup
            config_manager.offer_connection_test(api_logger, connection_logger)
        
        # Load config with option to prompt for missing fields
        try:
            config = config_manager.load_config(prompt_for_missing=True)
            
            # Reinitialize logging with configured levels
            api_log_level = config.get('api_log_level', 'INFO')
            connection_log_level = config.get('connection_log_level', 'INFO')
            api_logger, connection_logger = setup_logging(api_log_level, connection_log_level)
            
        except ValueError as e:
            print(f"✗ Configuration error: {str(e)}")
            return 1
        
        # Handle test connection
        if args.testconnection:
            print(f"Testing connection to PingOne environment: {config['friendly_name']}...")
            client = PingOneClient(config, api_logger)
            success, message = client.test_connection()
            if success:
                print(f"✓ Connection successful: {message}")
                log_connection(connection_logger, config['friendly_name'])
                return 0
            else:
                print(f"✗ Connection failed: {message}")
                # Offer to reconfigure and test in loop
                if config_manager.prompt_to_reconfigure_and_test(api_logger, connection_logger):
                    print("\n✓ Connection successful! Please run the command again.")
                    return 0
                return 1
        
        # Initialize PingOne client
        client = PingOneClient(config, api_logger)
        
        # Test connection before proceeding
        success, message = client.test_connection()
        if not success:
            print(f"✗ Connection failed: {message}")
            # Offer to reconfigure and test in loop
            if config_manager.prompt_to_reconfigure_and_test(api_logger, connection_logger):
                print("\nConfiguration updated. Please run the command again.")
                return 0
            return 1
        
        log_connection(connection_logger, config['friendly_name'])
        
        # Determine which attributes to use
        if args.additionalattributes:
            attributes = config_manager.get_additional_attributes()
            if not attributes:
                print("No additional attributes defined in p1person.properties")
                return 1
        else:
            attributes = DEFAULT_ATTRIBUTES.copy()
        
        # Apply prefix if specified
        if args.prefix:
            attributes = {f"{args.prefix}{key}": value for key, value in attributes.items()}
        
        # Initialize attribute manager
        attr_manager = AttributeManager(client, attributes, args.dryrun)
        
        # Handle display
        if args.display:
            print(f"\nDisplaying attributes in PingOne environment: {config['friendly_name']}")
            attr_manager.display_attributes(args.additionalattributes)
            return 0
        
        # Handle remove
        if args.remove:
            print(f"\nRemoving attributes from PingOne environment: {config['friendly_name']}")
            
            # Confirmation prompt unless --yes is specified
            if not args.yes and not args.dryrun:
                attr_type = "additional" if args.additionalattributes else "default"
                attr_count = len(attributes)
                print(f"\n⚠️  WARNING: You are about to remove {attr_count} {attr_type} attribute(s).")
                print("This action cannot be undone.\n")
                response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
                if response not in ['yes', 'y']:
                    print("\nOperation cancelled.")
                    return 0
            
            attr_manager.remove_attributes()
            return 0
        
        # Handle clear
        if args.clear:
            print(f"\nClearing attribute values in PingOne environment: {config['friendly_name']}")
            
            # Confirmation prompt unless --yes is specified
            if not args.yes and not args.dryrun:
                attr_type = "additional" if args.additionalattributes else "default"
                attr_count = len(attributes)
                print(f"\n⚠️  WARNING: You are about to clear values for {attr_count} {attr_type} attribute(s).")
                print("This will remove all data from these attributes for all users.\n")
                response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
                if response not in ['yes', 'y']:
                    print("\nOperation cancelled.")
                    return 0
            
            attr_manager.clear_attributes()
            return 0
        
        # Default action: create attributes
        print(f"\nCreating attributes in PingOne environment: {config['friendly_name']}")
        attr_manager.create_attributes()
        
        # Handle Skynet easter egg
        if args.Skynet:
            # Check if attributes exist (either they were there before or just created)
            success, existing_attrs, _ = client.get_schema_attributes()
            if success:
                # Check if our attributes are present
                attr_names = list(attributes.keys())
                existing_names = [attr.get('name') for attr in existing_attrs.get('_embedded', {}).get('attributes', [])]
                has_attributes = any(name in existing_names for name in attr_names)
                
                if has_attributes:
                    print("\n" + "="*70)
                    print("Skynet Protocol Activated: Creating resistance fighter...")
                    print("="*70)
                    
                    # Create Sarah Connor user
                    sarah_connor = {
                        'username': 'sconnor',
                        'email': 'sconnor@theresistance.org',
                        'name': {
                            'given': 'Sarah',
                            'family': 'Connor'
                        },
                        'lifecycle': {
                            'status': 'ACCOUNT_OK'
                        },
                        'title': 'Guerilla Fighter',
                        'description': 'Mother of the Resistance.',
                        'telephoneNumber': '555-9175',
                        'homePhone': '5559175',
                        'mobile': '555-1776',
                        'homePostalAddress': '11844 Hamlin St, Los Angeles, CA',
                        'employeeType': 'Resistance Fighter'
                    }
                    
                    success, user, error = client.create_user(sarah_connor)
                    if success:
                        print(f"✓ User created successfully: {user.get('username')}")
                        print(f"  User ID: {user.get('id')}")
                        print(f"  Email: {user.get('email')}")
                        print(f"  Name: {user.get('name', {}).get('given')} {user.get('name', {}).get('family')}")
                        print("\n  Come with me if you want to live.")
                    else:
                        print(f"✗ Failed to create user: {error}")
        
        # Handle Cyberdyne easter egg
        if args.Cyberdyne:
            # Check if attributes exist (either they were there before or just created)
            success, existing_attrs, _ = client.get_schema_attributes()
            if success:
                # Check if our attributes are present
                attr_names = list(attributes.keys())
                existing_names = [attr.get('name') for attr in existing_attrs.get('_embedded', {}).get('attributes', [])]
                has_attributes = any(name in existing_names for name in attr_names)
                
                if has_attributes:
                    print("\n" + "="*70)
                    print("Cyberdyne Systems Initiated: Creating lead architect...")
                    print("="*70)
                    
                    # Create Miles Dyson user
                    miles_dyson = {
                        'username': 'mdyson',
                        'email': 'mdyson@cyberdyne.com',
                        'name': {
                            'given': 'Miles',
                            'family': 'Dyson'
                        },
                        'lifecycle': {
                            'status': 'ACCOUNT_OK'
                        },
                        'title': 'Director of Special Projects',
                        'description': 'Lead Architect of the Neural-Net Processor; primary developer of the Skynet initiative.',
                        'telephoneNumber': '555-1995',
                        'homePhone': '555-1995',
                        'mobile': '555-1984',
                        'homePostalAddress': '30065 Pacific Coast Highway, Malibu, CA',
                        'employeeNumber': '00001',
                        'employeeType': 'Executive / Scientist'
                    }
                    
                    success, user, error = client.create_user(miles_dyson)
                    if success:
                        print(f"✓ User created successfully: {user.get('username')}")
                        print(f"  User ID: {user.get('id')}")
                        print(f"  Email: {user.get('email')}")
                        print(f"  Name: {user.get('name', {}).get('given')} {user.get('name', {}).get('family')}")
                        print("\n  I feel like I'm gonna throw up.")
                    else:
                        print(f"✗ Failed to create user: {error}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"ERROR: {str(e)}")
        api_logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
