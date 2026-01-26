import type { Category, Product, CategoryCreate, ProductCreate } from "./types";

const API_URL = "http://localhost:8000";

// Categories
export async function getCategories(): Promise<Category[]> {
  const response = await fetch(`${API_URL}/categories/`);
  if (!response.ok) throw new Error("Failed to fetch categories");
  return response.json();
}

export async function getCategory(id: number): Promise<Category> {
  const response = await fetch(`${API_URL}/categories/${id}`);
  if (!response.ok) throw new Error("Failed to fetch category");
  return response.json();
}

export async function createCategory(
  category: CategoryCreate,
): Promise<Category> {
  const response = await fetch(`${API_URL}/categories/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(category),
  });
  if (!response.ok) throw new Error("Failed to create category");
  return response.json();
}

// Products
export async function getProducts(categoryId?: number): Promise<Product[]> {
  const url = categoryId
    ? `${API_URL}/products/?category_id=${categoryId}`
    : `${API_URL}/products/`;
  const response = await fetch(url);
  if (!response.ok) throw new Error("Failed to fetch products");
  return response.json();
}

export async function getProduct(id: number): Promise<Product> {
  const response = await fetch(`${API_URL}/products/${id}`);
  if (!response.ok) throw new Error("Failed to fetch product");
  return response.json();
}

export async function createProduct(product: ProductCreate): Promise<Product> {
  const response = await fetch(`${API_URL}/products/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(product),
  });
  if (!response.ok) throw new Error("Failed to create product");
  return response.json();
}
