export interface Category {
  id: number;
  name: string;
  description: string | null;
}

export interface Product {
  id: number;
  name: string;
  description: string | null;
  price: number;
  category_id: number | null;
}

export interface CategoryCreate {
  name: string;
  description?: string | null;
}

export interface ProductCreate {
  name: string;
  description?: string | null;
  price: number;
  category_id?: number | null;
}
