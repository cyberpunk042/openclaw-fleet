# commit-commands

**Type:** Claude Code Plugin (Official Anthropic)
**Source:** Anthropic marketplace
**Installed for:** DevOps

## What It Does

Git commit workflow automation. Provides `/commit-commands:commit` skill that analyzes staged changes, generates conventional commit messages, and handles the commit workflow. Understands conventional commit format (type(scope): description).

## Fleet Use Case

DevOps makes frequent infrastructure commits. commit-commands ensures consistent conventional commit format across infrastructure changes — matching fleet standards.

Note: fleet agents already use fleet_commit (MCP tool) which enforces conventional commits with LaborStamp. commit-commands is complementary — it helps BEFORE the fleet_commit call by staging and formatting.

## Relationships

- INSTALLED FOR: devops
- COMPLEMENTS: fleet_commit tool (fleet_commit adds LaborStamp, commit-commands helps staging)
- CONNECTS TO: conventional commits standard (type(scope): description format)
- CONNECTS TO: trail system (commit events in trail)
- CONNECTS TO: /diff command (review changes before commit)
