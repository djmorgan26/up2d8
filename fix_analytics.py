#!/usr/bin/env python3
"""
Fix SQL execute statements to wrap with text()
"""

import re

file_path = "/Users/davidmorgan/Documents/Repositories/up2d8/backend/api/services/analytics_tracker.py"

with open(file_path, 'r') as f:
    content = f.read()

# Pattern to match self.db.execute with SQL string and parameters
# This handles multi-line SQL strings
pattern = r'self\.db\.execute\(\s*(""".*?""")\s*,\s*(\{[^}]+\})\s*\)'

# Replace with text() wrapper
replacement = r'self.db.execute(text(\1), \2)'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Also handle execute statements without parameters (in get_ methods)
pattern2 = r'result = self\.db\.execute\(\s*(""".*?""")\s*,\s*(\{[^}]+\})\s*\)'
replacement2 = r'result = self.db.execute(text(\1), \2)'
content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Fixed {file_path}")
