#!/usr/bin/env python3
import sys, json, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path(os.getenv('VAULT_PATH', Path(__file__).parent))
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASS = os.getenv('SMTP_PASS', '')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

def log_action(action, details, status='success'):
    logs_dir = VAULT_PATH / 'Logs'
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.json'
    entry = {'timestamp': datetime.now().isoformat(), 'action_type': f'email_{action}', 'actor': 'email_mcp_server', 'parameters': details, 'result': status}
    try:
        existing = []
        if log_file.exists():
            raw = log_file.read_text().strip()
            if raw:
                existing = json.loads(raw) if isinstance(json.loads(raw), list) else [json.loads(raw)]
        existing.append(entry)
        log_file.write_text(json.dumps(existing, indent=2))
    except Exception:
        pass

def handle_send_email(params):
    to = params.get('to', '')
    subject = params.get('subject', '')
    body = params.get('body', '')
    cc = params.get('cc', '')
    if DRY_RUN:
        log_action('draft', {'to': to, 'subject': subject})
        return {'content': [{'type': 'text', 'text': f'[DRY RUN] Email to {to}: {subject}'}]}
    if not SMTP_USER or not SMTP_PASS:
        return {'content': [{'type': 'text', 'text': 'SMTP not configured. Set SMTP_USER and SMTP_PASS env vars.'}], 'isError': True}
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER; msg['To'] = to; msg['Subject'] = subject
        if cc: msg['Cc'] = cc
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        recipients = [to] + ([cc] if cc else [])
        server.sendmail(SMTP_USER, recipients, msg.as_string())
        server.quit()
        log_action('sent', {'to': to, 'subject': subject})
        return {'content': [{'type': 'text', 'text': f'Email sent to {to}'}]}
    except Exception as e:
        log_action('failed', {'to': to, 'subject': subject, 'error': str(e)}, 'error')
        return {'content': [{'type': 'text', 'text': str(e)}], 'isError': True}

TOOLS = [
    {'name': 'send_email', 'description': 'Send an email via SMTP', 'inputSchema': {'type': 'object', 'properties': {'to': {'type': 'string', 'description': 'Recipient email'}, 'subject': {'type': 'string', 'description': 'Email subject'}, 'body': {'type': 'string', 'description': 'Email body'}, 'cc': {'type': 'string', 'description': 'CC recipient (optional)'}}, 'required': ['to', 'subject', 'body']}},
    {'name': 'get_status', 'description': 'Get MCP server status', 'inputSchema': {'type': 'object', 'properties': {}, 'required': []}}
]

def handle_request(request):
    method = request.get('method', '')
    req_id = request.get('id', None)
    params = request.get('params', {})
    if method == 'initialize':
        result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'email-mcp-server', 'version': '1.0.0'}}
    elif method == 'tools/list':
        result = TOOLS
    elif method == 'tools/call':
        tool_name = params.get('name', '')
        tool_args = params.get('arguments', {})
        if tool_name == 'send_email':
            result = handle_send_email(tool_args)
        elif tool_name == 'get_status':
            result = {'content': [{'type': 'text', 'text': json.dumps({'dry_run': DRY_RUN, 'smtp_configured': bool(SMTP_USER and SMTP_PASS), 'vault_path': str(VAULT_PATH)})}]}
        else:
            result = {'content': [{'type': 'text', 'text': f'Unknown tool: {tool_name}'}], 'isError': True}
    elif method == 'notifications/initialized':
        return None
    else:
        return {'jsonrpc': '2.0', 'id': req_id, 'error': {'code': -32601, 'message': f'Unknown method: {method}'}} if req_id else None
    if req_id is not None:
        return {'jsonrpc': '2.0', 'id': req_id, 'result': result}
    return None

def main():
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response:
                sys.stdout.write(json.dumps(response) + '\n')
                sys.stdout.flush()
        except json.JSONDecodeError as e:
            sys.stderr.write(f'Invalid JSON: {e}\n')
            sys.stderr.flush()

if __name__ == '__main__':
    main()
