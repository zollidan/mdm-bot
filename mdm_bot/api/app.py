"""
FastAPI server for Telegram Mini App API endpoints
"""
import math
import logging
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from contextlib import asynccontextmanager

from mdm_bot.core import AsyncSessionFactory, Product, settings
from mdm_bot.core.search import get_meili_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize MeiliSearch on startup"""
    logger.info("Starting FastAPI application...")

    try:
        # Initialize MeiliSearch client and sync products
        meili = await get_meili_client()
        await meili.sync_products()
        logger.info("MeiliSearch initialized and synced successfully")
    except Exception as e:
        logger.warning(f"MeiliSearch initialization failed (will work without search): {e}")

    yield

    logger.info("Shutting down FastAPI application...")


app = FastAPI(
    title="MDM Bot API",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# CORS configuration with environment variable support
allowed_origins = (
    settings.ALLOWED_ORIGINS.split(",")
    if settings.ALLOWED_ORIGINS != "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)


# Pydantic models for API
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    image: Optional[str] = None
    vendor_code: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ProductsListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class SearchResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    query: str


@app.get("/api/products", response_model=ProductsListResponse)
async def get_products(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество товаров на странице")
):
    """Get paginated product list"""
    try:
        async with AsyncSessionFactory() as session:
            # Count total products
            count_query = select(func.count(Product.id))
            total_result = await session.execute(count_query)
            total = total_result.scalar()

            # Calculate pagination
            total_pages = math.ceil(total / limit)
            offset = (page - 1) * limit

            # Get products for current page
            query = (
                select(Product)
                .order_by(Product.id)
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(query)
            products = result.scalars().all()

            # Build response
            return ProductsListResponse(
                items=[ProductResponse.model_validate(p) for p in products],
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Get specific product information"""
    try:
        async with AsyncSessionFactory() as session:
            query = select(Product).where(Product.id == product_id)
            result = await session.execute(query)
            product = result.scalar_one_or_none()

            if not product:
                raise HTTPException(status_code=404, detail="Товар не найден")

            return ProductResponse.model_validate(product)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@app.get("/api/search", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=100, description="Максимум результатов")
):
    """Search products using MeiliSearch"""
    try:
        # Get MeiliSearch client
        meili = await get_meili_client()

        # Search for product IDs
        product_ids = meili.search_products(q, limit=limit)

        if not product_ids:
            return SearchResponse(items=[], total=0, query=q)

        # Fetch products from database
        async with AsyncSessionFactory() as session:
            query = select(Product).where(Product.id.in_(product_ids))
            result = await session.execute(query)
            products = result.scalars().all()

            # Sort by the order from MeiliSearch
            products_dict = {p.id: p for p in products}
            sorted_products = [products_dict[pid] for pid in product_ids if pid in products_dict]

            return SearchResponse(
                items=[ProductResponse.model_validate(p) for p in sorted_products],
                total=len(sorted_products),
                query=q
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {"status": "ok", "service": "mdm-bot-api"}


# HTML routes with Jinja2 templates
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/products", response_class=HTMLResponse)
async def products_page(request: Request):
    """Product catalog page"""
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/products/{product_id}", response_class=HTMLResponse)
async def product_detail_page(request: Request, product_id: int):
    """Product detail page"""
    return templates.TemplateResponse(
        "product_detail.html",
        {
            "request": request,
            "product_id": product_id,
            "product": None 
        }
    )
    
@app.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    return templates.TemplateResponse(
        "support.html",
        {
            "request": request
        }
    )


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
