# Testing Instructions for MongoDB Migration

## Prerequisites

Before testing, ensure you have:
- Docker and Docker Compose installed
- Python 3.11+ installed
- Git repository cloned

## Step 1: Clean Previous Setup

```bash
# Stop all running containers
docker-compose down -v

# Remove old volumes (CAUTION: This deletes all data!)
docker volume prune -f

# Clear Python cache
find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

## Step 2: Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Create/activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
. venv/bin/activate  # Alternative syntax
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Start MongoDB

```bash
# From project root
docker-compose up -d mongodb

# Verify MongoDB is running
docker-compose ps

# Expected output:
# NAME                 IMAGE      STATUS         PORTS
# up2d8-mongodb        mongo:7    Up X seconds   0.0.0.0:27017->27017/tcp
```

## Step 4: Verify MongoDB Connection

```bash
# Test MongoDB connection
docker exec -it up2d8-mongodb mongosh --eval "db.adminCommand('ping')"

# Expected output:
# { ok: 1 }

# List databases
docker exec -it up2d8-mongodb mongosh --eval "show dbs"
```

## Step 5: Initialize Database and Indexes

```bash
# From backend directory (with venv activated)
cd backend
export MONGODB_URL="mongodb://localhost:27017/"
export COSMOS_DB_CONNECTION_STRING="mongodb://localhost:27017/"
export COSMOS_DB_NAME="up2d8"

python3 -c "
from api.db.session import get_database
from api.db.cosmos_db import create_indexes

print('Connecting to MongoDB...')
db = get_database()
print(f'Connected to database: {db.name}')

print('Creating indexes...')
create_indexes()
print('Indexes created successfully!')
"
```

## Step 6: Test Authentication System

### 6a. Start the Backend API

```bash
# Option 1: Using Docker (Recommended)
docker-compose up -d api

# View logs
docker-compose logs -f api

# Option 2: Local development
cd backend
source venv/bin/activate
export MONGODB_URL="mongodb://localhost:27017/"
export COSMOS_DB_CONNECTION_STRING="mongodb://localhost:27017/"
export COSMOS_DB_NAME="up2d8"
export JWT_SECRET_KEY="dev_secret_key_change_in_production_12345678901234567890"
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="1440"
export REFRESH_TOKEN_EXPIRE_DAYS="7"

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6b. Test API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "UP2D8 API",
  "version": "0.1.0",
  "environment": "development"
}
```

**API Documentation:**
Open browser to: http://localhost:8000/docs

**User Signup:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'
```

Expected response (save the `access_token`):
```json
{
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "full_name": "Test User",
    "tier": "free",
    "status": "active",
    "onboarding_completed": false
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**User Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

**Get Current User (Protected Route):**
```bash
# Replace YOUR_ACCESS_TOKEN with actual token from signup/login
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected response:
```json
{
  "id": "uuid-here",
  "email": "test@example.com",
  "full_name": "Test User",
  "tier": "free",
  "status": "active",
  "onboarding_completed": false,
  "created_at": "2025-10-30T...",
  "last_login_at": "2025-10-30T..."
}
```

## Step 7: Test Preferences API

**Get Preferences:**
```bash
curl -X GET http://localhost:8000/api/v1/preferences/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected: Default preferences created automatically

**Update Preferences:**
```bash
curl -X PUT http://localhost:8000/api/v1/preferences/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subscribed_companies": ["OpenAI", "Anthropic"],
    "subscribed_industries": ["AI", "Machine Learning"],
    "digest_frequency": "daily",
    "article_count_per_digest": 10
  }'
```

## Step 8: Verify Data in MongoDB

```bash
# Connect to MongoDB shell
docker exec -it up2d8-mongodb mongosh

# In mongosh:
use up2d8

# List collections
show collections

# Count users
db.users.countDocuments()

# View a user
db.users.findOne()

# View user preferences
db.user_preferences.findOne()

# Exit mongosh
exit
```

## Step 9: Start Full Stack (Optional)

```bash
# Start all services (MongoDB, Backend, Frontend, Workers)
docker-compose up -d

# View logs
docker-compose logs -f

# Access services:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Frontend: http://localhost:5173
# - Mongo Express (with --profile tools): http://localhost:8081
```

## Step 10: Test with Mongo Express UI (Optional)

```bash
# Start with tools profile
docker-compose --profile tools up -d

# Open browser to: http://localhost:8081
# Username: admin
# Password: admin

# Browse collections and data visually
```

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: No module named 'pymongo'"

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 2: "MONGODB_URL or COSMOS_DB_CONNECTION_STRING environment variable is not set"

**Solution:**
```bash
# Set environment variables
export MONGODB_URL="mongodb://localhost:27017/"
export COSMOS_DB_CONNECTION_STRING="mongodb://localhost:27017/"
export COSMOS_DB_NAME="up2d8"
```

### Issue 3: Connection refused to MongoDB

**Solution:**
```bash
# Check if MongoDB is running
docker-compose ps

# Restart MongoDB if needed
docker-compose up -d mongodb

# Check logs
docker-compose logs mongodb
```

### Issue 4: "JWT_SECRET_KEY environment variable must be set"

**Solution:**
```bash
export JWT_SECRET_KEY="dev_secret_key_change_in_production_12345678901234567890"
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="1440"
export REFRESH_TOKEN_EXPIRE_DAYS="7"
```

### Issue 5: Import errors for routers (feedback, digests, analytics, scraping)

**Known Issue:** Some routers still use SQLAlchemy and haven't been fully migrated yet.

**Solution:** These routers will need to be updated following the patterns in:
- `/Users/davidmorgan/Documents/Repositories/up2d8/MONGODB_MIGRATION_SUMMARY.md`
- `/Users/davidmorgan/Documents/Repositories/up2d8/backend/api/routers/preferences.py` (reference implementation)

**Endpoints that work:**
- ✅ `/health` - Health check
- ✅ `/api/v1/auth/signup` - User registration
- ✅ `/api/v1/auth/login` - User login
- ✅ `/api/v1/auth/refresh` - Token refresh
- ✅ `/api/v1/auth/me` - Get current user
- ✅ `/api/v1/preferences/me` - Get preferences (partially working)

**Endpoints that need migration:**
- ⚠️ `/api/v1/preferences/me` (PUT) - Update preferences
- ⚠️ `/api/v1/feedback/*` - All feedback endpoints
- ⚠️ `/api/v1/digests/*` - All digest endpoints
- ⚠️ `/api/v1/analytics/*` - All analytics endpoints
- ⚠️ `/api/v1/scraping/*` - All scraping endpoints
- ⚠️ `/api/v1/chat/*` - All chat endpoints

## Success Criteria

✅ MongoDB container starts successfully
✅ Backend API starts without errors
✅ User can signup with email/password
✅ User can login and receive JWT tokens
✅ Protected routes work with JWT authentication
✅ User preferences can be created and retrieved
✅ Data persists in MongoDB
✅ Collections and indexes are created

## Next Steps After Testing

1. **Complete Router Migrations:**
   - Use `MONGODB_MIGRATION_SUMMARY.md` as a guide
   - Follow patterns from `auth.py` and `preferences.py`
   - Update one router at a time
   - Test each router after migration

2. **Update Service Layer:**
   - Migrate memory services (short_term, digest_context, long_term)
   - Update analytics_tracker
   - Update relevance_scorer

3. **Update Celery Configuration:**
   - Configure Celery to use MongoDB or memory broker
   - Test background tasks

4. **Update Tests:**
   - Rewrite unit tests to use MongoDB
   - Update integration tests
   - Add new MongoDB-specific tests

## Rollback Plan (If Needed)

If you need to rollback to PostgreSQL:

```bash
# Restore old models file
cd backend/api/db
mv models.py models_mongodb.py
mv models_sqlalchemy_backup.py models.py

# Restore old session file (you'll need to recreate it or use git)
git restore session.py

# Restore old docker-compose.yml
git restore ../../docker-compose.yml

# Restore old requirements.txt
git restore ../requirements.txt

# Restart with PostgreSQL
docker-compose down -v
docker-compose up -d
```

---

**Last Updated:** 2025-10-30
**Migration Status:** Core infrastructure complete, authentication working, some routers pending
