#!/usr/bin/env sh
set -e
DIR="$(cd "$(dirname "$0")" && pwd)/keys"
mkdir -p "$DIR"
if [ -f "$DIR/private.key" ]; then
  echo "Keys already exist in $DIR"
  exit 0
fi
openssl genrsa -out "$DIR/private.key" 2048
openssl rsa -in "$DIR/private.key" -pubout -out "$DIR/public.key"
echo "Keys created in $DIR"
