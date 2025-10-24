#!/bin/bash

echo "=========================================="
echo "Testing UP2D8 Email Digest System"
echo "=========================================="
echo ""

echo "Sending test digest to: davidjmorgan26@gmail.com"
echo ""

docker-compose exec -T worker python3 -c "
from workers.tasks.digests import send_test_digest

# Send test digest
result = send_test_digest.apply_async(
    args=['davidjmorgan26@gmail.com', 'David Morgan']
)

print(f'Task ID: {result.id}')
print(f'Task State: {result.state}')
print('Waiting for result (max 60 seconds)...')
print('')

try:
    output = result.get(timeout=60)
    print('✅ Test digest task completed!')
    print('')
    print('Result:')
    import json
    print(json.dumps(output, indent=2))
except Exception as e:
    print(f'❌ Task failed: {e}')
"

echo ""
echo "=========================================="
echo "Check your email!"
echo "=========================================="
