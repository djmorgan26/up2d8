#!/usr/bin/env python3
"""
Test script to verify the enhanced email template works correctly.
"""

import sys
sys.path.insert(0, '/home/user/up2d8/packages/functions')

from shared.email_template import get_newsletter_template, get_plain_text_newsletter

# Test data with all new fields
test_articles = [
    {
        'id': 'art1',
        'title': 'AI Breakthrough in Healthcare',
        'summary': 'Researchers have developed a new AI model that can detect diseases earlier than traditional methods. This breakthrough could save millions of lives.',
        'link': 'https://example.com/ai-healthcare',
        'published': '2025-01-15',
        'image_url': 'https://placehold.co/600x300/3b82f6/white?text=AI+Healthcare',
        'topic': 'Technology',
        'source': 'TechCrunch',
        'read_time': '5 min',
        'published_time_ago': '2h ago'
    },
    {
        'id': 'art2',
        'title': 'New Climate Agreement Reached',
        'summary': 'World leaders have agreed on ambitious new climate targets at the global summit.',
        'link': 'https://example.com/climate',
        'published': '2025-01-15',
        'topic': 'World News',
        'source': 'Reuters',
        'read_time': '3 min',
        'published_time_ago': '5h ago'
    }
]

print("Testing CONCISE format...")
print("=" * 80)

html_concise = get_newsletter_template(
    articles=test_articles,
    user_name="John",
    newsletter_format="concise",
    user_topics=["Technology", "World News", "Health"],
    unsubscribe_url="https://example.com/unsubscribe",
    variant="A"
)

# Check key features are present
checks = [
    ("Preheader text", "display: none" in html_concise and "personalized stories" in html_concise),
    ("Mobile CSS", "@media only screen and (max-width: 600px)" in html_concise),
    ("Dark mode CSS", "@media (prefers-color-scheme: dark)" in html_concise),
    ("Unsubscribe link", "unsubscribe" in html_concise.lower()),
    ("Alt text", 'alt="' in html_concise),
    ("Aria labels", 'aria-label=' in html_concise),
    ("Topic badge", "Technology" in html_concise),
    ("Article image", test_articles[0]['image_url'] in html_concise),
    ("Personalization", "Technology" in html_concise and "World News" in html_concise),
    ("User name", "John" in html_concise),
]

all_passed = True
for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if not result:
        all_passed = False

print("\n" + "=" * 80)
print("Testing DETAILED format...")
print("=" * 80)

html_detailed = get_newsletter_template(
    articles=test_articles,
    user_name="Jane",
    newsletter_format="detailed",
    user_topics=["Technology"],
    unsubscribe_url="https://example.com/unsubscribe",
    variant="B"
)

# Check detailed-specific features
detailed_checks = [
    ("Metadata shown", "TechCrunch" in html_detailed),
    ("Read time shown", "5 min" in html_detailed or "📖" in html_detailed),
    ("Feedback buttons", "Was this article helpful" in html_detailed),
    ("Variant B emoji", "🗞️" in html_detailed),
    ("Longer summary", len(html_detailed) > len(html_concise)),
]

for check_name, result in detailed_checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if not result:
        all_passed = False

print("\n" + "=" * 80)
print("Testing plain text version...")
print("=" * 80)

text_version = get_plain_text_newsletter(
    articles=test_articles,
    user_name="Alice"
)

text_checks = [
    ("Contains title", test_articles[0]['title'] in text_version),
    ("Contains summary", "Researchers have developed" in text_version),
    ("Contains link", test_articles[0]['link'] in text_version),
    ("User name", "Alice" in text_version),
]

for check_name, result in text_checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if not result:
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nEmail template features:")
    print("  ✓ Mobile-responsive design with media queries")
    print("  ✓ Dark mode support")
    print("  ✓ Accessibility (alt text, aria labels)")
    print("  ✓ Unsubscribe link (legal compliance)")
    print("  ✓ Preheader text for email previews")
    print("  ✓ Article preview images")
    print("  ✓ Topic tags")
    print("  ✓ Format preference (concise vs detailed)")
    print("  ✓ Metadata (source, time, read time)")
    print("  ✓ Feedback buttons (detailed mode)")
    print("  ✓ Enhanced personalization")
    print("  ✓ A/B testing variants")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED")
    print("=" * 80)
    sys.exit(1)
