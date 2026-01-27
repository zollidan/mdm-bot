export interface Category {
  id: number;
  name: string;
  icon: string;
  color: string;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  categoryId: number;
  image?: string;
  rating: number;
  reviews: number;
  isNew?: boolean;
  discount?: number;
}
