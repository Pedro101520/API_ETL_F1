import requests
import os
import streamlit as st
import json

from google.cloud import storage
from google.oauth2 import service_account

class Salvar():
    def get_storage_client(self):
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return storage.Client()
        
        credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        return storage.Client(
            credentials=credentials,
            project=credentials.project_id
        )