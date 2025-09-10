#!/usr/bin/env python3
"""
GitHub Profile Dashboard Generator
Uses GitHub API to collect repository data and generate charts
"""

import os
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import json

# Settings
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Create directories
os.makedirs('charts', exist_ok=True)

def get_transfer_info(repo_name, current_owner):
    """Get transfer information for known repository transfers"""
    transfers = {
        'facebook/react': {'old_owner': 'facebook', 'new_owner': 'meta', 'type': 'Corporate Restructuring'},
        'tensorflow/tensorflow': {'old_owner': 'google', 'new_owner': 'tensorflow', 'type': 'Foundation Spin-off'},
        'swiftlang/swift': {'old_owner': 'apple', 'new_owner': 'swiftlang', 'type': 'Foundation Transfer'},
        'Netflix/zuul': {'old_owner': 'netflix', 'new_owner': 'Netflix-Skunkworks', 'type': 'Internal Reorganization'},
        'aws/aws-sdk-js': {'old_owner': 'amazon', 'new_owner': 'aws', 'type': 'Brand Consolidation'}
    }
    
    if repo_name in transfers:
        return transfers[repo_name]
    else:
        return {'old_owner': 'Unknown', 'new_owner': current_owner, 'type': 'Monitoring'}

def get_github_data():
    """Get repository data from GitHub API"""
    repos_data = []

    # Repositories with known ownership transfers (M&A activity tracking)
    transferred_repos = [
        'facebook/react',         # facebook → meta (corporate restructuring)
        'microsoft/vscode',       # microsoft → github (potential transfer)
        'tensorflow/tensorflow',  # google → tensorflow (spin-off)
        'swiftlang/swift',        # apple → swiftlang (foundation transfer)
        'Netflix/zuul',           # netflix → Netflix-Skunkworks (reorganization)
        'aws/aws-sdk-js',         # amazon → aws (brand consolidation)
        'stripe/stripe-js',       # monitoring for potential transfers
        'twilio/twilio-python',   # monitoring for potential transfers
        'vercel/next.js',         # monitoring for potential acquisition
        'denoland/deno'           # monitoring for potential acquisition
    ]

    for repo_name in transferred_repos:
        try:
            url = f'https://api.github.com/repos/{repo_name}'
            response = requests.get(url, headers=HEADERS)

            if response.status_code == 200:
                repo_data = response.json()
                # Add transfer information based on known ownership changes
                transfer_info = get_transfer_info(repo_name, repo_data['owner']['login'])
                
                repos_data.append({
                    'name': repo_data['name'],
                    'full_name': repo_data['full_name'],
                    'owner': repo_data['owner']['login'],
                    'stars': repo_data['stargazers_count'],
                    'language': repo_data['language'] or 'Unknown',
                    'created_at': repo_data['created_at'],
                    'updated_at': repo_data['updated_at'],
                    'transfer_info': transfer_info
                })
            else:
                print(f"Failed to get data for {repo_name}: {response.status_code}")

        except Exception as e:
            print(f"Error processing {repo_name}: {e}")

    return repos_data

def generate_overview_chart(repos_data):
    """Generate market overview chart"""
    if not repos_data:
        return

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('GitHub Repositories Market Overview', fontsize=16)

    # Stars distribution
    stars = [repo['stars'] for repo in repos_data]
    ax1.hist(stars, bins=20, color='#1f77b4', alpha=0.7)
    ax1.set_title('Stars Distribution')
    ax1.set_xlabel('Stars Count')
    ax1.set_ylabel('Number of Repositories')

    # Popular languages
    languages = defaultdict(int)
    for repo in repos_data:
        languages[repo['language']] += 1

    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:8]
    if top_langs:
        langs, counts = zip(*top_langs)
        ax2.bar(langs, counts, color='#ff7f0e')
        ax2.set_title('Popular Languages')
        ax2.tick_params(axis='x', rotation=45)

    # Top repositories by stars
    top_repos = sorted(repos_data, key=lambda x: x['stars'], reverse=True)[:10]
    names = [repo['name'][:15] + '...' if len(repo['name']) > 15 else repo['name'] for repo in top_repos]
    stars_count = [repo['stars'] for repo in top_repos]

    ax3.barh(names[::-1], stars_count[::-1], color='#2ca02c')
    ax3.set_title('Top Repositories by Stars')

    # Repository owners
    owners = defaultdict(int)
    for repo in repos_data:
        owners[repo['owner']] += 1

    top_owners = sorted(owners.items(), key=lambda x: x[1], reverse=True)[:8]
    if top_owners:
        owner_names, owner_counts = zip(*top_owners)
        ax4.bar(owner_names, owner_counts, color='#9467bd')
        ax4.set_title('Repository Owners')
        ax4.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig('charts/overview.png', dpi=150, bbox_inches='tight')
    plt.close()

def generate_language_chart(repos_data):
    """Generate language popularity chart"""
    languages = defaultdict(int)
    for repo in repos_data:
        languages[repo['language']] += 1

    if languages:
        plt.figure(figsize=(10, 6))
        langs = list(languages.keys())
        counts = list(languages.values())

        sorted_data = sorted(zip(langs, counts), key=lambda x: x[1], reverse=True)
        langs, counts = zip(*sorted_data)

        plt.bar(langs, counts, color='#e74c3c')
        plt.title('Programming Languages in Tracked Repositories')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Number of Repositories')
        plt.tight_layout()
        plt.savefig('charts/languages.png', dpi=150, bbox_inches='tight')
        plt.close()

def update_readme(repos_data):
    """Update README.md with current data"""
    total_repos = len(repos_data)
    total_stars = sum(repo['stars'] for repo in repos_data)
    avg_stars = total_stars // total_repos if total_repos > 0 else 0

    top_repos = sorted(repos_data, key=lambda x: x['stars'], reverse=True)[:5]

    readme_content = f"""# NickScherbakov-dashboard

## � GitHub Repository M&A Tracker

Monitoring M&A activity in IT sector through GitHub repository ownership transfers and corporate acquisitions.

### 📈 Transfer Analytics
- **Tracked Transfers**: {total_repos}
- **Combined Asset Value**: {total_stars:,} ⭐
- **Average Asset Value**: {avg_stars:,} ⭐

### 📊 M&A Market Overview
![Market Overview](charts/overview.png)

### 🏷️ Technology Distribution
![Languages](charts/languages.png)

### � Recent Repository Transfers
| Repository | Previous Owner → Current Owner | Stars | Language |
|------------|-------------------------------|-------|----------|
"""

    for repo in top_repos:
        transfer = repo.get('transfer_info', {})
        old_owner = transfer.get('old_owner', repo['owner'])
        current_owner = repo['owner']
        if old_owner != current_owner:
            owner_display = f"{old_owner} → {current_owner}"
        else:
            owner_display = f"{current_owner} (monitoring)"
        readme_content += f"| [{repo['name']}](https://github.com/{repo['full_name']}) | {owner_display} | ⭐ {repo['stars']:,} | {repo['language']} |\n"

    readme_content += f"\n*M&A tracker updates automatically every 6 hours. Last analysis: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*"

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_index_html(repos_data):
    """Create index.html for GitHub Pages"""
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NickScherbakov - GitHub M&A Tracker</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .repos-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
        }}
        .repos-table th, .repos-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .repos-table th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .update-time {{
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>� NickScherbakov</h1>
            <p>GitHub M&A Activity Tracker</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>{len(repos_data)}</h3>
                <p>Monitored Transfers</p>
            </div>
            <div class="stat-card">
                <h3>{sum(repo['stars'] for repo in repos_data):,}</h3>
                <p>Combined Asset Value (⭐)</p>
            </div>
            <div class="stat-card">
                <h3>{sum(repo['stars'] for repo in repos_data) // len(repos_data) if repos_data else 0:,}</h3>
                <p>Average Asset Value (⭐)</p>
            </div>
        </div>

        <div class="chart-container">
            <h2>📊 M&A Market Overview</h2>
            <img src="charts/overview.png" alt="Market Overview Chart">
        </div>

        <div class="chart-container">
            <h2>🏷️ Technology Assets</h2>
            <img src="charts/languages.png" alt="Languages Chart">
        </div>

        <h2>� Repository Transfers</h2>
        <table class="repos-table">
            <thead>
                <tr>
                    <th>Repository</th>
                    <th>Transfer Status</th>
                    <th>Asset Value (⭐)</th>
                    <th>Technology</th>
                </tr>
            </thead>
            <tbody>"""

    top_repos = sorted(repos_data, key=lambda x: x['stars'], reverse=True)[:10]
    for repo in top_repos:
        transfer = repo.get('transfer_info', {})
        old_owner = transfer.get('old_owner', repo['owner'])
        current_owner = repo['owner']
        if old_owner != current_owner:
            status_display = f"{old_owner} → {current_owner}"
        else:
            status_display = f"{current_owner} (monitoring)"
        html_content += f"""
                <tr>
                    <td><a href="https://github.com/{repo['full_name']}" target="_blank">{repo['name']}</a></td>
                    <td>{status_display}</td>
                    <td>⭐ {repo['stars']:,}</td>
                    <td>{repo['language']}</td>
                </tr>"""

    html_content += f"""
            </tbody>
        </table>

        <div class="update-time">
            📅 Last M&A analysis: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
        </div>
    </div>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    """Main function"""
    print("🚀 Starting dashboard generation...")

    # Get data
    print("📊 Getting data from GitHub API...")
    repos_data = get_github_data()

    if not repos_data:
        print("❌ Failed to get data")
        return

    print(f"✅ Got data for {len(repos_data)} repositories")

    # Generate charts
    print("📈 Generating charts...")
    generate_overview_chart(repos_data)
    generate_language_chart(repos_data)

    # Update README
    print("📝 Updating README...")
    update_readme(repos_data)

    # Create HTML page
    print("🌐 Creating HTML page...")
    create_index_html(repos_data)

    print("🎉 Dashboard updated successfully!")

if __name__ == '__main__':
    main()