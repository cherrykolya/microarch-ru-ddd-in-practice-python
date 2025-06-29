# Database Migrations

This directory contains database migrations for the project. We use Alembic for managing database migrations.

## Structure

```
migrations/
├── versions/        # Migration version files
├── env.py          # Environment configuration
├── README.md       # This file
└── alembic.ini     # Alembic configuration
```

## Commands

- Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

- Apply migrations:
```bash
alembic upgrade head
```

- Rollback last migration:
```bash
alembic downgrade -1
```

- Show current migration version:
```bash
alembic current
```

- Show migration history:
```bash
alembic history
```

## Best Practices

1. Each migration should be atomic and focused on a specific change
2. Always test migrations on a copy of production data before applying to production
3. Include both 'upgrade' and 'downgrade' operations
4. Use meaningful descriptions in migration names
5. Review auto-generated migrations before committing
