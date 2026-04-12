# Stack

## Overview
Syntra is a Django-based hackathon management platform currently utilizing a traditional server-side rendering (SSR) architecture with Django Templates and Tailwind CSS.

## Core Stacks
| Layer | Technology | Details |
|-------|------------|---------|
| **Backend** | Django 6.0.3 | High-level Python Web framework. |
| **Language** | Python 3.13 | (Inferred from .venv/pycache info) |
| **Database** | SQLite | Development database; defined in `settings.py`. |
| **Auth** | Django Allauth | Handles Registration, Authentication, and Social OAuth. |
| **Styling** | Tailwind CSS | Utility-first CSS framework via CDN in templates. |
| **Frontend** | Django Templates | Server-side rendering with block/include logic. |

## Key Libraries
- `django-allauth`: Social authentication (Google, GitHub providers configured).
- `PyJWT`: JSON Web Token implementation (ready for API conversion).
- `requests`: HTTP library for external API integrations.
- `cryptography`: Security utilities.

## Infrastructure
- Local development environment.
- Path handling using `pathlib.Path`.
- Environment variables managed via `.env` and `python-dotenv`.
