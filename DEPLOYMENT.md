# Deployment Guide for PythonAnywhere

## Environment Variables Setup

Since PythonAnywhere doesn't automatically load `.env` files, you need to set environment variables manually in your web app configuration.

### Steps for PythonAnywhere:

1. **Go to your PythonAnywhere Dashboard**
2. **Click on "Web" tab**
3. **Click on your web app**
4. **Scroll down to "Environment variables" section**
5. **Add the following variables:**

```
SECRET_KEY=your-very-secret-key-here
FLASK_DEBUG=False
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
SESSION_COOKIE_SECURE=True
```

## Database Location

The application is now configured to:
- Create the `instance` folder automatically if it doesn't exist
- Store the SQLite database (`data.sqlite`) inside the `instance` folder
- Print the database path on startup for debugging

## File Structure After Deployment

```
/home/yourusername/mysite/
├── flask_app.py
├── requirements.txt
├── instance/
│   └── data.sqlite  (created automatically)
├── db/
├── routes/
├── templates/
└── static/
```

## Important Notes

1. **Environment Variables**: Always use environment variables for sensitive information like secret keys and email passwords
2. **Database**: The SQLite database will be created in the `instance` folder automatically
3. **Debug Mode**: Set `FLASK_DEBUG=False` in production
4. **Email**: Use app-specific passwords for Gmail (not your regular password)
5. **HTTPS**: Set `SESSION_COOKIE_SECURE=True` if using HTTPS

## Testing the Deployment

After deployment, check the error log in PythonAnywhere to see:
- Database path confirmation
- Any initialization errors
- Email configuration status

The app will print useful debug information on startup to help troubleshoot any issues.
