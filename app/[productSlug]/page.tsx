import { ArrowLeft, ArrowRight } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { db } from "@/db";
import { products } from "@/db/schema";
import { eq } from "drizzle-orm";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ productSlug: string }>;
}): Promise<Metadata> {
  const { productSlug } = await params;
  const productId = parseInt(productSlug);

  if (isNaN(productId)) {
    return {
      title: "Product Not Found",
    };
  }

  const [product] = await db
    .select()
    .from(products)
    .where(eq(products.id, productId));

  if (!product) {
    return {
      title: "Product Not Found",
    };
  }

  return {
    title: `${product.name} | MDM BOY`,
    description: product.description || `View details for ${product.name}`,
  };
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ productSlug: string }>;
}) {
  const { productSlug } = await params;

  // Parse productSlug as id
  const productId = parseInt(productSlug);

  if (isNaN(productId)) {
    notFound();
  }

  // Fetch product from database
  const [product] = await db
    .select()
    .from(products)
    .where(eq(products.id, productId));

  if (!product) {
    notFound();
  }

  const inStock = product.stock > 0;

  return (
    <div className="pt-20 min-h-screen">
      {/* Back Navigation */}
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 py-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-black transition-colors"
        >
          <ArrowLeft size={16} />
          Back to Catalog
        </Link>
      </div>

      {/* Product Detail */}
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24">
          {/* Left - Image Placeholder */}
          <div>
            <div className="aspect-square bg-[#f5f5f5] sticky top-32">
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                <span className="text-sm">Product Image</span>
              </div>
            </div>
          </div>

          {/* Right - Content */}
          <div className="lg:py-8">
            <div>
              <h1 className="text-4xl md:text-5xl font-light mb-6">{product.name}</h1>
              {product.description && (
                <p className="text-gray-600 text-lg leading-relaxed mb-8">
                  {product.description}
                </p>
              )}
            </div>

            <div className="h-px bg-gray-200 my-8" />

            {/* Price */}
            <div className="mb-8">
              <p className="text-3xl font-light">
                ${(product.price / 100).toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </p>
            </div>

            {/* Contact Button */}
            <div>
              <Link
                href="/contact"
                className="w-full lg:w-auto inline-flex items-center justify-center gap-3 bg-black text-white px-8 py-4 text-sm uppercase tracking-wider hover:bg-gray-800 transition-colors"
              >
                CONTACT FOR INQUIRY
                <ArrowRight size={16} />
              </Link>
              <p className="text-sm text-gray-400 mt-4">
                This is a catalog item. Contact us for pricing and availability.
              </p>
            </div>

            <div className="h-px bg-gray-200 my-12" />

            {/* Stock Status */}
            <div>
              <div className="flex items-center gap-2">
                <div
                  className={`w-2 h-2 rounded-full ${inStock ? "bg-green-500" : "bg-gray-400"}`}
                />
                <p className="text-sm text-gray-500">
                  {inStock ? `In Stock (${product.stock} available)` : "Out of Stock"}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
