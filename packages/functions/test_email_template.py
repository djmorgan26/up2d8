#!/usr/bin/env python3
"""Test the email template without sending."""
import sys
import os

# Add the functions directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.email_template import get_newsletter_template, get_plain_text_newsletter

# Sample articles
sample_articles = [
    {
        'title': 'Breaking: Major AI Breakthrough Announced',
        'summary': 'Researchers at a leading tech company have announced a significant breakthrough in artificial intelligence, potentially revolutionizing how we interact with technology.',
        'link': 'https://example.com/article1',
        'published': '2025-11-15'
    },
    {
        'title': 'Climate Summit Reaches Historic Agreement',
        'summary': 'World leaders have come together to sign a groundbreaking climate agreement aimed at reducing global emissions by 50% over the next decade.',
        'link': 'https://example.com/article2',
        'published': '2025-11-15'
    },
    {
        'title': 'New Study Reveals Health Benefits of Mediterranean Diet',
        'summary': 'A comprehensive 10-year study shows that following a Mediterranean diet can significantly reduce the risk of heart disease and improve overall longevity.',
        'link': 'https://example.com/article3',
        'published': '2025-11-14'
    }
]

print("=" * 80)
print("TESTING EMAIL TEMPLATE")
print("=" * 80)

# Generate HTML template
html_content = get_newsletter_template(sample_articles, "David")
print("\n✅ HTML template generated successfully!")
print(f"Length: {len(html_content)} characters")

# Generate plain text template
text_content = get_plain_text_newsletter(sample_articles, "David")
print("\n✅ Plain text template generated successfully!")
print(f"Length: {len(text_content)} characters")

# Save to file for inspection
output_file = "/tmp/test_newsletter.html"
with open(output_file, 'w') as f:
    f.write(html_content)

print(f"\n✅ HTML saved to: {output_file}")
print("\nYou can open this file in a browser to see how the email looks!")

print("\n" + "=" * 80)
print("PREVIEW OF PLAIN TEXT VERSION:")
print("=" * 80)
print(text_content[:500] + "...\n")

print("=" * 80)
print("✅ Template test completed successfully!")
print("=" * 80)
