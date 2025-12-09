# Labels Setup for Followers/Stars Tracking

This directory contains the setup for creating required labels for the followers/stars tracking workflow.

## Prerequisites

⚠️ **IMPORTANT**: Issues must be enabled on the repository before creating labels or running the tracking workflow.

To enable issues:
1. Go to repository Settings
2. Scroll down to the "Features" section
3. Check the "Issues" checkbox
4. Save changes

## Required Labels

The following labels are required for the `.github/workflows/track-followers-stars.yml` workflow:

1. **new-follower** (color: `0E8A16` - green)
   - Description: New follower notification
   - Used to tag issues created when someone follows the profile

2. **new-star** (color: `FBCA04` - yellow)
   - Description: New star notification
   - Used to tag issues created when someone stars the repository

3. **needs-attention** (color: `D93F0B` - red)
   - Description: Requires owner attention
   - Used to flag notifications that need review

## How to Create Labels

### Option 1: GitHub Actions Workflow (Recommended)

1. Go to Actions tab in the repository
2. Find "Create Required Labels" workflow
3. Click "Run workflow"
4. The labels will be created automatically

### Option 2: GitHub CLI

Run the script from the repository root:

```bash
./create_labels.sh
```

Or manually:

```bash
gh label create "new-follower" --color "0E8A16" --description "New follower notification"
gh label create "new-star" --color "FBCA04" --description "New star notification"
gh label create "needs-attention" --color "D93F0B" --description "Requires owner attention"
```

### Option 3: GitHub Web Interface

1. Go to repository Settings → Labels
2. Click "New label" for each:
   - Name: `new-follower`, Color: `#0E8A16`, Description: `New follower notification`
   - Name: `new-star`, Color: `#FBCA04`, Description: `New star notification`
   - Name: `needs-attention`, Color: `#D93F0B`, Description: `Requires owner attention`

## Verification

To verify the labels are created:

```bash
gh label list | grep -E "(new-follower|new-star|needs-attention)"
```

Or visit: https://github.com/NickScherbakov/NickScherbakov/labels
