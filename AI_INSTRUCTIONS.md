# AI Assistant Instructions
## Serenity Wellness Studio Flask Project

### 🏗️ Database Development Rules

#### Rule 1: Always Check db/models.py
When creating any file or function related to database operations:
- **MUST** first review `db/models.py` to understand existing models and schema
- Ensure consistency with existing database structure
- Follow established naming conventions and relationships
- Verify model fields before creating queries or migrations
- Check existing relationships (User, Service, Booking, SiteSettings, etc.)

#### Rule 1.1: Database Consistency
- Use existing model imports: `from db.models import User, Service, Booking, SiteSettings`
- Follow SQLAlchemy patterns established in the project
- Maintain referential integrity with foreign keys
- Use established field types and constraints

### 📚 Documentation Standards

#### Rule 2: Documentation Limits
- **Maximum length**: 100 lines
- **Style**: Concise and clear
- **Location**: All documentation files MUST be created in `documentation/` folder
- **Focus**: Essential information only
- **Format**: Markdown (.md) files preferred

#### Rule 2.1: Documentation Structure
```
documentation/
├── api/          # API documentation
├── setup/        # Installation and setup guides
├── features/     # Feature documentation
└── troubleshoot/ # Common issues and solutions
```

### 🧪 Testing Standards

#### Rule 3: Test File Organization
- All test files MUST be created under `test/` folder
- Follow naming convention: `test_<module_name>.py`
- Maintain organized test structure within test directory
- Use pytest framework for consistency

#### Rule 3.1: Test Structure
```
test/
├── test_auth.py      # Authentication tests
├── test_booking.py   # Booking system tests
├── test_admin.py     # Admin panel tests
└── test_api.py       # API endpoint tests
```

### 🌐 Flask Endpoint Structure

#### Rule 4: Organized Template and Static Files
When creating a new endpoint in the Flask project:
- **MUST** create a separate folder in `templates/` using the endpoint name
- **MUST** create a separate folder in `static/` using the same endpoint name
- Place all HTML templates for the endpoint in `templates/<endpoint_name>/`
- Place all CSS, JavaScript, and other static assets in `static/<endpoint_name>/`
- This ensures clear organization and prevents file conflicts

#### Rule 4.1: File Organization Example
```
For endpoint 'wellness':
templates/wellness/
├── index.html
├── services.html
└── booking.html

static/wellness/
├── wellness.css
├── wellness.js
└── images/
```

### 📱 Mobile-First Development

#### Rule 5: Mobile Responsiveness
- **ALWAYS** implement mobile-first design
- Include viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- Use CSS media queries for responsive breakpoints:
  - Mobile: ≤480px
  - Tablet: ≤768px
  - Desktop: >768px
- Test touch interactions and swipe gestures

#### Rule 5.1: Mobile CSS Structure
```css
/* Mobile First (base styles) */
.element { /* mobile styles */ }

/* Tablet */
@media (min-width: 481px) { /* tablet styles */ }

/* Desktop */
@media (min-width: 769px) { /* desktop styles */ }
```

### 🚀 JavaScript Best Practices

#### Rule 6: JavaScript Organization
- Use ES6+ features and modern syntax
- Implement proper error handling with try-catch blocks
- Add null checks for DOM elements before manipulation
- Use event delegation for dynamic content
- Implement touch/swipe support for mobile devices

#### Rule 6.1: JavaScript Safety Pattern
```javascript
// Always check if elements exist
const element = document.getElementById('myElement');
if (element) {
    // Safe to use element
    element.addEventListener('click', handleClick);
}
```

### 🎨 CSS and Styling Guidelines

#### Rule 7: CSS Organization
- Use BEM methodology for class naming
- Implement CSS custom properties (variables) for consistency
- Follow mobile-first responsive design principles
- Use meaningful class names that describe purpose, not appearance

#### Rule 7.1: CSS File Structure
```css
/* === GLOBAL === */
/* Reset and base styles */

/* === COMPONENTS === */
/* Reusable component styles */

/* === UTILITIES === */
/* Helper and utility classes */

/* === RESPONSIVE === */
/* Media queries */
```

### 🔧 Flask Application Rules

#### Rule 8: Route Organization
- Group related routes in blueprints
- Use descriptive route names
- Implement proper error handling
- Follow RESTful conventions where applicable

#### Rule 8.1: Blueprint Structure
```python
# routes/wellness.py
from flask import Blueprint

wellness_bp = Blueprint('wellness', __name__, url_prefix='/wellness')

@wellness_bp.route('/')
def index():
    return render_template('wellness/index.html')
```

### 🛡️ Security Best Practices

#### Rule 9: Security Implementation
- Always validate and sanitize user input
- Use CSRF protection on forms
- Implement proper authentication checks
- Follow secure coding practices for file uploads

#### Rule 9.1: Form Security
```python
# Always use CSRF tokens in forms
{% csrf_token %}

# Validate file uploads
if file and allowed_file(file.filename):
    # Process file safely
```

### 🎯 Performance Optimization

#### Rule 10: Performance Guidelines
- Optimize images for web (WebP format preferred)
- Minimize JavaScript and CSS files for production
- Use lazy loading for images when appropriate
- Implement efficient database queries

### 🔄 Version Control

#### Rule 11: Git Best Practices
- Make atomic commits with clear messages
- Never commit sensitive data (credentials, keys)
- Use `.gitignore` for environment-specific files
- Keep commit messages descriptive and concise

### 📋 Code Review Checklist

#### Rule 12: Pre-Deployment Checks
- [ ] Mobile responsiveness verified
- [ ] Database models consistency checked
- [ ] JavaScript null safety implemented
- [ ] CSS follows mobile-first approach
- [ ] Documentation updated (if applicable)
- [ ] Tests written (if new functionality)
- [ ] Security considerations addressed
- [ ] Performance implications considered

### 🎨 Design System

#### Rule 13: Visual Consistency
- Use established color palette and typography
- Follow existing component patterns
- Maintain consistent spacing and layout
- Ensure accessibility standards (WCAG compliance)

### 📧 Error Handling

#### Rule 14: Error Management
- Implement graceful error handling
- Provide user-friendly error messages
- Log errors appropriately for debugging
- Use try-catch blocks in JavaScript
- Handle database exceptions in Python

### 🌟 Wellness Studio Specific

#### Rule 15: Brand Consistency
- Maintain wellness/healing theme in all UI elements
- Use calming color schemes (earth tones, soft colors)
- Implement smooth animations and transitions
- Focus on user experience and accessibility
- Ensure content is appropriate for wellness/therapy context

---

## Quick Reference Commands

### Database
```bash
# Check models
cat db/models.py

# Run migrations
python migrate_db.py
```

### Testing
```bash
# Run tests
pytest test/

# Run specific test
pytest test/test_booking.py
```

### Development
```bash
# Start development server
python start_app.py

# Check JavaScript syntax
node -c static/filename.js
```

### File Organization
```
project/
├── db/models.py          # Database models
├── routes/               # Flask blueprints
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── test/                 # Test files
├── documentation/        # Documentation
└── AI_INSTRUCTIONS.md    # This file
```

**Remember**: Always prioritize mobile functionality, security, and user experience in the wellness/therapy context.
