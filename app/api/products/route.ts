import { NextResponse } from 'next/server';
import { db } from '@/src/db';
import { products } from '@/src/db/schema';

export async function GET() {
  try {
    const allProducts = await db.select().from(products);
    return NextResponse.json(allProducts);
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch products' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const [newProduct] = await db
      .insert(products)
      .values({
        name: body.name,
        description: body.description,
        price: body.price,
        stock: body.stock || 0,
      })
      .returning();

    return NextResponse.json(newProduct, { status: 201 });
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json(
      { error: 'Failed to create product' },
      { status: 500 }
    );
  }
}
