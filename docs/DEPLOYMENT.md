# Deployment Guide

## Target

Normal Linux VPS with Docker Engine and Docker Compose plugin installed.

## Assumptions

- Docker is already installed
- Outbound HTTPS to `https://api.deepseek.com` is allowed
- Only ports `80` or `443` for the proxy and optionally `8101` through `8110` for direct access are exposed

## Recommended Steps

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Set `DEEPSEEK_API_KEY`
4. Optionally set `ADMIN_TOKEN`
5. Run `docker compose up -d --build`

## Firewall

- Allow inbound `80` and `443` for public proxy use
- Keep direct challenge ports private unless you intentionally want them reachable
- Do not expose internal Docker networking

## TLS

Place a host-level reverse proxy or load balancer in front of `reverse-proxy`, or replace the nginx container with your preferred TLS-terminating setup.

## Secrets

- Store DeepSeek credentials in `.env`
- Do not bake the API key into images
- Rotate `.env` and redeploy when changing credentials

## Restart Policy

The compose file uses `restart: unless-stopped` for challenge services.

## Resource Limits

- Inference is remote, so CPU and memory usage remain moderate
- SQLite and lightweight retrieval keep storage overhead small
- Consider host-level memory and CPU quotas if running alongside other workloads

## Log Rotation

Configure Docker daemon log rotation on the host. The repository does not assume unlimited JSON log growth.

## Backups

Session state lives inside challenge-local SQLite files under `/tmp/data` in the containers and is intentionally disposable. Persistent backups are generally unnecessary unless you customize the state directory.

## Upgrades

1. Pull the latest source
2. Review `DESIGN.md` and `docs/ADMIN.md` for changes
3. Rebuild: `docker compose up -d --build`

## Reverse Proxy Notes

- Public lobby: `/`
- Challenge routes: `/c/01/` through `/c/10/`
- Each challenge also listens on its own internal and optional host port

## Security Notes

- Containers run as non-root users
- `read_only` filesystems are enabled
- `cap_drop: ALL`
- `no-new-privileges`
- No privileged mode, host networking, or Docker socket mounts
