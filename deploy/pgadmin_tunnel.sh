#!/usr/bin/env bash
# Start SSH tunnel for pgAdmin to connect to vesta exclusion_list database.
# Usage: bash deploy/pgadmin_tunnel.sh
# Keep this terminal open while using pgAdmin.

LOCAL_PORT=15432
REMOTE_PORT=5433
SERVER="${DEPLOY_HOST:?Set DEPLOY_HOST e.g. user@your-server}"

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

ssh -N -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" "${SERVER}"
