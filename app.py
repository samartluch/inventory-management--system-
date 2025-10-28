from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Product
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
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
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_products = Product.query.filter_by(user_id=current_user.id).count()
    low_stock = Product.query.filter(Product.user_id == current_user.id, Product.quantity < 10).count()
    return render_template('dashboard.html', total_products=total_products, low_stock=low_stock)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
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
    
    return render_template('add_product.html')

@app.route('/inventory')
@login_required
def inventory():
    products = Product.query.filter_by(user_id=current_user.id).all()
    return render_template('inventory.html', products=products)

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
    
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id, user_id=current_user.id).first_or_404()
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('inventory'))

@app.route('/report')
@login_required
def report():
    products = Product.query.filter_by(user_id=current_user.id).all()
    total_quantity = sum(product.quantity for product in products)
    total_value = sum(product.quantity * product.price for product in products)
    return render_template('report.html', products=products, total_quantity=total_quantity, total_value=total_value)

@app.route('/api/report')
@login_required
def api_report():
    products = Product.query.filter_by(user_id=current_user.id).all()
    total_quantity = sum(product.quantity for product in products)
    total_value = sum(product.quantity * product.price for product in products)
    
    report_data = {
        'total_products': len(products),
        'total_quantity': total_quantity,
        'total_value': round(total_value, 2),
        'products': [product.to_dict() for product in products]
    }
    
    return jsonify(report_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)