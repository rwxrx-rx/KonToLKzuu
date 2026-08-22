#!/usr/bin/env bash
set -e

RAW_INPUT="$1"
CLEAN_NAME="${RAW_INPUT%.xml}"
TARGET_NAME="${CLEAN_NAME}.xml"

mkdir -p ~/.bin
curl -s https://storage.googleapis.com/git-repo-downloads/repo > ~/.bin/repo
chmod a+rx ~/.bin/repo
export PATH=~/.bin:$PATH

echo "🔍 Searching for manifest file: $TARGET_NAME"
FOUND_FILE=$(find "$GITHUB_WORKSPACE" -type f -iname "$TARGET_NAME" -not -path "*/.git/*" -not -path "*/toolchain/*" | head -n 1)

if [ -z "$FOUND_FILE" ] || [ ! -f "$FOUND_FILE" ]; then
  echo "::error::File $TARGET_NAME NOT FOUND on GitHub Runner!"
  exit 1
fi

echo "✅ Manifest file found at: $FOUND_FILE"
mkdir -p local-manifest
cp "$FOUND_FILE" local-manifest/default.xml

cd local-manifest
git init
git config user.name "GitHub Action"
git config user.email "action@github.com"
git add default.xml
git commit -m "Local manifest init"
git branch -M main
cd ..

repo init -u ./local-manifest -b main
git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
repo sync -c -j$(nproc --all) --no-tags --no-clone-bundle
