import os
import sys
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory, session
from flask_cors import CORS
from models import db, User, Bill
from pdf_generator import generate_invoice_pdf

def get_base_dir():
    """
    Returns base directory. When frozen by PyInstaller,
    sys.frozen is True and sys._MEIPASS holds bundled assets.
    Persistent data (DB, PDFs) should live in the directory containing the exe.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))

def get_assets_dir():
    """
    Returns location of bundled frontend static assets.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'static_dist')
    # In development or standard python run
    local_static = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static_dist')
    if os.path.exists(local_static):
        return local_static
    # Fallback to frontend dist if present
    frontend_dist = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'frontend', 'dist')
    if os.path.exists(frontend_dist):
        return os.path.abspath(frontend_dist)
    return local_static

base_dir = get_base_dir()
data_dir = os.path.join(base_dir, 'data')
invoices_dir = os.path.join(data_dir, 'invoices')
os.makedirs(invoices_dir, exist_ok=True)

db_path = os.path.join(data_dir, 'billing.db')

app = Flask(__name__, static_folder=None)
app.config['SECRET_KEY'] = 'billing-system-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5000", "http://127.0.0.1:5000"])

db.init_app(app)

def init_db():
    with app.app_context():
        db.create_all()
        # Seed default admin user if no users exist
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("[INFO] Seeded default user: admin / admin123")

# --- Authentication Endpoints ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if len(password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters long'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False}), 200
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({'authenticated': False}), 200
    return jsonify({'authenticated': True, 'user': user.to_dict()}), 200

# --- Billing Endpoints ---

@app.route('/api/bills', methods=['GET'])
def get_bills():
    search = request.args.get('search', '').strip()
    query = Bill.query
    if search:
        query = query.filter(
            (Bill.invoice_number.ilike(f"%{search}%")) |
            (Bill.customer_name.ilike(f"%{search}%")) |
            (Bill.customer_email.ilike(f"%{search}%"))
        )
    bills = query.order_by(Bill.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bills]), 200

@app.route('/api/bills', methods=['POST'])
def create_bill():
    data = request.get_json() or {}
    
    customer_name = data.get('customer_name', '').strip()
    if not customer_name:
        return jsonify({'error': 'Customer name is required'}), 400
    
    items = data.get('items', [])
    if not items or not isinstance(items, list):
        return jsonify({'error': 'At least one item is required'}), 400

    # Calculate totals
    subtotal = 0.0
    cleaned_items = []
    for item in items:
        name = str(item.get('name', '')).strip()
        if not name:
            continue
        try:
            qty = float(item.get('qty', 1))
            unit_price = float(item.get('unit_price', 0.0))
        except (ValueError, TypeError):
            qty = 1
            unit_price = 0.0
        line_total = round(qty * unit_price, 2)
        subtotal += line_total
        cleaned_items.append({
            'name': name,
            'qty': qty,
            'unit_price': unit_price,
            'total': line_total
        })

    if not cleaned_items:
        return jsonify({'error': 'Please provide at least one valid item'}), 400

    subtotal = round(subtotal, 2)
    try:
        tax_rate = float(data.get('tax_rate', 0.0))
    except (ValueError, TypeError):
        tax_rate = 0.0

    tax_amount = round(subtotal * (tax_rate / 100.0), 2)
    grand_total = round(subtotal + tax_amount, 2)

    # Generate invoice number
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    random_suffix = uuid.uuid4().hex[:4].upper()
    invoice_number = f"INV-{timestamp}-{random_suffix}"

    pdf_filename = f"{invoice_number}.pdf"
    pdf_filepath = os.path.join(invoices_dir, pdf_filename)

    bill = Bill(
        invoice_number=invoice_number,
        customer_name=customer_name,
        customer_email=data.get('customer_email', '').strip(),
        customer_phone=data.get('customer_phone', '').strip(),
        customer_address=data.get('customer_address', '').strip(),
        subtotal=subtotal,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        grand_total=grand_total,
        notes=data.get('notes', '').strip(),
        pdf_filename=pdf_filename
    )
    bill.set_items(cleaned_items)

    db.session.add(bill)
    db.session.commit()

    # Generate PDF file
    bill_dict = bill.to_dict()
    try:
        generate_invoice_pdf(bill_dict, pdf_filepath)
    except Exception as e:
        print(f"[ERROR] Failed to generate PDF: {e}")

    return jsonify({
        'message': 'Bill created successfully',
        'bill': bill_dict,
        'download_url': f"/api/bills/{bill.id}/download"
    }), 201

@app.route('/api/bills/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    bill = Bill.query.get(bill_id)
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    return jsonify(bill.to_dict()), 200

@app.route('/api/bills/<int:bill_id>/download', methods=['GET'])
def download_bill_pdf(bill_id):
    bill = Bill.query.get(bill_id)
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404

    pdf_filepath = os.path.join(invoices_dir, bill.pdf_filename)
    if not os.path.exists(pdf_filepath):
        # Regenerate if missing
        try:
            generate_invoice_pdf(bill.to_dict(), pdf_filepath)
        except Exception as e:
            return jsonify({'error': f"Failed to generate PDF: {str(e)}"}), 500

    return send_file(
        pdf_filepath,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{bill.invoice_number}.pdf"
    )

# --- Frontend Static Serving ---

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    assets_dir = get_assets_dir()
    if not os.path.exists(assets_dir):
        return (
            "<h3>Frontend is not built yet.</h3>"
            "<p>Please build the React frontend or run in dev mode.</p>"
        ), 200

    requested_file = os.path.join(assets_dir, path)
    if path != "" and os.path.exists(requested_file):
        return send_from_directory(assets_dir, path)
    else:
        index_file = os.path.join(assets_dir, 'index.html')
        if os.path.exists(index_file):
            return send_from_directory(assets_dir, 'index.html')
        return "<h3>index.html not found in build directory.</h3>", 404

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask server at http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)
