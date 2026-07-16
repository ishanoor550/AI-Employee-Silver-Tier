#!/usr/bin/env node
import { createInterface } from 'readline';

const VAULT_PATH = process.env.VAULT_PATH || '.';
const DRY_RUN = process.env.DRY_RUN !== 'false';

const TOOLS = [
  { name: 'send_email', description: 'Send an email via SMTP', inputSchema: { type: 'object', properties: { to: { type: 'string' }, subject: { type: 'string' }, body: { type: 'string' }, cc: { type: 'string' } }, required: ['to', 'subject', 'body'] } },
  { name: 'get_status', description: 'Get MCP server status', inputSchema: { type: 'object', properties: {}, required: [] } },
];

function handleRequest(req) {
  const { id, method, params = {} } = req;
  if (method === 'initialize') {
    return { id, result: { protocolVersion: '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'email-mcp-server', version: '1.0.0' } } };
  }
  if (method === 'notifications/initialized') return null;
  if (method === 'tools/list') return { id, result: TOOLS };
  if (method === 'tools/call') {
    const { name, arguments: args } = params;
    if (name === 'get_status') return { id, result: { content: [{ type: 'text', text: JSON.stringify({ dry_run: DRY_RUN, vault_path: VAULT_PATH }) }] } };
    if (name === 'send_email') return { id, result: { content: [{ type: 'text', text: `[DRY RUN] Email to ${args.to}: ${args.subject} (body: ${(args.body || '').substring(0, 50)}...)` }] } };
    return { id, result: { content: [{ type: 'text', text: `Unknown tool: ${name}` }], isError: true } };
  }
  return { id, error: { code: -32601, message: `Unknown method: ${method}` } };
}

const rl = createInterface({ input: process.stdin, output: process.stdout, terminal: false });
rl.on('line', (line) => {
  try {
    const req = JSON.parse(line.trim());
    const res = handleRequest(req);
    if (res) console.log(JSON.stringify(res));
  } catch (e) {
    console.error('Parse error:', e.message);
  }
});
