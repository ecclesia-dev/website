#!/bin/sh
# deploy.sh — rsync site to ecclesiadev.com VPS
# Usage: sh scripts/deploy.sh
# Requires: ~/.ssh/ecclesia_dev key, rsync

set -e

REMOTE_USER="deploy"
REMOTE_HOST="ecclesiadev.com"
REMOTE_DIR="/var/www/htdocs/ecclesiadev.com/"
SSH_KEY="$HOME/.ssh/ecclesia_dev"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)/"

echo "==> Deploying to $REMOTE_HOST..."

rsync -avz --delete \
  --exclude='.git/' \
  --exclude='.github/' \
  --exclude='scripts/install-hooks.sh' \
  --exclude='scripts/deploy.sh' \
  --exclude='Makefile' \
  --exclude='README.md' \
  --exclude='LICENSE' \
  --exclude='.gitignore' \
  -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=yes" \
  "$LOCAL_DIR" \
  "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"

echo "==> Fixing permissions..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=yes \
  "$REMOTE_USER@$REMOTE_HOST" \
  "find $REMOTE_DIR -type d -exec chmod 755 {} + && find $REMOTE_DIR -type f -exec chmod 644 {} + && chown -R deploy:daemon $REMOTE_DIR"

echo "==> Done. Site live at https://$REMOTE_HOST"
