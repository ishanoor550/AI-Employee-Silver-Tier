#!/usr/bin/env python3
"""
Simple File System Watcher for AI Employee (no external dependencies)
Monitors a drop folder for new files and creates actionable markdown files
"""

import time
import logging
import shutil
from pathlib import Path

class SimpleFileSystemWatcher:
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.drop_folder = self.vault_path / 'Dropbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.processed_files = set()  # Track files we've already processed

        # Ensure directories exist
        self.drop_folder.mkdir(exist_ok=True)
        self.needs_action.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('watcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SimpleFileSystemWatcher')

    def scan_for_new_files(self):
        """Scan the drop folder for new files"""
        new_files = []
        try:
            for item in self.drop_folder.iterdir():
                if item.is_file() and item.name not in self.processed_files:
                    new_files.append(item)
                    self.processed_files.add(item.name)
        except Exception as e:
            self.logger.error(f'Error scanning drop folder: {e}')
        return new_files

    def process_file(self, file_path: Path):
        """Process a new file by copying it to Needs_Action and creating metadata"""
        try:
            # Wait a moment to ensure file is fully written
            time.sleep(1)

            if file_path.exists():
                dest = self.needs_action / f'FILE_{file_path.name}'
                shutil.copy2(file_path, dest)
                self.create_metadata(file_path, dest)
                self.logger.info(f'Processed file: {file_path.name} -> {dest.name}')
        except Exception as e:
            self.logger.error(f'Error processing file {file_path.name}: {e}')

    def create_metadata(self, source: Path, dest: Path):
        """Create markdown metadata file for the processed file"""
        meta_path = dest.with_suffix('.md')
        meta_path.write_text(f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
processed: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

New file dropped for processing.

Original file: {source.name}
File size: {source.stat().st_size} bytes
Detected at: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Suggested Actions
- [ ] Review file contents
- [ ] Determine appropriate action
- [ ] File or process accordingly
''')

    def run(self):
        """Main watcher loop"""
        self.logger.info(f'Starting Simple File System Watcher')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Monitoring: {self.drop_folder}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')

        while True:
            try:
                new_files = self.scan_for_new_files()
                for file_path in new_files:
                    self.process_file(file_path)

                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.logger.info('Stopping watcher...')
                break
            except Exception as e:
                self.logger.error(f'Unexpected error in watcher loop: {e}')
                time.sleep(self.check_interval)  # Wait before retrying

if __name__ == "__main__":
    watcher = SimpleFileSystemWatcher(Path(__file__).parent.absolute())
    watcher.run()