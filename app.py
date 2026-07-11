from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from functools import wraps

from config import Config
from database import db  # Import db from database module

# Import models after db is defined
from models import User, Farmer, Buyer, Product, Order, OrderItem, Promotion, Feedback

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Import models first to ensure they're defined before initializing db
    from models import User, Farmer, Buyer, Product, Order, OrderItem, Promotion, Feedback
    
    # Initialize database
    db.init_app(app)
    
    return app

app = create_app()

# Helper function to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to check user role
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if not user or user.role not in allowed_roles:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# File upload helper
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Helper function to ensure cart quantities are integers
def normalize_cart_quantities():
    cart = session.get('cart', {})
    normalized_cart = {}
    for product_id, quantity in cart.items():
        # Convert both key and value to integers
        try:
            key = int(product_id)
            normalized_cart[key] = int(quantity)
        except (ValueError, TypeError):
            # Skip invalid entries
            continue
    session['cart'] = normalized_cart

# Routes

# Debug route to test static image rendering
@app.route('/test-image')
def test_image():
    """Test route to verify static image serving"""
    # Get a product that has an image
    product_with_image = Product.query.filter(Product.image_path.isnot(None)).first()
    if product_with_image:
        image_filename = product_with_image.image_path
        # Create a simple HTML response with the image
        html_response = f'''
        <!DOCTYPE html>
        <html>
        <head><title>Image Test</title></head>
        <body>
            <h1>Static Image Test</h1>
            <p>Testing image: {image_filename}</p>
            <img src="/static/images/uploads/{image_filename}" alt="Test Image" style="max-width: 300px; border: 2px solid #ccc; padding: 5px;">
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
        '''
        return html_response
    else:
        return "<h1>No products with images found</h1><a href='/'>Back to Home</a>"

@app.route('/')
def index():
    # Get featured products (approved products with promotions or high ratings)
    featured_products = Product.query.filter_by(status='approved').limit(6).all()
    
    # Get promoted products
    promoted_products = []
    for product in Product.query.filter_by(status='approved').all():
        if product.promotions:
            active_promo = next((promo for promo in product.promotions if promo.is_active), None)
            if active_promo:
                promoted_products.append(product)
    
    # Limit to 4 promoted products
    promoted_products = promoted_products[:4]
    
    return render_template('index.html', featured_products=featured_products, promoted_products=promoted_products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            
            # Redirect based on user role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            elif user.role == 'buyer':
                return redirect(url_for('browse_products'))
            else:
                flash('Invalid user role', 'error')
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        farm_name = request.form.get('farm_name', '')
        location = request.form.get('location', '')
        contact_number = request.form.get('contact_number', '')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create role-specific profile
            if role == 'farmer':
                farmer = Farmer(user_id=user.id, farm_name=farm_name, location=location, contact_number=contact_number)
                db.session.add(farmer)
            elif role == 'buyer':
                buyer = Buyer(user_id=user.id, contact_number=contact_number)
                db.session.add(buyer)
            
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Farmer routes
@app.route('/farmer/dashboard')
@login_required
@role_required(['farmer'])
def farmer_dashboard():
    user = User.query.get(session['user_id'])
    farmer = Farmer.query.filter_by(user_id=user.id).first()
    products = Product.query.filter_by(farmer_id=farmer.id).all()
    
    # Calculate some stats
    total_products = len(products)
    active_products = len([p for p in products if p.status == 'approved'])
    pending_products = len([p for p in products if p.status == 'pending'])
    
    return render_template('farmer/dashboard.html', 
                          farmer=farmer, 
                          products=products,
                          total_products=total_products,
                          active_products=active_products,
                          pending_products=pending_products)

@app.route('/farmer/add-product', methods=['GET', 'POST'])
@login_required
@role_required(['farmer'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        
        # Handle image upload - store only filename, not full path
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = str(int(datetime.now().timestamp()))
                filename = f"{timestamp}_{filename}"
                # Ensure upload directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_filename = filename  # Store only filename
        
        # Get farmer ID
        user = User.query.get(session['user_id'])
        farmer = Farmer.query.filter_by(user_id=user.id).first()
        
        # Create product
        product = Product(
            farmer_id=farmer.id,
            name=name,
            description=description,
            category=category,
            price=price,
            quantity=quantity,
            image_path=image_filename,  # Store only filename
            status='pending'  # Products need admin approval
        )
        
        try:
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully! Awaiting admin approval.', 'success')
            return redirect(url_for('farmer_dashboard'))
        except Exception as e:
            flash('Failed to add product. Please try again.', 'error')
    
    return render_template('farmer/add_product.html')

@app.route('/farmer/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required(['farmer'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Ensure the logged-in farmer owns this product
    user = User.query.get(session['user_id'])
    farmer = Farmer.query.filter_by(user_id=user.id).first()
    if product.farmer_id != farmer.id:
        flash('Access denied.', 'error')
        return redirect(url_for('farmer_dashboard'))
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.category = request.form['category']
        product.price = float(request.form['price'])
        product.quantity = int(request.form['quantity'])
        
        # Handle image upload - store only filename
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = str(int(datetime.now().timestamp()))
                filename = f"{timestamp}_{filename}"
                # Ensure upload directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Remove old image if exists
                if product.image_path:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                product.image_path = filename  # Store only filename
        
        try:
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('farmer_dashboard'))
        except Exception as e:
            flash('Failed to update product. Please try again.', 'error')
    
    return render_template('farmer/edit_product.html', product=product)

@app.route('/farmer/delete-product/<int:product_id>', methods=['POST'])
@login_required
@role_required(['farmer'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Ensure the logged-in farmer owns this product
    user = User.query.get(session['user_id'])
    farmer = Farmer.query.filter_by(user_id=user.id).first()
    if product.farmer_id != farmer.id:
        flash('Access denied.', 'error')
        return redirect(url_for('farmer_dashboard'))
    
    try:
        # Remove image file if exists
        if product.image_path:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        flash('Failed to delete product. Please try again.', 'error')
    
    return redirect(url_for('farmer_dashboard'))

@app.route('/farmer/orders')
@login_required
@role_required(['farmer'])
def farmer_orders():
    user = User.query.get(session['user_id'])
    farmer = Farmer.query.filter_by(user_id=user.id).first()
    
    # Get all orders that contain products from this farmer
    order_ids = db.session.query(OrderItem.order_id).join(Product).filter(Product.farmer_id == farmer.id).distinct().subquery()
    orders = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).all()
    
    # Group order items by order
    order_details = []
    for order in orders:
        order_items = OrderItem.query.join(Product).filter(
            OrderItem.order_id == order.id,
            Product.farmer_id == farmer.id
        ).all()
        order_details.append({'order': order, 'order_items': order_items})
    
    return render_template('farmer/orders.html', order_details=order_details)


@app.route('/farmer/update-order/<int:order_id>', methods=['POST'])
@login_required
@role_required(['farmer'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Check if this order contains products from this farmer
    user = User.query.get(session['user_id'])
    farmer = Farmer.query.filter_by(user_id=user.id).first()
    
    order_items = OrderItem.query.join(Product).filter(
        OrderItem.order_id == order.id,
        Product.farmer_id == farmer.id
    ).all()
    
    if not order_items:
        flash('You do not have permission to update this order.', 'error')
        return redirect(url_for('farmer_orders'))
    
    new_status = request.form.get('status')
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    
    if new_status in valid_statuses:
        order.status = new_status
        try:
            db.session.commit()
            flash(f'Order status updated to {new_status}.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to update order status. Please try again.', 'error')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('farmer_orders'))


@app.route('/farmer/analytics')
@login_required
@role_required(['farmer'])
def farmer_analytics():
    user = User.query.get(session['user_id'])
    farmer = Farmer.query.filter_by(user_id=user.id).first()
    products = Product.query.filter_by(farmer_id=farmer.id).all()
    
    # Prepare data for analytics
    product_stats = []
    for product in products:
        # Count orders for this product
        order_count = 0
        total_revenue = 0
        
        order_items = OrderItem.query.filter_by(product_id=product.id).all()
        for item in order_items:
            order = Order.query.get(item.order_id)
            if order.status in ['confirmed', 'shipped', 'delivered']:
                order_count += item.quantity
                total_revenue += item.price * item.quantity
        
        avg_rating = product.average_rating
        product_stats.append({
            'product': product,
            'order_count': order_count,
            'total_revenue': total_revenue,
            'avg_rating': avg_rating
        })
    
    return render_template('farmer/analytics.html', product_stats=product_stats)

# Buyer routes
@app.route('/browse')
def browse_products():
    category_filter = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    query = Product.query.filter_by(status='approved')
    
    if category_filter:
        query = query.filter(Product.category.ilike(f'%{category_filter}%'))
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.all()
    
    # Get all unique categories for filter dropdown
    categories = [p.category for p in Product.query.filter_by(status='approved').distinct(Product.category)]
    
    return render_template('buyer/browse.html', products=products, categories=categories)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    if product.status != 'approved':
        flash('Product not available', 'error')
        return redirect(url_for('browse_products'))
    
    # Get related products (same category)
    related_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product_id,
        Product.status == 'approved'
    ).limit(4).all()
    
    # Get feedback for this product
    feedbacks = Feedback.query.filter_by(product_id=product_id).all()
    
    return render_template('buyer/product_detail.html', 
                          product=product, 
                          related_products=related_products,
                          feedbacks=feedbacks)

@app.route('/cart')
@login_required
def view_cart():
    # Normalize cart quantities to ensure they are all integers
    normalize_cart_quantities()
    
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        # Ensure product_id is an integer for database lookup
        try:
            product_id_int = int(product_id)
        except (ValueError, TypeError):
            continue
        product = Product.query.get(product_id_int)
        if product:
            # Convert quantity to int to avoid type comparison errors
            quantity_int = int(quantity)
            item_total = product.price * quantity_int
            cart_items.append({
                'product': product,
                'quantity': quantity_int,
                'item_total': item_total
            })
            total += item_total
    
    return render_template('buyer/cart.html', cart_items=cart_items, total=total)

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.status != 'approved':
        flash('Product not available', 'error')
        return redirect(url_for('browse_products'))
    
    cart = session.get('cart', {})
    # Ensure we're working with integers
    # Check for both integer and string keys
    current_quantity = 0
    if product_id in cart:
        current_quantity = int(cart[product_id])
    elif str(product_id) in cart:
        current_quantity = int(cart[str(product_id)])
    
    # Store with integer key
    cart[int(product_id)] = current_quantity + 1
    session['cart'] = cart
    
    # Normalize all quantities in cart to ensure they are integers
    normalize_cart_quantities()
    
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('view_cart'))

@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
@role_required(['buyer'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    # Check for both integer and string keys
    if product_id in cart:
        del cart[product_id]
    elif str(product_id) in cart:
        del cart[str(product_id)]
    else:
        # Try to find the key by converting
        for key in list(cart.keys()):
            try:
                if int(key) == product_id:
                    del cart[key]
                    break
            except (ValueError, TypeError):
                continue
    
    session['cart'] = cart
    # Normalize all remaining quantities in session to ensure they are integers
    normalize_cart_quantities()
    flash('Item removed from cart', 'success')
    return redirect(url_for('view_cart'))

@app.route('/update-cart/<int:product_id>', methods=['POST'])
@login_required
@role_required(['buyer'])
def update_cart_quantity(product_id):
    try:
        quantity_str = request.form.get('quantity')
        if quantity_str is None:
            flash('Quantity not provided', 'error')
            return redirect(url_for('view_cart'))
        
        quantity = int(quantity_str)
        if quantity <= 0:
            return redirect(url_for('remove_from_cart', product_id=product_id))
        
        cart = session.get('cart', {})
        # Store as integer to maintain type consistency
        # Ensure product_id is stored as integer key
        cart[int(product_id)] = quantity
        session['cart'] = cart
        
        # Normalize all quantities in cart to ensure they are integers
        normalize_cart_quantities()
        
    except ValueError:
        # Handle case where quantity is not a valid integer
        flash('Invalid quantity entered', 'error')
    except Exception as e:
        # Handle any other exceptions
        flash('Error updating cart quantity', 'error')
    
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
@role_required(['buyer'])
def checkout():
    if request.method == 'POST':
        # Normalize cart quantities to ensure they are all integers
        normalize_cart_quantities()
        
        cart = session.get('cart', {})
        if not cart:
            flash('Cart is empty', 'error')
            return redirect(url_for('view_cart'))
        
        # Get buyer
        user = User.query.get(session['user_id'])
        buyer = Buyer.query.filter_by(user_id=user.id).first()
        
        # Calculate total
        total = 0
        cart_items = []
        for product_id, quantity in cart.items():
            product = Product.query.get(product_id)
            if product and product.status == 'approved':
                # Convert quantity to int to avoid type comparison errors
                quantity_int = int(quantity)
                if product.quantity >= quantity_int:
                    total += product.price * quantity_int
                    cart_items.append({'product': product, 'quantity': quantity_int})
            else:
                flash(f'Item {product.name} is no longer available in requested quantity', 'error')
                return redirect(url_for('view_cart'))
        
        if total == 0:
            flash('Cart is empty or invalid', 'error')
            return redirect(url_for('view_cart'))
        
        # Process the order with delivery information
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        zip_code = request.form.get('zip', '')
        payment_method = request.form.get('payment_method', 'cod')
        
        # Create order
        order = Order(
            buyer_id=buyer.id,
            total_amount=total,
            status='pending',
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            payment_method=payment_method
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items and update product quantities
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['product'].price
            )
            db.session.add(order_item)
            
            # Update product quantity
            item['product'].quantity -= item['quantity']
        
        try:
            db.session.commit()
            session['cart'] = {}  # Clear cart
            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_history'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to place order. Please try again.', 'error')
            return redirect(url_for('view_cart'))
    
    # Handle GET request - show checkout page
    # Normalize cart quantities to ensure they are all integers
    normalize_cart_quantities()
    
    cart = session.get('cart', {})
    if not cart:
        flash('Cart is empty', 'error')
        return redirect(url_for('view_cart'))
    
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(product_id)
        if product:
            quantity_int = int(quantity)
            item_total = product.price * quantity_int
            cart_items.append({
                'product': product,
                'quantity': quantity_int,
                'item_total': item_total
            })
            total += item_total
    
    # Calculate delivery fee
    delivery_fee = 50.00
    grand_total = total + delivery_fee
    
    return render_template('buyer/checkout.html', cart_items=cart_items, total=total, delivery_fee=delivery_fee, grand_total=grand_total)

@app.route('/orders')
@login_required
@role_required(['buyer'])
def order_history():
    user = User.query.get(session['user_id'])
    buyer = Buyer.query.filter_by(user_id=user.id).first()
    orders = Order.query.filter_by(buyer_id=buyer.id).order_by(Order.created_at.desc()).all()
    
    return render_template('buyer/order_history.html', orders=orders)

@app.route('/feedback/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required(['buyer'])
def add_feedback(product_id):
    product = Product.query.get_or_404(product_id)
    user = User.query.get(session['user_id'])
    buyer = Buyer.query.filter_by(user_id=user.id).first()
    
    # Check if buyer already submitted feedback for this product
    existing_feedback = Feedback.query.filter_by(product_id=product_id, buyer_id=buyer.id).first()
    if existing_feedback:
        flash('You have already submitted feedback for this product', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment']
        
        if 1 <= rating <= 5:
            feedback = Feedback(
                product_id=product_id,
                buyer_id=buyer.id,
                rating=rating,
                comment=comment
            )
            db.session.add(feedback)
            db.session.commit()
            flash('Feedback submitted successfully!', 'success')
        else:
            flash('Rating must be between 1 and 5', 'error')
        
        return redirect(url_for('product_detail', product_id=product_id))
    
    return render_template('buyer/feedback.html', product=product)

@app.route('/order/<int:order_id>')
@login_required
@role_required(['buyer'])
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    user = User.query.get(session['user_id'])
    buyer = Buyer.query.filter_by(user_id=user.id).first()
    
    # Ensure the logged-in buyer owns this order
    if order.buyer_id != buyer.id:
        flash('Access denied.', 'error')
        return redirect(url_for('order_history'))
    
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    
    return render_template('buyer/order_detail.html', order=order, order_items=order_items)

# Admin routes
@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
@role_required(['admin'])
def admin_dashboard():
    total_users = User.query.count()
    total_farmers = Farmer.query.count()
    total_buyers = Buyer.query.count()
    total_products = Product.query.count()
    pending_products = Product.query.filter_by(status='pending').count()
    total_orders = Order.query.count()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_farmers=total_farmers,
                          total_buyers=total_buyers,
                          total_products=total_products,
                          pending_products=pending_products,
                          total_orders=total_orders)

@app.route('/admin/users')
@login_required
@role_required(['admin'])
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/toggle-user-status/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    # In a real app, you might want to deactivate users instead of changing roles
    # For now, we'll just show how this might work
    flash(f'Toggled status for user {user.name}', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/products')
@login_required
@role_required(['admin'])
def admin_products():
    pending_products = Product.query.filter_by(status='pending').all()
    approved_products = Product.query.filter_by(status='approved').all()
    
    return render_template('admin/approve_products.html',
                          pending_products=pending_products,
                          approved_products=approved_products)

@app.route('/admin/all-products')
@login_required
@role_required(['admin'])
def admin_manage_products():
    # Get all products regardless of status
    all_products = Product.query.all()
    
    return render_template('admin/manage_products.html', all_products=all_products)

@app.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.category = request.form['category']
        product.price = float(request.form['price'])
        product.quantity = int(request.form['quantity'])
        
        # Handle image upload - store only filename
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = str(int(datetime.now().timestamp()))
                filename = f"{timestamp}_{filename}"
                # Ensure upload directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Remove old image if exists
                if product.image_path:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                product.image_path = filename  # Store only filename
        
        try:
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin_manage_products'))
        except Exception as e:
            flash('Failed to update product. Please try again.', 'error')
    
    return render_template('admin/edit_product.html', product=product)

@app.route('/admin/approve-product/<int:product_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def approve_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.status = 'approved'
    db.session.commit()
    flash(f'Product "{product.name}" approved successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/reject-product/<int:product_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def reject_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.status = 'rejected'
    db.session.commit()
    flash(f'Product "{product.name}" rejected!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/analytics')
@login_required
@role_required(['admin'])
def admin_analytics():
    # Calculate various analytics
    total_revenue = 0
    completed_orders = Order.query.filter(Order.status.in_(['delivered', 'confirmed'])).all()
    for order in completed_orders:
        total_revenue += order.total_amount
    
    # Top selling products
    top_products = []
    all_products = Product.query.all()
    for product in all_products:
        total_sold = 0
        order_items = OrderItem.query.filter_by(product_id=product.id).all()
        for item in order_items:
            order = Order.query.get(item.order_id)
            if order.status in ['delivered', 'confirmed']:
                total_sold += item.quantity
        top_products.append({'product': product, 'sold': total_sold})
    
    # Sort by sold quantity
    top_products.sort(key=lambda x: x['sold'], reverse=True)
    top_products = top_products[:5]  # Top 5
    
    return render_template('admin/analytics.html',
                          total_revenue=total_revenue,
                          completed_orders=len(completed_orders),
                          top_products=top_products)

# Marketing routes
@app.route('/featured')
def featured_products():
    # Get products with active promotions
    featured_products = []
    all_products = Product.query.filter_by(status='approved').all()
    for product in all_products:
        active_promo = next((promo for promo in product.promotions if promo.is_active), None)
        if active_promo:
            featured_products.append(product)
    
    return render_template('marketing/featured.html', featured_products=featured_products)

@app.route('/promotions')
def promotions():
    # Get all active promotions
    active_promotions = []
    all_products = Product.query.filter_by(status='approved').all()
    for product in all_products:
        for promo in product.promotions:
            if promo.is_active:
                active_promotions.append({
                    'product': product,
                    'promotion': promo
                })
    
    return render_template('marketing/promotions.html', promotions=active_promotions)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)