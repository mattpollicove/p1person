# Quick Start Guide - p1person

## First Time Setup

1. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   This will create a virtual environment, install dependencies, and run tests.

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Configure PingOne connection:**
   ```bash
   python p1person.py -n
   ```
   You'll be prompted to enter:
   - Friendly Name (e.g., "Production Environment")
   - Environment ID (from PingOne console)
   - Client ID (from your worker app in PingOne)
   - Client Secret (will be encrypted and stored securely)
   
   **After entering credentials, you'll be asked:**
   - "Would you like to test the connection now? (y/n)"
   - If test fails, you can retry, update config, or quit
   - Testing loops until connection succeeds or you decline

4. **Test your connection (if not done in step 3):**
   ```bash
   python p1person.py -t
   ```

## Configuration Options

### Logging Levels (Optional)

Add to `p1person.properties` to control log verbosity:

```properties
# Valid levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
api_log_level=INFO
connection_log_level=INFO
```

- **DEBUG**: Detailed troubleshooting information
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages only  
- **ERROR**: Error messages only
- **CRITICAL**: Critical errors only

## Common Tasks

### Create Default inetOrgPerson Attributes
```bash
python p1person.py
```

### Create Attributes with a Custom Prefix
```bash
python p1person.py -p MyCompany
# Creates: MyCompanytitle, MyCompanymanager, etc.
```

### View Existing Attributes
```bash
# View default attributes
python p1person.py -d

# View additional custom attributes only
python p1person.py -d -a
```

### Test Before Making Changes (Dry Run)
```bash
python p1person.py --dryrun
python p1person.py -p CustomPrefix --dryrun
python p1person.py -r --dryrun  # Test removal without actually removing
```

### Remove Attributes
```bash
# Remove with confirmation prompt
python p1person.py -r

# Remove without confirmation prompt
python p1person.py -r -y

# Remove with prefix
python p1person.py -r -p MyCompany

# Remove additional attributes
python p1person.py -r -a -y
```

### Clear Attribute Values (Disable)
```bash
# Clear with confirmation prompt
python p1person.py -c

# Clear without confirmation
python p1person.py -c -y

# Clear additional attributes
python p1person.py -c -a
```

### Use Custom Attributes
1. Edit `p1person.properties` and add your custom attributes:
   ```properties
   # Additional Custom Attributes
   badgeNumber=Employee badge number
   costCenter=Department cost center code
   ```
2. Create the attributes:
   ```bash
   python p1person.py -a
   ```
3. Display them:
   ```bash
   python p1person.py -d -a
   ```
4. Remove them:
   ```bash
   python p1person.py -r -a -y
   ```

## PingOne Requirements

### Required Scopes for Worker App
Your PingOne worker application needs these scopes:
- `p1:read:user`
- `p1:update:user`
- `p1:read:userSchema`
- `p1:update:userSchema`

### Setup in PingOne Console
1. Go to **Applications** → **Worker** apps
2. Create a new Worker app or use existing
3. Enable required scopes
4. Copy the Client ID and Client Secret
5. Note your Environment ID (in URL or environment settings)

## Troubleshooting

### "Configuration file not found"
- Run `python p1person.py -n` to create configuration

### Incomplete Configuration
- If your `p1person.properties` is missing fields, the application will prompt you to enter them
- You can choose to fill in the missing values or exit

### "Authentication failed"
- Verify your Client ID and Secret are correct
- Check that the Worker app has required scopes
- Ensure the Environment ID is correct
- The application will offer to re-enter credentials after connection failures
- Connection testing loops until successful or you decline

### Connection Test Loop
When connection fails, you have options:
- **(r)etry** - Test the same configuration again
- **(u)pdate** - Enter new connection details
- **(q)uit** - Exit the connection test

The application will keep testing until you succeed or choose to quit.

### Client Secret Issues
- If only the client secret is corrupted or invalid, you'll be prompted to enter just that field
- You don't need to re-enter all connection details

### "Failed to create attribute"
- Check that you have schema update permissions
- Verify the attribute name is valid (no special characters)
- Review `logs/YYYYMMDD_apilog.log` for details

## Log Files

All logs are stored in the `logs/` directory with date-stamped filenames:

- `YYYYMMDD_connections.log` - Connection history
- `YYYYMMDD_apilog.log` - Detailed API calls

## Getting Help

```bash
python p1person.py -h
```

## Deactivating Virtual Environment

When you're done:
```bash
deactivate
```

## Version Information

Current version: **0.2**

Version increments by 0.01 on each GitHub push unless manually updated.

## Security Notes

- Client secrets are encrypted using Fernet (AES-256)
- Configuration file has restricted permissions (owner read-only)
- Encryption keys are machine-specific
- Never commit `p1person.properties` or `.p1person.key` to version control
