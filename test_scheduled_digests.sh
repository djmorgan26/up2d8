#!/bin/bash

echo "=========================================="
echo "Testing UP2D8 Scheduled Digest System"
echo "=========================================="
echo ""

# Step 1: Login to get access token
echo "Step 1: Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"davidjmorgan26@gmail.com","password":"password12345"}')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed. Please make sure your account exists."
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Logged in successfully"
echo ""

# Step 2: Get current preferences
echo "Step 2: Getting current preferences..."
curl -s -X GET "http://localhost:8000/api/v1/preferences/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

# Step 3: Update preferences to receive digest in the next hour
echo "Step 3: Updating preferences..."
CURRENT_HOUR=$(date -u +%H)
NEXT_HOUR=$(printf "%02d" $(( (10#$CURRENT_HOUR + 1) % 24 )))
DELIVERY_TIME="${NEXT_HOUR}:00"

echo "Current UTC hour: $CURRENT_HOUR"
echo "Setting delivery time to: $DELIVERY_TIME UTC (next hour)"
echo ""

UPDATE_RESPONSE=$(curl -s -X PUT "http://localhost:8000/api/v1/preferences/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"delivery_time\": \"$DELIVERY_TIME\",
    \"timezone\": \"UTC\",
    \"delivery_days\": [1, 2, 3, 4, 5, 6, 7],
    \"digest_frequency\": \"daily\",
    \"subscribed_companies\": [\"OpenAI\", \"Anthropic\", \"Google\"]
  }")

echo "$UPDATE_RESPONSE" | python3 -m json.tool
echo ""

# Step 4: Manually trigger scheduled digest generation for current hour
echo "Step 4: Manually triggering scheduled digest generation..."
echo "(This simulates what Celery Beat will do every hour)"
echo ""

docker-compose exec -T worker python3 -c "
from workers.tasks.digests import generate_scheduled_digests

# Test with next hour to see if user is scheduled
print('Testing scheduled digest generation for hour $NEXT_HOUR...')
result = generate_scheduled_digests.apply_async(args=[$NEXT_HOUR])

print(f'Task ID: {result.id}')
print('Waiting for result...')
print('')

try:
    output = result.get(timeout=30)
    print('✅ Scheduled digest task completed!')
    print('')
    print('Result:')
    import json
    print(json.dumps(output, indent=2))

    if output['tasks_queued'] > 0:
        print('')
        print('🎉 SUCCESS! Your account is scheduled to receive a digest!')
    else:
        print('')
        print('ℹ️  No tasks queued. This means either:')
        print('   - Your delivery time does not match the test hour')
        print('   - Today is not in your delivery_days')
        print('   - Your account status is not active')
except Exception as e:
    print(f'❌ Task failed: {e}')
"

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Celery Beat will automatically run every hour"
echo "2. Check worker logs: docker-compose logs -f worker"
echo "3. Check beat logs: docker-compose logs -f beat"
echo "4. You should receive an email at: davidjmorgan26@gmail.com"
echo ""
