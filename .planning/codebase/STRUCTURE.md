# Structure

## Directory Layout
```text
syntra/                 # Root Django Project Directory
├── accounts/           # User authentication and profiles
│   ├── forms.py        # Signup, Login, Profile forms
│   ├── models.py       # Custom User model
│   └── views.py        # Auth logic and onboarding flow
├── core/               # Landing pages and base structure
│   └── templates/      # Main landing page (home.html)
├── judge/              # Judging logic (Basic placeholders)
├── organizer/          # Event management logic (Basic placeholders)
├── participant/        # Hacker dashboards (Basic placeholders)
├── super_admin/        # Management dashboard (Basic placeholders)
├── syntra/             # Project configuration (settings, urls, wsgi)
├── templates/          # Global templates directory
├── static/             # Global static assets (CSS, JS, Images)
├── manage.py           # Django CLI
├── requirements.txt    # Backend dependencies
└── .env                # Environment configuration
```

## Module Analysis
- **`accounts`**: The most developed module, containing core models and complex redirect logic.
- **Role Apps (`judge`, `organizer`, etc.)**: Minimal implementations currently, consisting mostly of a single dashboard view and placeholder templates.
- **Templates**: Centralized in `templates/` and app-specific `templates/` folders.
