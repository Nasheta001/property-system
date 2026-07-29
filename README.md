# Property System

A production-grade, multi-tenant property management SaaS platform.

## Stack

| Layer      | Technology                                                            |
| ---------- | ---------------------------------------------------------------------- |
| Frontend   | Angular 20 (standalone, signals), Angular Material, Tailwind CSS, SCSS |
| Backend    | Django 5, Django REST Framework, SimpleJWT                             |
| Database   | PostgreSQL 16                                                          |
| Cache/Broker | Redis 7                                                               |
| Async jobs | Celery (worker + beat)                                                 |
| Proxy      | Nginx                                                                   |
| Packaging  | Docker / Docker Compose                                                |

## Architecture

```
Platform Owner
  └─ Organization (tenant root)
       └─ Property
            └─ Building
                 └─ Floor
                      └─ Unit
```

Every domain model below `Organization` is tenant-scoped: rows carry an
`organization` foreign key, every queryset is filtered by the caller's
active organization (resolved from the `X-Organization-ID` header via
`CurrentOrganizationMiddleware`), and object-level checks guarantee one
tenant can never read or write another tenant's data.

Backend apps follow a clean separation:

- `apps.core` — base models (UUID PK, soft delete, audit fields, timestamps),
  shared permissions, pagination, exception handling, health checks.
- `apps.users` — authentication (JWT), user profile.
- `apps.organizations` — tenants and memberships/roles.
- `apps.properties` — the property/building/floor/unit hierarchy.

Frontend follows a feature-based layout:

```
frontend/src/app/
  core/       # services, guards, interceptors, models — no UI
  shared/     # layout shells (public/dashboard) and reusable UI components
  features/   # routed pages: landing, auth, dashboard
```

## Getting started

### Prerequisites

- Docker and Docker Compose

### Run everything

```bash
cp .env.example .env
docker compose up --build
```

This starts: PostgreSQL, Redis, the Django API + admin, a Celery worker,
Celery beat, the Angular dev server, and an Nginx reverse proxy in front of
all of it.

| URL                          | What                                      |
| ----------------------------- | ------------------------------------------ |
| http://localhost              | The app (proxied: `/` → Angular, `/api` and `/admin` → Django) |
| http://localhost/admin/       | Django admin                              |
| http://localhost/api/v1/docs/ | OpenAPI (Swagger) docs                    |
| http://localhost/health/      | Liveness/readiness probe                  |

### Seed demo data

```bash
docker compose exec backend python manage.py seed_demo_data
```

Creates a demo organization ("Green Holdings") with two buildings, three
floors each, and a handful of units, plus two logins:

- `owner@demo.propertysystem.local` / `DemoPassword123!` (role: owner)
- `manager@demo.propertysystem.local` / `DemoPassword123!` (role: property_manager)

### Running things individually

Backend only:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/development.txt
cp ../.env.example .env   # adjust POSTGRES_HOST / REDIS_URL to localhost
python manage.py migrate
python manage.py runserver
```

Frontend only:

```bash
cd frontend
npm install
npm start   # ng serve on http://localhost:4200
```

## Multi-tenancy in practice

The frontend selects an "active organization" (persisted in `localStorage`)
and the `authInterceptor` attaches it as `X-Organization-ID` on every API
request, alongside the JWT `Authorization` header. On the backend,
`CurrentOrganizationMiddleware` resolves that header into `request.organization`
/ `request.membership` after validating the user has an active membership —
every `TenantScopedModelViewSet` then filters its queryset by that
organization automatically, and stamps it on create.

## Environment variables

See [`.env.example`](.env.example) for the full list. Copy it to `.env`
before running Docker Compose.

## Repository layout

```
property-system/
├── backend/            # Django project
│   ├── config/         # settings, urls, celery app
│   └── apps/
│       ├── core/
│       ├── users/
│       ├── organizations/
│       └── properties/
├── frontend/            # Angular workspace
│   └── src/app/
│       ├── core/
│       ├── shared/
│       └── features/
├── infra/
│   └── nginx/            # reverse proxy config used by docker-compose
├── docker-compose.yml
└── .env.example
```

## Roadmap

See the "Repository Status" section of the latest change for completed vs.
remaining features.
