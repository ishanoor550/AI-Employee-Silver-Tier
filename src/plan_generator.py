#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from datetime import datetime

def generate_plan(action_file_path: str) -> dict:
    vault = Path(__file__).parent.parent.absolute()
    action_file = Path(action_file_path)
    plans_dir = vault / 'Plans'
    plans_dir.mkdir(exist_ok=True)

    if not action_file.exists():
        return {'error': f'Action file not found: {action_file_path}'}

    content = action_file.read_text()
    item_type = 'task'
    item_source = 'Unknown'
    for line in content.split('\n'):
        if line.startswith('type:'):
            item_type = line.split(':', 1)[1].strip()
        if line.startswith('from:'):
            item_source = line.split(':', 1)[1].strip()
        if line.startswith('subject:'):
            item_source = line.split(':', 1)[1].strip()

    plan_content = f'''---
created: {datetime.now().isoformat()}
source_file: {action_file.name}
source_type: {item_type}
status: pending_approval
---

## Objective
Process {item_type} from {item_source}

## Analysis
An action item has been detected and needs to be processed.

Type: {item_type}
Source: {item_source}

## Steps
- [ ] Review the action item details
- [ ] Determine what actions are required
- [ ] Check Company Handbook for applicable rules
- [ ] Execute the required actions
- [ ] Log completion

## Source Content
{content[:500]}
'''

    plan_filename = f'PLAN_{action_file.stem}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    plan_path = plans_dir / plan_filename
    plan_path.write_text(plan_content)

    return {
        'status': 'created',
        'plan_file': str(plan_path),
        'plan_name': plan_filename,
        'source': action_file.name,
        'type': item_type
    }

if __name__ == '__main__':
    if len(sys.argv) > 1:
        result = generate_plan(sys.argv[1])
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({'error': 'Usage: python plan_generator.py <action_file_path>'}))
