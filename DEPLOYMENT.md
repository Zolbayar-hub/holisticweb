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

## File Upload Configuration for PythonAnywhere

The home image upload feature requires proper directory permissions on PythonAnywhere:

### After deployment, run this command in a PythonAnywhere console:

```bash
cd /home/yourusername/mysite
python3 fix_upload_permissions.py
```

### Manual permission fix (if needed):

```bash
# Navigate to your app directory
cd /home/yourusername/mysite

# Create upload directories with proper permissions
mkdir -p static/uploads/home
mkdir -p static/uploads/services
mkdir -p static/uploads/about_images

# Set directory permissions
chmod 755 static/uploads
chmod 755 static/uploads/home
chmod 755 static/uploads/services
chmod 755/about_images

# Fix any existing file permissions
find static/uploads -type f -exec chmod 644 {} \;
```

### Troubleshooting File Uploads:

1. **Check the debug endpoint**: Visit `/web_admin/debug/file-system` as admin to see directory status
2. **Check error logs**: In PythonAnywhere Dashboard > Web > Error log
3. **Verify static file mapping**: Ensure `/static/` is mapped to your `static` folder
4. **Test file permissions**: Upload a test image and check if it appears

## Testing the Deployment

After deployment, check the error log in PythonAnywhere to see:
- Database path confirmation
- Any initialization errors
- Email configuration status
- File upload directory creation

The app will print useful debug information on startup to help troubleshoot any issues.

### Common PythonAnywhere Issues:

1. **Upload folder permissions**: Use the fix script above
2. **Static file serving**: Verify static files mapping in web app configuration
3. **File path separators**: Code handles both Windows and Unix paths
4. **Large file uploads**: Default limit is 10MB, adjust if needed
