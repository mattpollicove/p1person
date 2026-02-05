"""
PingOne API Client
Handles authentication and API communication with PingOne
"""

import time
from datetime import datetime, timedelta

import requests

# Constants
TOKEN_PREVIEW_LENGTH = 20
DEFAULT_TIMEOUT = 30
RETRY_DELAY = 1


class PingOneClient:
    """Client for interacting with PingOne Management API."""
    
    # PingOne API base URLs
    API_BASE_URLS = {
        'NA': 'https://api.pingone.com/v1',
        'EU': 'https://api.pingone.eu/v1',
        'ASIA': 'https://api.pingone.asia/v1',
        'CA': 'https://api.pingone.ca/v1'
    }
    
    def __init__(self, config, logger, region='NA'):
        """
        Initialize PingOne client.
        
        Args:
            config: Configuration dictionary with connection details
            logger: Logger instance for API calls
            region: PingOne region (NA, EU, ASIA, CA)
        """
        self.config = config
        self.logger = logger
        self.region = region
        self.base_url = self.API_BASE_URLS.get(region, self.API_BASE_URLS['NA'])
        self.environment_id = config['environment_id']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        
        # Token management
        self._access_token = None
        self._token_expiry = None
    
    def _log_api_call(self, method, url, status_code, response_time, error=None):
        """
        Log API call details.
        
        Args:
            method: HTTP method
            url: Request URL
            status_code: HTTP status code
            response_time: Request duration in seconds
            error: Error message if any
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'url': url,
            'status_code': status_code,
            'response_time_ms': round(response_time * 1000, 2),
            'error': error
        }
        
        if error:
            self.logger.error(f"API Call Failed: {method} {url} - {error}")
        else:
            self.logger.info(f"API Call: {method} {url} - Status: {status_code} - Time: {log_entry['response_time_ms']}ms")
    
    def _get_access_token(self):
        """
        Obtain OAuth2 access token from PingOne.
        Uses client credentials grant type.
        
        Returns:
            str: Access token
            
        Raises:
            Exception: If authentication fails
        """
        # Return cached token if still valid
        if self._access_token and self._token_expiry:
            if datetime.now() < self._token_expiry - timedelta(minutes=5):
                return self._access_token
        
        # Token endpoint according to PingOne documentation
        token_url = f'https://auth.pingone.com/{self.environment_id}/as/token'
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(token_url, data=data, headers=headers, timeout=30)
            response_time = time.time() - start_time
            
            self._log_api_call('POST', token_url, response.status_code, response_time)
            
            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data['access_token']
                # Set expiry with buffer
                expires_in = token_data.get('expires_in', 3600)
                self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                # Log token scopes for debugging
                scopes = token_data.get('scope', 'No scopes returned')
                token_type = token_data.get('token_type', 'Unknown')
                token_preview = (self._access_token[:TOKEN_PREVIEW_LENGTH] + '...' 
                                if len(self._access_token) > TOKEN_PREVIEW_LENGTH 
                                else self._access_token)
                self.logger.info(f"Access token obtained. Type: {token_type}, Scopes: {scopes}")
                self.logger.debug(f"Token preview: {token_preview}, Length: {len(self._access_token)}")
                
                # Verify token format (should be JWT: xxx.yyy.zzz)
                if self._access_token.count('.') != 2:
                    self.logger.warning(f"Access token may not be a valid JWT format. Dots found: {self._access_token.count('.')}")
                
                return self._access_token
            else:
                error_msg = f"Authentication failed: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('error_description', error_detail.get('error', ''))}"
                except:
                    error_msg += f" - {response.text}"
                
                self._log_api_call('POST', token_url, response.status_code, response_time, error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            error_msg = f"Network error during authentication: {str(e)}"
            self._log_api_call('POST', token_url, 0, response_time, error_msg)
            raise Exception(error_msg)
    
    def test_connection(self):
        """
        Test connection to PingOne by attempting to authenticate and fetch environment details.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Get access token
            token = self._get_access_token()
            
            # Try to fetch environment details to verify connection
            url = f"{self.base_url}/environments/{self.environment_id}"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=30)
            response_time = time.time() - start_time
            
            self._log_api_call('GET', url, response.status_code, response_time)
            
            if response.status_code == 200:
                env_data = response.json()
                env_name = env_data.get('name', 'Unknown')
                return True, f"Connected to environment: {env_name}"
            else:
                error_msg = f"Failed to fetch environment details: {response.status_code}"
                return False, error_msg
                
        except Exception as e:
            return False, str(e)
    
    def _get_user_schema_id(self):
        """
        Get the User schema ID for this environment.
        Caches the result to avoid repeated API calls.
        
        Returns:
            tuple: (success: bool, schema_id: str or None, error: str or None)
        """
        # Cache the schema ID
        if hasattr(self, '_user_schema_id') and self._user_schema_id:
            return True, self._user_schema_id, None
        
        endpoint = f"environments/{self.environment_id}/schemas"
        success, data, error = self._make_request('GET', endpoint)
        
        if not success:
            return False, None, f"Failed to get schemas: {error}"
        
        # Find the User schema
        if data and '_embedded' in data and 'schemas' in data['_embedded']:
            for schema in data['_embedded']['schemas']:
                if schema.get('name') == 'User':
                    self._user_schema_id = schema.get('id')
                    return True, self._user_schema_id, None
        
        return False, None, "Could not find User schema"
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """
        Make authenticated request to PingOne API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (relative to base_url)
            data: Request body (dict)
            params: Query parameters (dict)
            
        Returns:
            tuple: (success: bool, response_data: dict or None, error_message: str or None)
        """
        try:
            token = self._get_access_token()
            
            url = f"{self.base_url}/{endpoint}"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Debug logging for POST requests
            if method.upper() == 'POST':
                token_preview = (token[:TOKEN_PREVIEW_LENGTH] + '...' 
                                if len(token) > TOKEN_PREVIEW_LENGTH 
                                else token)
                self.logger.debug(f"Making {method} request to {url}")
                self.logger.debug(f"Using token: {token_preview} (length: {len(token)})")
                self.logger.debug(f"Authorization header: Bearer {token_preview}...")
            
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            
            # Log the API call
            if response.status_code >= 400:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    if 'message' in error_detail:
                        error_msg += f" - {error_detail['message']}"
                    
                    # Special handling for 403 Forbidden
                    if response.status_code == 403:
                        # Log full response for debugging
                        self.logger.debug(f"403 Response: {error_detail}")
                        self.logger.debug(f"Response headers: {dict(response.headers)}")
                        
                        error_msg += "\n\n⚠️  PERMISSION ISSUE DETECTED:"
                        error_msg += "\nYour Worker App may lack the required permissions."
                        error_msg += "\nRequired roles: 'Environment Admin' or 'Identity Data Admin'"
                        error_msg += f"\nPlease check your Worker App (Client ID: {self.client_id}) in the PingOne console."
                        if 'details' in error_detail:
                            error_msg += f"\nDetails: {error_detail['details']}"
                        # Also check for specific error codes
                        if 'code' in error_detail:
                            error_msg += f"\nError code: {error_detail['code']}"
                except Exception as parse_error:
                    self.logger.debug(f"Could not parse error response: {parse_error}")
                    self.logger.debug(f"Raw response text: {response.text}")
                self._log_api_call(method.upper(), url, response.status_code, response_time, error_msg)
            else:
                self._log_api_call(method.upper(), url, response.status_code, response_time)
            
            # Handle response
            if response.status_code in [200, 201, 204]:
                if response.status_code == 204:
                    return True, None, None
                try:
                    return True, response.json(), None
                except:
                    return True, None, None
            else:
                error_msg = f"API request failed: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('message', error_detail)}"
                    
                    # Add helpful context for 403 errors
                    if response.status_code == 403:
                        error_msg += "\n\nThis is likely a permissions issue. Your Worker App needs:"
                        error_msg += "\n  • Environment Admin role, OR"
                        error_msg += "\n  • Identity Data Admin role"
                        error_msg += f"\n\nCheck Worker App permissions in PingOne console for Client ID: {self.client_id}"
                except:
                    error_msg += f" - {response.text}"
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            self.logger.error(f"API request timeout: {method} {endpoint}")
            return False, None, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.logger.error(f"API request error: {method} {endpoint} - {error_msg}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"Unexpected error in API request: {method} {endpoint} - {error_msg}", exc_info=True)
            return False, None, error_msg
    
    def get_schema_attributes(self):
        """
        Get all schema attributes for the environment.
        Uses the PingOne Management API to retrieve user schema attributes.
        First gets the User schema, then retrieves its attributes.
        
        Returns:
            tuple: (success: bool, attributes: list or None, error: str or None)
        """
        # Get the User schema ID
        success, user_schema_id, error = self._get_user_schema_id()
        
        if not success:
            return False, None, error
        
        # Now get the attributes for the User schema
        attrs_endpoint = f"environments/{self.environment_id}/schemas/{user_schema_id}/attributes"
        return self._make_request('GET', attrs_endpoint)
    
    def get_attribute_by_name(self, attribute_name):
        """
        Get a specific attribute by name.
        
        Args:
            attribute_name: Name of the attribute
            
        Returns:
            tuple: (success: bool, attribute: dict or None, error: str or None)
        """
        success, data, error = self.get_schema_attributes()
        
        if not success:
            return False, None, error
        
        # Search for attribute in embedded items
        if data and '_embedded' in data and 'attributes' in data['_embedded']:
            for attr in data['_embedded']['attributes']:
                if attr.get('name') == attribute_name:
                    return True, attr, None
        
        return True, None, None  # Not found, but no error
    
    def create_attribute(self, name, description, data_type='STRING'):
        """
        Create a custom user attribute.
        According to PingOne documentation, custom attributes must be created under a specific schema.
        
        Args:
            name: Attribute name
            description: Attribute description
            data_type: Data type (STRING, BOOLEAN, INTEGER, JSON)
            
        Returns:
            tuple: (success: bool, attribute: dict or None, error: str or None)
        """
        # Get the User schema ID
        success, user_schema_id, error = self._get_user_schema_id()
        
        if not success:
            return False, None, error
        
        # Create attribute under the User schema
        endpoint = f"environments/{self.environment_id}/schemas/{user_schema_id}/attributes"
        
        # Payload according to PingOne API documentation
        payload = {
            'name': name,
            'displayName': name,
            'description': description,
            'type': data_type,
            'enabled': True,
            'unique': False,
            'multivalued': False
        }
        
        return self._make_request('POST', endpoint, data=payload)
    
    def delete_attribute(self, attribute_id):
        """
        Delete a custom attribute by ID.
        
        Args:
            attribute_id: ID of the attribute to delete
            
        Returns:
            tuple: (success: bool, data: None, error: str or None)
        """
        # Get the User schema ID
        success, user_schema_id, error = self._get_user_schema_id()
        
        if not success:
            return False, None, error
        
        endpoint = f"environments/{self.environment_id}/schemas/{user_schema_id}/attributes/{attribute_id}"
        return self._make_request('DELETE', endpoint)
    
    def update_attribute(self, attribute_id, enabled=None, description=None):
        """
        Update an attribute's properties.
        
        Args:
            attribute_id: ID of the attribute
            enabled: Enable/disable the attribute
            description: Update description
            
        Returns:
            tuple: (success: bool, attribute: dict or None, error: str or None)
        """
        # Get the User schema ID
        success, user_schema_id, error = self._get_user_schema_id()
        
        if not success:
            return False, None, error
        
        endpoint = f"environments/{self.environment_id}/schemas/{user_schema_id}/attributes/{attribute_id}"
        
        payload = {}
        if enabled is not None:
            payload['enabled'] = enabled
        if description is not None:
            payload['description'] = description
        
        return self._make_request('PATCH', endpoint, data=payload)
    
    def create_user(self, user_data):
        """
        Create a user in PingOne.
        
        Args:
            user_data: Dictionary containing user attributes
            
        Returns:
            tuple: (success: bool, user: dict or None, error: str or None)
        """
        endpoint = f"environments/{self.environment_id}/users"
        return self._make_request('POST', endpoint, data=user_data)
