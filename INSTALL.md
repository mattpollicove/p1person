# Installation & Setup Instructions

## p1person - PingOne Custom Attribute Management Tool

**Version:** 0.2

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Dependencies](#dependencies)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows with WSL
- **Python**: Version 3.7 or higher
- **pip**: Python package installer (usually included with Python)
- **Internet Connection**: Required for PingOne API access

### Verify Prerequisites

Check your Python version:

**On macOS/Linux:**
```bash
python3 --version
```

**On Windows:**
```cmd
python --version
```

Check pip installation:

**On macOS/Linux:**
```bash
pip3 --version
```

**On Windows:**
```cmd
python -m pip --version
```

If Python or pip is not installed, visit [python.org](https://www.python.org/downloads/) to download the latest version.

---

## Installation Methods

### Method 1: Automated Setup (Recommended)

The automated setup script handles virtual environment creation, dependency installation, and testing.

#### On macOS/Linux:

1. **Make the setup script executable:**
   ```bash
   chmod +x setup.sh
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

   The script will:
   - Verify Python 3 installation
   - Create a virtual environment in `./venv`
   - Install all required dependencies
   - Run unit tests to verify installation

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Proceed to [Configuration](#configuration)**

#### On Windows:

1. **Run the setup script:**
   ```cmd
   setup.bat
   ```

   The script will:
   - Verify Python installation
   - Create a virtual environment in `.\venv`
   - Install all required dependencies
   - Run unit tests to verify installation

2. **Activate the virtual environment:**
   ```cmd
   venv\Scripts\activate.bat
   ```

3. **Proceed to [Configuration](#configuration)**

### Method 2: Manual Setup

If you prefer manual installation or need more control:

#### Step 1: Create Virtual Environment

Create a Python virtual environment (recommended):
```bash
python3 -m venv venv
```

#### Step 2: Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

#### Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests>=2.31.0` - For HTTP API calls to PingOne
- `cryptography>=41.0.0` - For secure credential storage

#### Step 5: Verify Installation

Run the unit tests:
```bash
python test_p1person.py
```

All tests should pass. If any tests fail, see [Troubleshooting](#troubleshooting).

---

## Dependencies

### Required Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| requests | ≥2.31.0 | HTTP requests for PingOne API calls |
| cryptography | ≥41.0.0 | Secure credential encryption/storage |

### Standard Library Dependencies

The following are included with Python (no installation needed):
- `os` - Operating system interface
- `sys` - System-specific parameters
- `json` - JSON parsing
- `argparse` - Command-line argument parsing
- `configparser` - Configuration file handling
- `logging` - Application logging
- `unittest` - Unit testing framework

---

## Configuration

### Initial Configuration

After installation, configure your PingOne connection:

```bash
python p1person.py -n
```

You will be prompted to enter:

1. **Friendly Name**: A descriptive name for your environment
   ```
   Example: "Production Environment" or "Dev Environment"
   ```

2. **Environment ID**: Your PingOne environment identifier
   ```
   Found in: PingOne Console → Environment Settings
   Format: UUID (e.g., 12345678-1234-1234-1234-123456789012)
   ```

3. **Client ID**: Worker application client ID
   ```
   Found in: PingOne Console → Applications → [Your Worker App] → Configuration
   Format: UUID
   ```

4. **Client Secret**: Worker application client secret
   ```
   Found in: PingOne Console → Applications → [Your Worker App] → Configuration
   Note: Will be encrypted and stored securely
   ```

### Configuration Files

After configuration, the following files are created:

- **`p1person.properties`**: Main configuration file
  - Environment ID
  - Client ID
  - Encrypted client secret
  - API endpoints

- **`logs/`**: Log directory
  - Connection logs
  - API operation logs
  - Date-stamped log files

### Optional Configuration

Edit `p1person.properties` to customize:

```properties
# Logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
api_log_level=INFO
connection_log_level=INFO

# Custom attribute prefix (optional)
attribute_prefix=custom_

# Additional custom attributes (comma-separated)
custom_attributes=employeeType,department,division
```

---

## Verification

### Test Connection

Verify your PingOne connection:
```bash
python p1person.py -t
```

Expected output:
```
✓ Successfully authenticated with PingOne
✓ Connection test passed
```

### Display Attributes

List all inetOrgPerson schema attributes:
```bash
python p1person.py -d
```

### Run Unit Tests

Execute the test suite:
```bash
python test_p1person.py
```

Expected output:
```
.........
----------------------------------------------------------------------
Ran X tests in Y.ZZZs

OK
```

---

## Troubleshooting

### Python Not Found

**Error:** `python3: command not found`

**Solution:** Install Python 3.7+ from [python.org](https://www.python.org/downloads/)

### Permission Denied on setup.sh

**Error:** `Permission denied: ./setup.sh`

**Solution:** Make the script executable:
```bash
chmod +x setup.sh
```

### pip Install Fails

**Error:** `Could not install packages due to an EnvironmentError`

**Solution:** Use a virtual environment or add `--user` flag:
```bash
pip install --user -r requirements.txt
```

### Virtual Environment Already Activated

**Symptom:** Command prompt shows `(venv)` prefix

**Solution:** Deactivate before reactivating:
```bash
deactivate
source venv/bin/activate
```

### Connection Test Fails

**Error:** `Authentication failed` or `Connection error`

**Possible causes:**
1. Incorrect Environment ID, Client ID, or Client Secret
2. Worker app does not have required permissions
3. Network connectivity issues

**Solution:**
1. Reconfigure connection: `python p1person.py -n`
2. Verify worker app has `Organization Administrator` role
3. Check network/firewall settings

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'requests'` or `'cryptography'`

**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Cryptography Build Issues

**Error:** `Failed building wheel for cryptography`

**Solution (macOS):** Install required system libraries:
```bash
brew install openssl rust
```

**Solution (Linux):** Install build dependencies:
```bash
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
```

---

## Uninstallation

To remove p1person:

1. **Deactivate virtual environment:**
   ```bash
   deactivate
   ```

2. **Remove the project directory:**
   ```bash
   cd ..
   rm -rf P1person
   ```

3. **Remove configuration (if stored elsewhere):**
   ```bash
   # No system-wide configuration is installed
   ```

---

## Next Steps

After successful installation:

1. **Read the Quick Start Guide**: See [QUICKSTART.md](QUICKSTART.md)
2. **Review Available Commands**: Run `python p1person.py -h`
3. **Create Attributes**: Use `python p1person.py -c` to create attributes
4. **Explore Documentation**: Check [README.md](README.md) for full feature list

---

## Getting Help

- **Documentation**: See [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md)
- **Validation**: See [VALIDATION.md](VALIDATION.md) for testing procedures
- **Project Summary**: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for technical details
- **License**: See [LICENSE](LICENSE) for licensing information

---

*Last Updated: February 9, 2026*
