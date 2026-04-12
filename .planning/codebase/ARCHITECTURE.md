# Architecture

## System Overview
Syntra follows a Monolithic architecture using the Django MVC (Model-View-Template) pattern.

## Design Patterns
- **Custom User Implementation**: Uses an `AbstractUser` extension in the `accounts` app to handle multiple roles and profile completion states.
- **Role-Based Access Control (RBAC)**: Implemented via custom decorators (`@role_required`) and role checks in views/middleware.
- **Middleware Redirection**: `UserFlowMiddleware` enforces a strict onboarding flow (Signup -> Role Selection -> Profile Completion -> Dashboard).

## Component Boundaries
| App | Responsibility |
|-----|----------------|
| **Accounts** | Identity, authentication, role management, and onboarding flows. |
| **Core** | Main landing pages and shared site-wide functionality. |
| **Super Admin** | Administrative control layer for the entire platform. |
| **Organizer** | Hackathon event management logic. |
| **Participant** | Hacker-facing features (Project submission, team formation). |
| **Judge** | Project evaluation and scoring logic. |
| **Volunteers** | Operational support features. |

## Data Flow
1. **Request**: HTTP request arrives from the browser.
2. **Middleware**: `UserFlowMiddleware` checks if the user needs to complete their profile or select a role.
3. **Routing**: `ROOT_URLCONF` (`syntra.urls`) delegates to app-specific URL configurations.
4. **Logic**: Views process data using Forms and Models.
5. **Response**: Server renders HTML templates using the Django Template Engine.
