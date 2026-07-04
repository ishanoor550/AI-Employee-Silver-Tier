import time
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None):
        super().__init__(vault_path, check_interval=30)
        self.session_path = session_path or str(Path(vault_path) / 'whatsapp_session')
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing', 'quote']
        self.page = None
        self.browser = None

    def check_for_updates(self) -> list:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.logger.warning('Playwright not installed. Run: pip install playwright && playwright install chromium')
            return []
        try:
            with sync_playwright() as p:
                self.browser = p.chromium.launch_persistent_context(
                    self.session_path, headless=True
                )
                self.page = self.browser.pages[0]
                self.page.goto('https://web.whatsapp.com', timeout=30000)
                try:
                    self.page.wait_for_selector('[data-testid="chat-list"]', timeout=15000)
                except Exception:
                    self.logger.warning('WhatsApp Web not logged in. Scan QR code first.')
                    self.browser.close()
                    return []
                unread = self.page.query_selector_all('[aria-label*="unread"]')
                messages = []
                for chat in unread:
                    text = chat.inner_text().lower()
                    if any(kw in text for kw in self.keywords):
                        sender = chat.get_attribute('aria-label') or 'Unknown'
                        messages.append({'text': chat.inner_text(), 'sender': sender})
                self.browser.close()
                return messages
        except Exception as e:
            self.logger.error(f'Error checking WhatsApp: {e}')
            if self.browser:
                try:
                    self.browser.close()
                except Exception:
                    pass
            return []

    def create_action_file(self, item) -> Path:
        content = f'''---
type: whatsapp
from: {item.get('sender', 'Unknown')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Message Content
{item.get('text', 'No content')}

## Suggested Actions
- [ ] Reply to sender
- [ ] Flag for follow-up
- [ ] Archive after processing
'''
        filename = f'WHATSAPP_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        filepath = self.needs_action / filename
        filepath.write_text(content)
        return filepath

if __name__ == '__main__':
    watcher = WhatsAppWatcher(Path(__file__).parent.parent.absolute())
    watcher.run()
