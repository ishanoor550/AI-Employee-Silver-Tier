import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_dir = self.vault_path / 'Logs'
        self.check_interval = check_interval
        self.vault_path.mkdir(exist_ok=True)
        self.needs_action.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass

    def log_event(self, event_type: str, details: dict):
        timestamp = time.strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{timestamp}.json'
        import json
        entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'watcher': self.__class__.__name__,
            'event_type': event_type,
            'details': details
        }
        try:
            existing = []
            if log_file.exists():
                existing = json.loads(log_file.read_text())
                if not isinstance(existing, list):
                    existing = [existing]
            existing.append(entry)
            log_file.write_text(json.dumps(existing, indent=2))
        except Exception as e:
            self.logger.error(f'Failed to log event: {e}')

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    path = self.create_action_file(item)
                    self.log_event('action_created', {'file': str(path)})
            except Exception as e:
                self.logger.error(f'Error in watcher loop: {e}')
            time.sleep(self.check_interval)
