# Changelog

All notable changes to the p1person project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2] - 2026-02-05

### Changed
- Converted all attribute operations to columnar display format
- Optimized code with constants for magic strings and numbers
- Removed unused imports and improved import organization
- Added configurable logging levels in properties file
- Improved string formatting throughout

### Fixed
- Removed tests.log functionality
- Fixed test file logger references

## [0.1] - 2026-02-04

### Added
- Initial release of p1person
- Command-line interface for PingOne custom attribute management
- Secure configuration management with encrypted client secrets
- Support for inetOrgPerson LDAP schema attributes:
  - title
  - businessCategory
  - carLicense
  - departmentNumber
  - employeeNumber
  - employeeType
  - homePhone
  - homePostalAddress
  - manager
  - preferredLanguage
  - roomNumber
  - secretary
- Command-line arguments:
  - `-h/--help` - Display help information
  - `-p/--prefix` - Add prefix to attribute names
  - `-c/--clear` - Clear attribute values (disable attributes)
  - `-r/--remove` - Remove attributes
  - `-d/--display` - Display existing attributes
  - `-t/--testconnection` - Test PingOne connection
  - `--dryrun` - Test operations without making changes
  - `-n/--newconnection` - Configure new connection
  - `-a/--additionalattributes` - Use custom attributes from config
  - `-v/--version` - Display version information
- PingOne API client with OAuth2 authentication
- Comprehensive error handling and validation
- Date-stamped logging:
  - Connection log (connections.log)
  - API call log (apilog.log)

- Unit test suite covering:
  - Configuration management
  - API client operations
  - Attribute management
  - Error handling
- Documentation:
  - README.md with usage instructions
  - CHANGELOG.md for version tracking
  - requirements.txt for dependencies
  - Inline code comments
- Security features:
  - Encrypted storage of client secrets
  - Machine-specific encryption keys
  - Restricted file permissions on configuration
- Smart attribute handling:
  - Skips existing attributes with notice
  - Validates argument combinations
  - Provides clear status messages
- Interactive setup wizard for first-time configuration

### Technical Details
- Python 3.7+ compatible
- Uses Fernet symmetric encryption for secrets
- Implements PingOne Management API v1
- Supports multiple PingOne regions (NA, EU, ASIA, CA)
- Token caching with automatic refresh
- Comprehensive request/response logging
- Timeout protection on all API calls
- Graceful error handling throughout

### Development Practices
- Follows PEP 8 style guidelines
- Comprehensive unit test coverage
- Clear separation of concerns (MVC-like architecture)
- No hardcoded credentials or secrets
- All API endpoints verified against PingOne documentation
- Defensive programming with try/catch blocks
- No infinite loops - all iterations bounded
- Structured logging with timestamps
