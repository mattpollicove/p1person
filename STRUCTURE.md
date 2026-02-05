# p1person Project Structure

```
P1person/
│
├── 📄 Core Application Files
│   ├── p1person.py                    # Main CLI entry point (executable)
│   ├── config_manager.py              # Configuration & encryption handler
│   ├── pingone_client.py              # PingOne API client
│   ├── attribute_manager.py           # Attribute CRUD operations
│   └── logger.py                      # Logging infrastructure
│
├── 🧪 Testing
│   └── test_p1person.py               # Unit test suite (16 tests)
│
├── 📚 Documentation
│   ├── README.md                      # Complete documentation
│   ├── CHANGELOG.md                   # Version history
│   ├── QUICKSTART.md                  # Quick start guide
│   ├── PROJECT_SUMMARY.md             # Project summary
│   └── STRUCTURE.md                   # This file
│
├── ⚙️ Configuration
│   ├── requirements.txt               # Python dependencies
│   ├── .gitignore                     # Git ignore rules
│   ├── p1person.properties            # Connection config (created at runtime)
│   └── .p1person.key                  # Encryption key (created at runtime)
│
├── 🔨 Setup & Automation
│   ├── setup.sh                       # Automated setup script (executable)
│   └── .github/
│       └── workflows/
│           └── version-bump.yml       # GitHub Actions for versioning
│
├── 📊 Logs (created at runtime)
│   └── logs/
│       ├── YYYYMMDD_connections.log   # Connection history
│       └── YYYYMMDD_apilog.log        # API call logs
│
└── 🐍 Python Environment
    └── venv/                           # Virtual environment (gitignored)
```

## File Descriptions

### Core Application (Python)

**p1person.py** (8.2 KB)
- Main application entry point
- CLI argument parsing with argparse
- Orchestrates all operations
- Version: 0.2

**config_manager.py** (7.9 KB)
- Loads/saves configuration
- Encrypts/decrypts client secrets using Fernet
- Interactive setup wizard
- Machine-specific key derivation

**pingone_client.py** (12.9 KB)
- OAuth2 client credentials authentication
- PingOne Management API v1 wrapper
- Token caching with automatic refresh
- Comprehensive error handling
- Request logging with timing

**attribute_manager.py** (11.0 KB)
- Create attributes
- Display attributes
- Remove attributes
- Clear/disable attributes
- Dry run mode support
- Progress reporting

**logger.py** (4.4 KB)
- Date-stamped log file creation
- API call logging
- Connection logging
- Test logging
- Formatted output

### Testing

**test_p1person.py** (12.7 KB)
- 16 unit tests covering all modules
- Mock-based API testing
- Configuration encryption tests
- Attribute operation tests
- 100% pass rate

### Documentation

**README.md** (9.1 KB)
- Complete project documentation
- Installation instructions
- Usage examples
- API reference
- Troubleshooting guide

**CHANGELOG.md** (2.8 KB)
- Version history
- Changes per release
- Technical details

**QUICKSTART.md** (3.1 KB)
- Fast getting-started guide
- Common tasks
- PingOne setup requirements
- Security notes

**PROJECT_SUMMARY.md** (7.1 KB)
- Project overview
- Features checklist
- Architecture diagram
- Development standards

### Configuration Files

**requirements.txt** (349 bytes)
```
requests>=2.31.0
cryptography>=41.0.0
```

**.gitignore** (1.9 KB)
- Excludes sensitive files
- Python build artifacts
- IDE files
- Log files
- Virtual environment

### Setup & Automation

**setup.sh** (1.8 KB)
- Automated setup script
- Creates virtual environment
- Installs dependencies
- Runs tests
- Provides next steps

**.github/workflows/version-bump.yml** (1.8 KB)
- Automatic version increment (+0.01)
- Updates CHANGELOG.md
- Commits changes
- Runs on push to main

## Runtime Files (Not in Git)

### Configuration (Created on First Run)

**p1person.properties**
- Standard Java properties format (key=value pairs)
- Friendly name
- Environment ID
- Client ID
- Encrypted client secret
- Optional logging levels (api_log_level, connection_log_level)
- Additional attributes (prefixed with additional_attribute.)
- Comments for documentation
- Permissions: 600 (owner only)

**.p1person.key**
- Encryption key (60 bytes)
- Machine-specific
- Permissions: 600 (owner only)

### Logs (Created at Runtime)

**YYYYMMDD_connections.log**
- Timestamp of each connection
- Friendly name of environment
- Connection success/failure

**YYYYMMDD_apilog.log**
- HTTP method and URL
- Status code
- Response time (ms)
- Error messages

## Dependencies Graph

```
p1person.py
    │
    ├─→ config_manager.py
    │       └─→ cryptography (Fernet, PBKDF2HMAC)
    │
    ├─→ pingone_client.py
    │       └─→ requests
    │
    ├─→ attribute_manager.py
    │       └─→ pingone_client.py
    │
    └─→ logger.py
            └─→ logging (stdlib)

test_p1person.py
    └─→ unittest (stdlib)
```

## Size Summary

| Category | Files | Total Size |
|----------|-------|------------|
| Python Code | 5 | ~52 KB |
| Tests | 1 | ~13 KB |
| Documentation | 5 | ~29 KB |
| Config | 3 | ~3 KB |
| Scripts | 2 | ~4 KB |
| **Total** | **16** | **~101 KB** |

## Permissions

| File | Mode | Notes |
|------|------|-------|
| p1person.py | 755 | Executable |
| setup.sh | 755 | Executable |
| p1person.properties | 600 | Owner only (created at runtime) |
| .p1person.key | 600 | Owner only (created at runtime) |
| Other .py files | 644 | Standard |
| Documentation | 644 | Standard |

## Module Relationships

```
┌─────────────────┐
│   p1person.py   │ ◄── Entry Point
│   (Main CLI)    │
└────────┬────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
┌─────────────────┐                  ┌─────────────────┐
│ config_manager  │                  │     logger      │
│  (Config I/O)   │                  │   (Logging)     │
└─────────────────┘                  └─────────────────┘
         │                                     ▲
         │                                     │
         ▼                                     │
┌─────────────────┐                           │
│ pingone_client  │───────────────────────────┘
│   (API Layer)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│attribute_manager│
│ (Business Logic)│
└─────────────────┘
```

## Data Flow

1. **User Input** → CLI Parser (p1person.py)
2. **Configuration** → config_manager → Decrypt credentials
3. **Authentication** → pingone_client → Get OAuth2 token
4. **Operation** → attribute_manager → Execute via API client
5. **Logging** → logger → Write to date-stamped files
6. **Output** → Console → Display results

## Security Architecture

```
p1person.properties (on disk)
    │
    │ Contains: client_secret_encrypted (Base64)
    │
    ▼
config_manager._decrypt_secret()
    │
    │ Uses: .p1person.key (Fernet key)
    │ Algorithm: AES-256-CBC
    │
    ▼
client_secret (in memory only)
    │
    │ Never logged, never displayed
    │
    ▼
pingone_client (OAuth2 flow)
    │
    │ Sent over HTTPS only
    │
    ▼
PingOne API
```

## Best Practices Applied

✅ Separation of Concerns (each module has one responsibility)  
✅ DRY Principle (shared logger, no code duplication)  
✅ Fail-Safe Defaults (secure by default)  
✅ Defense in Depth (multiple security layers)  
✅ Comprehensive Error Handling (try/catch everywhere)  
✅ Clear Naming Conventions (readable code)  
✅ Documentation at All Levels (code, API, user docs)  

---

**Last Updated**: 2026-02-05  
**Version**: 0.2
