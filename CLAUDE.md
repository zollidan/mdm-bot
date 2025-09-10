# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MDM Bot is a Telegram e-commerce bot for a store catalog built with Python 3.10+. It provides product search, cart management, favorites, order processing, and user profile management.

**Architecture Stack:**
- `aiogram 3.x` - Async Telegram bot framework with polling
- `SQLAlchemy` (sync) - Database ORM with declarative models  
- `SQLite` (dev) / PostgreSQL (production) - Database layer
- `pydantic-settings` - Configuration management via `.env`

## Key Commands

**Development:**
- `python main.py` - Start the bot
- `python convert.py` - Import products from CSV (`old_db_lite.csv`)
- `docker-compose up -d` - Start PostgreSQL container
- Setup: Create `.env` with `BOT_TOKEN=your_bot_token`

**Dependencies:**
- `pip install -e .` or `pip install aiogram art asyncpg psycopg2 pydantic-settings "sqlalchemy[asyncio]"`
- Python 3.10+ required

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
- Development: SQLite (`sqlite:///test.db`)
- Production: PostgreSQL via environment variables in `database.py`
- Session management uses synchronous SQLAlchemy with `Session()` context managers

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

**Database Switching:**
- Comment/uncomment lines in `database.py` to switch between SQLite and PostgreSQL
- PostgreSQL settings configured via docker-compose.yaml

**CSV Import:**
- Place `old_db_lite.csv` in project root with semicolon delimiter
- Run `python convert.py` to seed database with products

**Bot Token Setup:**
- Copy `.env.example` to `.env` (if exists) or create with `BOT_TOKEN=your_token`
- Bot runs in polling mode, no webhook setup needed

**Error Handling:**
- Most handlers have try/catch blocks with user-friendly error messages
- Logging configured to `mdm.log` file with INFO level

**Known Issues (from PLAN.md):**
- Some import statements and callback patterns need alignment
- Profile validation is basic (regex for phone numbers)
- No quantity controls in cart (MVP scope limitation)