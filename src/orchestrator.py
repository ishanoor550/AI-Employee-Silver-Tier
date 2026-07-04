#!/usr/bin/env python3
import time
import json
import logging
import sys
import shutil
from pathlib import Path
from datetime import datetime

def setup_logging(vault_path):
    log_file = Path(vault_path) / 'orchestrator.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('Orchestrator')

class Orchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        self.dirs = {
            'needs_action': self.vault_path / 'Needs_Action',
            'plans': self.vault_path / 'Plans',
            'pending_approval': self.vault_path / 'Pending_Approval',
            'approved': self.vault_path / 'Approved',
            'rejected': self.vault_path / 'Rejected',
            'done': self.vault_path / 'Done',
            'logs': self.vault_path / 'Logs',
            'inbox': self.vault_path / 'Inbox',
            'dropbox': self.vault_path / 'Dropbox',
        }
        for d in self.dirs.values():
            d.mkdir(exist_ok=True)
        self.check_interval = 10
        self.max_iterations = 20
        self.processed_sources = set()
        self.log = logging.getLogger('Orchestrator')

    def scan_needs_action(self) -> list:
        if not self.dirs['needs_action'].exists():
            return []
        items = sorted(self.dirs['needs_action'].iterdir(), key=lambda f: f.stat().st_mtime)
        return [f for f in items if f.is_file() and f.suffix == '.md' and f.name not in self.processed_sources]

    def extract_metadata(self, content: str) -> dict:
        meta = {'type': 'task', 'from': 'Unknown', 'source': 'Unknown'}
        for line in content.split('\n'):
            for key in ['type', 'from', 'subject', 'original_name']:
                if line.lower().startswith(f'{key}:'):
                    val = line.split(':', 1)[1].strip()
                    meta[key] = val
        meta['source'] = meta.get('from', meta.get('source', 'Unknown'))
        return meta

    def create_plan(self, action_file: Path) -> Path:
        content = action_file.read_text(encoding='utf-8')
        meta = self.extract_metadata(content)

        plan_content = f"""---
created: {datetime.now().isoformat()}
source: {action_file.name}
type: {meta.get('type', 'task')}
from: {meta.get('source', 'Unknown')}
status: pending_approval
---

## Objective
Process {meta.get('type', 'task')} from {meta.get('source', 'Unknown')}

## Source
{action_file.name}

## Analysis Steps
1. Review the action item
2. Determine required actions per Company_Handbook.md
3. Execute or route for approval
4. Log and archive

## Action Checklist
- [ ] Review source file contents
- [ ] Check Company_Handbook.md for applicable rules
- [ ] Determine if human approval needed
- [ ] Route to Pending_Approval if sensitive
- [ ] Execute action (email, post, etc.)
- [ ] Log the action
- [ ] Move completed files to /Done

## Approval Decision
- Move this file to /Approved to authorize the action
- Move this file to /Rejected to decline
"""

        plan_name = f'PLAN_{action_file.stem}.md'
        plan_path = self.dirs['plans'] / plan_name
        plan_path.write_text(plan_content, encoding='utf-8')

        archive_dir = self.dirs['done'] / 'sources'
        archive_dir.mkdir(exist_ok=True)
        shutil.move(str(action_file), str(archive_dir / action_file.name))
        self.processed_sources.add(action_file.name)
        self.log.info(f'Plan created: {plan_name} from {action_file.name}')
        return plan_path

    def process_approvals(self):
        if not self.dirs['approved'].exists():
            return 0
        count = 0
        for item in sorted(self.dirs['approved'].iterdir()):
            if item.is_file():
                dest = self.dirs['done'] / f'DONE_{item.name}'
                shutil.move(str(item), str(dest))
                self._log('action_approved', {'file': item.name, 'moved_to': 'Done'})
                count += 1
                self.log.info(f'Approved: {item.name}')
        return count

    def process_rejections(self):
        if not self.dirs['rejected'].exists():
            return 0
        count = 0
        for item in sorted(self.dirs['rejected'].iterdir()):
            if item.is_file():
                dest = self.dirs['done'] / f'REJECTED_{item.name}'
                shutil.move(str(item), str(dest))
                self._log('action_rejected', {'file': item.name, 'moved_to': 'Done'})
                count += 1
                self.log.info(f'Rejected: {item.name}')
        return count

    def _log(self, action_type: str, details: dict):
        log_file = self.dirs['logs'] / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
            'details': details
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
            log_file.write_text(json.dumps(existing, indent=2), encoding='utf-8')
        except Exception as e:
            self.log.error(f'Log write failed: {e}')

    def update_dashboard(self):
        pending = len(list(self.dirs['needs_action'].glob('*.md'))) if self.dirs['needs_action'].exists() else 0
        plans = len(list(self.dirs['plans'].glob('*.md'))) if self.dirs['plans'].exists() else 0
        done = len(list(self.dirs['done'].rglob('*'))) if self.dirs['done'].exists() else 0
        approval = len(list(self.dirs['pending_approval'].glob('*.md'))) if self.dirs['pending_approval'].exists() else 0

        content = f"""# Dashboard

Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Workflow Status
| Stage | Count |
|-------|-------|
| Needs Action | {pending} |
| Active Plans | {plans} |
| Pending Approval | {approval} |
| Completed | {done} |

## Today's Focus
- [ ] Process Needs_Action items
- [ ] Review pending approvals
- [ ] Check watchers

## System
- Orchestrator: Running
- Interval: {self.check_interval}s
"""
        self.dirs['vault_path'] = self.vault_path
        dashboard_path = self.vault_path / 'Dashboard.md'
        dashboard_path.write_text(content, encoding='utf-8')
        self.log.info('Dashboard updated')

    def ralph_wiggum_loop(self, task_description: str) -> bool:
        self.log.info(f'Ralph Wiggum: {task_description}')
        for i in range(1, self.max_iterations + 1):
            items = self.scan_needs_action()
            if not items:
                approved = self.process_approvals()
                rejected = self.process_rejections()
                if approved == 0 and rejected == 0:
                    self.log.info(f'Ralph Wiggum: All clear at iteration {i}')
                    return True
            else:
                for item in items[:3]:
                    self.create_plan(item)
            time.sleep(self.check_interval)
        self.log.warning('Ralph Wiggum: Max iterations reached')
        return False

    def run_once(self):
        items = self.scan_needs_action()
        for item in items:
            self.create_plan(item)
        approved = self.process_approvals()
        rejected = self.process_rejections()
        self.update_dashboard()
        return len(items) + approved + rejected

    def run(self):
        self.log.info('=' * 50)
        self.log.info('AI Employee Orchestrator - Silver Tier')
        self.log.info(f'Vault: {self.vault_path}')
        self.log.info('=' * 50)
        while True:
            try:
                processed = self.run_once()
                if processed > 0:
                    self.log.info(f'Processed {processed} items this cycle')
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.log.info('Orchestrator stopped by user')
                break
            except Exception as e:
                self.log.error(f'Orchestrator error: {e}')
                time.sleep(self.check_interval)

def main():
    vault = Path(__file__).parent.parent.resolve()
    setup_logging(str(vault))
    orch = Orchestrator(str(vault))
    orch.run()

if __name__ == '__main__':
    main()
