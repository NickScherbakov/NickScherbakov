#!/bin/bash

# New content for the daily-thought section
NEW_CONTENT="Your thought for today: $(date '+%Y-%m-%d')"

# Extract current content from the README.md
CURRENT_CONTENT=$(awk '/^## daily-thought/,/^## / {if (!/^## /) print}' README.md)

# Check if the current content is different from the new content
if [ "$CURRENT_CONTENT" != "$NEW_CONTENT" ]; then
  # Update the README.md if different
  sed -i.bak "/^## daily-thought/,/^## /{/^## /!d; r /dev/stdin" README.md <<EOF
$NEW_CONTENT
EOF
  rm README.md.bak # Remove backup file created by sed
  echo "README.md updated."
else
  echo "No change needed for README.md."
fi
