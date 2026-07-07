#!/usr/bin/env bash
# Start SSH tunnel for pgAdmin to connect to vesta exclusion_list database.
# Usage: bash deploy/pgadmin_tunnel.sh
# Keep this terminal open while using pgAdmin.

LOCAL_PORT=15432
REMOTE_PORT=5433
SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"
SERVER="${SERVER//$'\r'/}"

# #region agent log
DEBUG_LOG="/Users/aiden/Documents/emrts/州exclusion list/.cursor/debug-f8aa2e.log"
_has_cr=0
[[ "$DEPLOY_HOST" == *$'\r'* ]] && _has_cr=1
printf '{"sessionId":"f8aa2e","timestamp":%s,"location":"pgadmin_tunnel.sh:SERVER","message":"SSH target resolved","data":{"server_len":%s,"deploy_host_len":%s,"has_carriage_return":%s},"hypothesisId":"A","runId":"post-fix"}\n' \
  "$(python3 -c 'import time; print(int(time.time()*1000))' 2>/dev/null || date +%s000)" \
  "${#SERVER}" "${#DEPLOY_HOST}" "$_has_cr" >> "$DEBUG_LOG" 2>/dev/null || true
# #endregion

echo "Starting SSH tunnel: localhost:${LOCAL_PORT} -> vesta:${REMOTE_PORT}"
echo ""
echo "pgAdmin connection settings:"
echo "  Host:     localhost"
echo "  Port:     ${LOCAL_PORT}"
echo "  Database: exclusion_list"
echo "  Username: aiden"
echo "  Password: (same as PGPASSWORD in ~/.bashrc on vesta)"
echo ""
echo "Install pgAdmin if needed: https://www.pgadmin.org/download/pgadmin-4-macos/"
echo "Press Ctrl+C to stop the tunnel."
echo ""

# ServerAlive* keeps idle tunnels from being dropped by NAT/firewall timeouts.
ssh -N \
  -o ServerAliveInterval=60 \
  -o ServerAliveCountMax=3 \
  -o ExitOnForwardFailure=yes \
  -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" \
  "${SERVER}"
