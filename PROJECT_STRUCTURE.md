# Project Structure

This document describes the organized structure of the MDM Bot project.

## Directory Layout

```
mdm-bot/
├── mdm_bot/                 # Main package
│   ├── __init__.py
│   ├── bot.py              # Bot entry point
│   ├── run_api.py          # API entry point
│   │
│   ├── core/               # Core modules
│   │   ├── __init__.py
│   │   ├── config.py       # Settings with pydantic-settings
│   │   ├── database.py     # SQLAlchemy async engine and session
│   │   ├── models.py       # Database models
│   │   └── search.py       # MeiliSearch client
│   │
│   ├── handlers/           # Bot handlers
│   │   ├── __init__.py
│   │   └── start.py        # /start command handler
│   │
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── keyboards.py    # Inline keyboard builders
│   │   └── formatters.py   # Text formatting helpers
│   │
│   ├── api/                # FastAPI application
│   │   ├── __init__.py
│   │   └── app.py          # API routes and endpoints
│   │
│   └── scripts/            # Utility scripts
│       ├── __init__.py
│       └── import_csv.py   # CSV import for products
│
├── templates/              # Jinja2 HTML templates
├── static/                 # Static files (CSS, JS, images)
│
├── bot.py                  # DEPRECATED: Use python -m mdm_bot.bot
├── main.py                 # DEPRECATED: Use python -m mdm_bot.bot
├── config.py               # DEPRECATED: Import from mdm_bot.core
├── database.py             # DEPRECATED: Import from mdm_bot.core
├── models.py               # DEPRECATED: Import from mdm_bot.core
├── kbs.py                  # DEPRECATED: Import from mdm_bot.utils
├── utils.py                # DEPRECATED: Import from mdm_bot.utils
├── convert.py              # DEPRECATED: Use mdm_bot.scripts.import_csv
│
├── docker-compose.yaml     # Docker Compose configuration
├── Dockerfile              # Docker image build
├── pyproject.toml          # Project dependencies (uv)
├── uv.lock                 # Locked dependencies
└── .env                    # Environment variables (not in git)
```

## Running the Application

### Development (Local)

**Start the bot:**
```bash
python -m mdm_bot.bot
# or (backward compatible)
python main.py
```

**Start the API server:**
```bash
uvicorn mdm_bot.api.app:app --reload --host 0.0.0.0 --port 8000
# or
python -m mdm_bot.run_api
```

**Import products from CSV:**
```bash
python -m mdm_bot.scripts.import_csv
# or (backward compatible)
python convert.py
```

### Production (Docker)

**Start all services:**
```bash
docker compose up -d
```

**View logs:**
```bash
docker compose logs -f bot
docker compose logs -f api
```

**Import products (in container):**
```bash
docker compose exec bot uv run python -m mdm_bot.scripts.import_csv
```

## Module Import Patterns

### New (Recommended)
```python
# Core modules
from mdm_bot.core import settings, AsyncSessionFactory, create_tables
from mdm_bot.core import User, Product, CartItem, Orders
from mdm_bot.core import MeiliSearchClient, get_meili_client

# Utilities
from mdm_bot.utils import get_main_keyboard, format_product_card

# API
from mdm_bot.api import app
```

### Old (Backward Compatible)
```python
# Still works but deprecated
from config import settings
from database import AsyncSessionFactory, create_tables
from models import User, Product
from kbs import main_kb, product_kb
from utils import make_product_card
```

## Key Changes

1. **Organized Package Structure**: Code is now organized into logical modules (core, handlers, utils, api, scripts)

2. **Proper Python Package**: `mdm_bot` is now a proper Python package with `__init__.py` files and clear module boundaries

3. **Backward Compatibility**: Old import paths still work through compatibility shims in root directory

4. **Consistent Naming**: Functions use consistent naming patterns:
   - `get_*` for getters/builders (e.g., `get_main_keyboard`)
   - `format_*` for formatters (e.g., `format_product_card`)

5. **Docker Integration**: Docker commands updated to use new module paths

6. **Fixed Typo**: `Settins` renamed to `Settings` in config

## Migration Guide

To migrate existing code:

1. **Update imports** to use new paths:
   ```python
   # Old
   from config import settings

   # New
   from mdm_bot.core import settings
   ```

2. **Update function names** if using utilities:
   ```python
   # Old
   from kbs import main_kb

   # New
   from mdm_bot.utils import get_main_keyboard
   ```

3. **Update Docker commands** (already done in docker-compose.yaml):
   ```yaml
   # Old
   command: uv run main.py

   # New
   command: uv run python -m mdm_bot.bot
   ```

## Benefits

- ✅ Clear separation of concerns
- ✅ Easier to navigate and understand
- ✅ Better IDE support and autocomplete
- ✅ Scalable for future growth
- ✅ Professional Python package structure
- ✅ Backward compatible with existing code
