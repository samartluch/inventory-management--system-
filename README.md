# 📦 Inventory Management System

A comprehensive web-based inventory management system built with Flask that helps businesses track products, manage stock levels, process orders, and generate reports.

## ✨ Features

### 🔐 User Authentication
- Secure user registration and login system
- Password hashing with Werkzeug security
- Session management with Flask-Login
- User-specific data isolation

### 📊 Dashboard
- Real-time inventory statistics
- Total products count
- Low stock alerts (products with quantity < 10)
- Out of stock notifications
- Total orders tracking
- Recent products overview
- Low stock products display

### 📦 Product Management
- Add new products with detailed information
- Edit existing product details
- Delete products from inventory
- Track product information:
  - Name and description
  - Category
  - Quantity
  - Price
  - Supplier information
  - Creation and update timestamps

### 🔍 Advanced Inventory Features
- **Search & Filter**: Search products by name, description, or supplier
- **Category Filtering**: Filter products by category
- **Stock Status Filtering**: Filter by in-stock, low-stock, or out-of-stock items
- **Multi-column Sorting**: Sort by name, category, quantity, price, total value, or supplier
- **Stock Status Indicators**: Visual badges for stock levels
- **Total Value Calculation**: Automatic calculation of inventory value

### 🛒 Order Management
- Create new orders with multiple items
- Auto-generated unique order numbers (ORD-XXXXXXXX)
- Track customer information (name, email, phone)
- Order status management (pending, completed, cancelled)
- Edit existing orders
- Delete orders
- Automatic inventory updates on order completion
- Order items with quantity and pricing
- Total amount calculation

### 📈 Reporting
- Generate comprehensive inventory reports
- Export data in JSON format
- View total products, quantities, and values
- Category-wise breakdown
- Detailed product listings

## 🛠️ Technologies Used

### Backend
- **Python 3.x** - Programming language
- **Flask 2.3.3** - Web framework
- **Flask-SQLAlchemy 3.0.5** - ORM for database operations
- **Flask-Login 0.6.3** - User session management
- **Werkzeug 2.3.7** - Password hashing and security
- **SQLite** - Database

### Frontend
- **HTML5** - Structure
- **Tailwind CSS** - Styling and responsive design
- **JavaScript** - Interactive features
- **Font Awesome** - Icons

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/username/inventory-management-system.git
cd inventory-management-system
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000/`

### 5. Default Login Credentials
On first run, a test user is automatically created:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change these credentials after first login in a production environment!

## 📁 Project Structure

```
inventory-management-system/
│
├── app.py                  # Main application file with routes and logic
├── models.py              # Database models (User, Product, Order, OrderItem)
├── requirements.txt       # Python dependencies
│
├── instance/
│   └── inventory.db      # SQLite database (auto-generated)
│
├── static/
│   ├── style.css         # Custom CSS styles
│   └── script.js         # JavaScript for interactive features
│
└── templates/
    ├── base.html         # Base template with navigation
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── dashboard.html    # Main dashboard
    ├── inventory.html    # Product listing with search/filter
    ├── add_product.html  # Add new product form
    ├── edit_product.html # Edit product form
    ├── orders.html       # Orders listing
    ├── add_order.html    # Create new order form
    ├── edit_order.html   # Edit order form
    └── report.html       # Inventory reports
```

## 💾 Database Schema

### User Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password_hash` - Hashed password
- `created_at` - Account creation timestamp

### Product Table
- `id` - Primary key
- `name` - Product name
- `category` - Product category
- `quantity` - Stock quantity
- `price` - Unit price
- `supplier` - Supplier information
- `description` - Product description
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `user_id` - Foreign key to User

### Order Table
- `id` - Primary key
- `order_number` - Unique order identifier
- `customer_name` - Customer name
- `customer_email` - Customer email
- `customer_phone` - Customer phone
- `status` - Order status (pending/completed/cancelled)
- `total_amount` - Total order value
- `notes` - Additional notes
- `created_at` - Order creation timestamp
- `updated_at` - Last update timestamp
- `user_id` - Foreign key to User

### OrderItem Table
- `id` - Primary key
- `order_id` - Foreign key to Order
- `product_id` - Foreign key to Product
- `quantity` - Ordered quantity
- `unit_price` - Price at time of order

## 🔑 Key Features Explained

### Stock Level Alerts
- **In Stock**: Quantity ≥ 10 (Green badge)
- **Low Stock**: 0 < Quantity < 10 (Yellow badge)
- **Out of Stock**: Quantity = 0 (Red badge)

### Order Processing
1. Create order with customer details
2. Add multiple products to order
3. System automatically calculates total amount
4. On order completion, inventory is automatically updated
5. Stock quantities are reduced based on order items

### Search & Filter System
- Real-time search across product names, descriptions, and suppliers
- Category-based filtering
- Stock status filtering
- Sortable columns for better data organization

## 🔒 Security Features

- Password hashing using Werkzeug's security functions
- Session-based authentication with Flask-Login
- User-specific data isolation (users can only see their own data)
- CSRF protection (built into Flask)
- SQL injection prevention through SQLAlchemy ORM

## 🎨 User Interface

- Clean and modern design with Tailwind CSS
- Responsive layout for mobile and desktop
- Intuitive navigation
- Visual feedback for user actions (flash messages)
- Color-coded stock status indicators
- Interactive tables with sorting and filtering

## 📝 API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout

### Dashboard
- `GET /dashboard` - Main dashboard view

### Products
- `GET /inventory` - View all products
- `GET/POST /add_product` - Add new product
- `GET/POST /edit_product/<id>` - Edit product
- `POST /delete_product/<id>` - Delete product

### Orders
- `GET /orders` - View all orders
- `GET/POST /add_order` - Create new order
- `GET/POST /edit_order/<id>` - Edit order
- `POST /delete_order/<id>` - Delete order
- `POST /complete_order/<id>` - Mark order as completed

### Reports
- `GET /report` - View reports page
- `GET /api/report` - Get report data (JSON)

## 🚧 Future Enhancements

- [ ] Export reports to PDF/Excel
- [ ] Barcode/QR code generation for products
- [ ] Email notifications for low stock
- [ ] Multi-user roles (admin, manager, staff)
- [ ] Product images upload
- [ ] Advanced analytics and charts
- [ ] Supplier management module
- [ ] Purchase order management
- [ ] Inventory forecasting
- [ ] Mobile app integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

Your Name - [GitHub Profile](https://github.com/username)

## 🙏 Acknowledgments

- Flask documentation and community
- Tailwind CSS for the styling framework
- Font Awesome for icons

---

**Note**: Remember to change the default admin credentials and update the `SECRET_KEY` in `app.py` before deploying to production!





