# Elinity Dashboard

A modern, responsive admin dashboard built with FastAPI, HTML, CSS, and JavaScript.

## Features

- **User Management**: View and manage users
- **Analytics**: Track user engagement and platform performance
- **Responsive Design**: Works on desktop and mobile devices
- **Secure Authentication**: Basic authentication (replace with your preferred auth method in production)
- **Modern UI**: Built with Tailwind CSS for a clean, professional look

## Prerequisites

- Python 3.7+
- PostgreSQL (or your preferred database)
- Node.js and npm (for frontend assets if needed)

## Installation

1. Clone the repository
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required packages:
   ```bash
   pip install -r ../requirements-dashboard.txt
   ```
4. Set up your environment variables in a `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/elinity
   SECRET_KEY=your-secret-key-here
   ```
5. Run the database migrations:
   ```bash
   alembic upgrade head
   ```
6. Start the development server:
   ```bash
   uvicorn app:app --reload
   ```
7. Open your browser and navigate to `http://localhost:8000`

## Default Credentials

- **Username**: admin
- **Password**: admin123

**Note**: Change these credentials in production!

## Project Structure

```
dashboard/
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   │   └── styles.css    # Custom styles
│   └── js/
│       └── main.js      # Main JavaScript file
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── dashboard.html   # Dashboard home
│   ├── users.html       # Users management
│   ├── analytics.html   # Analytics page
│   └── settings.html    # Settings page
├── app.py               # Main FastAPI application
├── auth.py              # Authentication utilities
└── config.py            # Configuration settings
```

## Customization

### Styling

This dashboard uses Tailwind CSS for styling. To customize the styles:

1. Install Tailwind CSS:
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init
   ```
2. Configure `tailwind.config.js` to scan your template files
3. Rebuild the CSS when making changes:
   ```bash
   npx tailwindcss -i ./static/css/input.css -o ./static/css/styles.css --watch
   ```

### Adding New Pages

1. Create a new HTML file in the `templates` directory
2. Extend the base template: `{% extends "base.html" %}`
3. Add your content within the `{% block content %}` tags
4. Add a new route in `app.py` to serve the page

## Security Considerations

- Replace the default credentials with secure ones in production
- Implement proper authentication and authorization
- Use HTTPS in production
- Sanitize all user inputs
- Keep dependencies up to date

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
