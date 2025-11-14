# Daily Digest Email Debugging Guide

**Date**: 2025-11-14
**Issue**: Not receiving daily digest emails

---

## System Overview

The daily digest email system works as follows:

1. **Azure Timer Trigger** runs at **14:00 UTC (9 AM EST)** daily
2. **NewsletterGenerator** function (`packages/functions/NewsletterGenerator/__init__.py:32`)
   - Fetches all users from Cosmos DB
   - Fetches unprocessed articles
   - For each user with email notifications enabled:
     - Filters articles by user topics
     - Generates newsletter using Gemini 2.5 Flash AI
     - Sends via Brevo SMTP
   - Marks articles as processed

---

## Potential Issues & Diagnostic Steps

### Issue #1: Azure Function Not Deployed or Running ⚠️ MOST LIKELY

**Symptoms**: No emails ever received, regardless of other settings

**Check**:
```bash
# 1. Check if function app is running
az functionapp list --resource-group <your-resource-group> --query "[].{name:name, state:state}" --output table

# 2. Check function app status
az functionapp show --name <function-app-name> --resource-group <resource-group> --query "{name:name, state:state, enabled:enabled}" --output json

# 3. View recent executions
az monitor activity-log list --resource-id <function-app-resource-id> --max-events 10

# 4. Check logs in real-time
az functionapp log tail --name <function-app-name> --resource-group <resource-group>
```

**Via Azure Portal**:
1. Go to **Azure Portal** → **Function Apps** → Select your function app
2. Check **Overview** → Ensure "Running" status
3. Go to **Functions** → **NewsletterGenerator** → **Monitor**
4. Check **Invocations** tab for recent executions
5. Check **Logs** for any errors

**Solution**:
- If function app is stopped: Start it
- If not deployed: Deploy using `func azure functionapp publish <function-app-name>`
- If schedule is disabled: Enable timer trigger

---

### Issue #2: No Unprocessed Articles ⚠️ VERY LIKELY

**Symptoms**: Function runs but sends 0 emails

**Logic** (from `packages/functions/NewsletterGenerator/__init__.py:71-73`):
```python
if not articles:
    logger.info("No new articles to process.")
    return  # Function exits early!
```

**Check via Cosmos DB**:
```javascript
// Connect to Cosmos DB and run:
db.articles.count({ processed: false })

// Should return > 0 for emails to send
```

**Check via Backend API**:
```bash
curl https://<your-backend>.azurewebsites.net/api/articles | jq '.[] | select(.processed == false)'
```

**Root Causes**:
- DailyArticleScraper not running (scheduled 08:00 UTC)
- DailyArticleScraper failing to create articles
- All articles already marked as processed

**Solution**:
```javascript
// Temporary fix: Reset processed flag for testing
db.articles.updateMany({}, { $set: { processed: false } })

// Or add new RSS feeds and run DailyArticleScraper
```

---

### Issue #3: Email Notifications Disabled ⚠️ LIKELY

**Logic** (from `packages/functions/NewsletterGenerator/__init__.py:85-90`):
```python
email_notifications = user_preferences.get('email_notifications', True)

if not email_notifications:
    logger.info("Email notifications disabled for user", user_email=user['email'])
    continue  # Skips this user
```

**Check via Cosmos DB**:
```javascript
// Find your user
db.users.findOne({ email: "your-email@example.com" })

// Check preferences.email_notifications field
// Should be true (or missing, defaults to true)
```

**Check via Backend API**:
```bash
# Get user ID from your JWT token or database
curl https://<backend>.azurewebsites.net/api/users/<user-id> \
  -H "Authorization: Bearer <your-jwt-token>"
```

**Solution**:
- Enable via Web App: **Settings** → **Notifications** → Enable "Email Notifications"
- Or manually update database:
```javascript
db.users.updateOne(
  { email: "your-email@example.com" },
  { $set: { "preferences.email_notifications": true } }
)
```

---

### Issue #4: No Topics Configured ⚠️ LIKELY

**Logic** (from `packages/functions/NewsletterGenerator/__init__.py:99-106`):
```python
relevant_articles = [a for a in articles if any(topic.lower() in a.get('title', '').lower() or
                                                 topic.lower() in a.get('summary', '').lower()
                                                 for topic in user_topics)]

if not relevant_articles:
    logger.info("No relevant articles for user", user_email=user['email'], topics=user_topics)
    continue  # No email sent!
```

**Check**:
```javascript
db.users.findOne(
  { email: "your-email@example.com" },
  { topics: 1, email: 1 }
)

// topics array should not be empty
// Example: ["AI", "technology", "startups"]
```

**Solution**:
- Add topics via Web App: **Settings** → **Preferences** → Select topics
- Or manually:
```javascript
db.users.updateOne(
  { email: "your-email@example.com" },
  { $set: { topics: ["AI", "technology", "business"] } }
)
```

---

### Issue #5: Wrong Newsletter Frequency

**Logic** (from `packages/functions/NewsletterGenerator/__init__.py:84-97`):
```python
newsletter_frequency = user_preferences.get('newsletter_frequency', 'daily')

if not should_send_newsletter(newsletter_frequency):
    logger.info("Skipping user due to frequency setting", ...)
    continue
```

**Frequency Rules** (from `packages/functions/NewsletterGenerator/__init__.py:17-30`):
- `"daily"`: Always sends
- `"weekly"`: Only sends on Mondays
- `"monthly"`: Only sends on 1st of month

**Check**:
```javascript
db.users.findOne(
  { email: "your-email@example.com" },
  { "preferences.newsletter_frequency": 1 }
)

// Should be "daily" to receive every day
```

**Today**: Thursday, 2025-11-14 (weekday 3)
- If frequency is "weekly", you won't receive until next Monday

**Solution**:
- Change to "daily" via Web App or:
```javascript
db.users.updateOne(
  { email: "your-email@example.com" },
  { $set: { "preferences.newsletter_frequency": "daily" } }
)
```

---

### Issue #6: SMTP Configuration Error

**Unlikely if other users are receiving emails**

**Check**:
```bash
# Test SMTP connection
cd /home/user/up2d8/packages/functions
python tests/test_smtp.py
```

**Environment Variables Required**:
- `BREVO_SMTP_USER`
- `BREVO_SMTP_HOST=smtp-relay.brevo.com`
- `BREVO_SMTP_PORT=587`
- `SENDER_EMAIL`

**Key Vault Secrets Required**:
- `UP2D8-SMTP-KEY`

---

### Issue #7: Emails Going to Spam

**Check**:
1. Check your spam/junk folder
2. Check Promotions tab (Gmail)
3. Add `davidjmorgan26@gmail.com` to contacts

---

## Quick Diagnostic Commands

### 1. Check Azure Function Status
```bash
az functionapp show \
  --name <function-app-name> \
  --resource-group <resource-group> \
  --query "{name:name, state:state, enabled:enabled}"
```

### 2. Check Recent Function Executions
```bash
# Via Azure Portal
# Functions → NewsletterGenerator → Monitor → Invocations

# Look for executions at 14:00 UTC
# Check for errors or "No new articles" messages
```

### 3. Manual Trigger (Testing)
```bash
# Via Azure Portal
# Functions → NewsletterGenerator → Code + Test → Run

# Or via API
curl -X POST https://<function-app>.azurewebsites.net/admin/functions/NewsletterGenerator \
  -H "x-functions-key: <master-key>"
```

### 4. Check Database Directly
```javascript
// Connect to Cosmos DB and run:

// 1. Find your user
db.users.findOne({ email: "your-email@example.com" })

// 2. Count unprocessed articles
db.articles.count({ processed: false })

// 3. Check if any articles match your topics
db.articles.find(
  {
    processed: false,
    $or: [
      { title: /AI/i },
      { summary: /AI/i }
    ]
  }
).limit(5)
```

---

## Recommended Action Plan

**Step 1**: Check if function is deployed and running
```bash
az functionapp show --name <function-app-name> --resource-group <resource-group>
```

**Step 2**: Check Azure Function logs for NewsletterGenerator
- Look for recent executions at 14:00 UTC
- Check for error messages

**Step 3**: Verify your user settings in database
```javascript
db.users.findOne({ email: "your-email@example.com" })
```

Ensure:
- ✅ `preferences.email_notifications: true`
- ✅ `preferences.newsletter_frequency: "daily"`
- ✅ `topics: ["AI", "technology", ...]` (not empty)

**Step 4**: Check for unprocessed articles
```javascript
db.articles.count({ processed: false })
```

If 0, run DailyArticleScraper or reset:
```javascript
db.articles.updateMany({}, { $set: { processed: false } })
```

**Step 5**: Manual test trigger
- Go to Azure Portal → Functions → NewsletterGenerator → Code + Test → Run
- Check logs for execution details

**Step 6**: Test SMTP directly
```bash
cd packages/functions
python tests/test_smtp.py
```

---

## Most Likely Root Causes (Ranked)

1. **No unprocessed articles in database** (70% probability)
   - DailyArticleScraper not running or failing
   - All articles already processed

2. **User has no topics configured** (60% probability)
   - Newsletter skips user if no topic matches

3. **Azure Function not deployed or running** (40% probability)
   - Check function app status in Azure Portal

4. **Email notifications disabled** (30% probability)
   - Check user preferences in database

5. **Wrong frequency setting** (20% probability)
   - User set to "weekly" or "monthly"

6. **Schedule mismatch** (10% probability)
   - Check if function actually runs at 14:00 UTC

---

## Files to Check

- **Function Code**: `packages/functions/NewsletterGenerator/__init__.py`
- **Schedule Config**: `packages/functions/NewsletterGenerator/function.json`
- **Email Service**: `packages/functions/shared/email_service.py`
- **Test Script**: `packages/functions/tests/test_smtp.py`
- **Deployment Guide**: `packages/functions/DEPLOYMENT_GUIDE.md`

---

## Next Steps

Please run the diagnostic commands above and share:
1. Azure Function app status
2. Recent NewsletterGenerator execution logs
3. Your user document from Cosmos DB
4. Article count (processed vs unprocessed)

This will help identify the exact root cause.
