import os
import time
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str = None):
        super().__init__(vault_path, check_interval=120)
        self.creds_path = credentials_path or os.path.join(vault_path, 'credentials.json')
        self.service = None
        self.processed_ids = set()
        self._init_service()

    def _init_service(self):
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            creds = None
            token_file = Path(self.vault_path) / 'token.pickle'
            if token_file.exists():
                import pickle
                with open(token_file, 'rb') as t:
                    creds = pickle.load(t)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                else:
                    return
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Gmail service initialized')
        except ImportError:
            self.logger.warning('Google client libraries not installed. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client')
        except Exception as e:
            self.logger.error(f'Failed to initialize Gmail service: {e}')

    def check_for_updates(self) -> list:
        if not self.service:
            return []
        try:
            results = self.service.users().messages().list(
                userId='me', q='is:unread', maxResults=10
            ).execute()
            messages = results.get('messages', [])
            return [m for m in messages if m['id'] not in self.processed_ids]
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []

    def create_action_file(self, message) -> Path:
        msg = self.service.users().messages().get(
            userId='me', id=message['id'], format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        snippet = msg.get('snippet', '')
        content = f'''---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content
{snippet}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
'''
        filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
        filepath.write_text(content)
        self.processed_ids.add(message['id'])
        return filepath

if __name__ == '__main__':
    watcher = GmailWatcher(Path(__file__).parent.parent.absolute())
    watcher.run()
