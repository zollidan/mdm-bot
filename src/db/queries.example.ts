import { db } from './index';
import { users, products } from './schema';
import { eq, and, or, like, gte } from 'drizzle-orm';

// Example queries for reference

// Select all users
export async function getAllUsers() {
  return await db.select().from(users);
}

// Select user by id
export async function getUserById(id: number) {
  return await db.select().from(users).where(eq(users.id, id));
}

// Insert new user
export async function createUser(name: string, email: string) {
  return await db.insert(users).values({ name, email }).returning();
}

// Update user
export async function updateUser(id: number, data: { name?: string; email?: string }) {
  return await db
    .update(users)
    .set({ ...data, updatedAt: new Date() })
    .where(eq(users.id, id))
    .returning();
}

// Delete user
export async function deleteUser(id: number) {
  return await db.delete(users).where(eq(users.id, id)).returning();
}

// Search products by name
export async function searchProducts(query: string) {
  return await db
    .select()
    .from(products)
    .where(like(products.name, `%${query}%`));
}

// Get active products with price greater than or equal to amount
export async function getActiveProductsAbovePrice(minPrice: number) {
  return await db
    .select()
    .from(products)
    .where(and(eq(products.isActive, true), gte(products.price, minPrice)));
}
