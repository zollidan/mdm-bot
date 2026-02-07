import Link from "next/link";

export const Footer = () => {
  return (
    <footer className="border-t border-gray-200">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12 py-16 lg:py-24">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 lg:gap-8">
          {/* Brand Column */}
          <div className="lg:col-span-1">
            <h3 className="text-xl font-semibold mb-4">FORME</h3>
            <p className="text-gray-500 text-sm leading-relaxed max-w-xs">
              Curated furniture and objects for the contemporary home. Design
              that serves life, not complicates it.
            </p>
          </div>

          {/* Navigation Column */}
          <div>
            <h4 className="text-label text-gray-400 mb-6">Navigation</h4>
            <ul className="space-y-3">
              {[
                { name: "Home", href: "/" },
                { name: "Catalog", href: "/catalog" },
                { name: "About", href: "/about" },
                { name: "Contact", href: "/contact" },
              ].map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className="text-sm text-gray-600 hover:text-black transition-colors"
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Categories Column */}
          <div>
            <h4 className="text-label text-gray-400 mb-6">Categories</h4>
            <ul className="space-y-3">
              {[
                { name: "Furniture", slug: "furniture" },
                { name: "Lighting", slug: "lighting" },
                { name: "Decor", slug: "decor" },
                { name: "Objects", slug: "objects" },
              ].map((item) => (
                <li key={item.name}>
                  <Link
                    href={`/catalog?category=${item.slug}`}
                    className="text-sm text-gray-600 hover:text-black transition-colors"
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
        {/* Bottom Bar */}
        <div className="mt-16 pt-8 border-t border-gray-200 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <p className="text-xs text-gray-400">
            © 2024 FORME. All rights reserved.
          </p>
          <div className="flex gap-6">
            <Link
              href="/privacy"
              className="text-xs text-gray-400 hover:text-black transition-colors"
            >
              Privacy Policy
            </Link>
            <Link
              href="/terms"
              className="text-xs text-gray-400 hover:text-black transition-colors"
            >
              Terms of Service
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
