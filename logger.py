"""
Logging Module for p1person
Handles connection and API call logging with date-stamped files
"""

import logging
from datetime import datetime
from pathlib import Path

# Constants
DATE_FORMAT_FILE = '%Y%m%d'
DATE_FORMAT_LOG = '%Y-%m-%d %H:%M:%S'
LOG_DIR_NAME = 'logs'
DEFAULT_LOG_LEVEL = 'INFO'


def get_log_filename(prefix):
    """
    Generate date-stamped log filename.
    
    Args:
        prefix: Log file prefix (e.g., 'connections', 'apilog')
        
    Returns:
        str: Filename in format YYYYMMDD_prefix.log
    """
    date_str = datetime.now().strftime('%Y%m%d')
    return f"{date_str}_{prefix}.log"


def setup_logging(api_log_level='INFO', connection_log_level='INFO'):
    """
    Setup logging for API calls and connections.
    Creates date-stamped log files.
    
    Args:
        api_log_level: Logging level for API logger (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        connection_log_level: Logging level for connection logger (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        tuple: (api_logger, connection_logger)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Convert string level to logging constant
    api_level = getattr(logging, api_log_level.upper(), logging.INFO)
    connection_level = getattr(logging, connection_log_level.upper(), logging.INFO)
    
    # Setup API logger
    api_logger = logging.getLogger('p1person.api')
    api_logger.setLevel(api_level)
    api_logger.handlers.clear()  # Clear any existing handlers
    
    api_log_file = log_dir / get_log_filename('apilog')
    api_handler = logging.FileHandler(api_log_file)
    api_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt=DATE_FORMAT_LOG
    )
    api_handler.setFormatter(api_formatter)
    api_logger.addHandler(api_handler)
    
    # Setup connection logger
    connection_logger = logging.getLogger('p1person.connections')
    connection_logger.setLevel(connection_level)
    connection_logger.handlers.clear()  # Clear any existing handlers
    
    connection_log_file = log_dir / get_log_filename('connections')
    connection_handler = logging.FileHandler(connection_log_file)
    connection_formatter = logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt=DATE_FORMAT_LOG
    )
    connection_handler.setFormatter(connection_formatter)
    connection_logger.addHandler(connection_handler)
    
    return api_logger, connection_logger


def log_connection(logger, friendly_name):
    """
    Log a successful connection.
    
    Args:
        logger: Connection logger instance
        friendly_name: Friendly name of the connection
    """
    try:
        logger.info(f"Connection established: {friendly_name}")
    except Exception as e:
        # If logging fails, print to stderr but don't crash
        import sys
        print(f"WARNING: Failed to log connection: {str(e)}", file=sys.stderr)


def log_api_call(logger, method, url, status_code, response_time_ms, error=None):
    """
    Log an API call.
    
    Args:
        logger: API logger instance
        method: HTTP method
        url: Request URL
        status_code: HTTP status code
        response_time_ms: Response time in milliseconds
        error: Error message if any
    """
    try:
        if error:
            logger.error(
                f"{method} {url} - Status: {status_code} - "
                f"Time: {response_time_ms}ms - Error: {error}"
            )
        else:
            logger.info(
                f"{method} {url} - Status: {status_code} - "
                f"Time: {response_time_ms}ms"
            )
    except Exception as e:
        # If logging fails, print to stderr but don't crash
        import sys
        print(f"WARNING: Failed to log API call: {str(e)}", file=sys.stderr)



