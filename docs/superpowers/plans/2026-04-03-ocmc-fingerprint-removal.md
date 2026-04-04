# OCMC Fingerprint Removal — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove all "openclaw" identifiers from OCMC API responses and frontend, delivered as fleet patches.

**Architecture:** Create fleet patches that rename `openclaw_session_id` → `session_id` in backend model/schema/services/API, add an Alembic migration for the column rename, and replace frontend branding strings. All delivered via the existing `patches/` + `apply-patches.sh` mechanism.

**Tech Stack:** Python (SQLModel, Alembic, FastAPI), TypeScript (Next.js), git diff patches

**Spec:** `docs/superpowers/specs/2026-04-03-ocmc-fingerprint-removal.md`

---

## File Structure

All work happens in `vendor/openclaw-mission-control/`. Changes are captured as patches in `patches/`.

**Backend files to modify (column rename `openclaw_session_id` → `session_id`):**
- `backend/app/models/agents.py:28`
- `backend/app/schemas/agents.py:239-242`
- `backend/app/services/openclaw/provisioning_db.py` (~8 references)
- `backend/app/services/openclaw/provisioning.py` (~5 references)
- `backend/app/services/openclaw/admin_service.py` (~3 references)
- `backend/app/services/openclaw/coordination_service.py` (~4 references)
- `backend/app/services/openclaw/policies.py:55`
- `backend/app/services/openclaw/internal/agent_key.py:19`
- `backend/app/services/webhooks/dispatch.py` (~2 references)
- `backend/app/api/board_webhooks.py` (~2 references)
- `backend/app/api/board_group_memory.py` (~2 references)
- `backend/app/api/boards.py` (~4 references)
- `backend/app/api/board_memory.py` (~4 references)
- `backend/app/api/approvals.py` (~2 references)
- `backend/app/api/tasks.py` (~11 references)

**New migration file:**
- `backend/migrations/versions/xxxx_rename_openclaw_session_id.py`

**Frontend files to modify:**
- `frontend/src/app/layout.tsx:13`
- `frontend/src/app/agents/page.tsx:36`
- `frontend/src/app/agents/[agentId]/page.tsx:244,311`
- `frontend/src/app/invite/page.tsx:85`
- `frontend/src/app/gateways/page.tsx:98,128`
- `frontend/src/app/gateways/[gatewayId]/edit/page.tsx:168`
- `frontend/src/app/gateways/new/page.tsx:119`
- `frontend/src/components/atoms/BrandMark.tsx:9`
- `frontend/src/components/agents/AgentsTable.tsx:120,124`
- `frontend/src/components/organisms/LandingHero.tsx:37`
- `frontend/src/components/organisms/OrgSwitcher.tsx:71`
- `frontend/src/components/templates/LandingShell.tsx:22,27,92,153`
- `frontend/src/components/templates/DashboardShell.tsx:61`
- `frontend/src/components/molecules/HeroCopy.tsx:6`
- `frontend/src/lib/gateway-form.ts:3`
- `frontend/src/api/generated/model/agentRead.ts:39-40`

**Compose file:**
- `compose.yml:1`

---

### Task 1: Backend Column Rename — Model, Schema, Services

**Files:**
- Modify: All backend `.py` files listed above in `vendor/openclaw-mission-control/`

- [ ] **Step 1: Rename in model and schema**

In `vendor/openclaw-mission-control/`, run:

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control

# Rename the field in all backend Python files
find backend/ -name '*.py' -not -path '*/migrations/*' -not -path '*__pycache__*' \
  -exec sed -i 's/openclaw_session_id/session_id/g' {} +
```

- [ ] **Step 2: Update the schema description**

In `backend/app/schemas/agents.py`, the description says "Optional openclaw session token." — fix it:

```bash
sed -i 's/Optional openclaw session token/Optional session token/' \
  backend/app/schemas/agents.py
```

- [ ] **Step 3: Verify no openclaw_session_id remains in backend (excluding migrations)**

```bash
grep -rn 'openclaw_session_id' backend/ --include='*.py' | grep -v migrations | grep -v __pycache__
```

Expected: zero hits.

- [ ] **Step 4: Commit the backend changes (in vendor, temporary)**

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control
git add -A
git commit -m "rename: openclaw_session_id -> session_id in backend"
```

---

### Task 2: Alembic Migration for Column Rename

**Files:**
- Create: `patches/0007-migration-rename-session-id.py`

- [ ] **Step 1: Create the migration file**

```python
"""Rename openclaw_session_id to session_id.

Revision ID: 0007_rename_session
Revises: (auto-detected)
"""
from alembic import op

revision = "0007_rename_session"
down_revision = None  # Will be set by apply-patches.sh or alembic
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename the column
    op.alter_column("agents", "openclaw_session_id", new_column_name="session_id")
    # Rename the index
    op.drop_index("ix_agents_openclaw_session_id", table_name="agents")
    op.create_index("ix_agents_session_id", "agents", ["session_id"])


def downgrade() -> None:
    op.alter_column("agents", "session_id", new_column_name="openclaw_session_id")
    op.drop_index("ix_agents_session_id", table_name="agents")
    op.create_index("ix_agents_openclaw_session_id", "agents", ["openclaw_session_id"])
```

Save to `patches/0007-migration-rename-session-id.py`.

- [ ] **Step 2: Commit**

```bash
cd /home/jfortin/openclaw-fleet
git add patches/0007-migration-rename-session-id.py
git commit -m "feat: add migration to rename openclaw_session_id to session_id"
```

---

### Task 3: Generate Backend Patch

**Files:**
- Create: `patches/0007-rename-openclaw-session-id.patch`

- [ ] **Step 1: Generate the patch from vendor changes**

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control
git diff HEAD~1 > /home/jfortin/openclaw-fleet/patches/0007-rename-openclaw-session-id.patch
```

- [ ] **Step 2: Reset the vendor to clean state**

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control
git reset --hard HEAD~1
```

- [ ] **Step 3: Verify the patch applies cleanly**

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control
git apply --check ../../patches/0007-rename-openclaw-session-id.patch
```

Expected: no errors.

- [ ] **Step 4: Commit the patch**

```bash
cd /home/jfortin/openclaw-fleet
git add patches/0007-rename-openclaw-session-id.patch
git commit -m "feat: patch to rename openclaw_session_id in MC backend"
```

---

### Task 4: Frontend Branding Patch

**Files:**
- Modify: All frontend files listed above in `vendor/openclaw-mission-control/`

- [ ] **Step 1: Apply branding replacements**

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control

# Replace "OpenClaw Mission Control" → "Mission Control"
find frontend/src/ -type f \( -name '*.tsx' -o -name '*.ts' \) \
  -exec sed -i 's/OpenClaw Mission Control/Mission Control/g' {} +

# Replace standalone "OpenClaw" branding → "Mission Control" or remove
sed -i 's/Join your team in OpenClaw/Join your team/g' frontend/src/app/invite/page.tsx
sed -i 's/Manage OpenClaw gateway connections/Manage gateway connections/g' frontend/src/app/gateways/page.tsx
sed -i 's/managing your OpenClaw connections/managing your connections/g' frontend/src/app/gateways/page.tsx
sed -i 's/this OpenClaw gateway/this gateway/g' frontend/src/app/gateways/*/edit/page.tsx
sed -i 's/an OpenClaw gateway/a gateway/g' frontend/src/app/gateways/new/page.tsx
sed -i 's/OPENCLAW/MC/g' frontend/src/components/atoms/BrandMark.tsx
sed -i "s/OpenClaw home/home/g" frontend/src/components/templates/LandingShell.tsx
sed -i 's/<div className="logo-name">OpenClaw<\/div>/<div className="logo-name">Mission Control<\/div>/g' frontend/src/components/templates/LandingShell.tsx
sed -i 's/<h3>OpenClaw<\/h3>/<h3>Mission Control<\/h3>/g' frontend/src/components/templates/LandingShell.tsx
sed -i 's/OpenClaw\. All rights reserved/Mission Control. All rights reserved/g' frontend/src/components/templates/LandingShell.tsx

# Replace openclaw_session_id references in frontend
find frontend/src/ -type f \( -name '*.tsx' -o -name '*.ts' \) \
  -exec sed -i 's/openclaw_session_id/session_id/g' {} +

# Replace localStorage key
find frontend/src/ -type f \( -name '*.tsx' -o -name '*.ts' \) \
  -exec sed -i 's/openclaw_org_switch/org_switch/g' {} +

# Replace default workspace root
sed -i 's/~\/.openclaw/~\/.openarms/g' frontend/src/lib/gateway-form.ts

# Replace generated API model
sed -i 's/Optional openclaw session token/Optional session token/g' frontend/src/api/generated/model/agentRead.ts
```

- [ ] **Step 2: Update compose.yml**

```bash
sed -i 's/name: openclaw-mission-control/name: mission-control/' compose.yml
```

- [ ] **Step 3: Verify no openclaw remains in frontend source**

```bash
grep -ri 'openclaw' frontend/src/ --include='*.tsx' --include='*.ts' | grep -v node_modules | head -10
```

Expected: zero hits.

- [ ] **Step 4: Commit and generate patch**

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control
git add -A
git commit -m "rename: remove openclaw branding from frontend"
git diff HEAD~1 > /home/jfortin/openclaw-fleet/patches/0008-remove-openclaw-frontend-branding.patch
git reset --hard HEAD~1
```

- [ ] **Step 5: Verify patch applies cleanly**

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control
git apply --check ../../patches/0008-remove-openclaw-frontend-branding.patch
```

- [ ] **Step 6: Commit the patch**

```bash
cd /home/jfortin/openclaw-fleet
git add patches/0008-remove-openclaw-frontend-branding.patch
git commit -m "feat: patch to remove openclaw branding from MC frontend"
```

---

### Task 5: Apply and Verify

- [ ] **Step 1: Apply all patches**

```bash
cd /home/jfortin/openclaw-fleet
bash scripts/apply-patches.sh
```

- [ ] **Step 2: Verify backend is clean**

```bash
grep -rn 'openclaw_session_id' vendor/openclaw-mission-control/backend/ --include='*.py' \
  | grep -v migrations/versions/658dca | grep -v __pycache__
```

Expected: zero hits (the original init migration still has the old column name — that's historical and correct).

- [ ] **Step 3: Verify frontend is clean**

```bash
grep -ri 'openclaw' vendor/openclaw-mission-control/frontend/src/ \
  --include='*.tsx' --include='*.ts' | grep -v node_modules
```

Expected: zero hits.

- [ ] **Step 4: Rebuild MC containers**

```bash
cd /home/jfortin/openclaw-fleet/vendor/openclaw-mission-control
docker compose build
docker compose up -d
```

- [ ] **Step 5: Verify API response is clean**

Wait for backend to start, then:

```bash
curl -sf -H "Authorization: Bearer $(grep LOCAL_AUTH_TOKEN /home/jfortin/openclaw-fleet/.env | cut -d= -f2)" \
  http://localhost:8000/api/v1/agents | python3 -c "
import json, sys
data = json.load(sys.stdin)
items = data.get('items', data) if isinstance(data, dict) else data
for a in items:
    if 'openclaw_session_id' in a:
        print(f'FAIL: openclaw_session_id found in agent {a.get(\"name\",\"?\")}')
        sys.exit(1)
    if 'session_id' in a:
        print(f'OK: session_id present for {a.get(\"name\",\"?\")}')
print('PASS: no openclaw_session_id in API responses')
"
```

- [ ] **Step 6: Final commit**

```bash
cd /home/jfortin/openclaw-fleet
git add patches/
git commit -m "feat: OCMC fingerprint removal — patches 0007 + 0008"
```

---

## Summary

| Task | Description | Steps |
|------|-------------|-------|
| 1 | Backend column rename (model, schema, services, API) | 4 |
| 2 | Alembic migration for column rename | 2 |
| 3 | Generate backend patch | 4 |
| 4 | Frontend branding patch | 6 |
| 5 | Apply and verify | 6 |
| **Total** | | **22 steps** |
