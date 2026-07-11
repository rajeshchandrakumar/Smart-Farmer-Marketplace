# Smart Farmer Marketplace and E-Digital Marketing System

A comprehensive Flask-based digital marketplace that connects farmers directly with buyers and provides e-digital marketing tools for farmers.

## Features

- **Multi-role Authentication**: Admin, Farmer, and Buyer accounts with role-based access control
- **Farmer Module**: Product management, inventory tracking, analytics
- **Buyer Module**: Product browsing, shopping cart, order management, reviews
- **Admin Module**: User management, product approval, platform analytics
- **Marketing Module**: Featured products, promotions, discount management
- **Session-based Authentication**: Secure login/logout functionality
- **Responsive Design**: Mobile-friendly UI using Bootstrap

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Database**: SQLite
- **Authentication**: Session-based with password hashing

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

1. Initialize the database with sample data:
   ```bash
   python db_init.py
   ```
   This creates the database with sample users and products.

## Running the Application

1. Run the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

## Sample Accounts

After running `db_init.py`, the following sample accounts will be available:

### Admin Account
- Email: `admin@smartfarmer.com`
- Password: `admin123`

### Farmer Accounts
- Email: `rajesh@example.com`
- Password: `farmer123`

- Email: `priya@example.com`
- Password: `farmer123`

### Buyer Accounts
- Email: `amit@example.com`
- Password: `buyer123`

- Email: `sneha@example.com`
- Password: `buyer123`

## Project Structure

```
smart-farmer-marketplace/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── database.py               # Database instance
├── requirements.txt          # Dependencies
├── db_init.py                # Database initialization script
├── init_db.py                # Alternative database initialization
├── models/                   # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── farmer.py
│   ├── buyer.py
│   ├── product.py
│   ├── order.py
│   ├── promotion.py
│   └── feedback.py
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── uploads/
└── templates/                # HTML templates
    ├── base.html
    ├── index.html
    ├── auth/
    ├── farmer/
    ├── buyer/
    ├── admin/
    └── marketing/
```

## Functionality Overview

### For Farmers
- Register and login to manage their farm
- Add, edit, and delete products
- Upload product images
- Track product analytics
- Create promotions and discounts

### For Buyers
- Browse and search products
- Add products to cart
- Place orders
- View order history
- Submit feedback and ratings

### For Admins
- Manage users (farmers and buyers)
- Approve or reject product listings
- Monitor orders and transactions
- View platform analytics
- Manage featured products and promotions

## Security Features

- Passwords are securely hashed using Werkzeug
- Session-based authentication
- Input validation and sanitization
- Role-based access control

## Database Schema

The application uses SQLite with the following tables:
- users (id, name, email, password_hash, role, created_at)
- farmers (farmer_id, user_id, farm_name, location, contact_number)
- buyers (buyer_id, user_id, contact_number)
- products (product_id, farmer_id, name, description, category, price, quantity, image_path, status, created_at)
- orders (order_id, buyer_id, total_amount, status, created_at)
- order_items (order_item_id, order_id, product_id, quantity, price)
- promotions (promo_id, product_id, discount_percent, start_date, end_date, description)
- feedback (feedback_id, product_id, buyer_id, rating, comment, created_at)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational purposes. Feel free to use and modify as needed.