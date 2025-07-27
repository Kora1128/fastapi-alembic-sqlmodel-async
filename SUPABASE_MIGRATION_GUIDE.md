# Migration Guide: PostgreSQL to Supabase

This guide will help you migrate your existing FastAPI application from a local PostgreSQL database to Supabase.

## What is Supabase?

Supabase is an open-source Firebase alternative that provides:
- Managed PostgreSQL database
- Real-time subscriptions
- Built-in authentication
- Edge functions
- Dashboard for database management
- Automatic API generation
- Row Level Security (RLS)

## Why Migrate to Supabase?

1. **Managed Infrastructure**: No need to manage PostgreSQL servers
2. **Scalability**: Automatic scaling based on usage
3. **Built-in Features**: Authentication, real-time, and more
4. **Cost-Effective**: Free tier available, pay-as-you-scale pricing
5. **Developer Experience**: Excellent dashboard and tooling
6. **Backup & Recovery**: Automatic backups and point-in-time recovery

## Migration Steps

### Step 1: Setup Supabase Project

1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project
3. Choose a region close to your users
4. Set a strong database password
5. Wait for the project to be provisioned

### Step 2: Get Connection Details

1. In your Supabase dashboard, go to **Settings** → **Database**
2. Note down the connection information:
   - Host: `db.<project-ref>.supabase.co`
   - Database: `postgres`
   - User: `postgres`
   - Port: `5432`
   - Password: The one you set during project creation

### Step 3: Update Environment Variables

Update your `.env` file with Supabase credentials:

```bash
# Supabase Database Configuration
DATABASE_HOST=db.<your-project-ref>.supabase.co
DATABASE_USER=postgres
DATABASE_PASSWORD=<your-supabase-password>
DATABASE_NAME=postgres
DATABASE_CELERY_NAME=postgres
DATABASE_PORT=5432

# Alternative: Use connection URL
SUPABASE_DATABASE_URL=postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
```

### Step 4: Export Existing Data (If Applicable)

If you have existing data in your local PostgreSQL:

```bash
# Export your current database
pg_dump -h localhost -U postgres -p 5454 your_database > backup.sql

# Or using Docker
docker compose -f docker-compose-dev.yml exec database pg_dump -U postgres your_database > backup.sql
```

### Step 5: Run Migrations

```bash
# Use the Supabase development environment
make run-dev-supabase

# Run Alembic migrations
make add-supabase-migration

# Initialize with sample data
make init-supabase-db
```

### Step 6: Import Existing Data (If Applicable)

If you have a backup from step 4:

```bash
# Connect to Supabase and import
psql -h db.<project-ref>.supabase.co -U postgres -d postgres < backup.sql
```

Or use the Supabase dashboard SQL editor to run your SQL scripts.

### Step 7: Update Production Deployment

Update your production environment:

1. Set production Supabase credentials in your production `.env`
2. Deploy using: `docker compose up --build`
3. The production docker-compose.yml is already configured for external databases

## Key Differences

### Database Schema
- Supabase uses the `postgres` database by default
- Both main app and Celery can use the same database
- Tables are created in the `public` schema by default

### Connection Pooling
- Supabase handles connection pooling automatically
- You can still configure pool settings in your application

### Security
- Supabase provides Row Level Security (RLS)
- API keys for different access levels
- Built-in authentication (optional to use)

## Troubleshooting

### Connection Issues
- Verify your project reference in the connection string
- Check that your IP is allowed (Supabase allows all IPs by default)
- Ensure you're using the correct password

### Migration Errors
- Run migrations step by step if auto-generation fails
- Check Supabase logs in the dashboard
- Verify your models are compatible with PostgreSQL

### Performance
- Monitor query performance in Supabase dashboard
- Use indexes for frequently queried columns
- Consider upgrading to a higher tier if needed

## Advanced Features (Optional)

### Supabase Auth Integration
You can optionally integrate Supabase Auth instead of JWT:

```python
# Future enhancement - replace JWT with Supabase Auth
# This would require additional configuration
```

### Real-time Subscriptions
Enable real-time features:

```sql
-- Enable real-time for a table
ALTER PUBLICATION supabase_realtime ADD TABLE your_table;
```

### Row Level Security
Enable RLS for better security:

```sql
-- Enable RLS
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own data" ON your_table
    FOR SELECT USING (auth.uid() = user_id);
```

## Support

- Supabase Documentation: [docs.supabase.com](https://docs.supabase.com)
- Community Discord: [discord.supabase.com](https://discord.supabase.com)
- GitHub Issues: For template-specific issues

## Rollback Plan

If you need to rollback to local PostgreSQL:

1. Export data from Supabase
2. Update `.env` to use local database settings
3. Run `make run-dev` instead of `make run-dev-supabase`
4. Import data to local database