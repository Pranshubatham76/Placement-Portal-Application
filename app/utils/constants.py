"""Application constants and enumerations"""

# User Roles
ROLE_ADMIN = 'admin'
ROLE_COMPANY = 'company'
ROLE_STUDENT = 'student'

VALID_ROLES = [ROLE_ADMIN, ROLE_COMPANY, ROLE_STUDENT]

# Approval Statuses
APPROVAL_PENDING = 'pending'
APPROVAL_APPROVED = 'approved'
APPROVAL_REJECTED = 'rejected'

APPROVAL_STATUSES = [APPROVAL_PENDING, APPROVAL_APPROVED, APPROVAL_REJECTED]

# Application Statuses
APP_STATUS_APPLIED = 'applied'
APP_STATUS_SHORTLISTED = 'shortlisted'
APP_STATUS_SELECTED = 'selected'
APP_STATUS_REJECTED = 'rejected'

APPLICATION_STATUSES = [
    APP_STATUS_APPLIED,
    APP_STATUS_SHORTLISTED,
    APP_STATUS_SELECTED,
    APP_STATUS_REJECTED
]

# Placement Drive Statuses
DRIVE_STATUS_PENDING = 'pending'
DRIVE_STATUS_APPROVED = 'approved'
DRIVE_STATUS_REJECTED = 'rejected'
DRIVE_STATUS_ACTIVE = 'active'
DRIVE_STATUS_CLOSED = 'closed'

DRIVE_STATUSES = [
    DRIVE_STATUS_PENDING,
    DRIVE_STATUS_APPROVED,
    DRIVE_STATUS_REJECTED,
    DRIVE_STATUS_ACTIVE,
    DRIVE_STATUS_CLOSED
]

# Job Types
JOB_TYPE_FULL_TIME = 'full-time'
JOB_TYPE_INTERNSHIP = 'internship'

JOB_TYPES = [JOB_TYPE_FULL_TIME, JOB_TYPE_INTERNSHIP]

# Academic Branches
BRANCH_CSE = 'Computer Science'
BRANCH_IT = 'Information Technology'
BRANCH_ECE = 'Electronics and Communication'
BRANCH_EEE = 'Electrical and Electronics'
BRANCH_MECH = 'Mechanical'
BRANCH_CIVIL = 'Civil'
BRANCH_CHEM = 'Chemical'
BRANCH_OTHER = 'Other'

BRANCHES = [
    BRANCH_CSE,
    BRANCH_IT,
    BRANCH_ECE,
    BRANCH_EEE,
    BRANCH_MECH,
    BRANCH_CIVIL,
    BRANCH_CHEM,
    BRANCH_OTHER
]

# File Upload
ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_RESUME_SIZE_MB = 5
MAX_RESUME_SIZE_BYTES = MAX_RESUME_SIZE_MB * 1024 * 1024

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Flash Message Categories
FLASH_SUCCESS = 'success'
FLASH_INFO = 'info'
FLASH_WARNING = 'warning'
FLASH_DANGER = 'danger'

# Date Formats
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DISPLAY_DATE_FORMAT = '%d %b %Y'
DISPLAY_DATETIME_FORMAT = '%d %b %Y, %I:%M %p'
