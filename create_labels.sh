#!/bin/bash
# Script to create required labels for the followers/stars tracking workflow
# Usage: ./create_labels.sh

set -e

echo "Creating labels for followers/stars tracking workflow..."
echo ""

# Create new-follower label (green)
echo "Creating 'new-follower' label..."
gh label create "new-follower" \
  --color "0E8A16" \
  --description "New follower notification" \
  --force 2>&1 || echo "Label 'new-follower' already exists or could not be created"

# Create new-star label (yellow)
echo "Creating 'new-star' label..."
gh label create "new-star" \
  --color "FBCA04" \
  --description "New star notification" \
  --force 2>&1 || echo "Label 'new-star' already exists or could not be created"

# Create needs-attention label (red)
echo "Creating 'needs-attention' label..."
gh label create "needs-attention" \
  --color "D93F0B" \
  --description "Requires owner attention" \
  --force 2>&1 || echo "Label 'needs-attention' already exists or could not be created"

echo ""
echo "✅ Label creation complete!"
echo ""
echo "Verifying labels..."
gh label list | grep -E "(new-follower|new-star|needs-attention)"
