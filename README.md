# Personal AI Employee - Silver Tier

**Functional Assistant** - Building on Bronze foundation with multi-watcher support, MCP integration, and Human-in-the-Loop workflow.

## Silver Tier Features

- **3 Watcher Scripts**: Gmail, WhatsApp, LinkedIn
- **LinkedIn Auto-Posting**: Generate and schedule business posts
- **Claude Reasoning Loop**: Plan.md creation for all actions
- **Email MCP Server**: Send emails through MCP protocol
- **Human-in-the-Loop**: Approval workflow for sensitive actions
- **Task Scheduling**: Daily briefings and weekly audits
- **Agent Skills**: All AI functionality as Claude Agent Skills

## Architecture

```
AI_Employee_Vault/
├── .claude/skills/          # Claude Agent Skills
├── src/                     # Python source files
│   ├── base_watcher.py      # Abstract base watcher
│   ├── gmail_watcher.py     # Gmail monitoring
│   ├── whatsapp_watcher.py  # WhatsApp monitoring
│   ├── linkedin_watcher.py  # LinkedIn automation
│   ├── orchestrator.py      # Master orchestrator
│   ├── scheduler.py         # Task scheduling
│   └── plan_generator.py    # Plan.md generator
├── email_mcp_server.py      # Email MCP server
├── mcp.json                 # MCP server config
├── Business_Goals.md        # Business objectives
├── Company_Handbook.md      # Rules of engagement
├── Dashboard.md             # Real-time status
├── Inbox/                   # File drop zone
├── Needs_Action/            # Items needing processing
├── Plans/                   # Generated plans
├── Pending_Approval/        # Awaiting human review
├── Approved/                # Human-approved items
├── Rejected/                # Human-rejected items
├── Done/                    # Completed items
├── Logs/                    # Audit trail
├── Briefings/               # Daily/weekly reports
├── Signals/                 # Cross-component signals
└── Accounting/              # Financial records
```

## Setup

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. For WhatsApp watcher, install Playwright browsers:
   ```
   playwright install chromium
   ```

3. Configure Gmail API credentials:
   - Create project at console.cloud.google.com
   - Enable Gmail API
   - Download credentials.json to vault root

4. Update mcp.json with your SMTP credentials:
   - Set SMTP_USER and SMTP_PASS environment variables
   - Set DRY_RUN to "false" when ready to send real emails

5. Start the orchestrator:
   ```
   python src/orchestrator.py
   ```

6. Start individual watchers:
   ```
   python src/gmail_watcher.py
   python src/whatsapp_watcher.py
   python src/linkedin_watcher.py
   ```

7. Schedule daily tasks:
   ```
   python src/scheduler.py
   ```

## Agent Skills

All AI functionality is implemented as Claude Agent Skills in `.claude/skills/`:
- `process-needs-action.skill` - Process action items
- `complete-task.skill` - Complete and archive tasks
- `update-dashboard.skill` - Update dashboard status
- `send-email.skill` - Send emails via MCP
- `linkedin-post.skill` - LinkedIn social media management
- `approval-workflow.skill` - Human-in-the-loop approvals
