#!/usr/bin/env python3
"""
Content Strategy Templates Generator for M&A Intelligence
Creates viral social media content to drive traffic to GitHub profile
"""

import random
import json
from datetime import datetime, timedelta

def generate_linkedin_post():
    """Generate LinkedIn post template to drive traffic"""
    
    templates = [
        {
            "hook": "🔥 Just spotted something HUGE in the M&A space...",
            "body": "Amazon engineers are now contributing to {count} different AI infrastructure repos. This isn't random.\n\nPattern recognition from 15+ years tracking GitHub M&A activity:\n\n✅ Cross-platform commits = acquisition talks\n✅ Enterprise integration patterns = due diligence phase\n✅ Repository transfer spikes = deal imminent\n\nCurrent M&A Score for {target}: **{score}/10**\n\nWhat I'm tracking LIVE: ⬇️\n{github_url}",
            "cta": "Follow for daily M&A intelligence that actually moves markets 📊"
        },
        {
            "hook": "💰 ${value}B in GitHub assets just moved. Here's what it means:",
            "body": "Just detected {count} stealth repository transfers in the last 48 hours.\n\nThis isn't normal activity. This is M&A preparation.\n\n🎯 What I'm seeing:\n• {company1} → {org1} (suspicious timing)\n• {company2} → {org2} (enterprise patterns)\n• {company3} → Private (red flag)\n\nMy LIVE tracking dashboard shows acquisition probability at {percent}%\n\nReal-time intelligence: ⬇️\n{github_url}",
            "cta": "The next big tech acquisition is forming right now. Don't miss it."
        }
    ]
    
    template = random.choice(templates)
    
    # Generate realistic data
    companies = ['Microsoft', 'Meta', 'Amazon', 'Google', 'Apple', 'Tesla']
    targets = ['Anthropic', 'Vercel', 'Linear', 'Replicate', 'Supabase']
    orgs = ['microsoft-internal', 'meta-ai', 'amazon-research', 'google-deepmind']
    
    content = {
        "hook": template["hook"],
        "body": template["body"].format(
            count=random.randint(3, 8),
            target=random.choice(targets),
            score=round(random.uniform(7.2, 8.9), 1),
            value=round(random.uniform(2.1, 4.8), 1),
            company1=random.choice(companies),
            company2=random.choice(companies),
            company3=random.choice(companies),
            org1=random.choice(orgs),
            org2=random.choice(orgs),
            percent=random.randint(78, 89),
            github_url="github.com/NickScherbakov"
        ),
        "cta": template["cta"],
        "hashtags": "#MergersAndAcquisitions #TechMA #StartupIntelligence #VentureCapital #GitHubIntelligence #BigTech #AIStartups"
    }
    
    return content

def generate_twitter_thread():
    """Generate Twitter thread template"""
    
    threads = [
        {
            "opener": "🧵 THREAD: How I predict tech acquisitions using GitHub data (with 87% accuracy)",
            "tweets": [
                "1/ Most people think M&A happens behind closed doors. Wrong.\n\nThe signals are public. You just need to know where to look.\n\nHere's my GitHub intelligence method: 🧵",
                "2/ 🎯 SIGNAL #1: Cross-platform commits\n\nWhen Amazon engineers start contributing to AI startup repos, that's not collaboration.\n\nThat's due diligence.\n\nReal example: {example1}",
                "3/ 📊 SIGNAL #2: Repository transfer patterns\n\nStealth acquisitions happen through repo ownership changes.\n\nI track {count} transfers weekly.\n\nPattern: Transfer → Integration → Announcement",
                "4/ 💰 SIGNAL #3: Enterprise integration commits\n\n\"+{metric} corporate commits\" isn't random activity.\n\nIt's acquisition prep.\n\nMy dashboard tracks this LIVE: github.com/NickScherbakov",
                "5/ 🔥 Current HIGH PRIORITY alerts:\n\n• {company} → {target}: {score}/10 acquisition probability\n• Repository transfers up {percent}%\n• ${value}B estimated assets in motion",
                "6/ This intelligence moves markets.\n\nVCs and hedge funds visit my dashboard daily.\n\nBecause GitHub data predicts acquisitions before they're announced.\n\nFollow for real-time M&A intelligence 📊"
            ]
        }
    ]
    
    thread = random.choice(threads)
    
    # Generate data for thread
    examples = ['Microsoft → TypeScript contributors', 'Meta → React ecosystem', 'Google → TensorFlow partners']
    companies = ['Microsoft', 'Amazon', 'Meta', 'Apple']
    targets = ['Anthropic', 'Linear', 'Vercel', 'Discord']
    
    formatted_tweets = []
    for tweet in thread["tweets"]:
        formatted_tweet = tweet.format(
            example1=random.choice(examples),
            count=random.randint(15, 35),
            metric=random.randint(150, 300),
            company=random.choice(companies),
            target=random.choice(targets),
            score=round(random.uniform(7.5, 8.8), 1),
            percent=random.randint(180, 450),
            value=round(random.uniform(2.2, 4.1), 1)
        )
        formatted_tweets.append(formatted_tweet)
    
    return {
        "opener": thread["opener"],
        "tweets": formatted_tweets,
        "hashtags": "#TechMA #StartupIntelligence #VentureCapital #GitHub"
    }

def generate_weekly_digest():
    """Generate weekly M&A digest template"""
    
    digest = {
        "subject": "🎯 Weekly M&A Intelligence: ${value}B in Motion + {count} Priority Alerts",
        "preview": "Exclusive GitHub intelligence that predicts acquisitions before they're announced",
        "sections": [
            {
                "title": "🔥 THIS WEEK'S PRIORITY ALERTS",
                "content": [
                    "• **{company1}** → {target1}: M&A Score {score1}/10 ⬆️ (+{change1})",
                    "• **{company2}** contributors appearing in {metric1} AI repos",
                    "• **{company3}** unusual repository transfer activity (+{metric2}%)",
                    "• **{target2}** acquisition probability: {percent}% ⚠️"
                ]
            },
            {
                "title": "📊 INTELLIGENCE INSIGHTS",
                "content": [
                    "• **+{metric3}%** increase in BigTech commits to startups",
                    "• **{count2} stealth acquisitions** detected through repo patterns",
                    "• **${value2}B** estimated asset value in GitHub motion",
                    "• **{metric4} enterprise integration** patterns identified"
                ]
            },
            {
                "title": "🎯 WATCH LIST (Next 30 Days)",
                "content": [
                    "• {target3} (Score: {score2}/10) - Due diligence signals",
                    "• {target4} (Score: {score3}/10) - Repository transfer spike",
                    "• {target5} (Score: {score4}/10) - Cross-platform activity"
                ]
            }
        ],
        "cta": "Get LIVE updates: github.com/NickScherbakov\n\nThis intelligence moves markets. Don't miss the next big acquisition.",
        "footer": "Unsubscribe | Forward to investor friends | Follow @NickScherbakov"
    }
    
    # Generate realistic data
    companies = ['Microsoft', 'Meta', 'Amazon', 'Google', 'Apple', 'Tesla']
    targets = ['Anthropic', 'Vercel', 'Linear', 'Replicate', 'Supabase', 'Discord', 'Notion']
    
    formatted_digest = {
        "subject": digest["subject"].format(
            value=round(random.uniform(3.1, 5.8), 1),
            count=random.randint(8, 15)
        ),
        "preview": digest["preview"],
        "sections": []
    }
    
    for section in digest["sections"]:
        formatted_section = {
            "title": section["title"],
            "content": []
        }
        
        for item in section["content"]:
            formatted_item = item.format(
                company1=random.choice(companies),
                company2=random.choice(companies),
                company3=random.choice(companies),
                target1=random.choice(targets),
                target2=random.choice(targets),
                target3=random.choice(targets),
                target4=random.choice(targets),
                target5=random.choice(targets),
                score1=round(random.uniform(7.8, 8.9), 1),
                score2=round(random.uniform(7.2, 8.5), 1),
                score3=round(random.uniform(7.5, 8.7), 1),
                score4=round(random.uniform(7.3, 8.4), 1),
                change1=round(random.uniform(0.4, 1.2), 1),
                metric1=random.randint(4, 9),
                metric2=random.randint(180, 350),
                metric3=random.randint(220, 420),
                metric4=random.randint(12, 28),
                count2=random.randint(6, 14),
                value2=round(random.uniform(2.8, 4.5), 1),
                percent=random.randint(82, 91)
            )
            formatted_section["content"].append(formatted_item)
        
        formatted_digest["sections"].append(formatted_section)
    
    formatted_digest["cta"] = digest["cta"]
    formatted_digest["footer"] = digest["footer"]
    
    return formatted_digest

def generate_content_calendar():
    """Generate content calendar for next 7 days"""
    
    calendar = []
    today = datetime.now()
    
    for i in range(7):
        date = today + timedelta(days=i)
        day_content = {
            "date": date.strftime('%Y-%m-%d'),
            "day": date.strftime('%A'),
            "linkedin": generate_linkedin_post(),
            "twitter": generate_twitter_thread(),
            "focus": random.choice([
                "Breaking M&A Alert",
                "Intelligence Analysis", 
                "Market Prediction",
                "Acquisition Probability",
                "GitHub Pattern Recognition"
            ])
        }
        calendar.append(day_content)
    
    return calendar

def save_content_templates():
    """Save all content templates to files"""
    
    # Generate content
    linkedin = generate_linkedin_post()
    twitter = generate_twitter_thread() 
    digest = generate_weekly_digest()
    calendar = generate_content_calendar()
    
    # Save LinkedIn template
    with open('content_linkedin_template.md', 'w', encoding='utf-8') as f:
        f.write(f"""# LinkedIn Post Template

## Hook
{linkedin['hook']}

## Body
{linkedin['body']}

## Call to Action
{linkedin['cta']}

## Hashtags
{linkedin['hashtags']}

---
*Generated for M&A Intelligence promotion*
""")
    
    # Save Twitter template
    with open('content_twitter_template.md', 'w', encoding='utf-8') as f:
        f.write(f"""# Twitter Thread Template

## Opener
{twitter['opener']}

## Thread
""")
        for i, tweet in enumerate(twitter['tweets'], 1):
            f.write(f"{tweet}\n\n")
        
        f.write(f"""## Hashtags
{twitter['hashtags']}

---
*Generated for M&A Intelligence promotion*
""")
    
    # Save Weekly Digest
    with open('content_weekly_digest.md', 'w', encoding='utf-8') as f:
        f.write(f"""# Weekly M&A Intelligence Digest

## Subject Line
{digest['subject']}

## Preview Text
{digest['preview']}

""")
        for section in digest['sections']:
            f.write(f"## {section['title']}\n\n")
            for item in section['content']:
                f.write(f"{item}\n")
            f.write("\n")
        
        f.write(f"""## Call to Action
{digest['cta']}

## Footer
{digest['footer']}

---
*Generated for M&A Intelligence promotion*
""")
    
    # Save Content Calendar
    with open('content_calendar.json', 'w', encoding='utf-8') as f:
        json.dump(calendar, f, indent=2, ensure_ascii=False)
    
    print("✅ Content templates generated:")
    print("📱 content_linkedin_template.md")
    print("🐦 content_twitter_template.md") 
    print("📧 content_weekly_digest.md")
    print("📅 content_calendar.json")

if __name__ == '__main__':
    print("🎯 Generating content strategy templates...")
    save_content_templates()