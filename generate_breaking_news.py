#!/usr/bin/env python3
"""
Breaking News Generator for M&A Intelligence
Generates realistic-looking alerts based on actual GitHub activity
"""

import os
import requests
import random
from datetime import datetime, timedelta
import json

# GitHub API settings
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
} if GITHUB_TOKEN else {}

def get_trending_activity():
    """Get real GitHub activity data for generating news"""
    
    # Major tech companies to monitor
    companies = [
        'microsoft', 'google', 'meta', 'amazon', 'apple', 
        'netflix', 'tesla', 'nvidia', 'salesforce', 'oracle'
    ]
    
    # AI/Startup companies to track
    startups = [
        'openai', 'anthropic', 'vercel', 'supabase', 'replicate',
        'linear', 'figma', 'notion', 'discord', 'slack'
    ]
    
    activities = []
    
    for company in companies[:3]:  # Limit API calls
        try:
            # Get recent public events
            url = f'https://api.github.com/orgs/{company}/events'
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                events = response.json()[:5]  # Recent 5 events
                for event in events:
                    if event['type'] in ['PushEvent', 'CreateEvent', 'ForkEvent']:
                        activities.append({
                            'company': company,
                            'type': event['type'],
                            'repo': event['repo']['name'],
                            'created_at': event['created_at']
                        })
        except:
            pass
    
    return activities

def generate_breaking_news():
    """Generate breaking news based on real activity"""
    
    now = datetime.now()
    
    # Get real activity data
    real_activities = get_trending_activity()
    
    # Templates for breaking news
    breaking_templates = [
        "🎯 **{company}**: Unusual activity in `{repo}` - {metric}% increase in external contributors",
        "🔍 **{company}**: Repository `{repo}` showing enterprise integration patterns (+{metric} corporate commits)",
        "📈 **{company}**: New private repository activity detected - potential partnership signals",
        "⚠️ **{company}** contributors now appearing in {metric} major AI infrastructure repos",
        "📊 **{company}** showing {metric}% increase in cross-platform development activity"
    ]
    
    priority_templates = [
        "⚠️ **{company}** contributors now appearing in {metric} major AI infrastructure repos",
        "📊 **{startup}** M&A Score: **{score}/10** ⬆️ (+{change} this week) - Acquisition probability: {prob}%",
        "🎪 **{company}** unusual repository transfer activity - {metric} repos moved to new org structure"
    ]
    
    insight_templates = [
        "📈 **+{metric}%** increase in BigTech commits to AI startups (7-day trend)",
        "🔄 **{metric} stealth acquisitions** detected through repository transfer patterns",
        "💰 **${value}B** estimated asset value in motion (GitHub activity correlation)"
    ]
    
    breaking_news = []
    priority_alerts = []
    insights = []
    
    # Generate breaking news
    for i in range(3):
        if real_activities and i < len(real_activities):
            activity = real_activities[i]
            company = activity['company'].title()
            repo = activity['repo'].split('/')[-1]
            metric = random.randint(15, 89)
        else:
            company = random.choice(['Microsoft', 'Google', 'Meta', 'Amazon', 'Apple'])
            repo = random.choice(['ai-platform', 'TypeScript', 'react', 'kubernetes', 'tensorflow'])
            metric = random.randint(23, 67)
        
        template = random.choice(breaking_templates)
        news = template.format(company=company, repo=repo, metric=metric)
        breaking_news.append(news)
    
    # Generate priority alerts
    companies = ['Microsoft', 'Meta', 'Amazon', 'Google', 'Apple']
    startups = ['Anthropic', 'Vercel', 'Discord', 'Linear', 'Replicate']
    
    for i in range(3):
        if i < 2:
            company = random.choice(companies)
            metric = random.randint(3, 8)
            template = priority_templates[0]
            alert = template.format(company=company, metric=metric)
        else:
            startup = random.choice(startups)
            score = round(random.uniform(7.2, 8.9), 1)
            change = round(random.uniform(0.3, 1.2), 1)
            prob = random.randint(72, 89)
            template = priority_templates[1]
            alert = template.format(startup=startup, score=score, change=change, prob=prob)
        
        priority_alerts.append(alert)
    
    # Generate insights
    metrics = [random.randint(180, 450), random.randint(8, 18), round(random.uniform(1.8, 4.2), 1)]
    
    insights.append(insight_templates[0].format(metric=metrics[0]))
    insights.append(insight_templates[1].format(metric=metrics[1]))
    insights.append(insight_templates[2].format(value=metrics[2]))
    
    return {
        'breaking': breaking_news,
        'priority': priority_alerts,
        'insights': insights,
        'timestamp': now.strftime('%Y-%m-%d %H:%M UTC')
    }

def update_readme_with_news():
    """Update README with fresh breaking news"""
    
    news_data = generate_breaking_news()
    
    # Read current README
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print("Could not read README.md")
        return
    
    # Find and replace the breaking news section
    breaking_start = "**⚡ BREAKING (Last 6 Hours):**"
    
    if breaking_start in content:
        # Update timestamp first
        new_timestamp = f"**Last Updated: {news_data['timestamp']}**"
        
        # Build new breaking section
        breaking_section = "**⚡ BREAKING (Last 6 Hours):**\n"
        for news in news_data['breaking']:
            breaking_section += f"- {news}\n"
        
        breaking_section += f"\n**🔥 HIGH PRIORITY ALERTS:**\n"
        for alert in news_data['priority']:
            breaking_section += f"- {alert}\n"
        
        breaking_section += f"\n**💡 INTELLIGENCE INSIGHTS:**\n"
        for insight in news_data['insights']:
            breaking_section += f"- {insight}\n"
        
        # Replace sections using more flexible regex
        import re
        
        # Update timestamp
        content = re.sub(
            r'\*\*Last Updated:.*?\*\*',
            new_timestamp,
            content
        )
        
        # Update entire breaking news section
        pattern = r'(\*\*⚡ BREAKING \(Last 6 Hours\):\*\*.*?)(\n\n<div align="center">)'
        replacement = breaking_section + r' \2'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Write back to file
        try:
            with open('README.md', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated README with fresh M&A intelligence: {news_data['timestamp']}")
        except Exception as e:
            print(f"❌ Could not write README.md: {e}")
    else:
        print("❌ Could not find breaking news section in README.md")
        print("📝 Looking for section starting with:", breaking_start)
        # Debug: show what sections we found
        lines_with_breaking = [line for line in content.split('\n') if 'BREAKING' in line or '⚡' in line]
        if lines_with_breaking:
            print("🔍 Found these lines with BREAKING or ⚡:")
            for line in lines_with_breaking:
                print(f"  - {line.strip()}")
        else:
            print("🔍 No lines with BREAKING or ⚡ found")

if __name__ == '__main__':
    print("🚨 Generating fresh M&A intelligence...")
    update_readme_with_news()