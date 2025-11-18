# 🔧 Production Migration Fix

## Problem
Your production API at `https://fastapi.kevinlinportfolio.com` is returning 500 errors because the database migrations haven't been applied yet.

The latest fixes (nullable address columns in orders, etc.) need to be migrated to production.

---

## Solution: SSH into Production and Run Migrations

### Step 1: SSH into your DigitalOcean server
```bash
ssh kevinlin192003@159.89.245.206
```

### Step 2: Navigate to your app directory
```bash
cd /var/www/fastapi-app
```

### Step 3: Activate virtual environment
```bash
source venv/bin/activate
```

### Step 4: Check current migration status
```bash
alembic current
```

This shows which migration is currently applied.

### Step 5: Run migrations
```bash
alembic upgrade head
```

This will apply all pending migrations including:
- Making order address columns nullable
- Any other pending schema changes

### Step 6: Restart the app
```bash
pm2 restart fastapi-app
```

### Step 7: Test the API
```bash
curl https://fastapi.kevinlinportfolio.com/health
```

Should return status "ok"

---

## Alternative: Use the deploy script
```bash
cd /var/www/fastapi-app
source venv/bin/activate
python scripts/deploy.py
pm2 restart fastapi-app
```

---

## Verify It Worked

### Test address creation:
```bash
curl -X POST 'https://fastapi.kevinlinportfolio.com/api/v1/addresses/' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "shipping",
    "first_name": "John",
    "last_name": "Doe",
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "country": "US",
    "phone": "555-1234",
    "is_default": true
  }'
```

Should return 200 with the created address!

---

## Common Issues

### Issue 1: Permission Denied
```bash
sudo chown -R kevinlin192003:kevinlin192003 /var/www/fastapi-app
```

### Issue 2: Alembic can't find config
```bash
# Make sure you're in the app directory
cd /var/www/fastapi-app
ls alembic.ini  # Should exist
```

### Issue 3: Database connection error
```bash
# Check if DATABASE_URL is set
echo $DATABASE_URL

# If not, export it (get from your secrets)
export DATABASE_URL="postgresql://..."
```

---

## After Migration is Applied

Your production API will work with:
- ✅ Order creation without shipping address
- ✅ Address management endpoints
- ✅ Payment intent creation
- ✅ All the fixes you just pushed!

Then you can update your frontend to use the production URL! 🚀
