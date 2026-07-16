# Vault Organizer Skill

**File:** `.openclaw/skills/vault-organizer/SKILL.md`

## Description
Organizes files in AI_Employee_Vault — routes Inbox items, manages Needs_Action/Pending_Approval directories, creates task plans, and generates briefings.

## Triggers
- "organize my vault" or "check what needs attention"
- New files in Inbox/ or Dropbox/

## Workflows
1. **Route Inbox Items** — read `.md` files in Inbox/, categorize, move to Needs_Action/ or Pending_Approval/
2. **Check Pending Items** — summarize counts and priorities from Needs_Action/ and Pending_Approval/
3. **Create Plans** — write markdown plan files to Plans/ with timestamp
4. **Daily Briefing** — scan Needs_Action/, Pending_Approval/, Logs/ and produce briefing

## Dependencies
- EmailMCPServer (for email notifications)
