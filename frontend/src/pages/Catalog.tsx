import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Search, 
  ShoppingCart, 
  ShoppingBag,
  Star, 
  Heart,
  Package,
  X,
  ChevronDown,
  Grid3X3,
  List,
  Percent,
  Home as HomeIcon,
  SlidersHorizontal
} from 'lucide-react';
import { categories, products } from '@/data/mockData';

const iconMap: Record<string, React.ElementType> = {
  Smartphone: Package,
  Shirt: Package,
  Footprints: Package,
  Home: Package,
  Dumbbell: Package,
  Sparkles: Package,
};

export default function Catalog() {
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'popular' | 'price-asc' | 'price-desc' | 'new'>('popular');
  const [favorites, setFavorites] = useState<number[]>([]);
  const [cart, setCart] = useState<number[]>([]);
  const [showSortMenu, setShowSortMenu] = useState(false);

  const filteredProducts = useMemo(() => {
    let result = [...products];
    
    if (selectedCategory !== null) {
      result = result.filter(p => p.categoryId === selectedCategory);
    }
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(p => 
        p.name.toLowerCase().includes(query) || 
        p.description.toLowerCase().includes(query)
      );
    }
    
    switch (sortBy) {
      case 'price-asc':
        result.sort((a, b) => a.price - b.price);
        break;
      case 'price-desc':
        result.sort((a, b) => b.price - a.price);
        break;
      case 'new':
        result.sort((a, b) => (b.isNew ? 1 : 0) - (a.isNew ? 1 : 0));
        break;
      default:
        result.sort((a, b) => b.rating - a.rating);
    }
    
    return result;
  }, [selectedCategory, searchQuery, sortBy]);

  const toggleFavorite = (id: number) => {
    setFavorites(prev => 
      prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]
    );
  };

  const addToCart = (id: number) => {
    setCart(prev => [...prev, id]);
  };

  const clearFilters = () => {
    setSelectedCategory(null);
    setSearchQuery('');
    setSortBy('popular');
  };

  const hasActiveFilters = selectedCategory !== null || searchQuery || sortBy !== 'popular';

  const sortLabels: Record<string, string> = {
    'popular': 'по популярности',
    'price-asc': 'сначала дешевле',
    'price-desc': 'сначала дороже',
    'new': 'сначала новые'
  };

  return (
    <div className="min-h-screen bg-[#FFFEF9] tg-webapp">
      {/* Header */}
      <header className="neo-header sticky top-0 z-50">
        <div className="max-w-md mx-auto px-4 py-3">
          <div className="flex items-center gap-3">
            <Link to="/">
              <button className="w-10 h-10 bg-white border-2 border-black rounded-xl flex items-center justify-center">
                <ArrowLeft className="w-5 h-5" />
              </button>
            </Link>
            <div className="flex-1">
              <h1 className="text-lg font-black lowercase">каталог</h1>
              <p className="text-xs font-medium text-gray-500">{filteredProducts.length} товаров</p>
            </div>
            <button className="w-10 h-10 bg-white border-2 border-black rounded-xl flex items-center justify-center relative">
              <ShoppingCart className="w-5 h-5" />
              {cart.length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-400 border-2 border-black rounded-full text-white text-xs font-bold flex items-center justify-center">
                  {cart.length}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Search Bar */}
      <div className="bg-white border-b-2 border-black px-4 py-3">
        <div className="max-w-md mx-auto">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="поиск товаров..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="neo-input w-full pl-10 pr-10 text-sm"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="bg-white border-b-2 border-black px-4 py-3 sticky top-[57px] z-40">
        <div className="max-w-md mx-auto">
          <div className="flex gap-2 overflow-x-auto scrollbar-hide -mx-4 px-4">
            <button
              onClick={() => setSelectedCategory(null)}
              className={selectedCategory === null ? 'neo-pill-active' : 'neo-pill'}
            >
              все
            </button>
            {categories.map((category) => {
              const IconComponent = iconMap[category.icon] || Package;
              const isSelected = selectedCategory === category.id;
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={isSelected ? 'neo-pill-active' : 'neo-pill'}
                >
                  <IconComponent className="w-4 h-4" />
                  <span className="truncate">{category.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-md mx-auto px-4 py-4 pb-28">
        {/* Toolbar */}
        <div className="flex items-center justify-between mb-4">
          <div className="relative">
            <button 
              onClick={() => setShowSortMenu(!showSortMenu)}
              className="neo-pill text-xs"
            >
              <SlidersHorizontal className="w-3 h-3" />
              {sortLabels[sortBy]}
              <ChevronDown className={`w-3 h-3 transition-transform ${showSortMenu ? 'rotate-180' : ''}`} />
            </button>
            
            {showSortMenu && (
              <div 
                className="absolute top-full left-0 mt-2 bg-white border-2 border-black rounded-xl overflow-hidden z-20 min-w-[160px]"
                style={{ boxShadow: '4px 4px 0px 0px rgba(0,0,0,1)' }}
              >
                {Object.entries(sortLabels).map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => {
                      setSortBy(key as any);
                      setShowSortMenu(false);
                    }}
                    className={`w-full px-4 py-2 text-left text-sm font-medium hover:bg-gray-50 ${
                      sortBy === key ? 'bg-[#FCD34D]' : ''
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <div className="flex bg-white border-2 border-black rounded-xl p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-lg transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-[#FCD34D] border-2 border-black' 
                    : 'text-gray-400'
                }`}
              >
                <Grid3X3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-1.5 rounded-lg transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-[#FCD34D] border-2 border-black' 
                    : 'text-gray-400'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
            
            {hasActiveFilters && (
              <button 
                onClick={clearFilters}
                className="w-8 h-8 bg-red-100 border-2 border-black rounded-lg flex items-center justify-center"
              >
                <X className="w-4 h-4 text-red-500" />
              </button>
            )}
          </div>
        </div>

        {/* Products */}
        {filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-gray-100 border-2 border-black rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-black mb-2">ничего не найдено</h3>
            <p className="text-sm text-gray-500 mb-4">попробуй изменить поиск</p>
            <button onClick={clearFilters} className="neo-btn text-sm">
              сбросить фильтры
            </button>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-2 gap-3' : 'space-y-3'}>
            {filteredProducts.map((product) => (
              <div
                key={product.id}
                className={viewMode === 'grid' ? 'neo-product-card' : 'neo-card-hover flex gap-3 p-3'}
              >
                <div className={`relative bg-gray-100 flex items-center justify-center overflow-hidden ${
                  viewMode === 'grid' 
                    ? 'h-32 border-b-2 border-black' 
                    : 'w-20 h-20 border-2 border-black rounded-xl flex-shrink-0'
                }`}>
                  <Package className={`text-gray-300 ${viewMode === 'grid' ? 'w-10 h-10' : 'w-8 h-8'}`} />
                  
                  <div className={`absolute flex flex-col gap-1 ${viewMode === 'grid' ? 'top-2 left-2' : 'top-1 left-1'}`}>
                    {product.isNew && (
                      <span className={`neo-badge ${viewMode === 'list' ? 'text-[10px] px-2 py-0.5' : ''}`}>new</span>
                    )}
                    {product.discount && (
                      <span className={`bg-red-400 text-white border-2 border-black rounded-full font-bold flex items-center gap-0.5 ${viewMode === 'list' ? 'text-[10px] px-2 py-0.5' : 'text-xs px-2 py-0.5'}`}>
                        <Percent className="w-3 h-3" />
                        -{product.discount}%
                      </span>
                    )}
                  </div>
                  
                  <button
                    onClick={() => toggleFavorite(product.id)}
                    className={`absolute bg-white border-2 border-black rounded-full flex items-center justify-center transition-colors ${
                      viewMode === 'grid' ? 'top-2 right-2 w-8 h-8' : 'top-1 right-1 w-6 h-6'
                    } ${favorites.includes(product.id) ? 'bg-red-100' : ''}`}
                  >
                    <Heart className={`${viewMode === 'grid' ? 'w-4 h-4' : 'w-3 h-3'} ${favorites.includes(product.id) ? 'fill-red-500 text-red-500' : 'text-gray-400'}`} />
                  </button>
                </div>
                
                <div className={viewMode === 'grid' ? 'p-3' : 'flex-1 min-w-0'}>
                  <h3 className={`font-bold text-black mb-1 ${viewMode === 'grid' ? 'text-sm line-clamp-2' : 'text-sm truncate'}`}>
                    {product.name}
                  </h3>
                  
                  {viewMode === 'grid' && (
                    <p className="text-xs text-gray-500 mb-2 line-clamp-1">
                      {product.description}
                    </p>
                  )}
                  
                  <div className="flex items-center gap-1 mb-2">
                    <Star className={`fill-[#FCD34D] text-black ${viewMode === 'grid' ? 'w-3 h-3' : 'w-3 h-3'}`} />
                    <span className={`font-bold ${viewMode === 'grid' ? 'text-xs' : 'text-xs'}`}>{product.rating}</span>
                    <span className="text-xs text-gray-400">({product.reviews})</span>
                  </div>
                  
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <span className={`font-black ${viewMode === 'grid' ? 'text-sm' : 'text-base'}`}>
                        {product.discount 
                          ? Math.round(product.price * (1 - product.discount / 100)).toLocaleString()
                          : product.price.toLocaleString()
                        } ₽
                      </span>
                      {product.discount && viewMode === 'grid' && (
                        <span className="text-xs text-gray-400 line-through ml-1">
                          {product.price.toLocaleString()} ₽
                        </span>
                      )}
                    </div>
                    
                    <button
                      onClick={() => addToCart(product.id)}
                      className={`bg-[#FCD34D] border-2 border-black rounded-lg flex items-center justify-center transition-all active:translate-x-[2px] active:translate-y-[2px] active:shadow-none ${
                        viewMode === 'grid' 
                          ? 'w-8 h-8' 
                          : 'px-3 py-1.5'
                      }`}
                      style={{ boxShadow: '2px 2px 0px 0px rgba(0,0,0,1)' }}
                    >
                      <ShoppingBag className={viewMode === 'grid' ? 'w-4 h-4' : 'w-4 h-4 mr-1'} />
                      {viewMode === 'list' && <span className="text-xs font-bold">в корзину</span>}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-black px-4 py-2 z-50">
        <div className="max-w-md mx-auto flex items-center justify-around">
          <Link to="/" className="flex flex-col items-center gap-1 p-2">
            <div className="w-10 h-10 bg-white border-2 border-black rounded-xl flex items-center justify-center">
              <HomeIcon className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold">главная</span>
          </Link>
          <Link to="/catalog" className="flex flex-col items-center gap-1 p-2">
            <div className="w-10 h-10 bg-[#FCD34D] border-2 border-black rounded-xl flex items-center justify-center">
              <Package className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold">каталог</span>
          </Link>
          <button className="flex flex-col items-center gap-1 p-2">
            <div className="w-10 h-10 bg-white border-2 border-black rounded-xl flex items-center justify-center relative">
              <ShoppingCart className="w-5 h-5" />
              {cart.length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-400 border-2 border-black rounded-full text-white text-xs font-bold flex items-center justify-center">
                  {cart.length}
                </span>
              )}
            </div>
            <span className="text-xs font-bold">корзина</span>
          </button>
        </div>
      </nav>

      {showSortMenu && (
        <div 
          className="fixed inset-0 z-10" 
          onClick={() => setShowSortMenu(false)}
        />
      )}
    </div>
  );
}
