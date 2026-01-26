# Celery Async Email Setup Guide

## Overview
This application uses **Celery** with **Redis** as a message broker to send emails asynchronously. This prevents blocking the main application thread while sending emails.

## Architecture

### Components:
1. **Flask Application** - Main web application
2. **Celery Worker** - Background task processor
3. **Redis** - Message broker and result backend
4. **Flask-Mail** - Email sending library

### Flow:
```
User Registration → Flask App → Celery Task Queue (Redis) → Celery Worker → Send Email
```

## Prerequisites

### 1. Install Redis
**Windows:**
- Download Redis from: https://github.com/microsoftarchive/redis/releases
- Or use Docker: `docker run -d -p 6379:6379 redis`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Mac
brew install redis
```

### 2. Start Redis Server
```bash
# Windows (if installed directly)
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis

# Linux
sudo systemctl start redis

# Mac
brew services start redis
```

### 3. Verify Redis is Running
```bash
redis-cli ping
# Should return: PONG
```

## Running the Application

### Terminal 1: Start Flask Application
```bash
python run.py
```

### Terminal 2: Start Celery Worker
**Linux/Mac:**
```bash
celery -A celery_worker.celery worker --loglevel=info
```

**Windows:**
```bash
celery -A celery_worker.celery worker --pool=solo --loglevel=info
```

### Terminal 3 (Optional): Start Celery Beat (for periodic tasks)
```bash
celery -A celery_worker.celery beat --loglevel=info
```

## Configuration

### Environment Variables (.env)
```env
# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TIMEZONE=Asia/Kolkata

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Task Configuration

### Current Tasks:
1. **send_email** - Sends emails asynchronously
   - Location: `app/celery_app/tasks.py`
   - Task name: `app.celery_app.tasks.send_email`

### Task Options:
- **countdown**: Delay in seconds before executing (currently 10s)
- **retry**: Enable automatic retries on failure
- **retry_policy**: Configure retry behavior
  - `max_retries`: Maximum number of retry attempts (3)
  - `interval_start`: Initial retry delay (0s)
  - `interval_step`: Increment for each retry (0.2s)
  - `interval_max`: Maximum retry delay (0.2s)
- **queue**: Task queue name (default)

## Usage Examples

### Sending an Email (Current Implementation)
```python
from flask import current_app

celery_app = current_app.extensions.get("celery")
if celery_app:
    celery_app.send_task(
        'app.celery_app.tasks.send_email',
        args=[
            "Subject Line",
            ["recipient@example.com"],
            "sender@example.com",
            "Email body content"
        ],
        countdown=10,
        retry=True,
        retry_policy={
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.2,
        },
        queue='default',
    )
```

### Creating a New Task
1. Add task function to `app/celery_app/tasks.py`:
```python
def my_new_task(arg1, arg2):
    """
    Description of what this task does
    """
    # Task logic here
    return result
```

2. Register the task in `app/celery_app/__init__.py`:
```python
celery_app.task(tasks.my_new_task, name='app.celery_app.tasks.my_new_task')
```

3. Call the task:
```python
celery_app.send_task('app.celery_app.tasks.my_new_task', args=[arg1, arg2])
```

## Monitoring

### Check Task Status
```python
# Get task result
result = celery_app.AsyncResult(task_id)
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
print(result.result)  # Task return value
```

### Celery Flower (Web-based monitoring)
```bash
pip install flower
celery -A celery_worker.celery flower
# Visit: http://localhost:5555
```

## Troubleshooting

### Issue: "Received unregistered task"
**Solution:** Make sure:
1. Task is properly registered in `__init__.py`
2. Celery worker is restarted after code changes
3. Task name matches exactly

### Issue: "Connection refused to Redis"
**Solution:**
1. Check if Redis is running: `redis-cli ping`
2. Verify CELERY_BROKER_URL in config
3. Check firewall settings

### Issue: "Mail sending failed"
**Solution:**
1. Verify email credentials in .env
2. For Gmail, use App Password (not regular password)
3. Check MAIL_USE_TLS and MAIL_PORT settings

### Issue: Tasks not executing
**Solution:**
1. Restart Celery worker
2. Check worker logs for errors
3. Verify task is being sent: check Flask logs

## Production Deployment

### Using Supervisor (Linux)
Create `/etc/supervisor/conf.d/celery.conf`:
```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A celery_worker.celery worker --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/worker.err.log
stdout_logfile=/var/log/celery/worker.out.log
```

### Using systemd (Linux)
Create `/etc/systemd/system/celery.service`:
```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A celery_worker.celery worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

### Docker Compose
```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  web:
    build: .
    command: python run.py
    depends_on:
      - redis
  
  celery:
    build: .
    command: celery -A celery_worker.celery worker --loglevel=info
    depends_on:
      - redis
```

## Best Practices

1. **Always handle exceptions** in tasks to prevent worker crashes
2. **Use retry policies** for network-dependent tasks (like email)
3. **Set appropriate timeouts** to prevent hanging tasks
4. **Monitor task queues** to prevent backlog
5. **Use different queues** for different priority tasks
6. **Log task execution** for debugging
7. **Test tasks independently** before integration

## Current Implementation Status

✅ **Completed:**
- Celery configuration with Flask
- Redis integration
- Email task implementation
- Retry policy configuration
- Error handling and logging
- Task registration and autodiscovery

✅ **Fixed Issues:**
1. Missing `mail` import in tasks.py
2. Incorrect import path in auth_service.py
3. Celery initialization issues
4. Task registration and autodiscovery
5. Flask app context handling

## Next Steps (Optional Enhancements)

1. **Add Celery Beat** for periodic tasks (e.g., cleanup, reminders)
2. **Implement task result tracking** for user feedback
3. **Add email templates** with HTML support
4. **Create admin dashboard** to monitor tasks
5. **Add task prioritization** with multiple queues
6. **Implement rate limiting** for email sending
7. **Add email queue management** (pause/resume)

## References

- [Celery Documentation](https://docs.celeryproject.org/)
- [Flask-Celery Integration](https://flask.palletsprojects.com/en/2.3.x/patterns/celery/)
- [Redis Documentation](https://redis.io/documentation)
- [Flask-Mail Documentation](https://pythonhosted.org/Flask-Mail/)
