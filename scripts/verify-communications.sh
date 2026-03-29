#!/usr/bin/env bash
set -euo pipefail

# Verify fleet communication infrastructure — all systems check.
# Run this before Plane integration or after any infrastructure change.
# Must pass all checks before proceeding.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Fleet Communication Verification ==="
echo ""

cd "$FLEET_DIR"
.venv/bin/python -c "
import asyncio
from fleet.infra.mc_client import MCClient
from fleet.infra.config_loader import ConfigLoader
from fleet.infra.irc_client import IRCClient
from fleet.infra.ntfy_client import NtfyClient
import json, os, httpx

async def verify():
    loader = ConfigLoader()
    env = loader.load_env()
    mc = MCClient(token=env['LOCAL_AUTH_TOKEN'])
    board_id = await mc.get_board_id()
    results = {}

    # MC API
    try:
        tasks = await mc.list_tasks(board_id)
        agents = await mc.list_agents()
        results['mc_api'] = f'OK — {len(tasks)} tasks, {len(agents)} agents'
    except Exception as e:
        results['mc_api'] = f'FAIL — {e}'

    # Board memory
    try:
        memory = await mc.list_memory(board_id, limit=3)
        results['board_memory'] = f'OK — {len(memory)} entries'
    except Exception as e:
        results['board_memory'] = f'FAIL — {e}'

    # Approvals
    try:
        approvals = await mc.list_approvals(board_id)
        results['approvals'] = f'OK — {len(approvals)} total'
    except Exception as e:
        results['approvals'] = f'FAIL — {e}'

    # IRC
    try:
        oc_path = os.path.expanduser('~/.openclaw/openclaw.json')
        with open(oc_path) as f:
            oc_cfg = json.load(f)
        gw_token = oc_cfg.get('gateway', {}).get('auth', {}).get('token', '')
        irc = IRCClient(gateway_token=gw_token)
        ok = await irc.notify('#fleet', '[verify] Communication check')
        results['irc'] = 'OK' if ok else 'FAIL'
    except Exception as e:
        results['irc'] = f'FAIL — {e}'

    # ntfy
    try:
        ntfy = NtfyClient()
        ok = await ntfy.publish(title='Fleet verify', message='Communication check', priority='info', tags=['test'])
        results['ntfy'] = 'OK' if ok else 'FAIL'
        await ntfy.close()
    except Exception as e:
        results['ntfy'] = f'FAIL — {e}'

    # Plane (optional — only checked if Plane containers are running)
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get('http://localhost:8080/')
            results['plane'] = f'OK — HTTP {resp.status_code}'
    except Exception:
        results['plane'] = 'SKIP — Plane not running (configure in Sprint 3)'

    # Gateway
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get('http://localhost:18789/')
            results['gateway'] = f'OK — HTTP {resp.status_code}'
    except Exception as e:
        results['gateway'] = f'FAIL — {e}'

    # Board lead
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get('http://localhost:8000/api/v1/agents',
                headers={'Authorization': f'Bearer {env[\"LOCAL_AUTH_TOKEN\"]}'})
            items = resp.json().get('items', resp.json())
            fo = next((a for a in items if a['name'] == 'fleet-ops'), {})
            is_lead = fo.get('is_board_lead', False)
        results['board_lead'] = 'OK' if is_lead else 'FAIL — fleet-ops not board lead'
    except Exception as e:
        results['board_lead'] = f'FAIL — {e}'

    await mc.close()

    all_ok = True
    for check, result in results.items():
        ok = result.startswith('OK') or result.startswith('SKIP')
        if not ok: all_ok = False
        icon = '✅' if result.startswith('OK') else ('⏭️' if result.startswith('SKIP') else '❌')
        print(f'  {icon} {check:20s} {result}')

    print()
    if all_ok:
        print('ALL CHECKS PASSED')
        exit(0)
    else:
        print('SOME CHECKS FAILED')
        exit(1)

asyncio.run(verify())
"