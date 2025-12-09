# Followers and Stars Tracking Setup

## Overview

This workflow automatically tracks new followers and stargazers on your GitHub profile, creating issue notifications to help you engage with your community.

## How It Works

The workflow runs every 6 hours and:
1. Fetches your current followers list
2. Compares with the previously saved list
3. Creates an issue for each new follower with their profile information
4. Does the same for new stargazers on your profile repository

## Required Labels

For the workflow to function properly, you need to create the following labels in your repository:

### Creating Labels via GitHub CLI

```bash
# Create new-follower label
gh label create "new-follower" \
  --description "Notification about a new follower" \
  --color "0E8A16"

# Create new-star label
gh label create "new-star" \
  --description "Notification about a new stargazer" \
  --color "FBCA04"

# Create needs-attention label
gh label create "needs-attention" \
  --description "Requires owner attention" \
  --color "D93F0B"
```

### Creating Labels via GitHub Web UI

1. Go to your repository on GitHub
2. Click on "Issues" tab
3. Click on "Labels" button
4. Click "New label" and create each of the following:

**Label 1: new-follower**
- Name: `new-follower`
- Description: `Notification about a new follower`
- Color: `#0E8A16` (green)

**Label 2: new-star**
- Name: `new-star`
- Description: `Notification about a new stargazer`
- Color: `#FBCA04` (yellow)

**Label 3: needs-attention**
- Name: `needs-attention`
- Description: `Requires owner attention`
- Color: `#D93F0B` (red)

## Files Structure

```
.github/
├── workflows/
│   └── track-followers-stars.yml    # Main workflow file
└── data/
    ├── followers.txt                 # Tracks followers list
    └── stargazers.txt                # Tracks stargazers list
```

## Manual Trigger

You can manually trigger the workflow at any time:
1. Go to "Actions" tab in your repository
2. Select "Track New Followers and Stars" workflow
3. Click "Run workflow" button

## What Happens When New Followers/Stars Are Detected

When the workflow detects new followers or stargazers, it:
1. Creates a detailed issue with user information including:
   - Name and bio
   - Location
   - Number of repositories and followers
   - Links to their profile and repositories
2. Labels the issue appropriately
3. Updates the tracking files
4. Commits the changes back to the repository

## Notifications

You'll receive GitHub notifications for each new issue created, allowing you to:
- Review the person's profile
- Decide whether to follow back
- Check out their interesting projects
- Star their repositories if you find them valuable

## Privacy Note

The tracking files (`.github/data/followers.txt` and `.github/data/stargazers.txt`) are stored in the repository and are public. They contain only GitHub usernames, which are already public information.
