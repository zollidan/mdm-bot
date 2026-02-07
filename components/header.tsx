"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Menu, X } from "lucide-react";

const navItems = [
  { id: "/", label: "Home" },
  { id: "/about", label: "About" },
  { id: "/contact", label: "Contact" },
];

export const Header = () => {
  const pathname = usePathname();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleMobileMenuClose = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled ? "bg-white/95 backdrop-blur-sm" : "bg-white"
        }`}
      >
        <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link
              href="/"
              className="text-xl font-semibold tracking-tight hover:opacity-70 transition-opacity"
            >
              FORME
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-12">
              {navItems.map((item) => (
                <Link
                  key={item.id}
                  href={item.id}
                  className={`text-label link-underline ${
                    pathname === item.id
                      ? "text-black"
                      : "text-gray-500 hover:text-black"
                  } transition-colors`}
                >
                  {item.label}
                </Link>
              ))}
            </nav>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 -mr-2"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Bottom border line */}
        <div className="h-px bg-gray-200" />
      </header>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-white md:hidden">
          <div className="flex flex-col items-start justify-center h-full px-8 pt-20">
            <nav className="flex flex-col gap-8">
              {navItems.map((item, index) => (
                <Link
                  key={item.id}
                  href={item.id}
                  onClick={handleMobileMenuClose}
                  className={`text-3xl font-medium text-left animate-slide-in stagger-${index + 1} ${
                    pathname === item.id ? "text-black" : "text-gray-400"
                  }`}
                  style={{ opacity: 0 }}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      )}
    </>
  );
};
