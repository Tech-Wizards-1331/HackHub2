# Concerns

## Technical Debt
- **Empty Apps**: Many apps (`judge`, `organizer`, `participant`, `volunteers`) have empty models and views that only render placeholders. This must be filled with real business logic.
- **CDN Dependency**: Tailwind CSS is loaded via CDN; it should be integrated into a build process for production.
- **Business Logic Displacement**: The user mentioned "tasks and groups" logic which is not present in the current codebase but is vital for the platform's utility.

## Deployment & Production
- **SQLite Database**: Suitable for development but must be migrated to PostgreSQL/MySQL for production-grade hackathons.
- **Debug Mode**: `DEBUG = True` in `settings.py`.

## Migration Risks
- **Frontend/Backend Coupling**: Currently, logic is heavily tied to Template context. Moving to JSON responses requires a complete rewrite of how data is injected into the UI (moving from `{{ variable }}` to dynamic JS rendering).
- **Authentication Shift**: Transitioning from session-based (SSR) to JWT/Token-based authentication while maintaining the same OAuth flow with `allauth` will require careful coordination.
- **Real-time Requirements**: The user mentioned WebSockets/Notifications. Integrating Django Channels into the current structure will add significant complexity to the deployment stack (Redis, Daphne/Uvicorn).
