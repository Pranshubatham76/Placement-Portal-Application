# Placement Portal Application

A comprehensive, production-ready Placement Portal built with **Flask**, **SQLAlchemy**, and **Celery**. This application streamlines the recruitment process for students, companies, and administrators.

## 🚀 Features

### 👨‍🎓 Student Module
- Profile management and resume upload.
- Browse and apply for upcoming placement drives.
- Track application status.
- Dashboard with personalized notifications.

### 🏢 Company Module
- Create and manage job/placement drives.
- View and filter student applications.
- Shortlist candidates for interviews.
- Communication with selected candidates.

### 🛡️ Admin Module
- Overall system management.
- User verification (Students & Companies).
- Advanced reporting and analytics.
- Email notifications management.

### ⚙️ Core Functionalities
- **Secure Authentication**: RBAC (Role-Based Access Control) with Flask-Login and Bcrypt.
- **Background Tasks**: Asynchronous email delivery and scheduled tasks using Celery and Redis.
- **Database**: Robust data modeling with SQLAlchemy and SQLite (for development).
- **Responsive UI**: Modern templates using Jinja2 and custom CSS.

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask
- **Database**: SQLite (SQLAlchemy ORM)
- **Task Queue**: Celery with Redis Broker
- **Security**: Bcrypt for password hashing, Flask-Login for session management
- **Email**: Flask-Mail for automated notifications
- **Environment**: python-dotenv for configuration management

## 📂 Project Structure

```text
Placement_Protal_Application/
├── app/                    # Core application logic
│   ├── models/             # Database schemas
│   ├── routes/             # Blueprints for modules
│   ├── services/           # Business logic
│   ├── templates/          # Jinja2 HTML templates
│   └── static/             # CSS, JS, and Images
├── celery_worker.py        # Celery entry point
├── config.py               # Application configuration
├── init_db.py              # Database initialization script
├── run.py                  # Main application entry point
└── requirement.txt         # Project dependencies
```

## 📜 Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Placement_Protal_Application
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirement.txt
   ```

4. **Initialize the Database**:
   ```bash
   python init_db.py
   ```

5. **Start Redis server** (required for Celery):
   ```bash
   redis-server
   ```

6. **Run Celery worker**:
   ```bash
   celery -A celery_worker.celery worker --loglevel=info
   ```

7. **Run the application**:
   ```bash
   python run.py
   ```

## 📧 Environment Variables
Create a `.env` file in the root directory and add the following:
```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///placement_portal.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

---
Generated with ❤️ by Antigravity.
