# Post-Merge Setup & Testing Guide

**Branch**: `claude/debug-daily-digest-emails-01LPni6yub8y6PDjQ9sJ4Udy`

After merging this PR into main, follow these steps to deploy and test the daily digest email system.

---

## 📦 What This PR Includes

### New Features
1. **NewsletterGeneratorManual** - HTTP-triggered function for manual testing
2. **Enhanced Logging** - Detailed logs for debugging newsletter issues
3. **Test Data Setup Script** - Easy way to prepare database for testing
4. **Diagnostic Tools** - Scripts to identify configuration issues

### Files Added/Modified
- ✅ `packages/functions/NewsletterGeneratorManual/` - Manual trigger endpoint
- ✅ `packages/functions/NewsletterGenerator/__init__.py` - Enhanced logging
- ✅ `packages/functions/tests/setup_test_data.py` - Test data setup
- ✅ `packages/functions/tests/diagnose_newsletter.py` - Diagnostic script
- ✅ `DEBUG_DAILY_DIGEST.md` - Comprehensive debugging guide
- ✅ `POST_MERGE_SETUP.md` - This file

---

## 🚀 Deployment Steps

### Step 1: Deploy Azure Functions

After merging to main, deploy the updated functions to Azure:

```bash
# Navigate to functions directory
cd packages/functions

# Deploy to Azure (replace with your function app name)
func azure functionapp publish <your-function-app-name>
```

**Expected Output:**
```
Getting site publishing info...
Uploading package...
Upload completed successfully.
Deployment completed successfully.
Functions in <your-function-app-name>:
    NewsletterGenerator - [timerTrigger]
    NewsletterGeneratorManual - [httpTrigger]
    ...
```

### Step 2: Verify Deployment

Check that both newsletter functions are deployed:

```bash
# List all functions
az functionapp function list \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --query "[?contains(name, 'Newsletter')].{name:name, triggerType:config.bindings[0].type}" \
  --output table
```

**Expected:**
| name                     | triggerType   |
|--------------------------|---------------|
| NewsletterGenerator      | timerTrigger  |
| NewsletterGeneratorManual| httpTrigger   |

---

## 🧪 Testing Process

### Phase 1: Setup Test Data

Run the test data setup script to ensure your database is ready:

```bash
# Option 1: Run locally (requires Azure credentials)
cd packages/functions
python tests/setup_test_data.py

# Enter your email when prompted
```

This will:
- ✅ Create/update your user with test-friendly settings
- ✅ Set topics: ["AI", "technology", "startup", "business", "innovation"]
- ✅ Enable email notifications
- ✅ Set frequency to "daily"
- ✅ Create sample articles (if needed)
- ✅ Reset articles to unprocessed state

### Phase 2: Get Function Key

You'll need the function key to call the manual trigger endpoint:

```bash
# Get the function key
az functionapp function keys list \
  --name <your-function-app-name> \
  --resource-group <your-resource-group> \
  --function-name NewsletterGeneratorManual \
  --query "default" \
  --output tsv
```

**Save this key** - you'll use it for testing.

### Phase 3: Manual Test Trigger

Test the newsletter generation manually:

```bash
# Replace placeholders:
# - <function-app-name>: your Azure function app name
# - <function-key>: the key from Phase 2
# - <your-email>: the email you set up in Phase 1

curl -v "https://<function-app-name>.azurewebsites.net/api/NewsletterGeneratorManual?code=<function-key>&email=<your-email>"
```

**Example:**
```bash
curl -v "https://up2d8-functions.azurewebsites.net/api/NewsletterGeneratorManual?code=abc123xyz&email=john@example.com"
```

**Expected Response (Success):**
```json
{
  "status": "success",
  "timestamp": "2025-11-14T...",
  "users_processed": 1,
  "articles_available": 5,
  "newsletters_sent": 1,
  "users_skipped": 0,
  "errors": 0,
  "details": {
    "skipped": [],
    "errors": []
  }
}
```

**If you get errors, the response will show:**
- Which users were skipped and why
- Any errors that occurred
- Article and user counts

### Phase 4: Check Your Email

Within 1-2 minutes, you should receive an email:

- **Subject**: "Your Daily News Digest"
- **From**: Your configured sender email (davidjmorgan26@gmail.com)
- **Content**: AI-generated newsletter with articles matching your topics

**If you don't receive it:**
1. Check spam/junk folder
2. Check Promotions tab (Gmail)
3. Review the Azure Function logs (see Troubleshooting section)

### Phase 5: Check Azure Function Logs

Monitor the logs to see detailed execution:

```bash
# Stream logs in real-time
az functionapp log tail \
  --name <your-function-app-name> \
  --resource-group <your-resource-group>
```

**Look for these log entries:**
```
INFO NewsletterGenerator function is executing
INFO Data fetched from database total_users=1 unprocessed_articles=5
INFO Processing user user_email=your@email.com topics=['AI', 'technology', ...]
INFO Articles filtered for user relevant_count=5
INFO Generating newsletter with Gemini article_count=5
INFO Newsletter content generated successfully
INFO Sending newsletter email
INFO Newsletter sent successfully
INFO Newsletter generation completed newsletters_sent=1 users_skipped=0 errors=0
```

### Phase 6: Test Scheduled Trigger

The automatic newsletter runs at **14:00 UTC (9 AM EST)** daily.

**To test the scheduled trigger:**

1. **Wait for next scheduled run** (14:00 UTC)
   - Or manually trigger it in Azure Portal:
   - Go to: Function Apps → NewsletterGenerator → Code + Test → Click "Run"

2. **Monitor execution:**
   ```bash
   # In Azure Portal
   Function Apps → NewsletterGenerator → Monitor → Invocations

   # Check for recent execution at 14:00 UTC
   ```

3. **Check logs** for the same log entries as Phase 5

---

## 🔍 Troubleshooting

### Issue: No email received

**Check 1: Response status**
```bash
# Look at the response from the manual trigger
# If newsletters_sent=0, check the "details" section for why
```

**Check 2: User settings in database**
```javascript
// Connect to Cosmos DB and verify:
db.users.findOne({ email: "your-email@example.com" })

// Ensure:
// - preferences.email_notifications: true
// - preferences.newsletter_frequency: "daily"
// - topics: [...] (not empty)
```

**Check 3: Articles available**
```javascript
// Check for unprocessed articles
db.articles.count({ processed: false })

// If 0, run:
db.articles.updateMany({}, { $set: { processed: false } })
```

**Check 4: Function logs**
```bash
# Stream logs and look for errors
az functionapp log tail --name <function-app-name> --resource-group <rg>
```

### Issue: Function returns errors

**Common errors and solutions:**

1. **"No new articles to process"**
   - Run DailyArticleScraper or reset articles: `db.articles.updateMany({}, {$set: {processed: false}})`

2. **"Error generating content with Gemini"**
   - Check Gemini API key in Key Vault: `UP2D8-GEMINI-API-Key`
   - Verify API quota hasn't been exceeded

3. **"Failed to send newsletter via SMTP"**
   - Check Brevo SMTP credentials
   - Verify Key Vault secret: `UP2D8-SMTP-KEY`
   - Check environment variables: `BREVO_SMTP_USER`, `BREVO_SMTP_HOST`, `BREVO_SMTP_PORT`

4. **"No relevant articles for user"**
   - User's topics don't match any article titles/summaries
   - Add more broad topics: ["AI", "technology", "business"]

### Issue: Deployment failed

**Solution:**
```bash
# Check function app status
az functionapp show \
  --name <function-app-name> \
  --resource-group <resource-group> \
  --query "{name:name, state:state, enabled:enabled}"

# If stopped, start it
az functionapp start \
  --name <function-app-name> \
  --resource-group <resource-group>

# Retry deployment
func azure functionapp publish <function-app-name>
```

---

## 📊 Verification Checklist

After completing all phases, verify:

- [ ] Both NewsletterGenerator and NewsletterGeneratorManual are deployed
- [ ] Test data setup script ran successfully
- [ ] Manual trigger endpoint returns `"newsletters_sent": 1`
- [ ] Email received in inbox (check spam if not)
- [ ] Azure Function logs show detailed execution steps
- [ ] No errors in logs
- [ ] User in database has correct settings
- [ ] Articles exist with `processed: false`

---

## 🎯 Testing Different Scenarios

### Test 1: Force Send (Ignore Frequency)

Send newsletter regardless of frequency setting:

```bash
curl "https://<function-app>.azurewebsites.net/api/NewsletterGeneratorManual?code=<key>&force=true&email=<your-email>"
```

### Test 2: Test All Users

Send to all users (not just one):

```bash
curl "https://<function-app>.azurewebsites.net/api/NewsletterGeneratorManual?code=<key>"
```

### Test 3: No Unprocessed Articles

Reset all articles to processed and see the warning:

```javascript
db.articles.updateMany({}, { $set: { processed: true } })
```

Then trigger:
```bash
curl "https://<function-app>.azurewebsites.net/api/NewsletterGeneratorManual?code=<key>"
```

Expected response:
```json
{
  "status": "warning",
  "message": "No new articles to process.",
  "users": 1,
  "articles": 0,
  "sent": 0
}
```

---

## 📝 Next Steps After Testing

Once testing is complete and emails are working:

1. **Monitor Daily Runs**
   - Check Azure Portal → Function Apps → Monitor
   - Verify execution at 14:00 UTC daily

2. **Review Logs Regularly**
   - Look for patterns in skipped users
   - Monitor error rates

3. **Adjust Topics as Needed**
   - Users can update via web app: Settings → Preferences

4. **Monitor DailyArticleScraper**
   - Ensure it runs at 08:00 UTC (before newsletter)
   - Verify new articles are created daily

5. **Check Email Deliverability**
   - Monitor Brevo dashboard for bounces/spam reports
   - Ensure sender reputation stays high

---

## 🔗 Quick Reference

### Function URLs

- **Manual Trigger**: `https://<function-app>.azurewebsites.net/api/NewsletterGeneratorManual?code=<key>&email=<email>`
- **Backend Health**: `https://up2d8.azurewebsites.net/api/health`

### Key Azure Resources

- **Function App**: `<your-function-app-name>`
- **Backend API**: `up2d8.azurewebsites.net`
- **Key Vault**: `<your-key-vault-name>`
- **Cosmos DB**: `up2d8` database

### Important Schedules (UTC)

- **08:00** - DailyArticleScraper runs
- **14:00** - NewsletterGenerator runs (9 AM EST)
- **11:00** - CrawlerOrchestrator runs

### Support Files

- **Debugging Guide**: `DEBUG_DAILY_DIGEST.md`
- **Diagnostic Script**: `packages/functions/tests/diagnose_newsletter.py`
- **Test Setup**: `packages/functions/tests/setup_test_data.py`

---

## ✅ Success Criteria

You'll know everything is working when:

1. ✅ Manual trigger returns `"newsletters_sent": 1`
2. ✅ Email arrives in your inbox within 2 minutes
3. ✅ Logs show detailed step-by-step execution
4. ✅ No errors in logs
5. ✅ Automatic trigger runs successfully at 14:00 UTC
6. ✅ Daily emails received at 9 AM EST

---

**Need Help?** Check `DEBUG_DAILY_DIGEST.md` for comprehensive troubleshooting guide.
