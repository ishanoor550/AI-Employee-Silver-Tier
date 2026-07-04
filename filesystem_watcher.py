#!/usr/bin/env python3
"""
File System Watcher for AI Employee
Monitors a drop folder for new files and creates actionable markdown files
"""

import time
import logging
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return

        source = Path(event.src_path)
        # Wait a moment to ensure file is fully written
        time.sleep(1)

        if source.exists():
            dest = self.needs_action / f'FILE_{source.name}'
            try:
                shutil.copy2(source, dest)
                self.create_metadata(source, dest)
                logging.info(f'Processed file: {source.name} -> {dest.name}')
            except Exception as e:
                logging.error(f'Error processing file {source.name}: {e}')

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

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('watcher.log'),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger('FileSystemWatcher')

    # Use current directory as vault path
    vault_path = Path(__file__).parent.absolute()
    drop_folder = vault_path / 'Dropbox'
    drop_folder.mkdir(exist_ok=True)

    logger.info(f'Starting File System Watcher')
    logger.info(f'Vault path: {vault_path}')
    logger.info(f'Monitoring: {drop_folder}')

    event_handler = DropFolderHandler(vault_path)
    observer = Observer()
    observer.schedule(event_handler, str(drop_folder), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Stopping watcher...')
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()