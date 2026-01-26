# Quick Testing Guide for Celery Email Implementation

## Prerequisites Check

### 1. Redis Installation
```bash
# Check if Redis is installed
redis-cli --version

# If not installed on Windows, use Docker:
docker run -d -p 6379:6379 redis
```

### 2. Python Dependencies
```bash
# Install required packages
pip install celery redis flask-mail
```

---

## Step-by-Step Testing

### Step 1: Start Redis Server
```bash
# Windows (Docker)
docker run -d -p 6379:6379 redis

# Verify Redis is running
redis-cli ping
# Expected output: PONG
```

### Step 2: Start Celery Worker

**Open a NEW terminal/command prompt** and run:

**Windows:**
```bash
# Navigate to project directory
cd f:\Placement_Protal_Application

# Start worker
celery -A celery_worker.celery worker --pool=solo --loglevel=info

# OR use the batch script
start_celery_worker.bat
```

**Linux/Mac:**
```bash
celery -A celery_worker.celery worker --loglevel=info
```

**Expected Output:**
```
-------------- celery@YOUR-PC v5.x.x
---- **** -----
--- * ***  * -- Windows-10.x.x
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         app:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ---- .> task events: OFF
--- ***** -----
 -------------- [queues]
                .> default          exchange=default(direct) key=default

[tasks]
  . app.celery_app.tasks.send_email

[2026-01-25 18:19:25,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2026-01-25 18:19:25,000: INFO/MainProcess] mingle: searching for neighbors
[2026-01-25 18:19:26,000: INFO/MainProcess] mingle: all alone
[2026-01-25 18:19:26,000: INFO/MainProcess] celery@YOUR-PC ready.
```

✅ **Important:** Look for `app.celery_app.tasks.send_email` in the tasks list!

### Step 3: Start Flask Application

**Open ANOTHER terminal/command prompt** and run:

```bash
# Navigate to project directory
cd f:\Placement_Protal_Application

# Start Flask app
python run.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 4: Test User Registration

1. **Open browser** and go to: `http://127.0.0.1:5000/register`

2. **Fill in registration form:**
   - Email: test@example.com
   - Password: Test@1234

3. **Submit the form**

4. **Check Flask terminal** - should see:
   ```
   [INFO] User registered successfully!
   ```

5. **Check Celery worker terminal** - should see:
   ```
   [INFO] Received task: app.celery_app.tasks.send_email[task-id]
   [INFO] Task app.celery_app.tasks.send_email[task-id] succeeded in 0.5s
   [INFO] Email sent successfully to ['test@example.com']
   ```

✅ **Success!** If you see these logs, async email is working!

---

## Troubleshooting

### Issue 1: "Received unregistered task"
**Symptom:**
```
[ERROR] Received unregistered task of type 'app.celery_app.tasks.send_email'
```

**Solution:**
1. Stop Celery worker (Ctrl+C)
2. Restart it:
   ```bash
   celery -A celery_worker.celery worker --pool=solo --loglevel=info
   ```

---

### Issue 2: "Connection refused" to Redis
**Symptom:**
```
[ERROR] Error: Connection refused
```

**Solution:**
1. Check if Redis is running:
   ```bash
   redis-cli ping
   ```
2. If not running, start Redis:
   ```bash
   docker run -d -p 6379:6379 redis
   ```

---

### Issue 3: No task execution
**Symptom:** Registration works but no logs in Celery worker

**Solution:**
1. Check if Celery worker is running
2. Check if task is registered (look for it in worker startup logs)
3. Restart both Flask app and Celery worker

---

### Issue 4: Email not actually sending
**Symptom:** Task succeeds but no email received

**Solution:**
1. Check email configuration in `.env`:
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password  # Not regular password!
   ```
2. For Gmail, create an App Password:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App Passwords
   - Generate new app password
   - Use that in MAIL_PASSWORD

---

## Verification Checklist

- [ ] Redis is running (`redis-cli ping` returns PONG)
- [ ] Celery worker is running and shows `app.celery_app.tasks.send_email` in tasks
- [ ] Flask app is running
- [ ] Registration creates user in database
- [ ] Celery worker logs show task received and succeeded
- [ ] Email credentials are correct in `.env`

---

## Testing Different Scenarios

### Test 1: Student Registration
```
URL: http://127.0.0.1:5000/register
Email: student@test.com
Password: Student@123

Expected: Welcome email sent after 10 seconds
```

### Test 2: Company Registration
```
URL: http://127.0.0.1:5000/register/company
Email: company@test.com
Password: Company@123
Company Name: Test Corp
HR Name: John Doe
HR Email: hr@testcorp.com
HR Contact: 1234567890
Website: https://testcorp.com
Address: 123 Test St
Description: Test company

Expected: Welcome email sent after 10 seconds
```

### Test 3: Password Reset OTP
```
URL: http://127.0.0.1:5000/forgot-password
Email: student@test.com

Expected: OTP email sent after 2 seconds
```

---

## Monitoring Tasks

### Check Active Tasks
```bash
celery -A celery_worker.celery inspect active
```

### Check Registered Tasks
```bash
celery -A celery_worker.celery inspect registered
```

### Purge All Tasks (Clear Queue)
```bash
celery -A celery_worker.celery purge
```

### Install Flower for Web Monitoring
```bash
pip install flower
celery -A celery_worker.celery flower

# Visit: http://localhost:5555
```

---

## Expected Timeline

1. **User clicks Register** → Instant response (0.1s)
2. **User saved to DB** → Instant (0.1s)
3. **Task sent to queue** → Instant (0.01s)
4. **User sees success message** → Instant (total ~0.2s)
5. **[Background] Task waits** → 10 seconds (countdown)
6. **[Background] Email sent** → 1-3 seconds
7. **[Background] Task completes** → Total ~13 seconds

**Key Point:** User doesn't wait for email sending!

---

## Success Indicators

✅ **Registration completes in < 1 second**  
✅ **User redirected to login page immediately**  
✅ **Celery worker logs show task received**  
✅ **Email sent in background**  
✅ **No errors in either terminal**  

---

## Common Mistakes to Avoid

❌ **Don't** forget to start Redis  
❌ **Don't** forget to start Celery worker  
❌ **Don't** use regular Gmail password (use App Password)  
❌ **Don't** restart only Flask (restart Celery too after code changes)  
❌ **Don't** use `--pool=prefork` on Windows (use `--pool=solo`)  

---

## Next Steps After Testing

1. ✅ Verify all email types work (registration, OTP, etc.)
2. ✅ Test error handling (wrong email config)
3. ✅ Test retry mechanism (disconnect Redis temporarily)
4. ✅ Monitor performance under load
5. ✅ Set up production deployment (see CELERY_SETUP.md)

---

**Happy Testing! 🎉**

For detailed documentation, see `CELERY_SETUP.md`  
For implementation review, see `CELERY_REVIEW.md`
