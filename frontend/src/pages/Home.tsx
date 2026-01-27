import { Link } from 'react-router-dom';
import { 
  ShoppingBag, 
  ArrowRight, 
  Sparkles, 
  TrendingUp, 
  Shield, 
  Zap,
  Package,
  Tag,
  Star,
  Smartphone,
  Shirt,
  Footprints,
  Home as HomeIcon,
  Dumbbell,
  ChevronRight
} from 'lucide-react';
import { categories, products } from '@/data/mockData';

const iconMap: Record<string, React.ElementType> = {
  Smartphone,
  Shirt,
  Footprints,
  Home: HomeIcon,
  Dumbbell,
  Sparkles,
};

export default function Home() {
  const featuredProducts = products.slice(0, 4);
  const newArrivals = products.filter(p => p.isNew).slice(0, 4);

  return (
    <div className="min-h-screen bg-[#FFFEF9] tg-webapp">
      {/* Header */}
      <header className="neo-header sticky top-0 z-50">
        <div className="max-w-md mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#FCD34D] border-2 border-black rounded-xl flex items-center justify-center">
                <ShoppingBag className="w-5 h-5 text-black" />
              </div>
              <div>
                <h1 className="text-lg font-black text-black leading-none">mdm bot</h1>
                <p className="text-xs font-medium text-gray-500">магазин</p>
              </div>
            </div>
            <Link to="/catalog">
              <button className="neo-btn text-sm py-2 px-3">
                <span className="hidden sm:inline">в магазин</span>
                <ArrowRight className="w-4 h-4 sm:hidden" />
              </button>
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-md mx-auto px-4 py-4 pb-24">
        {/* Hero Section */}
        <section className="mb-6">
          <div className="neo-card bg-[#FCD34D] p-5 relative overflow-hidden">
            <div className="absolute top-2 right-2 w-8 h-8 bg-white border-2 border-black rounded-full flex items-center justify-center transform rotate-12">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="absolute bottom-4 right-8 w-4 h-4 bg-black rounded-full opacity-20" />
            <div className="absolute top-8 right-16 w-2 h-2 bg-black rounded-full opacity-20" />
            
            <div className="relative z-10">
              <span className="neo-sticker mb-3 inline-block">новинки 2025</span>
              <h2 className="text-2xl font-black text-black mb-2 lowercase">
                открой мир<br/>шопинга
              </h2>
              <p className="text-sm font-medium text-black/70 mb-4">
                10 000+ товаров от топовых брендов
              </p>
              <Link to="/catalog">
                <button className="neo-btn-secondary w-full flex items-center justify-center gap-2 text-sm">
                  <ShoppingBag className="w-4 h-4" />
                  смотреть товары
                </button>
              </Link>
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="mb-6">
          <div className="grid grid-cols-3 gap-3">
            <div className="neo-card p-3 text-center">
              <div className="text-xl font-black text-black">10K+</div>
              <div className="text-xs font-medium text-gray-500">товаров</div>
            </div>
            <div className="neo-card p-3 text-center">
              <div className="text-xl font-black text-black">50K+</div>
              <div className="text-xs font-medium text-gray-500">клиентов</div>
            </div>
            <div className="neo-card p-3 text-center">
              <div className="text-xl font-black text-black">4.9</div>
              <div className="text-xs font-medium text-gray-500">рейтинг</div>
            </div>
          </div>
        </section>

        {/* Categories */}
        <section className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-black lowercase">категории</h3>
            <Link to="/catalog" className="text-sm font-bold text-black flex items-center gap-1">
              все <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="flex gap-3 overflow-x-auto scrollbar-hide pb-2 -mx-4 px-4">
            {categories.map((category) => {
              const IconComponent = iconMap[category.icon] || Package;
              return (
                <Link 
                  key={category.id} 
                  to="/catalog"
                  className="flex-shrink-0"
                >
                  <div className="neo-card-hover p-3 w-24 text-center">
                    <div className="w-10 h-10 bg-[#FCD34D] border-2 border-black rounded-xl flex items-center justify-center mx-auto mb-2">
                      <IconComponent className="w-5 h-5" />
                    </div>
                    <span className="text-xs font-bold block truncate">{category.name}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* New Arrivals */}
        <section className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-black lowercase">новинки</h3>
              <span className="neo-badge">hot</span>
            </div>
            <Link to="/catalog" className="text-sm font-bold text-black flex items-center gap-1">
              все <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            {newArrivals.map((product) => (
              <div key={product.id} className="neo-product-card">
                <div className="relative h-28 bg-gray-100 border-b-2 border-black flex items-center justify-center">
                  <Package className="w-10 h-10 text-gray-400" />
                  <div className="absolute top-2 left-2">
                    <span className="neo-badge text-[10px]">new</span>
                  </div>
                </div>
                <div className="p-3">
                  <h4 className="font-bold text-sm mb-1 line-clamp-1">{product.name}</h4>
                  <p className="text-xs text-gray-500 mb-2 line-clamp-1">{product.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="font-black text-sm">{product.price.toLocaleString()} ₽</span>
                    <div className="flex items-center gap-1">
                      <Star className="w-3 h-3 fill-[#FCD34D] text-black" />
                      <span className="text-xs font-bold">{product.rating}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Popular Products */}
        <section className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-black lowercase">популярное</h3>
              <div className="w-6 h-6 bg-red-400 border-2 border-black rounded-full flex items-center justify-center">
                <TrendingUp className="w-3 h-3 text-white" />
              </div>
            </div>
            <Link to="/catalog" className="text-sm font-bold text-black flex items-center gap-1">
              все <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="space-y-3">
            {featuredProducts.slice(0, 3).map((product) => (
              <div key={product.id} className="neo-card-hover flex gap-3 p-3">
                <div className="w-16 h-16 bg-gray-100 border-2 border-black rounded-xl flex-shrink-0 flex items-center justify-center">
                  <Package className="w-6 h-6 text-gray-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-bold text-sm mb-1 truncate">{product.name}</h4>
                  <p className="text-xs text-gray-500 mb-2 line-clamp-1">{product.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="font-black text-sm">{product.price.toLocaleString()} ₽</span>
                    <button className="w-7 h-7 bg-[#FCD34D] border-2 border-black rounded-lg flex items-center justify-center">
                      <ShoppingBag className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Features */}
        <section className="mb-6">
          <h3 className="text-lg font-black lowercase mb-3">почему мы</h3>
          <div className="space-y-3">
            <div className="neo-card flex items-center gap-3 p-3">
              <div className="w-10 h-10 bg-green-400 border-2 border-black rounded-xl flex items-center justify-center flex-shrink-0">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="font-bold text-sm">быстрая доставка</h4>
                <p className="text-xs text-gray-500">от 1 дня по всей россии</p>
              </div>
            </div>
            
            <div className="neo-card flex items-center gap-3 p-3">
              <div className="w-10 h-10 bg-blue-400 border-2 border-black rounded-xl flex items-center justify-center flex-shrink-0">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="font-bold text-sm">гарантия качества</h4>
                <p className="text-xs text-gray-500">возврат за 14 дней</p>
              </div>
            </div>
            
            <div className="neo-card flex items-center gap-3 p-3">
              <div className="w-10 h-10 bg-pink-400 border-2 border-black rounded-xl flex items-center justify-center flex-shrink-0">
                <Tag className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="font-bold text-sm">лучшие цены</h4>
                <p className="text-xs text-gray-500">скидки каждый день</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section>
          <div className="neo-card bg-[#FCD34D] p-5 text-center">
            <h3 className="text-xl font-black lowercase mb-2">
              готов к покупкам?
            </h3>
            <p className="text-sm font-medium text-black/70 mb-4">
              присоединяйся к тысячам довольных клиентов
            </p>
            <Link to="/catalog">
              <button className="neo-btn-secondary w-full flex items-center justify-center gap-2">
                <ShoppingBag className="w-4 h-4" />
                в каталог
              </button>
            </Link>
          </div>
        </section>
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-black px-4 py-2 z-50">
        <div className="max-w-md mx-auto flex items-center justify-around">
          <Link to="/" className="flex flex-col items-center gap-1 p-2">
            <div className="w-10 h-10 bg-[#FCD34D] border-2 border-black rounded-xl flex items-center justify-center">
              <HomeIcon className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold">главная</span>
          </Link>
          <Link to="/catalog" className="flex flex-col items-center gap-1 p-2">
            <div className="w-10 h-10 bg-white border-2 border-black rounded-xl flex items-center justify-center">
              <Package className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold">каталог</span>
          </Link>
          <button className="flex flex-col items-center gap-1 p-2">
            <div className="w-10 h-10 bg-white border-2 border-black rounded-xl flex items-center justify-center relative">
              <ShoppingBag className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-400 border-2 border-black rounded-full text-white text-xs font-bold flex items-center justify-center">
                0
              </span>
            </div>
            <span className="text-xs font-bold">корзина</span>
          </button>
        </div>
      </nav>
    </div>
  );
}
