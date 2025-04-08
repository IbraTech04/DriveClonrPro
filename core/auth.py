import os
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from typing import Optional

DISCOVERY_SERVICE_URL = 'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest'

class GoogleAuth:
    def __init__(self, creds_path: str, scopes: list[str], logger: Optional[logging.Logger] = None) -> None:
        self.service = None
        self.creds_path = creds_path
        self.scopes = scopes
        self.logger = logger or logging.getLogger(__name__)
        self.creds: Optional[Credentials] = None

    def authenticate(self) -> Optional[Credentials]:
        """
        Handles the OAuth flow using client secrets.
        Returns a valid Credentials object if successful.
        """
        self.logger.info("Starting authentication flow...")
        if not os.path.exists(self.creds_path):
            self.logger.error(f"Credentials file not found at {self.creds_path}")
            raise FileNotFoundError(f"Credentials file not found at {self.creds_path}")

        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, self.scopes)
            self.creds = flow.run_local_server(port=0)
            self.logger.info("Authentication successful.")
            return self.creds

        except Exception as e:
            self.logger.exception(f"Authentication failed: {e}")
            return None

    def build_new_service_from_creds(self):
        """
        Builds a new service using the credentials.
        """
        if not self.creds or not self.creds.valid:
            raise ValueError("Cannot build service: no valid credentials found.")

        self.logger.info("Building new service from credentials...")
        return build('drive', 'v3', credentials=self.creds, cache_discovery=False, discoveryServiceUrl=DISCOVERY_SERVICE_URL)

    def build_service(self, service_name: str, version: str, discovery_url: Optional[str] = None):
        """
        Returns an authorized API client service instance.
        """
        if not self.creds or not self.creds.valid:
            raise ValueError("Cannot build service: no valid credentials found.")

        self.logger.info(f"Building service: {service_name} v{version}")
        self.service = build(
            service_name,
            version,
            credentials=self.creds,
            discoveryServiceUrl=discovery_url
        ) if discovery_url else build(service_name, version, credentials=self.creds)
        return self.service
