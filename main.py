from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
import crud
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MDM Bot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Category endpoints
@app.post("/categories/", response_model=schemas.Category, tags=["Categories"])
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)) -> models.Category:
    return crud.create_category(db=db, category=category)


@app.get("/categories/", response_model=List[schemas.Category], tags=["Categories"])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[models.Category]:
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories


@app.get("/categories/{category_id}", response_model=schemas.Category, tags=["Categories"])
def read_category(category_id: int, db: Session = Depends(get_db)) -> models.Category:
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@app.put("/categories/{category_id}", response_model=schemas.Category, tags=["Categories"])
def update_category(
    category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)
) -> models.Category:
    db_category = crud.update_category(db, category_id=category_id, category=category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@app.delete("/categories/{category_id}", tags=["Categories"])
def delete_category(category_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    success = crud.delete_category(db, category_id=category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}


# Product endpoints
@app.post("/products/", response_model=schemas.Product, tags=["Products"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)) -> models.Product:
    return crud.create_product(db=db, product=product)


@app.get("/products/", response_model=List[schemas.Product], tags=["Products"])
def read_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> list[models.Product]:
    products = crud.get_products(db, skip=skip, limit=limit, category_id=category_id)
    return products


@app.get("/products/{product_id}", response_model=schemas.Product, tags=["Products"])
def read_product(product_id: int, db: Session = Depends(get_db)) -> models.Product:
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@app.put("/products/{product_id}", response_model=schemas.Product, tags=["Products"])
def update_product(
    product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)
) -> models.Product:
    db_product = crud.update_product(db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    success = crud.delete_product(db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@app.get("/", tags=["Root"])
def read_root() -> dict[str, str]:
    return {"message": "MDM Bot API", "docs": "/docs"}

