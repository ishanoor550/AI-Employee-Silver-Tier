#!/usr/bin/env python3
"""
LinkedIn Auto-Poster for AI Employee Silver Tier
Uses Playwright to automate LinkedIn posting via browser.
Session is persisted so you only login once.
"""
import time
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LinkedInPoster')

class LinkedInPoster:
    def __init__(self, vault_path: str, headless: bool = False):
        self.vault_path = Path(vault_path)
        self.session_dir = self.vault_path / 'linkedin_session'
        self.session_dir.mkdir(exist_ok=True)
        self.posts_drafts = self.vault_path / 'Signals'
        self.posts_drafts.mkdir(exist_ok=True)
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

    def _ensure_playwright(self):
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            logger.error('Playwright not installed. Run: pip install playwright && playwright install chromium')
            return False

    def start_browser(self):
        if not self._ensure_playwright():
            return False
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.context = self._pw.chromium.launch_persistent_context(
            user_data_dir=str(self.session_dir),
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        return True

    def login(self, email: str = None, password: str = None) -> bool:
        if not self.page:
            if not self.start_browser():
                return False
        self.page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
        time.sleep(2)
        if 'checkpoint' in self.page.url or 'feed' in self.page.url:
            logger.info('Already logged in (session restored)')
            return True
        if email and password:
            self.page.fill('#username', email)
            self.page.fill('#password', password)
            self.page.click('button[type="submit"]')
            time.sleep(3)
            if 'feed' in self.page.url:
                logger.info('Login successful')
                return True
        logger.info('Please log in manually in the browser window...')
        logger.info(f'Waiting up to 120 seconds at: {self.page.url}')
        for _ in range(120):
            time.sleep(1)
            if 'feed' in self.page.url or 'checkpoint' in self.page.url:
                logger.info('Login detected')
                return True
            if 'linkedin.com' in self.page.url and 'login' not in self.page.url:
                logger.info('Login detected (redirected)')
                return True
        logger.warning('Login timeout - session may not be saved')
        return False

    def create_post(self, content: str) -> bool:
        if not self.page:
            logger.error('Browser not started. Call start_browser() first.')
            return False
        try:
            self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')
            time.sleep(2)
            share_box = self.page.query_selector('[aria-label="Start a post"]')
            if not share_box:
                share_box = self.page.query_selector('.share-box-feed-entry__trigger')
            if not share_box:
                share_box = self.page.query_selector('[role="combobox"]')
            if share_box:
                share_box.click()
            else:
                self.page.goto('https://www.linkedin.com/in/me/recent-activity/')
                time.sleep(2)
                post_btn = self.page.query_selector('button:has-text("Start a post")')
                if post_btn:
                    post_btn.click()
                else:
                    logger.error('Could not find post button')
                    return False
            time.sleep(2)
            editor = self.page.query_selector('[role="textbox"][aria-label*="post"]')
            if not editor:
                editor = self.page.query_selector('.ql-editor')
            if not editor:
                editor = self.page.query_selector('[contenteditable="true"]')
            if editor:
                editor.fill(content)
            else:
                logger.error('Could not find text editor')
                return False
            time.sleep(1)
            post_button = self.page.query_selector('button:has-text("Post")')
            if not post_button:
                post_button = self.page.query_selector('[data-control-name="post"]')
            if post_button:
                post_button.click()
                logger.info('Post submitted successfully')
                time.sleep(2)
                self._log_post(content, 'posted')
                return True
            else:
                logger.warning('Post button not found - content drafted but not posted')
                self._log_post(content, 'drafted')
                return False
        except Exception as e:
            logger.error(f'Post failed: {e}')
            return False

    def generate_post_content(self, topic: str = None) -> str:
        from random import choice
        if not topic:
            topic = 'AI and Business Automation'
        templates = [
            f"Excited to share our journey with {topic}! We're building autonomous AI agents that handle business operations 24/7. The future of work is here. #AI #Automation #FutureOfWork #BusinessGrowth",
            f"Insight: {topic} is transforming how businesses operate. Our AI Employee handles emails, social media, and task management autonomously. What repetitive tasks would you automate? #Productivity #AI #Innovation",
            f"Big things happening! We're leveraging {topic} to create a Digital FTE that never sleeps, never takes breaks, and delivers consistent results. Cost savings of 85% vs human employees. #Business #Technology #AI #Efficiency",
            f"Lesson learned in {topic}: The key to successful AI automation is not replacing humans - it's augmenting them. Our AI handles the routine so we can focus on strategy. #Leadership #AI #DigitalTransformation",
            f"Proud milestone: Our AI Employee system is now processing emails, generating LinkedIn content, and managing business workflows autonomously. Built with Claude Code + Obsidian. #AIEmployee #Automation #Startup",
        ]
        return choice(templates)

    def post_from_business_goals(self) -> bool:
        goals_file = self.vault_path / 'Business_Goals.md'
        topic = 'AI Business Automation'
        if goals_file.exists():
            content = goals_file.read_text()
            for line in content.split('\n'):
                if line.strip().startswith('-') and 'AI' in line:
                    topic = line.split('-', 1)[1].strip()
                    break
        post_content = self.generate_post_content(topic)
        return self.create_post(post_content)

    def _log_post(self, content: str, status: str):
        log_file = self.vault_path / 'Logs' / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'linkedin_post',
            'content_preview': content[:100],
            'status': status
        }
        try:
            existing = []
            if log_file.exists():
                raw = log_file.read_text().strip()
                if raw:
                    existing = json.loads(raw)
                    if not isinstance(existing, list):
                        existing = [existing]
            existing.append(entry)
            log_file.write_text(json.dumps(existing, indent=2))
        except Exception as e:
            logger.error(f'Log failed: {e}')

    def close(self):
        if self.context:
            self.context.close()
        if self._pw:
            self._pw.stop()

if __name__ == '__main__':
    vault = Path(__file__).parent.parent.resolve()
    poster = LinkedInPoster(str(vault), headless='--headless' in sys.argv)
    if poster.start_browser():
        poster.login()
        poster.post_from_business_goals()
        poster.close()
