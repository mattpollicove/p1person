# p1person

PingOne Custom Attribute Management Tool - A command-line application for managing custom user attributes in PingOne based on the LDAP inetOrgPerson schema.

**Version:** 0.2

## Overview

`p1person` is a Python CLI application that connects to PingOne and manages custom user attributes. It supports creating, displaying, removing, and clearing attributes based on the LDAP inetOrgPerson schema.

## Features

- **Secure Configuration**: Stores PingOne connection details with encrypted client secrets
- **inetOrgPerson Attributes**: Creates standard LDAP schema attributes in PingOne
- **Custom Attributes**: Supports additional custom attributes via configuration
- **Prefix Support**: Add custom prefixes to attribute names
- **Dry Run Mode**: Test operations without making actual changes
- **Comprehensive Logging**: Tracks connections and API calls with date-stamped log files
- **Safe Operations**: Skips existing attributes and displays clear status messages

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Run initial setup to configure connection:

```bash
python p1person.py -n
```

## Configuration

### Initial Setup

On first run or when using `-n/--newconnection`, you'll be prompted to enter:

- **Friendly Name**: A descriptive name for your PingOne environment
- **Environment ID**: Your PingOne environment ID
- **Client ID**: OAuth2 client ID
- **Client Secret**: OAuth2 client secret (displayed as asterisks while typing)

Configuration is stored in `p1person.properties` with encrypted credentials.

**After configuration, you'll be offered to test the connection:**
- Choose 'y' to test immediately
- If the test fails, you can retry, update configuration, or quit
- Testing continues in a loop until successful or you decline

### Additional Attributes

To define custom attributes beyond the default inetOrgPerson schema:

1. Edit `p1person.properties` and add custom attributes:

```properties
# Additional Custom Attributes
customAttribute1=Description of custom attribute
customAttribute2=Another custom attribute
```

2. Use the `-a` flag to work with these custom attributes

### Logging Configuration

Log levels can be optionally configured in `p1person.properties`:

```properties
# Logging Configuration (Optional)
# Valid levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
api_log_level=INFO
connection_log_level=INFO
```

- **api_log_level**: Controls verbosity of API operation logs (default: INFO)
- **connection_log_level**: Controls verbosity of connection logs (default: INFO)
- Use `DEBUG` for detailed troubleshooting
- Use `WARNING` or `ERROR` for minimal logging

## Default Attributes

The following **12 inetOrgPerson attributes** are supported by default:

**Note:** The `title` and `preferredLanguage` attributes are intentionally excluded and will never be added or removed by this application.

| Attribute | Description |
|-----------|-------------|
| `title` | The user's job title |
| `businessCategory` | The type of business performed by the organization |
| `carLicense` | Vehicle license plate or registration |
| `company` | The name of the company or organization |
| `department` | The organizational department name |
| `departmentNumber` | Identifies a specific department |
| `employeeNumber` | A numeric or alphanumeric ID assigned by the organization |
| `employeeType` | The nature of employment (e.g., Contractor, Intern, Temp) |
| `homePhone` | The user's home telephone number |
| `homePostalAddress` | The user's home address |
| `manager` | The name of the user's manager. (This does not update as LDAP Manager does) |
| `o` | The organization name |
| `preferredLanguage` | The individual's preferred written or spoken language |
| `roomNumber` | The user's office or room number |
| `secretary` | The name of the user's administrative assistant. (This does not update as LDAP Manager does) |

## Usage

### Command Line Arguments

```bash
usage: p1person.py [-h] [-p PREFIX] [-c] [-r] [-d] [-t] [--dryrun] [-n] [-a] [-y] [-v]

p1person - PingOne Custom Attribute Management Tool

optional arguments:
  -h, --help            show this help message and exit
  -p PREFIX, --prefix PREFIX
                        Prepend a unique string to attribute names (can be used with -r)
  -c, --clear           Clear any assigned values for existing attributes (cannot be used with -r)
  -r, --remove          Remove the set of attributes (use with -p to remove prefixed attributes)
  -d, --display         Show the attributes defined in the system (cannot be used with -r)
  -t, --testconnection  Test connection properties from p1person.properties (standalone only)
  --dryrun              Test operations without making changes, display errors or info from PingOne
  -n, --newconnection   Initiate dialog to update connection information in p1person.properties
  -a, --additionalattributes
                        Read custom list of attributes from p1person.properties
  -y, --yes             Automatically accept all confirmations (use with -r or -c)
  -v, --version         show program's version number and exit
```

**Note:** The `-r` (remove) and `-c` (clear) operations will prompt for confirmation unless:
- The `--dryrun` flag is used, or
- The `-y/--yes` flag is specified to automatically accept changes

### Examples

**Create default attributes:**
```bash
python p1person.py
```

**Create additional custom attributes:**
```bash
python p1person.py -a
# Reads attributes from p1person.properties additional_attribute.* entries
```

**Create attributes with a prefix:**
```bash
python p1person.py -p PingPerson
# Creates: PingPersonmanager, PingPersondepartment, etc.
```

**Display existing default attributes:**
```bash
python p1person.py -d
```

**Display existing additional attributes:**
```bash
python p1person.py -d -a
```

**Remove attributes (with confirmation):**
```bash
python p1person.py -r
# Will prompt: Are you sure you want to continue? (yes/no):
```

**Remove attributes without confirmation:**
```bash
python p1person.py -r -y
# Skips confirmation prompt
```

**Remove additional attributes:**
```bash
python p1person.py -r -a -y
```

**Remove attributes with prefix:**
```bash
python p1person.py -r -p PingPerson
```

**Clear attribute values with confirmation:**
```bash
python p1person.py -c -a
# Will prompt for confirmation before clearing values
```

**Clear attribute values (disable attributes):**
```bash
python p1person.py -c
```

**Test connection:**
```bash
python p1person.py -t
```

**Configure new connection:**
```bash
python p1person.py -n
```

**Use custom attributes:**
```bash
python p1person.py -a
```

**Dry run mode (test without changes):**
```bash
python p1person.py --dryrun
python p1person.py -p MyPrefix --dryrun
```

### Argument Restrictions

- `-t/--testconnection` cannot be used with any other arguments
- `-p/--prefix` cannot be used with `-r/--remove`
- `-c/--clear` cannot be used with `-r/--remove`
- `-d/--display` cannot be used with `-r/--remove`

## Logging

### Connection Log

- **File**: `logs/YYYYMMDD_connections.log`
- **Purpose**: Tracks successful connections with timestamp and friendly name

### API Log

- **File**: `logs/YYYYMMDD_apilog.log`
- **Purpose**: Records all API calls including:
  - HTTP method and URL
  - Status code
  - Response time
  - Error messages (if any)

## Development

### Running Tests

Execute the unit test suite:

```bash
python test_p1person.py
```

Tests cover:
- Configuration management and encryption
- PingOne API client operations
- Attribute management functions
- Error handling and edge cases

### Project Structure

```
p1person/
├── p1person.py              # Main application entry point
├── config_manager.py        # Configuration and encryption handling
├── pingone_client.py        # PingOne API client
├── attribute_manager.py     # Attribute operations
├── logger.py                # Logging configuration
├── test_p1person.py         # Unit tests
├── p1person.properties      # Configuration file (created on first run)
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── CHANGELOG.md             # Version history
└── logs/                    # Log files directory
    ├── YYYYMMDD_connections.log
    └── YYYYMMDD_apilog.log
```

### Development Rules

1. **API Calls**: Only use documented PingOne API endpoints
2. **Error Handling**: All HTTP, async, and file operations must be wrapped in try/catch
3. **No Infinite Loops**: All loops must have max retries or timeouts
4. **Testing**: All new code must include unit tests
5. **Documentation**: Comments must be clear and up-to-date
6. **Logging**: All warnings and errors must be logged

## Security

- Client secrets are encrypted using Fernet (symmetric encryption)
- Password input masked with asterisks for visual feedback
- Encryption keys are derived from machine-specific data
- Configuration files have restricted permissions (owner read-only)
- Credentials are never logged or displayed in plain text

## Troubleshooting

### Connection Issues

1. Verify your PingOne credentials are correct
2. Check that the client has appropriate permissions
3. Ensure network connectivity to PingOne
4. Review `logs/YYYYMMDD_apilog.log` for detailed error messages
5. If connection fails, the application will offer to re-enter credentials
6. Connection testing loops until successful or you decline

### Missing Configuration Fields

If `p1person.properties` is incomplete or corrupted:
- The application will detect missing fields and prompt you to enter them
- If only the client secret is invalid, you'll be offered to update just that field
- All prompts include the option to decline and exit

### Authentication Failures

- Verify the Environment ID is correct
- Ensure the Client ID and Secret are valid
- Check that the OAuth client has the required scopes
- The application will offer to reconfigure after connection failures
- You can test the connection repeatedly until it succeeds

### Attribute Creation Failures

- Verify you have permissions to create schema attributes
- Check that attribute names are valid (no special characters)
- Review API log for specific error messages from PingOne

## API Reference

This tool uses the PingOne Management API:

- **Authentication**: OAuth2 Client Credentials flow
- **Base URL**: `https://api.pingone.com/v1` (or regional equivalent)
- **Endpoints Used**:
  - `POST /environments/{envId}/as/token` - Authentication
  - `GET /environments/{envId}` - Environment details
  - `GET /environments/{envId}/schemas` - Retrieve schema attributes
  - `POST /environments/{envId}/schemas/attributes` - Create attribute
  - `PATCH /environments/{envId}/schemas/attributes/{attrId}` - Update attribute
  - `DELETE /environments/{envId}/schemas/attributes/{attrId}` - Delete attribute

## License

This project is provided as-is for use with PingOne environments.

## Support

For issues related to:
- **PingOne API**: Consult PingOne documentation or support
- **This Tool**: Check logs and review error messages

## Version History

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Contributing

When contributing:
1. Follow the development rules outlined above
2. Add unit tests for new functionality
3. Update documentation as needed
4. Test thoroughly before committing
