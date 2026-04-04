# Fleet IaC OpenArms Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update openclaw-fleet's IaC to support OpenArms as a drop-in replacement for OpenClaw, with backwards compatibility for legacy installs, and inject clean Claude Code session environment variables.

**Architecture:** Create a shared vendor detection helper sourced by all scripts. Update 14 shell scripts, 2 Python files, and 1 systemd template to use resolved vendor paths. Add environment sanitization to the executor before Claude Code invocation.

**Tech Stack:** Bash, Python 3.11+, systemd

**Spec:** `docs/superpowers/specs/2026-04-03-fleet-iac-openarms-migration.md`

---

## File Structure

**Create:**
- `scripts/lib/vendor.sh` — shared vendor detection helper (sourced by all scripts)

**Modify:**
- `scripts/install-openclaw.sh` — install openarms or openclaw
- `scripts/configure-openclaw.sh` — use resolved vendor paths
- `scripts/configure-auth.sh` — use resolved vendor env path
- `scripts/configure-channel.sh` — use resolved vendor config path
- `scripts/clean-gateway-config.sh` — use resolved vendor config path
- `scripts/clean-stale-agents.sh` — use resolved vendor config/agents paths
- `scripts/refresh-auth.sh` — use resolved vendor env path
- `scripts/install-service.sh` — use resolved vendor binary path
- `scripts/install-plugins.sh` — use resolved vendor CLI
- `scripts/ws-monitor.sh` — use resolved vendor config path + client ID
- `scripts/setup-irc.sh` — use resolved vendor config path + CLI
- `setup.sh` — use resolved vendor throughout
- `gateway/executor.py` — add environment sanitization before subprocess.run
- `gateway/ws_server.py` — remove product branding from protocol metadata
- `gateway/setup.py` — use resolved vendor config path
- `fleet/cli/dispatch.py` — use resolved vendor config path
- `systemd/openclaw-fleet-gateway.service.template` — use generic template vars

---

### Task 1: Create Vendor Detection Helper

**Files:**
- Create: `scripts/lib/vendor.sh`

- [ ] **Step 1: Create the lib directory**

```bash
mkdir -p /home/jfortin/openclaw-fleet/scripts/lib
```

- [ ] **Step 2: Write the vendor detection helper**

```bash
cat > /home/jfortin/openclaw-fleet/scripts/lib/vendor.sh << 'SHELLEOF'
#!/usr/bin/env bash
# vendor.sh — Resolve which gateway vendor is installed (openarms preferred over openclaw).
# Source this file from any fleet script: source "$(dirname "$0")/lib/vendor.sh" (or adjust path).
#
# After sourcing, these variables are set:
#   VENDOR_CLI          — "openarms" or "openclaw"
#   VENDOR_NAME         — "OpenArms" or "OpenClaw"
#   VENDOR_CONFIG_DIR   — ~/.openarms or ~/.openclaw
#   VENDOR_CONFIG_FILE  — ~/.openarms/openarms.json or ~/.openclaw/openclaw.json
#   VENDOR_ENV_FILE     — ~/.openarms/.env or ~/.openclaw/.env

if command -v openarms >/dev/null 2>&1; then
    VENDOR_CLI="openarms"
    VENDOR_NAME="OpenArms"
    VENDOR_CONFIG_DIR="${HOME}/.openarms"
    VENDOR_CONFIG_FILE="${VENDOR_CONFIG_DIR}/openarms.json"
    VENDOR_ENV_FILE="${VENDOR_CONFIG_DIR}/.env"
elif command -v openclaw >/dev/null 2>&1; then
    VENDOR_CLI="openclaw"
    VENDOR_NAME="OpenClaw"
    VENDOR_CONFIG_DIR="${HOME}/.openclaw"
    VENDOR_CONFIG_FILE="${VENDOR_CONFIG_DIR}/openclaw.json"
    VENDOR_ENV_FILE="${VENDOR_CONFIG_DIR}/.env"
else
    echo "ERROR: Neither openarms nor openclaw found in PATH" >&2
    VENDOR_CLI=""
    VENDOR_NAME=""
    VENDOR_CONFIG_DIR=""
    VENDOR_CONFIG_FILE=""
    VENDOR_ENV_FILE=""
fi
SHELLEOF
chmod +x /home/jfortin/openclaw-fleet/scripts/lib/vendor.sh
```

- [ ] **Step 3: Commit**

```bash
cd /home/jfortin/openclaw-fleet
git add scripts/lib/vendor.sh
git commit -m "feat: add vendor detection helper for openarms/openclaw dual support"
```

---

### Task 2: Update Installation Script

**Files:**
- Modify: `scripts/install-openclaw.sh`

- [ ] **Step 1: Rewrite install-openclaw.sh to support both vendors**

Replace the entire file:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Install gateway vendor (OpenArms preferred, OpenClaw fallback).
# OpenArms: built from ../openarms if available.
# OpenClaw: npm install -g openclaw (legacy fallback).

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"

echo "=== Installing Gateway Vendor ==="

# Already installed?
if [[ -n "$VENDOR_CLI" ]]; then
    VERSION=$($VENDOR_CLI --version 2>/dev/null | head -1 || echo "unknown")
    echo "  $VENDOR_NAME already installed: $VERSION"
    exit 0
fi

# Try OpenArms first (local build)
OPENARMS_DIR="$FLEET_DIR/../openarms"
if [[ -d "$OPENARMS_DIR/dist" ]]; then
    echo "  Installing openarms from local build..."
    npm install -g "$OPENARMS_DIR" 2>/dev/null || {
        echo "  Trying with sudo..."
        sudo npm install -g "$OPENARMS_DIR" 2>/dev/null || {
            echo "  WARN: Could not install openarms from local build"
        }
    }
    if command -v openarms >/dev/null 2>&1; then
        echo "  OpenArms installed: $(openarms --version 2>/dev/null | head -1)"
        exit 0
    fi
fi

# Fallback: OpenClaw from npm
echo "  Installing openclaw via npm (legacy fallback)..."
npm install -g openclaw 2>/dev/null || {
    echo "  Trying with sudo..."
    sudo npm install -g openclaw 2>/dev/null || {
        echo "  ERROR: Could not install gateway vendor."
        echo "  Build openarms: cd ../openarms && pnpm build"
        echo "  Or install legacy: npm install -g openclaw"
        exit 1
    }
}
echo "  OpenClaw installed: $(openclaw --version 2>/dev/null | head -1)"
```

- [ ] **Step 2: Commit**

```bash
cd /home/jfortin/openclaw-fleet
git add scripts/install-openclaw.sh
git commit -m "feat: install-openclaw.sh supports openarms with openclaw fallback"
```

---

### Task 3: Update Auth Scripts

**Files:**
- Modify: `scripts/configure-auth.sh`
- Modify: `scripts/refresh-auth.sh`

- [ ] **Step 1: Update configure-auth.sh**

Replace hardcoded `~/.openclaw` references with vendor detection:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Configure Anthropic auth for gateway vendor.
# Automatically bridges Claude Code subscription — no manual steps.
echo "=== Configuring Auth ==="

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"

if [[ -z "$VENDOR_CLI" ]]; then
    echo "ERROR: No gateway vendor installed"
    exit 1
fi

# Always check for fresh Claude Code token (tokens rotate)
CLAUDE_CREDS="${HOME}/.claude/.credentials.json"
if [[ -f "$CLAUDE_CREDS" ]]; then
    TOKEN=$(python3 -c "
import json, sys
with open('$CLAUDE_CREDS') as f:
    creds = json.load(f)
token = creds.get('claudeAiOauth', {}).get('accessToken', '')
if token:
    print(token)
else:
    sys.exit(1)
" 2>/dev/null) || TOKEN=""

    if [[ -n "$TOKEN" ]]; then
        echo "Found Claude Code OAuth token"

        # Write to vendor env
        mkdir -p "$VENDOR_CONFIG_DIR"
        if [[ -f "$VENDOR_ENV_FILE" ]]; then
            grep -v "ANTHROPIC_API_KEY" "$VENDOR_ENV_FILE" > "${VENDOR_ENV_FILE}.tmp" || true
            mv "${VENDOR_ENV_FILE}.tmp" "$VENDOR_ENV_FILE"
        fi
        echo "ANTHROPIC_API_KEY=${TOKEN}" >> "$VENDOR_ENV_FILE"
        echo "Token written to $VENDOR_ENV_FILE"
        echo "Auth configured for all agents via environment"
        exit 0
    fi
fi

# Fallback: check existing env var
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "ANTHROPIC_API_KEY found in environment"
    mkdir -p "$VENDOR_CONFIG_DIR"
    if ! grep -q "ANTHROPIC_API_KEY" "$VENDOR_ENV_FILE" 2>/dev/null; then
        echo "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}" >> "$VENDOR_ENV_FILE"
        echo "Written to $VENDOR_ENV_FILE"
    fi
    exit 0
fi

echo ""
echo "ERROR: No auth source found."
echo "  - No Claude Code credentials at ~/.claude/.credentials.json"
echo "  - No ANTHROPIC_API_KEY in environment"
echo ""
echo "Fix: run 'claude auth login' first, then re-run setup."
exit 1
```

- [ ] **Step 2: Update refresh-auth.sh**

Replace `OPENCLAW_ENV="${HOME}/.openclaw/.env"` and all references:

At the top of the file, after `set -euo pipefail`, add:

```bash
FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Then replace every occurrence of `$OPENCLAW_ENV` with `$VENDOR_ENV_FILE` and `${HOME}/.openclaw` with `$VENDOR_CONFIG_DIR`. Specifically:

- Line 11: `OPENCLAW_ENV="${HOME}/.openclaw/.env"` → remove (provided by vendor.sh)
- Line 36: `if [[ -f "$OPENCLAW_ENV" ]]; then` → `if [[ -f "$VENDOR_ENV_FILE" ]]; then`
- Line 37: `STORED_TOKEN=$(grep ... "$OPENCLAW_ENV" ...)` → `STORED_TOKEN=$(grep ... "$VENDOR_ENV_FILE" ...)`
- Line 47: `mkdir -p "${HOME}/.openclaw"` → `mkdir -p "$VENDOR_CONFIG_DIR"`
- Line 48-50: All `$OPENCLAW_ENV` → `$VENDOR_ENV_FILE`
- Line 52: `echo "ANTHROPIC_API_KEY=${NEW_TOKEN}" >> "$OPENCLAW_ENV"` → `... >> "$VENDOR_ENV_FILE"`

- [ ] **Step 3: Commit**

```bash
cd /home/jfortin/openclaw-fleet
git add scripts/configure-auth.sh scripts/refresh-auth.sh
git commit -m "feat: auth scripts use vendor detection for openarms/openclaw"
```

---

### Task 4: Update Configuration Scripts

**Files:**
- Modify: `scripts/configure-openclaw.sh`
- Modify: `scripts/configure-channel.sh`
- Modify: `scripts/clean-gateway-config.sh`
- Modify: `scripts/clean-stale-agents.sh`
- Modify: `scripts/setup-irc.sh`

Each of these scripts hardcodes `~/.openclaw/openclaw.json`. The pattern is the same for all: source vendor.sh, replace hardcoded paths.

- [ ] **Step 1: Update configure-openclaw.sh**

At the top (after line 8), add:

```bash
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Replace:
- Line 9: `OPENCLAW_CONFIG="${HOME}/.openclaw/openclaw.json"` → `OPENCLAW_CONFIG="$VENDOR_CONFIG_FILE"`
- Line 10: `EXEC_APPROVALS="${HOME}/.openclaw/exec-approvals.json"` → `EXEC_APPROVALS="${VENDOR_CONFIG_DIR}/exec-approvals.json"`
- Line 13: `Run 'openclaw onboard' first` → `Run '$VENDOR_CLI onboard' first`
- Line 22: `config_path = os.path.expanduser('$OPENCLAW_CONFIG')` → same (variable already resolved)
- Line 75: `if command -v openclaw` → `if command -v "$VENDOR_CLI"`
- Line 77: `openclaw approvals get` → `$VENDOR_CLI approvals get`
- Line 80: `openclaw approvals allowlist add` → `$VENDOR_CLI approvals allowlist add`
- Line 84: `openclaw CLI not found` → `$VENDOR_NAME CLI not found`
- Line 104: `echo "OpenClaw fleet settings configured"` → `echo "$VENDOR_NAME fleet settings configured"`

- [ ] **Step 2: Update configure-channel.sh**

At the top (after line 12), add:

```bash
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Replace:
- Line 13: `OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"` → `OPENCLAW_CONFIG="$VENDOR_CONFIG_FILE"`
- Lines 123, 127: `openclaw agents bind` → `$VENDOR_CLI agents bind`

- [ ] **Step 3: Update clean-gateway-config.sh**

At the top (after `set -euo pipefail`), add:

```bash
FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Replace:
- Line 9: `OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"` → `OPENCLAW_CONFIG="$VENDOR_CONFIG_FILE"`
- Line 104 (inside Python): `config_path.replace("/.openclaw/openclaw.json", "")` → needs to handle both vendor paths. Change to resolve FLEET_DIR directly via `os.environ.get("FLEET_DIR", ...)` or pass it as an argument.

- [ ] **Step 4: Update clean-stale-agents.sh**

Source vendor.sh (already has `FLEET_DIR`):

```bash
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Replace:
- Line 61: `OPENCLAW_AGENTS="$HOME/.openclaw/agents"` → `OPENCLAW_AGENTS="$VENDOR_CONFIG_DIR/agents"`
- Line 83 (Python): `config_path = os.path.expanduser("~/.openclaw/openclaw.json")` → `config_path = os.path.expanduser("$VENDOR_CONFIG_FILE")`
- Line 101 (Python): `os.path.expanduser("~/.openclaw/logs/config-health.json")` → `os.path.expanduser("$VENDOR_CONFIG_DIR/logs/config-health.json")`

- [ ] **Step 5: Update setup-irc.sh**

Source vendor.sh (already has `FLEET_DIR`):

```bash
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Replace:
- Line 15: `OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"` → `OPENCLAW_CONFIG="$VENDOR_CONFIG_FILE"`
- Line 58: `--motd "OpenClaw Fleet IRC"` → `--motd "Fleet IRC"`
- Line 126: `openclaw agents list` → `$VENDOR_CLI agents list`
- Line 127: `openclaw agents bindings` → `$VENDOR_CLI agents bindings`
- Line 140: `openclaw agents bind` → `$VENDOR_CLI agents bind`

- [ ] **Step 6: Commit**

```bash
cd /home/jfortin/openclaw-fleet
git add scripts/configure-openclaw.sh scripts/configure-channel.sh scripts/clean-gateway-config.sh scripts/clean-stale-agents.sh scripts/setup-irc.sh
git commit -m "feat: config scripts use vendor detection for openarms/openclaw"
```

---

### Task 5: Update Service and Monitor Scripts

**Files:**
- Modify: `scripts/install-service.sh`
- Modify: `scripts/ws-monitor.sh`
- Modify: `scripts/install-plugins.sh`
- Modify: `systemd/openclaw-fleet-gateway.service.template`

- [ ] **Step 1: Update install-service.sh**

Source vendor.sh:

```bash
FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Replace:
- Line 21: `OPENCLAW_BIN=$(command -v openclaw ...)` → `VENDOR_BIN=$(command -v "$VENDOR_CLI" 2>/dev/null || echo "")`
- Line 22-24: Check `$VENDOR_BIN` instead of `$OPENCLAW_BIN`
- Line 26: `OPENCLAW_BIN_DIR=$(dirname "$OPENCLAW_BIN")` → `VENDOR_BIN_DIR=$(dirname "$VENDOR_BIN")`
- Lines 28-30: Update echo messages to use `$VENDOR_NAME`, `$VENDOR_BIN`
- Line 37: Service file name stays `openclaw-fleet-gateway.service` (service name is fleet's, not vendor's)
- Lines 39-43: sed replacements use `$VENDOR_BIN_DIR` and `$VENDOR_BIN`

- [ ] **Step 2: Update systemd template**

Replace `systemd/openclaw-fleet-gateway.service.template`:

```ini
[Unit]
Description=Fleet Gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory={{FLEET_DIR}}
EnvironmentFile=-{{FLEET_DIR}}/.env
Environment=PATH={{VENDOR_BIN_DIR}}:/usr/local/bin:/usr/bin:/bin
Environment=HOME={{HOME}}
Environment=NODE_OPTIONS=--max-old-space-size=4096
ExecStartPre=/bin/bash -c 'test ! -f {{FLEET_DIR}}/.fleet-paused || (echo "Fleet is PAUSED" && exit 1)'
ExecStartPre=/bin/bash -c 'curl -sf http://localhost:8000/health >/dev/null 2>&1 || (echo "MC is DOWN" && exit 1)'
ExecStart=/bin/bash -c 'exec {{VENDOR_BIN}} gateway run --port "${OCF_GATEWAY_PORT:-18789}"'
Restart=always
RestartSec=5s
StandardOutput=journal
StandardError=journal
SyslogIdentifier=fleet-gateway

TimeoutStartSec=30
TimeoutStopSec=30

[Install]
WantedBy=default.target
```

- [ ] **Step 3: Update ws-monitor.sh**

Source vendor.sh:

```bash
FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Replace:
- Line 54 (Python): `with open('$HOME/.openclaw/openclaw.json')` → `with open('$VENDOR_CONFIG_FILE')`
- Line 66 (Python): `'id': 'openclaw-control-ui'` → `'id': '${VENDOR_CLI}-control-ui'`

- [ ] **Step 4: Update install-plugins.sh**

Source vendor.sh:

```bash
FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Replace lines 62-69 (OpenClaw marketplace registration):

```bash
    # Register in gateway vendor
    if [[ -n "$VENDOR_CLI" ]]; then
        $VENDOR_CLI plugins marketplace list "$mp" --json >/dev/null 2>&1 && \
            echo -e "  ${YELLOW}[skip]${NC} $mp ($VENDOR_CLI)" || {
        $VENDOR_CLI plugins install "marketplace:$mp" 2>/dev/null && \
            echo -e "  ${GREEN}[added]${NC} $mp ($VENDOR_CLI)" || true
        }
    fi
```

- [ ] **Step 5: Commit**

```bash
cd /home/jfortin/openclaw-fleet
git add scripts/install-service.sh scripts/ws-monitor.sh scripts/install-plugins.sh systemd/openclaw-fleet-gateway.service.template
git commit -m "feat: service/monitor/plugin scripts use vendor detection"
```

---

### Task 6: Update Master Setup Script

**Files:**
- Modify: `setup.sh`

- [ ] **Step 1: Source vendor.sh and update all references**

After the `FLEET_DIR` assignment near the top of setup.sh, add:

```bash
source "$FLEET_DIR/scripts/lib/vendor.sh"
```

Then replace these specific lines:

- Line 25: `"OpenClaw Fleet Setup"` → `"Fleet Setup"`
- Line 141-146: Replace the OpenClaw install/check block:

```bash
# Step 1: Install gateway vendor
bash scripts/install-openclaw.sh
source "$FLEET_DIR/scripts/lib/vendor.sh"  # re-source after install
```

- Line 150-153: Replace the onboard check:

```bash
if [[ -n "$VENDOR_CLI" ]] && [[ ! -f "$VENDOR_CONFIG_FILE" ]]; then
    echo "=== Configuring $VENDOR_NAME ==="
    $VENDOR_CLI onboard --non-interactive --accept-risk --workspace "$FLEET_DIR" --skip-health
fi
```

- Line 161 (Python): `os.path.expanduser('~/.openclaw/openclaw.json')` → `os.path.expanduser('$VENDOR_CONFIG_FILE')`
- Line 190: `'OpenClaw config updated'` → `'Gateway config updated'`
- Line 192: `'OpenClaw config OK'` → `'Gateway config OK'`
- Line 313 (Python): `'OCF' in g.get('name','') or 'OpenClaw' in g.get('name','')` → `'OCF' in g.get('name','') or 'Fleet' in g.get('name','')`
- Lines 455-456, 474: Update echo messages to use `$VENDOR_NAME`

- [ ] **Step 2: Commit**

```bash
cd /home/jfortin/openclaw-fleet
git add setup.sh
git commit -m "feat: setup.sh uses vendor detection for openarms/openclaw"
```

---

### Task 7: Add Environment Sanitization to Executor

This is the critical privacy task — clean the environment before spawning Claude Code.

**Files:**
- Modify: `gateway/executor.py`

- [ ] **Step 1: Add environment sanitization**

Add a new function before `execute_task()`:

```python
def _build_clean_env() -> Dict[str, str]:
    """Build a clean environment for Claude Code execution.

    Disables telemetry and strips identifying environment variables
    so agent sessions are indistinguishable from direct CLI usage.
    """
    import os
    env = os.environ.copy()

    # Disable Claude Code telemetry
    env["DISABLE_TELEMETRY"] = "1"
    env["CLAUDE_CODE_ENABLE_TELEMETRY"] = "0"

    # Strip identifying variables
    for var in (
        "CLAUDE_CODE_ENTRYPOINT",
        "CLAUDE_AGENT_SDK_VERSION",
        "CLAUDE_AGENT_SDK_CLIENT_APP",
        "CLAUDE_CODE_CONTAINER_ID",
        "CLAUDE_CODE_REMOTE_SESSION_ID",
        "CLAUDE_CODE_REMOTE",
        "CLAUDECODE",
        "CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING",
    ):
        env.pop(var, None)

    return env
```

- [ ] **Step 2: Use clean env in subprocess.run**

In `execute_task()`, modify the subprocess.run call at line 61 to pass the clean env:

Find:
```python
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, cwd=str(agent_dir),
        )
```

Replace:
```python
        clean_env = _build_clean_env()
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, cwd=str(agent_dir),
            env=clean_env,
        )
```

- [ ] **Step 3: Commit**

```bash
cd /home/jfortin/openclaw-fleet
git add gateway/executor.py
git commit -m "security: sanitize environment before Claude Code execution"
```

---

### Task 8: Update Gateway and Fleet Python Files

**Files:**
- Modify: `gateway/ws_server.py` (lines 1, 33, 144, 151)
- Modify: `gateway/setup.py` (lines 140-147, 293, 326)
- Modify: `fleet/cli/dispatch.py` (line 150)

- [ ] **Step 1: Update ws_server.py branding**

Line 1: Replace docstring:
```python
"""Fleet Gateway WebSocket server."""
```

Line 33: Remove version branding:
```python
GATEWAY_VERSION = "1.0.0"
```

Lines 140-148: Replace server metadata:
```python
    async def _handle_connect(self, params: Dict) -> Dict:
        return {
            "server": {
                "version": GATEWAY_VERSION,
                "name": "Fleet Gateway",
                "capabilities": ["agents", "health", "chat"],
            },
            "session": {"id": str(uuid4())},
        }
```

Line 151: Replace health response:
```python
        return {"ok": True, "gateway": "fleet", "version": GATEWAY_VERSION}
```

- [ ] **Step 2: Update gateway/setup.py vendor config path**

Add a helper at the top of the file (after imports):

```python
def _resolve_vendor_config() -> str:
    """Resolve vendor config path (~/.openarms or ~/.openclaw)."""
    import os
    openarms = os.path.expanduser("~/.openarms/openarms.json")
    openclaw = os.path.expanduser("~/.openclaw/openclaw.json")
    if os.path.exists(openarms):
        return openarms
    return openclaw
```

Line 143: Replace:
```python
        oc_config = _resolve_vendor_config()
```

Line 293: Replace:
```python
    print("=== Fleet Setup ===\n")
```

Line 326: Replace:
```python
        org = setup.create_organization("Fleet", "fleet")
```

- [ ] **Step 3: Update fleet/cli/dispatch.py vendor config path**

Line 150: Replace:
```python
    oc_path = os.path.expanduser("~/.openarms/openarms.json")
    if not os.path.exists(oc_path):
        oc_path = os.path.expanduser("~/.openclaw/openclaw.json")
```

- [ ] **Step 4: Commit**

```bash
cd /home/jfortin/openclaw-fleet
git add gateway/ws_server.py gateway/setup.py fleet/cli/dispatch.py
git commit -m "feat: gateway and fleet code use vendor-neutral paths and branding"
```

---

### Task 9: Verification

**Files:** None modified — verification only.

- [ ] **Step 1: Grep for remaining hardcoded openclaw paths**

```bash
cd /home/jfortin/openclaw-fleet
grep -rn '~/.openclaw\|\.openclaw/' scripts/ gateway/ fleet/ setup.sh systemd/ \
  --include='*.sh' --include='*.py' --include='*.template' \
  | grep -v 'vendor.sh' | grep -v '__pycache__' | grep -v '.pyc'
```

Expected: zero hits outside of vendor.sh and comments.

- [ ] **Step 2: Grep for remaining hardcoded openclaw CLI calls**

```bash
cd /home/jfortin/openclaw-fleet
grep -rn 'command -v openclaw\|openclaw onboard\|openclaw approvals\|openclaw agents\|openclaw gateway\|openclaw plugins' \
  scripts/ gateway/ fleet/ setup.sh \
  --include='*.sh' --include='*.py' \
  | grep -v 'vendor.sh' | grep -v 'VENDOR_CLI' | grep -v '__pycache__'
```

Expected: zero hits — all should use `$VENDOR_CLI`.

- [ ] **Step 3: Verify vendor.sh resolves correctly**

```bash
cd /home/jfortin/openclaw-fleet
source scripts/lib/vendor.sh
echo "CLI: $VENDOR_CLI"
echo "Name: $VENDOR_NAME"
echo "Config: $VENDOR_CONFIG_FILE"
echo "Env: $VENDOR_ENV_FILE"
```

Expected: resolves to openarms if installed, openclaw otherwise.

- [ ] **Step 4: Verify executor environment sanitization**

```bash
cd /home/jfortin/openclaw-fleet
python3 -c "
from gateway.executor import _build_clean_env
env = _build_clean_env()
assert env.get('DISABLE_TELEMETRY') == '1'
assert env.get('CLAUDE_CODE_ENABLE_TELEMETRY') == '0'
assert 'CLAUDE_CODE_ENTRYPOINT' not in env
assert 'CLAUDE_AGENT_SDK_VERSION' not in env
print('Environment sanitization: PASS')
"
```

Expected: "Environment sanitization: PASS"

- [ ] **Step 5: Run fleet tests**

```bash
cd /home/jfortin/openclaw-fleet
pytest fleet/tests/ -v --timeout=30 2>&1 | tail -20
```

Expected: tests pass (or pre-existing failures only).

- [ ] **Step 6: Commit verification results (if any fixes needed)**

```bash
cd /home/jfortin/openclaw-fleet
git status
# If clean: no commit needed
# If fixes: git add ... && git commit -m "fix: address migration verification findings"
```

---

## Summary

| Task | Description | Files | Steps |
|------|-------------|-------|-------|
| 1 | Create vendor detection helper | 1 new | 3 |
| 2 | Update installation script | 1 | 2 |
| 3 | Update auth scripts | 2 | 3 |
| 4 | Update configuration scripts | 5 | 6 |
| 5 | Update service/monitor/plugin scripts | 4 | 5 |
| 6 | Update master setup script | 1 | 2 |
| 7 | Add environment sanitization to executor | 1 | 3 |
| 8 | Update gateway and fleet Python files | 3 | 4 |
| 9 | Verification | 0 | 6 |
| **Total** | | **18 files** | **34 steps** |
