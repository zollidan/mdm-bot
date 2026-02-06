# Database Setup Guide

## Quick Start

### 1. Start PostgreSQL with Docker Compose

```bash
docker-compose up -d
```

This will start PostgreSQL on `localhost:5432` with:
- Username: `postgres`
- Password: `postgres`
- Database: `mdm_bot`

### 2. Generate and Run Migrations

```bash
# Generate migrations from schema
npm run db:generate

# Push schema to database (for development)
npm run db:push

# Or run migrations (for production)
npm run db:migrate
```

### 3. Open Drizzle Studio (Optional)

```bash
npm run db:studio
```

This will open a visual database browser at `https://local.drizzle.studio`

## Available Scripts

- `npm run db:generate` - Generate migration files from schema
- `npm run db:push` - Push schema changes directly to database (dev only)
- `npm run db:migrate` - Run migration files
- `npm run db:studio` - Open Drizzle Studio

## Database Schema

The schema is defined in `src/db/schema.ts`. Example tables:

### Users Table
- `id` - Serial primary key
- `name` - Text, not null
- `email` - Text, unique, not null
- `created_at` - Timestamp
- `updated_at` - Timestamp

### Products Table
- `id` - Serial primary key
- `name` - Text, not null
- `description` - Text
- `price` - Integer, not null
- `stock` - Integer, default 0
- `is_active` - Boolean, default true
- `created_at` - Timestamp
- `updated_at` - Timestamp

## Usage in Next.js

### Server Component Example

```typescript
import { db } from '@/db';
import { products } from '@/db/schema';

export default async function ProductsPage() {
  const allProducts = await db.select().from(products);

  return (
    <div>
      {allProducts.map(product => (
        <div key={product.id}>{product.name}</div>
      ))}
    </div>
  );
}
```

### API Route Example

```typescript
// app/api/products/route.ts
import { db } from '@/db';
import { products } from '@/db/schema';
import { eq } from 'drizzle-orm';

export async function GET() {
  const allProducts = await db.select().from(products);
  return Response.json(allProducts);
}

export async function POST(request: Request) {
  const body = await request.json();

  const [newProduct] = await db
    .insert(products)
    .values({
      name: body.name,
      description: body.description,
      price: body.price,
    })
    .returning();

  return Response.json(newProduct);
}
```

## Environment Variables

Copy `.env.example` to `.env` and update if needed:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mdm_bot
```

## Stopping the Database

```bash
docker-compose down
```

To remove data volumes as well:

```bash
docker-compose down -v
```
