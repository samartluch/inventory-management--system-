from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string

# Initialize extensions
db = SQLAlchemy()

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    supplier = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'price': self.price,
            'supplier': self.supplier,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(20))
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'total_amount': self.total_amount,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }

# OrderItem model
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    # Relationship
    product = db.relationship('Product', backref='order_items')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown',
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.quantity * self.unit_price
        }

def generate_order_number():
    """Generate a unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'ORD-{timestamp}-{random_str}'

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_test_user():
    """Create a test user if none exists"""
    with app.app_context():
        if User.query.count() == 0:
            test_user = User(username='admin', email='admin@example.com')
            test_user.set_password('admin123')
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: admin / admin123")

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Debug print to see what's being submitted
        print(f"Login attempt - Username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"User found: {user.username}")
            print(f"Password check: {user.check_password(password)}")
        else:
            print("User not found")
        
        if user and user.check_password(password):
            login_user(user)
            print(f"Login successful for user: {username}")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            print("Login failed - invalid credentials")
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get products for current user
        products = Product.query.filter_by(user_id=current_user.id).all()
        total_products = len(products)
        
        # Calculate stock status
        low_stock = len([p for p in products if p.quantity < 10 and p.quantity > 0])
        out_of_stock = len([p for p in products if p.quantity == 0])
        
        # Order statistics
        total_orders = Order.query.filter_by(user_id=current_user.id).count()
        
        # Get recent products
        recent_products = Product.query.filter_by(user_id=current_user.id).order_by(Product.created_at.desc()).limit(5).all()
        
        # Get low stock products for alert
        low_stock_products = Product.query.filter(
            Product.user_id == current_user.id, 
            Product.quantity < 10,
            Product.quantity > 0
        ).order_by(Product.quantity.asc()).limit(6).all()
        
        return render_template('dashboard.html', 
                             total_products=total_products, 
                             low_stock=low_stock,
                             out_of_stock=out_of_stock,
                             total_orders=total_orders,
                             recent_products=recent_products,
                             low_stock_products=low_stock_products)
    except Exception as e:
        print(f"Error in dashboard route: {e}")
        flash('Error loading dashboard', 'error')
        return render_template('dashboard.html', 
                             total_products=0, 
                             low_stock=0,
                             out_of_stock=0,
                             total_orders=0,
                             recent_products=[],
                             low_stock_products=[])

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            category = request.form.get('category')
            quantity = int(request.form.get('quantity'))
            price = float(request.form.get('price'))
            supplier = request.form.get('supplier')
            description = request.form.get('description')
            
            product = Product(
                name=name,
                category=category,
                quantity=quantity,
                price=price,
                supplier=supplier,
                description=description,
                user_id=current_user.id
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('inventory'))
        except ValueError:
            flash('Please enter valid numeric values for quantity and price.', 'error')
        except Exception as e:
            flash('An error occurred while adding the product.', 'error')
    
    return render_template('add_product.html')

@app.route('/inventory')
@login_required
def inventory():
    products = Product.query.filter_by(user_id=current_user.id).all()
    # Get unique categories for the filter dropdown
    categories = list(set(product.category for product in products if product.category))
    categories.sort()
    
    return render_template('inventory.html', products=products, categories=categories)

@app.route('/api/products')
@login_required
def api_products():
    products = Product.query.filter_by(user_id=current_user.id).all()
    return jsonify([product.to_dict() for product in products])

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            product.name = request.form.get('name')
            product.category = request.form.get('category')
            product.quantity = int(request.form.get('quantity'))
            product.price = float(request.form.get('price'))
            product.supplier = request.form.get('supplier')
            product.description = request.form.get('description')
            product.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('inventory'))
        except ValueError:
            flash('Please enter valid numeric values for quantity and price.', 'error')
        except Exception as e:
            flash('An error occurred while updating the product.', 'error')
    
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash('An error occurred while deleting the product.', 'error')
    
    return redirect(url_for('inventory'))

# Order Routes
@app.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/add_order', methods=['GET', 'POST'])
@login_required
def add_order():
    if request.method == 'POST':
        try:
            # Create order
            order = Order(
                order_number=generate_order_number(),
                customer_name=request.form.get('customer_name'),
                customer_email=request.form.get('customer_email'),
                customer_phone=request.form.get('customer_phone'),
                notes=request.form.get('notes'),
                user_id=current_user.id
            )
            
            db.session.add(order)
            db.session.flush()  # Get order ID without committing
            
            # Process order items
            total_amount = 0
            product_ids = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')
            
            for i, product_id in enumerate(product_ids):
                if quantities[i] and int(quantities[i]) > 0:
                    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first()
                    if product:
                        quantity = int(quantities[i])
                        if quantity <= product.quantity:
                            # Create order item
                            order_item = OrderItem(
                                order_id=order.id,
                                product_id=product_id,
                                quantity=quantity,
                                unit_price=product.price
                            )
                            db.session.add(order_item)
                            
                            # Update product quantity
                            product.quantity -= quantity
                            product.updated_at = datetime.utcnow()
                            
                            total_amount += quantity * product.price
            
            order.total_amount = total_amount
            db.session.commit()
            
            flash('Order created successfully!', 'success')
            return redirect(url_for('orders'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the order.', 'error')
    
    # Get available products for the form and convert to dictionaries
    products = Product.query.filter_by(user_id=current_user.id).filter(Product.quantity > 0).all()
    products_data = [{
        'id': p.id,
        'name': p.name,
        'quantity': p.quantity,
        'price': float(p.price),
        'category': p.category
    } for p in products]
    
    return render_template('add_order.html', products=products_data)

@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Update order details
            order.customer_name = request.form.get('customer_name')
            order.customer_email = request.form.get('customer_email')
            order.customer_phone = request.form.get('customer_phone')
            order.status = request.form.get('status')
            order.notes = request.form.get('notes')
            order.updated_at = datetime.utcnow()
            
            # If status changed to cancelled, restore product quantities
            if order.status == 'cancelled':
                for item in order.items:
                    product = Product.query.get(item.product_id)
                    if product and product.user_id == current_user.id:
                        product.quantity += item.quantity
                        product.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Order updated successfully!', 'success')
            return redirect(url_for('orders'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the order.', 'error')
    
    return render_template('edit_order.html', order=order)

@app.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    try:
        # Restore product quantities before deleting
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product and product.user_id == current_user.id:
                product.quantity += item.quantity
                product.updated_at = datetime.utcnow()
        
        db.session.delete(order)
        db.session.commit()
        flash('Order deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the order.', 'error')
    
    return redirect(url_for('orders'))

@app.route('/api/orders')
@login_required
def api_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/products/available')
@login_required
def api_available_products():
    products = Product.query.filter_by(user_id=current_user.id).filter(Product.quantity > 0).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'quantity': p.quantity,
        'price': p.price,
        'category': p.category
    } for p in products])

@app.route('/report')
@login_required
def report():
    products = Product.query.filter_by(user_id=current_user.id).all()
    total_quantity = sum(product.quantity for product in products)
    total_value = sum(product.quantity * product.price for product in products)
    
    # Calculate category-wise breakdown
    categories = {}
    for product in products:
        if product.category not in categories:
            categories[product.category] = {'count': 0, 'quantity': 0, 'value': 0}
        categories[product.category]['count'] += 1
        categories[product.category]['quantity'] += product.quantity
        categories[product.category]['value'] += product.quantity * product.price
    
    return render_template('report.html', 
                         products=products, 
                         total_quantity=total_quantity, 
                         total_value=total_value,
                         categories=categories)

@app.route('/api/report')
@login_required
def api_report():
    products = Product.query.filter_by(user_id=current_user.id).all()
    total_quantity = sum(product.quantity for product in products)
    total_value = sum(product.quantity * product.price for product in products)
    
    # Category breakdown
    categories = {}
    for product in products:
        if product.category not in categories:
            categories[product.category] = {'count': 0, 'quantity': 0, 'value': 0}
        categories[product.category]['count'] += 1
        categories[product.category]['quantity'] += product.quantity
        categories[product.category]['value'] += product.quantity * product.price
    
    report_data = {
        'total_products': len(products),
        'total_quantity': total_quantity,
        'total_value': round(total_value, 2),
        'categories': categories,
        'products': [product.to_dict() for product in products]
    }
    
    return jsonify(report_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_test_user()  # Create test user on startup
    app.run(debug=True)