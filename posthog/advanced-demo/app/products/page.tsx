'use client'
import { useRouter } from 'next/navigation'
import { usePostHog } from 'posthog-js/react'
import { useEffect, useState } from 'react'

const products = [
  { id: 1, name: 'Wireless Headphones', price: 99, category: 'Electronics', image: '🎧', stock: 50 },
  { id: 2, name: 'Smart Watch', price: 199, category: 'Electronics', image: '⌚', stock: 30 },
  { id: 3, name: 'Laptop Stand', price: 49, category: 'Accessories', image: '💻', stock: 100 },
  { id: 4, name: 'USB-C Cable', price: 19, category: 'Accessories', image: '🔌', stock: 200 },
  { id: 5, name: 'Mechanical Keyboard', price: 129, category: 'Electronics', image: '⌨️', stock: 40 },
  { id: 6, name: 'Gaming Mouse', price: 79, category: 'Electronics', image: '🖱️', stock: 60 },
  { id: 7, name: 'Monitor Stand', price: 39, category: 'Accessories', image: '🖥️', stock: 80 },
  { id: 8, name: 'Webcam HD', price: 89, category: 'Electronics', image: '📹', stock: 25 },
]

export default function ProductsPage() {
  const router = useRouter()
  const posthog = usePostHog()
  const [selectedCategory, setSelectedCategory] = useState<string>('All')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    posthog?.capture('products_page_viewed', {
      page: 'products',
      total_products: products.length,
    })
  }, [posthog])

  const categories = ['All', ...Array.from(new Set(products.map(p => p.category)))]

  const filteredProducts = products.filter(p => {
    const matchesCategory = selectedCategory === 'All' || p.category === selectedCategory
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    posthog?.capture('product_filter_applied', {
      filter_type: 'category',
      filter_value: category,
      page: 'products',
    })
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    if (query) {
      posthog?.capture('product_search_performed', {
        search_query: query,
        results_count: filteredProducts.length,
        page: 'products',
      })
    }
  }

  const handleAddToCart = (product: typeof products[0]) => {
    posthog?.capture('add_to_cart', {
      product_id: product.id,
      product_name: product.name,
      product_price: product.price,
      product_category: product.category,
      page: 'products',
    })
    alert(`${product.name} added to cart!`)
  }

  const handleProductClick = (product: typeof products[0]) => {
    posthog?.capture('product_viewed', {
      product_id: product.id,
      product_name: product.name,
      product_price: product.price,
      product_category: product.category,
      page: 'products',
    })
    router.push(`/products/${product.id}`)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-bold mb-8">Our Products</h1>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex-1 min-w-[200px]">
              <input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="flex gap-2">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => handleCategoryChange(cat)}
                  className={`px-4 py-2 rounded-lg transition ${
                    selectedCategory === cat
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition overflow-hidden"
            >
              <div
                onClick={() => handleProductClick(product)}
                className="cursor-pointer"
              >
                <div className="text-6xl text-center py-8 bg-gray-50">{product.image}</div>
                <div className="p-4">
                  <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
                  <p className="text-gray-600 text-sm mb-2">{product.category}</p>
                  <p className="text-indigo-600 font-bold text-xl mb-2">${product.price}</p>
                  <p className="text-sm text-gray-500">In stock: {product.stock}</p>
                </div>
              </div>
              <div className="p-4 pt-0">
                <button
                  onClick={() => handleAddToCart(product)}
                  className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition"
                >
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>

        {filteredProducts.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600">No products found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  )
}
