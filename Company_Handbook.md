# Company Handbook

## Rules of Engagement

### Communication Guidelines
- Always be polite and professional in all communications
- Flag any payment over $500 for manual approval
- Respond to urgent messages within 1 business hour
- Keep all client communications confidential
- LinkedIn posts must be proofread and professional

### Work Hours & Availability
- AI Employee operates 24/7 for monitoring and processing
- Human oversight required for: financial transactions, legal communications, strategic decisions
- Watchers run continuously, actions require human approval loop
- Escalation path: AI Employee → Human Reviewer → Management

### Watcher Priorities
1. Gmail Watcher: Check every 2 minutes for urgent emails
2. WhatsApp Watcher: Check every 30 seconds for keyword messages
3. LinkedIn Automation: Generate posts every hour for review
4. File System Watcher: Monitor Dropbox for new files

### Human-in-the-Loop (HITL) Rules
- All financial transactions require approval file in /Pending_Approval
- New email contacts require approval before first reply
- LinkedIn posts require approval before publishing
- Move approval files to /Approved to authorize
- Move approval files to /Rejected to decline

### Data Handling & Privacy
- All data stored locally in the Obsidian vault
- No personal data shared with external services without explicit consent
- Regular backups of the vault recommended
- Sensitive information (.env, tokens, credentials) never stored in vault
- API credentials stored in environment variables only

### Task Processing Priority
1. Urgent client communications
2. Financial transactions requiring attention
3. LinkedIn business posts and engagement
4. Scheduled reports and audits
5. Routine maintenance and organization

### Silver Tier Capabilities
- Three watchers: Gmail, WhatsApp, LinkedIn
- Email MCP server for sending emails
- Human-in-the-loop approval workflow
- Automated LinkedIn posting for sales generation
- Daily briefings and weekly audits
- Plan.md creation for all action items
- Task scheduling via Windows Task Scheduler

### Quality Standards
- All outgoing communications proofread for tone and accuracy
- Financial calculations double-checked
- Actions logged for audit trail
- Continuous improvement through weekly reviews
- All AI functionality implemented as Agent Skills

---
*This handbook evolves with your AI Employee's capabilities. Current Tier: Silver*
