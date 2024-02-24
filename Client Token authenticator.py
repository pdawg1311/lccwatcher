from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# Load client configuration from JSON
client_config = json.load(open('token.json'))

# Define OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.addons.current.action.compose',
    'https://www.googleapis.com/auth/gmail.addons.current.message.action',
    'https://www.googleapis.com/auth/gmail.addons.current.message.metadata',
    'https://www.googleapis.com/auth/gmail.addons.current.message.readonly',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.insert',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.settings.sharing',
    'https://mail.google.com/'
]


# Run OAuth 2.0 flow
flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
credentials = flow.run_local_server()

# Save credentials to token.json
with open('token.json', 'w') as token:
    token.write(credentials.to_json())
