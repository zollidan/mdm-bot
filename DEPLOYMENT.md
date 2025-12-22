# Production Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Domain name (optional, for external access)
- SSL certificate (optional, for HTTPS)

## Quick Start

### 1. Prepare Environment Configuration

```bash
# Copy production environment template
cp .env.production .env

# Edit .env with your actual values
nano .env
```

**Required variables to configure:**
- `BOT_TOKEN` - Your Telegram bot token from @BotFather
- `POSTGRES_PASSWORD` - Strong database password (use random string)
- `MEILI_MASTER_KEY` - MeiliSearch master key (minimum 16 characters)

### 2. Deploy Services

```bash
# Start all services in production mode
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f bot
```

### 3. Initialize Database

The database tables will be created automatically on first bot startup.

### 4. Import Product Data (Optional)

```bash
# If you have CSV data to import
docker-compose exec bot uv run convert.py
```

## Service Configuration

### MeiliSearch (Production Mode)

- **Port**: 7700 (internal), exposed for admin dashboard
- **Environment**: Production (secure mode enabled)
- **Analytics**: Disabled for privacy
- **Resources**: 0.5 CPU, 1GB RAM limit
- **Data**: Persisted in `meilisearch-data` volume

**Access Dashboard:**
- Local: http://localhost:7700
- Requires `MEILI_MASTER_KEY` for authentication

### PostgreSQL Database

- **Port**: 5432 (exposed for external tools)
- **Image**: postgres:16-alpine
- **Resources**: 1 CPU, 4GB RAM limit
- **Data**: Persisted in `postgres-data` volume
- **Health checks**: Automatic with 5 retries

### Bot Service

- **Resources**: 1 CPU, 512MB RAM limit
- **Restart policy**: Unless stopped manually
- **Dependencies**: Waits for PostgreSQL and MeiliSearch health checks

## Environment Variables Reference

### Bot Configuration
- `BOT_TOKEN` - Telegram bot API token

### Database Configuration
- `POSTGRES_USER` - Database username (default: postgres_prod)
- `POSTGRES_PASSWORD` - Database password (REQUIRED)
- `POSTGRES_HOST` - Database host (default: postgres for Docker)
- `POSTGRES_PORT` - Database port (default: 5432)
- `POSTGRES_DB` - Database name (default: mdm_bot_db)

### MeiliSearch Configuration
- `MEILI_HOST` - MeiliSearch host (default: meilisearch for Docker)
- `MEILI_PORT` - MeiliSearch port (default: 7700)
- `MEILI_MASTER_KEY` - Master key for authentication (REQUIRED, min 16 chars)
- `MEILI_ENV` - Environment mode (development/production)

## Production Security Checklist

- [ ] Use strong, unique passwords for `POSTGRES_PASSWORD`
- [ ] Generate secure `MEILI_MASTER_KEY` (min 16 chars, use random string)
- [ ] Don't expose PostgreSQL port externally (comment out ports in production)
- [ ] Don't expose MeiliSearch port externally unless needed for admin access
- [ ] Use firewall rules to restrict access
- [ ] Keep Docker images updated
- [ ] Set up automatic backups for postgres-data volume
- [ ] Monitor logs for errors: `docker-compose logs -f`

## Maintenance Commands

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart specific service
docker-compose restart bot

# View service logs
docker-compose logs -f bot
docker-compose logs -f postgres
docker-compose logs -f meilisearch

# Update images and restart
docker-compose pull
docker-compose up -d --build

# Backup database
docker-compose exec postgres pg_dump -U postgres_prod mdm_bot_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres_prod mdm_bot_db < backup.sql
```

## Monitoring

### Check Service Health

```bash
# Check all services status
docker-compose ps

# Check resource usage
docker stats

# Check MeiliSearch health
curl http://localhost:7700/health

# Check PostgreSQL connection
docker-compose exec postgres pg_isready -U postgres_prod
```

### Troubleshooting

**Bot not starting:**
```bash
# Check bot logs
docker-compose logs bot

# Verify environment variables
docker-compose exec bot env | grep -E 'BOT_TOKEN|POSTGRES|MEILI'
```

**Database connection errors:**
```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection manually
docker-compose exec postgres psql -U postgres_prod -d mdm_bot_db
```

**MeiliSearch issues:**
```bash
# Check MeiliSearch logs
docker-compose logs meilisearch

# Verify master key is set
docker-compose exec meilisearch env | grep MEILI_MASTER_KEY

# Check health endpoint
curl http://localhost:7700/health
```

## Scaling Considerations

To scale for production load:

1. **Increase PostgreSQL resources** in docker-compose.yaml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: "2"
         memory: 8G
   ```

2. **Increase MeiliSearch resources** for large catalogs:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: "1"
         memory: 2G
   ```

3. **Use external PostgreSQL** (managed service) instead of Docker container

4. **Add Redis** for session management if bot traffic is high

## Backup Strategy

### Automated Backups

Create a cron job for daily backups:

```bash
# Add to crontab (crontab -e)
0 2 * * * cd /path/to/mdm-bot && docker-compose exec -T postgres pg_dump -U postgres_prod mdm_bot_db | gzip > backups/backup-$(date +\%Y\%m\%d).sql.gz
```

### Manual Backup

```bash
# Create backup directory
mkdir -p backups

# Backup database
docker-compose exec postgres pg_dump -U postgres_prod mdm_bot_db > backups/backup-$(date +%Y%m%d).sql

# Backup MeiliSearch data
docker-compose exec meilisearch curl -X POST http://localhost:7700/dumps \
  -H "Authorization: Bearer ${MEILI_MASTER_KEY}"
```

## Production Deployment Checklist

- [ ] Configure .env with production values
- [ ] Set secure passwords and keys
- [ ] Review resource limits in docker-compose.yaml
- [ ] Set up firewall rules
- [ ] Configure domain and SSL (if needed)
- [ ] Set up monitoring and alerting
- [ ] Configure automated backups
- [ ] Test bot functionality
- [ ] Document custom configuration
- [ ] Set up log rotation
- [ ] Plan maintenance windows
