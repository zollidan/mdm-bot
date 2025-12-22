# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MDM Bot is a Telegram e-commerce bot for a store catalog built with Python 3.10+. It provides product search, cart management, favorites, order processing, and user profile management.

**Architecture Stack:**
- `aiogram 3.x` - Async Telegram bot framework with polling
- `SQLAlchemy` (async) - Database ORM with declarative models
- `PostgreSQL` (production) / SQLite (legacy) - Database layer
- `MeiliSearch` - Full-text search engine for products
- `pydantic-settings` - Configuration management via `.env`

## Key Commands

**Development:**
- `docker-compose up -d` - Start all services (bot, PostgreSQL, MeiliSearch)
- `docker-compose logs -f bot` - View bot logs
- `python main.py` - Start bot locally (requires PostgreSQL + MeiliSearch running)
- `python convert.py` - Import products from CSV (`old_db_lite.csv`)

**Production:**
- `cp .env.production .env` - Use production environment template
- `docker-compose up -d` - Deploy all services
- See [DEPLOYMENT.md](DEPLOYMENT.md) for complete production guide

**Dependencies:**
- `pip install -e .` or `uv sync --locked` (recommended)
- Python 3.10+ required
- Docker & Docker Compose for containerized deployment

## Core Architecture

**Main Module Structure:**
- `main.py`: Bot handlers, FSM states, message processing with aiogram Dispatcher
- `models.py`: SQLAlchemy declarative models (User, Product, CartItem, Orders, etc.)
- `database.py`: Database engine, session factory, table creation
- `kbs.py`: Inline keyboard builders for bot UI
- `utils.py`: Text formatting helpers and product card builders
- `config.py`: Settings class with pydantic-settings integration

**Database Models:**
- `User`: Telegram users with profile info (name, phone, address)
- `Product`: Store items with pricing, images, vendor info
- `CartItem`: Shopping cart with quantities
- `Favorite`: User's saved products
- `Orders` + `OrderItems`: Order management system
- `Reviews`: User feedback (placeholder)

**Bot Flow Architecture:**
- FSM (Finite State Machine) for multi-step flows (search, profile editing)
- Callback-based navigation with inline keyboards
- Dynamic keyboard generation based on user state (cart/favorites status)

## Important Implementation Details

**Database Configuration:**
- Production: PostgreSQL via environment variables in `database.py`
- Connection uses async SQLAlchemy with `AsyncSession` and `asyncpg` driver
- Session factory: `AsyncSessionFactory` from `database.py`
- Auto-creates tables on startup via `create_tables()` function

**MeiliSearch Integration:**
- Client initialization in search-related modules
- Product indexing for fast full-text search
- Configuration via `MEILI_HOST`, `MEILI_PORT`, `MEILI_MASTER_KEY` environment variables
- See recent commit (58b020a) for MeiliSearch client implementation

**Bot Handler Patterns:**
- Handlers use `@dp.callback_query(F.data == "action")` for button callbacks
- State management with `SearchForm` and `ProfileForm` classes
- Product IDs extracted from callback data: `callback.data.split("_")[2]`

**Key UI Patterns:**
- Product cards show image + description with dynamic buttons
- Cart shows items with individual remove buttons and totals  
- Order flow requires complete user profile (name, phone, address)
- Search supports both vendor code and name matching (limited to 5 results)

## Development Notes

**Environment Configuration:**
- Development: Copy `.env.example` to `.env` and configure
- Production: Copy `.env.production` to `.env` with secure credentials
- Key variables: `BOT_TOKEN`, `POSTGRES_*`, `MEILI_HOST`, `MEILI_MASTER_KEY`
- Docker services use internal hostnames: `postgres`, `meilisearch`

**CSV Import:**
- Place `old_db_lite.csv` in project root with semicolon delimiter
- Run `python convert.py` to seed database with products
- Docker: `docker-compose exec bot uv run convert.py`

**Bot Configuration:**
- Runs in polling mode (no webhook setup needed)
- Logging configured to `mdm.log` file with INFO level
- Restart policy: `unless-stopped` in production

**Docker Services:**
- `bot` - Main Telegram bot (depends on postgres + meilisearch)
- `postgres` - PostgreSQL 16 Alpine with health checks
- `meilisearch` - Search engine v1.10 with production mode
- `postgresus` - PostgreSQL admin UI on port 4005

**Resource Limits (Production):**
- Bot: 1 CPU, 512MB RAM
- PostgreSQL: 1 CPU, 4GB RAM
- MeiliSearch: 0.5 CPU, 1GB RAM

**Error Handling:**
- Most handlers have try/catch blocks with user-friendly error messages
- Health checks ensure services are ready before bot starts

**Known Issues (from PLAN.md):**
- Profile validation is basic (regex for phone numbers)
- No quantity controls in cart (MVP scope limitation)

**Security Notes:**
- Use strong passwords for `POSTGRES_PASSWORD` (random string recommended)
- `MEILI_MASTER_KEY` must be minimum 16 characters
- Never commit `.env` files (already in .gitignore)
- In production, close external access to database and search ports