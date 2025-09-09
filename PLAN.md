MDM Bot — MVP Completion Plan

Overview
- Purpose: Telegram bot for product search, cart, favorites, checkout, and order tracking for MDM Store.
- Stack: `aiogram 3.x` (polling), `SQLAlchemy` (sync), DB: `SQLite` (dev) with commented Postgres, settings via `pydantic-settings` and `.env`.
- Key modules:
  - `main.py`: Handlers, FSM states, bot bootstrap.
  - `models.py`: SQLAlchemy models (users, products, favorites, cart, orders, reviews).
  - `database.py`: Engine, `Session`, `create_tables()`; currently `sqlite:///test.db`.
  - `kbs.py`: Inline keyboards builders.
  - `utils.py`: Text builders and small helpers.
  - `convert.py`: CSV → DB import script for products.
  - `config.py`: Environment settings (`BOT_TOKEN`).

Current Functionality
- Start and main menu, basic help page.
- Product search by vendor code and by name (limited to 5), product view with image and dynamic keyboard (cart/favorite toggle, specs/reviews placeholders).
- Favorites list with quick view.
- Cart page with items, totals; add/remove item handlers.
- Checkout summary and final order creation; orders list and order details.
- Profile page and edit flows (name, phone, address).

Critical Issues Found
1) Runtime errors / broken flows
- `main.py`: Uses `select(...)` but does not import it. Fix: `from sqlalchemy import select`.
- `utils.py`: `make_main_page_text(...)` builds string but never returns it. Fix: `return main_page_text`.
- `kbs.cart_kb(...)`: Delete button callback is `remove_item_cart_{id}` but handler expects `remove_cart_{id}`. Fix one side to match (prefer `remove_cart_...`).
- `convert.py`: `from main import Base, Product, url` is wrong. Fix: `from models import Base, Product` and `from database import engine` or `url`. Avoid importing `main` in a utility script.
- `models.Base.created_date`: `default=datetime.datetime.now()` is evaluated once at import time. Fix: `default=datetime.datetime.now` (callable).

2) Data/typing and UX inconsistencies
- Callback IDs parsed as `str` then compared to `Integer` columns. Cast to `int` for filters/joins.
- In `kbs.search_kb()` `kb.adjust(2, 2)` while only 2 buttons are defined (layout minor mismatch).
- Unused/placeholder buttons: specs/reviews/contact_manager/clear_cart/qty controls not implemented. Either hide or implement for MVP.

3) Packaging/config
- `pyproject.toml` lists `logging` (stdlib) as dependency — remove. Also requires Python `>=3.13` which may be unnecessarily strict; consider `>=3.10`.
- `config.py` class name typo `Settins` (works but confusing). Consider renaming to `Settings` and update import.
- Wide `from ... import *` in `main.py` and reliance on re-exported names increases coupling; keep for now, but avoid in future refactors.

MVP Definition (Scope)
- Stable start/main page with accurate stats and working keyboard.
- Search by vendor code and by name (limited list), product detail with image, dynamic add/remove to favorites and cart.
- Cart page: list items, totals, and working per-item removal. No quantity controls in MVP.
- Checkout: summary with user details and “Confirm” creates `Orders` and `OrderItems`, clears cart, confirmation message.
- Orders: list orders and view order details.
- Profile: view and edit name/phone/address with minimal validation.
- Help: static contact info.
- Import: CSV-to-DB loader to seed `products`.

Work Plan (Phases)

Phase 0 — Stabilize (fix showstoppers)
- Add `from sqlalchemy import select` to `main.py`.
- Return value from `utils.make_main_page_text`.
- Align cart delete callback: `kbs.cart_kb` → `remove_cart_{product_id}` or add handler for `remove_item_cart_`.
- Cast callback IDs to `int` where used in DB filters/joins.
- Fix `models.Base.created_date` default callable.
- Fix `convert.py` imports; use `database.engine` and `models` directly.
- Clean `pyproject.toml`: remove `logging`, relax Python version to `>=3.10`.
- Add minimal README with run instructions and `.env` example.

Phase 1 — Core flows solid
- Verify and finalize main page handler for `F.data == "main_page"`.
- Search: ensure list view keyboards open product; limit and paginate if needed (cut to 5 for MVP).
- Favorites: ensure view → product works; add/remove feedback toasts.
- Cart: ensure per-item remove works; drop unimplemented bulk/qty buttons for MVP.
- Checkout: ensure summary and `checkout_final` create order atomically; handle empty cart and missing profile data.

Phase 2 — Orders and Profile polish
- Orders: verify list and details; add graceful empty states.
- Profile edit: add basic phone validation, confirm messages and back-navigation.
- Help: ensure keyboard actions are consistent (no dead ends).

Phase 3 — Polish & Ops
- Logging cleanup (levels, rotate or file size cap if needed).
- Basic error boundaries and user-friendly messages.
- Optional: switch to Postgres in `database.py` via `.env` config; keep SQLite for dev.
- Optional: light pagination for large search results.

Out of Scope (post-MVP)
- Quantity controls in cart, clear cart, product specs, reviews CRUD, order cancel/repeat, delivery tracking, manager chat integration, payments.

Acceptance Criteria
- Bot starts without exceptions; `/start` registers user and shows main menu.
- Search by code and name returns results; product view buttons work (add/remove favorites and cart).
- Cart shows items and allows removal; totals correct.
- Checkout creates order and clears cart; orders list/details display correctly.
- Profile view/edit works; help page accessible.
- CSV import populates `products` without import errors.

Effort Estimate
- Phase 0: 2–4 hours.
- Phase 1: 4–6 hours.
- Phase 2: 2–3 hours.
- Phase 3: 2–3 hours (optional polish).

Immediate Next Steps
- Apply Phase 0 fixes, run locally with a test token, seed products via `convert.py`, and test flows end-to-end in a private chat.

