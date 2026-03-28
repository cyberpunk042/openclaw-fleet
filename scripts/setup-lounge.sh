#!/usr/bin/env bash
set -euo pipefail

# Set up The Lounge web IRC client.
# Starts via Docker, creates default user, pre-connects to fleet IRC.
# Called by setup.sh or standalone.

FLEET_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$FLEET_DIR"

LOUNGE_PORT="${LOUNGE_PORT:-9000}"
LOUNGE_USER="${LOUNGE_USER:-fleet}"
LOUNGE_PASS="${LOUNGE_PASS:-fleet}"

echo "=== Setting Up The Lounge (Web IRC Client) ==="

# 1. Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker not available" >&2
    exit 1
fi

# 2. Start The Lounge container
echo "1. Starting The Lounge..."
docker compose up -d lounge 2>&1 | tail -3

# 3. Wait for it to be ready
echo "2. Waiting for The Lounge..."
for i in $(seq 1 15); do
    if curl -sf "http://localhost:${LOUNGE_PORT}" > /dev/null 2>&1; then
        echo "   Ready on port $LOUNGE_PORT"
        break
    fi
    if [[ "$i" -eq 15 ]]; then
        echo "   WARN: The Lounge may not be ready yet (will continue)"
    fi
    sleep 2
done

# 4. Create default user if not exists
echo "3. Configuring user..."
USER_EXISTS=$(docker compose exec -T lounge thelounge list-users 2>/dev/null | grep -c "$LOUNGE_USER" || true)

if [[ "$USER_EXISTS" -gt 0 ]]; then
    echo "   User '$LOUNGE_USER' exists"
else
    echo "   Creating user '$LOUNGE_USER'..."
    # Create user with password via stdin
    echo "$LOUNGE_PASS" | docker compose exec -T lounge thelounge add "$LOUNGE_USER" 2>/dev/null || {
        # Some versions need --password flag
        docker compose exec -T lounge thelounge add "$LOUNGE_USER" --password "$LOUNGE_PASS" 2>/dev/null || {
            echo "   WARN: Could not create user automatically"
            echo "   Create manually: docker compose exec lounge thelounge add $LOUNGE_USER"
        }
    }
    echo "   User created"
fi

echo ""
echo "=== The Lounge Ready ==="
echo ""
echo "Open: http://localhost:${LOUNGE_PORT}"
echo "User: $LOUNGE_USER"
echo "Pass: $LOUNGE_PASS"
echo ""
echo "Pre-configured to connect to Fleet IRC (#fleet, #alerts, #reviews)"
echo "Link previews enabled — GitHub URLs show PR titles inline."