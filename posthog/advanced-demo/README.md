# PostHog Advanced Demo - E-commerce Application

A comprehensive e-commerce-style Next.js application demonstrating advanced PostHog analytics tracking with multiple user flows, conversion funnels, and detailed event tracking.

## Features

### 🛍️ E-commerce Features
- **Product Catalog** - Browse products with filtering and search
- **Product Details** - Detailed product pages with reviews
- **Shopping Cart** - Add/remove items, update quantities
- **Checkout Flow** - Multi-step checkout process
- **User Dashboard** - Order history and account management
- **Authentication** - Signup and login flows

### 📊 PostHog Analytics Tracking

**Page Views:**
- `homepage_viewed`
- `products_page_viewed`
- `product_detail_viewed`
- `cart_viewed`
- `checkout_page_viewed`
- `dashboard_viewed`

**User Actions:**
- `cta_clicked` - Button clicks (Shop Now, Sign Up)
- `product_viewed` - Product detail views
- `product_preview_clicked` - Homepage product clicks
- `add_to_cart` - Add to cart actions
- `cart_item_quantity_changed` - Cart updates
- `cart_item_removed` - Remove from cart
- `product_filter_applied` - Category filtering
- `product_search_performed` - Search queries
- `checkout_started` - Begin checkout
- `checkout_step_completed` - Multi-step progress
- `checkout_form_field_filled` - Form interactions
- `order_completed` - Purchase completion
- `signup_completed` - User registration
- `login_completed` - User login
- `feature_explored` - Feature interactions
- `reviews_viewed` - Product review views
- `buy_now_clicked` - Direct purchase

**User Identification:**
- User identification on signup/login
- User properties tracking
- Order history tracking

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd ductt-demo/posthog/advanced-demo
npm install
```

### Step 2: Run the Development Server

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

### Step 3: Generate Demo Data

1. **Browse Products:**
   - Visit homepage → Click "Shop Now"
   - Filter by category
   - Search for products
   - Click on products to view details

2. **Shopping Flow:**
   - Add products to cart
   - Update quantities
   - Remove items
   - Proceed to checkout

3. **Checkout Flow:**
   - Fill shipping information
   - Enter payment details
   - Review order
   - Complete purchase

4. **User Journey:**
   - Sign up for account
   - Login
   - View dashboard
   - Browse products
   - Make purchases

5. **Multiple Users:**
   - Open 5-10 incognito windows
   - Complete different flows
   - Some users abandon cart
   - Some users complete purchase
   - Some users just browse

6. **Wait 5-10 minutes** for PostHog to process

## PostHog Configuration

- **API Key**: `phc_B6jEmPA78ravxUqMDifZNNfdLSdZ1152BL076QzDPcv`
- **Host**: `https://us.i.posthog.com`
- **Autocapture**: Enabled
- **Session Replay**: Enabled
- **Page View Tracking**: Enabled

## Creating Analytics Insights

### 1. E-commerce Funnel
Create a funnel showing:
1. `homepage_viewed`
2. `products_page_viewed`
3. `product_detail_viewed`
4. `add_to_cart`
5. `checkout_started`
6. `checkout_step_completed` (step 1)
7. `checkout_step_completed` (step 2)
8. `order_completed`

### 2. Conversion Funnel
Track conversion from:
- Homepage → Products → Cart → Checkout → Purchase

### 3. Product Analytics
- Most viewed products
- Most added to cart
- Search queries
- Category preferences

### 4. User Behavior
- Time to purchase
- Cart abandonment rate
- Checkout completion rate
- Feature usage

### 5. Session Replay
- Watch users who abandoned cart
- See checkout drop-offs
- Understand product browsing patterns

## Project Structure

```
advanced-demo/
├── app/
│   ├── layout.tsx              # Root layout with navigation
│   ├── providers.tsx            # PostHog provider
│   ├── page.tsx                 # Homepage
│   ├── products/
│   │   ├── page.tsx             # Products listing
│   │   └── [id]/
│   │       └── page.tsx         # Product detail
│   ├── cart/
│   │   └── page.tsx             # Shopping cart
│   ├── checkout/
│   │   └── page.tsx             # Checkout flow
│   ├── signup/
│   │   └── page.tsx             # Signup page
│   ├── login/
│   │   └── page.tsx             # Login page
│   └── dashboard/
│       └── page.tsx             # User dashboard
├── package.json
└── README.md
```

## Event Tracking Details

### Product Interactions
- Product views with product details
- Add to cart with product info
- Product searches with query terms
- Category filters
- Product preview clicks

### Cart Interactions
- Cart views with item count and total value
- Quantity changes
- Item removals
- Cart abandonment tracking

### Checkout Flow
- Multi-step tracking
- Form field interactions
- Step completion
- Order completion with value

### User Actions
- Signup with user properties
- Login tracking
- Dashboard interactions
- Feature exploration

## Demo Scenarios

### Scenario 1: Successful Purchase
1. Visit homepage
2. Browse products
3. View product details
4. Add to cart
5. Complete checkout
6. Place order

### Scenario 2: Cart Abandonment
1. Visit homepage
2. Add products to cart
3. View cart
4. Start checkout
5. Abandon at payment step

### Scenario 3: Product Research
1. Visit homepage
2. Search products
3. Filter by category
4. View multiple products
5. Leave without purchasing

## Next Steps

1. Generate demo data by interacting with the app
2. Wait 5-10 minutes for PostHog to process
3. Create funnels and insights in PostHog dashboard
4. Watch session replays to understand user behavior
5. Analyze conversion rates and drop-off points

This advanced demo provides comprehensive analytics data for showcasing PostHog's capabilities!
