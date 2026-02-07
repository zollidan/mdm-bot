import { db } from "@/db";
import { products } from "@/db/schema";
import Link from "next/link";

export default async function HomePage() {
  // Fetch products directly from database (Server Component)
  const allProducts = await db.select().from(products);

  // Filter only active products
  const activeProducts = allProducts.filter(product => product.isActive);

  return (
    <div className="pt-20 min-h-screen">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 py-12 lg:py-16">
        {/* Page Header */}
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-light mb-4">CATALOG</h1>
          <p className="text-gray-500 max-w-xl">
            Browse our curated collection of furniture, lighting, and objects
            from renowned designers and manufacturers.
          </p>
        </div>

        {/* Product Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-12">
          {activeProducts.map((product) => (
            <Link
              key={product.id}
              href={`/${product.id}`}
              className="group cursor-pointer"
            >
              <div className="aspect-[4/3] bg-[#f5f5f5] mb-4 overflow-hidden">
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  {/* Placeholder for product image */}
                  <span className="text-sm">Product Image</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-start">
                  <h3 className="text-lg font-medium group-hover:text-gray-600 transition-colors">
                    {product.name}
                  </h3>
                  {product.stock === 0 && (
                    <span className="text-xs text-gray-400 uppercase tracking-wider">
                      Out of stock
                    </span>
                  )}
                </div>
                {product.description && (
                  <p className="text-gray-500 text-sm line-clamp-2">
                    {product.description}
                  </p>
                )}
                <p className="text-sm font-medium">
                  ${(product.price / 100).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </p>
              </div>
            </Link>
          ))}
        </div>

        {activeProducts.length === 0 && (
          <div className="text-center py-24">
            <p className="text-gray-500">No products available at the moment.</p>
          </div>
        )}
      </div>
    </div>
  );
}
