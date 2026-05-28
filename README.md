# Userprofile API

A Django REST API for user profile management with Google OAuth authentication, college email verification, and JWT tokens.

## Features

- User registration and authentication (email/password)
- Google OAuth Sign-In integration
- College email verification with OTP
- JWT token-based authentication
- User profile completion and management
- Custom User model

## Prerequisites

- Python 3.8+
- Django 6.0.3
- Django REST Framework
- PostgreSQL (optional, SQLite for development)

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd userprofile_api
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

Edit `.env` with:
- Your Django SECRET_KEY
- GOOGLE_CLIENT_ID for OAuth
- Email configuration (optional)

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication
- `POST /users/register/` - Register a new user
- `POST /users/login/` - Login and get JWT token
- `POST /users/token/refresh/` - Refresh JWT token
- `POST /users/google/` - Google OAuth Sign-In

### Profile
- `GET /users/profile/` - Get user profile (requires authentication)
- `PATCH /users/profile/complete/` - Complete user profile (requires authentication)
- `POST /users/profile/send-otp/` - Send OTP to college email (requires authentication)
- `POST /users/profile/verify-otp/` - Verify college email with OTP (requires authentication)

## Project Structure

```
userprofile_api/
├── Userprofile/          # Project settings
│   ├── settings.py       # Django settings
│   ├── urls.py           # URL configuration
│   ├── asgi.py           # ASGI config
│   └── wsgi.py           # WSGI config
├── users/                # User app
│   ├── models.py         # User model
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   ├── urls.py           # User URLs
│   ├── admin.py          # Django admin
│   └── migrations/       # Database migrations
├── manage.py             # Django CLI
└── db.sqlite3            # SQLite database (dev only)
```

## Security Notes

- Never commit `.env` or `SECRET_KEY` to version control
- Use environment variables for sensitive data
- Change the default SECRET_KEY in production
- Set `DEBUG = False` in production
- Use HTTPS in production
- Keep dependencies updated

## Development Tips

- The OTP email verification uses console backend for development (emails printed to console)
- For Gmail SMTP, enable "Less Secure Apps" or use an App Password
- Google OAuth requires valid GOOGLE_CLIENT_ID

## Database

The project uses SQLite for development. To switch to PostgreSQL:

1. Install psycopg2: `pip install psycopg2-binary`
2. Update `DATABASES` in `settings.py`
3. Run migrations

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

MIT License
