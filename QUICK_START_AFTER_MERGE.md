# ⚡ Quick Start - After Merging PR

**Branch**: `claude/debug-daily-digest-emails-01LPni6yub8y6PDjQ9sJ4Udy`

After you merge this PR into main, follow these **3 simple steps** to test your daily digest emails.

---

## 🎯 Your 3-Step Testing Process

### Step 1: Deploy to Azure (2 minutes)

```bash
cd packages/functions
func azure functionapp publish <your-function-app-name>
```

**Wait for**: "Deployment completed successfully"

---

### Step 2: Setup Test Data (1 minute)

```bash
python packages/functions/tests/setup_test_data.py
```

**When prompted**:
- Enter your email address
- Confirm to update settings: `y`

**This will**:
- ✅ Set your topics to: AI, technology, startup, business, innovation
- ✅ Enable email notifications
- ✅ Set frequency to "daily"
- ✅ Create/reset test articles

---

### Step 3: Test It! (2 minutes)

#### 3A: Get Your Function Key

In Azure Portal:
1. Go to Function Apps → [your-function-app]
2. Click "Functions" → "NewsletterGeneratorManual"
3. Click "Function Keys"
4. Copy the "default" key

#### 3B: Trigger the Newsletter

```bash
# Replace:
# - <function-app-name> with your Azure function app name
# - <function-key> with the key from 3A
# - <your-email> with your email address

curl "https://<function-app-name>.azurewebsites.net/api/NewsletterGeneratorManual?code=<function-key>&email=<your-email>"
```

**Example:**
```bash
curl "https://up2d8-functions.azurewebsites.net/api/NewsletterGeneratorManual?code=abc123xyz&email=john@example.com"
```

#### 3C: Check Response

**Success looks like:**
```json
{
  "status": "success",
  "newsletters_sent": 1,
  "users_skipped": 0,
  "errors": 0
}
```

**Check your email** - you should receive a newsletter within 1-2 minutes!

---

## ✅ That's It!

If you received the email, **everything is working!** 🎉

The scheduled newsletter will now run automatically at **9 AM EST (14:00 UTC)** daily.

---

## 🔍 If Something Went Wrong

### Response shows `"newsletters_sent": 0`?

**Check the response details:**
```json
{
  "details": {
    "skipped": [
      {"email": "you@example.com", "reason": "No articles matching topics: []"}
    ]
  }
}
```

**Common fixes:**

1. **"No articles matching topics"**
   ```bash
   # Run setup script again
   python packages/functions/tests/setup_test_data.py
   ```

2. **"No new articles to process"**
   ```javascript
   // In Cosmos DB:
   db.articles.updateMany({}, { $set: { processed: false } })
   ```

3. **"Email notifications disabled"**
   - Check web app: Settings → Notifications → Enable

---

## 📚 Need More Help?

- **Complete Guide**: See `POST_MERGE_SETUP.md`
- **Debugging**: See `DEBUG_DAILY_DIGEST.md`
- **Run Automated Tests**: `python packages/functions/tests/test_newsletter_end_to_end.py`

---

## 🎁 What This PR Gives You

1. **Manual Test Endpoint** - Test anytime without waiting for schedule
2. **Enhanced Logging** - See exactly what's happening in Azure logs
3. **Test Data Setup** - One command to prepare database
4. **Automated Tests** - Validate entire system
5. **Complete Documentation** - Step-by-step guides

---

**Ready to test?** Start with Step 1 above! 🚀
