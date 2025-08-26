from __future__ import annotations

import math
from datetime import datetime, timedelta, date
from decimal import Decimal

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////workspace/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dev-secret'

db = SQLAlchemy(app)

# Models
class Supplier(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), nullable=False)
	contact_email = db.Column(db.String(120))
	contact_phone = db.Column(db.String(50))

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sku = db.Column(db.String(64), unique=True, nullable=False)
	name = db.Column(db.String(120), nullable=False)
	cost_price = db.Column(db.Float, default=0.0)
	selling_price = db.Column(db.Float, default=0.0)
	supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
	supplier = db.relationship('Supplier', backref='products')

class InventoryItem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
	product = db.relationship('Product')
	quantity_on_hand = db.Column(db.Integer, default=0)
	reorder_level = db.Column(db.Integer, default=0)

class Equipment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), nullable=False)
	serial_number = db.Column(db.String(120))
	status = db.Column(db.String(50), default='Active')

class PendingItem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), nullable=False)
	description = db.Column(db.Text)
	status = db.Column(db.String(50), default='Open')
	due_date = db.Column(db.Date)

class PurchaseOrder(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	order_date = db.Column(db.Date, default=date.today)
	supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
	supplier = db.relationship('Supplier')
	total_cost = db.Column(db.Float, default=0.0)

class DeliveryNote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	delivery_date = db.Column(db.Date, default=date.today)
	purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'))
	purchase_order = db.relationship('PurchaseOrder')
	notes = db.Column(db.Text)

# Utilities

def currency(value: float) -> str:
	return f"${value:,.2f}"

@app.template_filter('currency')
def currency_filter(value):
	return currency(value or 0)

# Routes
@app.route('/')
def dashboard():
	return render_template('dashboard.html', title='Dashboard')

@app.route('/init-db')
def init_db():
	db.drop_all()
	db.create_all()
	seed()
	flash('Database initialized with sample data')
	return redirect(url_for('dashboard'))

# Core CRUD list pages (simple for MVP)
@app.route('/suppliers')
def suppliers_list():
	suppliers = Supplier.query.order_by(Supplier.name).all()
	return render_template('lists/suppliers.html', suppliers=suppliers, title='Suppliers')

@app.route('/suppliers/new', methods=['GET', 'POST'])
def supplier_new():
	if request.method == 'POST':
		name = request.form.get('name')
		contact_email = request.form.get('contact_email')
		contact_phone = request.form.get('contact_phone')
		db.session.add(Supplier(name=name, contact_email=contact_email, contact_phone=contact_phone))
		db.session.commit()
		return redirect(url_for('suppliers_list'))
	return render_template('forms/supplier_form.html', title='New Supplier')

@app.route('/products')
def products_list():
	products = Product.query.order_by(Product.name).all()
	return render_template('lists/products.html', products=products, title='Products')

@app.route('/products/new', methods=['GET', 'POST'])
def product_new():
	if request.method == 'POST':
		sku = request.form.get('sku')
		name = request.form.get('name')
		cost_price = float(request.form.get('cost_price') or 0)
		selling_price = float(request.form.get('selling_price') or 0)
		supplier_id = int(request.form.get('supplier_id') or 0) or None
		product = Product(sku=sku, name=name, cost_price=cost_price, selling_price=selling_price, supplier_id=supplier_id)
		db.session.add(product)
		db.session.commit()
		return redirect(url_for('products_list'))
	suppliers = Supplier.query.all()
	return render_template('forms/product_form.html', suppliers=suppliers, title='New Product')

@app.route('/inventory')
def inventory_list():
	items = InventoryItem.query.all()
	return render_template('lists/inventory.html', items=items, title='Inventory')

@app.route('/inventory/new', methods=['GET', 'POST'])
def inventory_new():
	if request.method == 'POST':
		product_id = int(request.form.get('product_id'))
		quantity_on_hand = int(request.form.get('quantity_on_hand') or 0)
		reorder_level = int(request.form.get('reorder_level') or 0)
		item = InventoryItem(product_id=product_id, quantity_on_hand=quantity_on_hand, reorder_level=reorder_level)
		db.session.add(item)
		db.session.commit()
		return redirect(url_for('inventory_list'))
	products = Product.query.all()
	return render_template('forms/inventory_form.html', products=products, title='New Inventory Item')

@app.route('/equipment')
def equipment_list():
	equipment = Equipment.query.all()
	return render_template('lists/equipment.html', equipment=equipment, title='Equipment')

@app.route('/equipment/new', methods=['GET', 'POST'])
def equipment_new():
	if request.method == 'POST':
		name = request.form.get('name')
		serial_number = request.form.get('serial_number')
		status = request.form.get('status')
		db.session.add(Equipment(name=name, serial_number=serial_number, status=status))
		db.session.commit()
		return redirect(url_for('equipment_list'))
	return render_template('forms/equipment_form.html', title='New Equipment')

@app.route('/pendings')
def pendings_list():
	pendings = PendingItem.query.order_by(PendingItem.due_date.asc().nulls_last()).all()
	return render_template('lists/pendings.html', pendings=pendings, title='Pendings')

@app.route('/pendings/new', methods=['GET', 'POST'])
def pendings_new():
	if request.method == 'POST':
		title = request.form.get('title')
		description = request.form.get('description')
		status = request.form.get('status')
		due_date_str = request.form.get('due_date')
		due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
		db.session.add(PendingItem(title=title, description=description, status=status, due_date=due_date))
		db.session.commit()
		return redirect(url_for('pendings_list'))
	return render_template('forms/pending_form.html', title='New Pending Item')

@app.route('/purchase-orders')
def po_list():
	pos = PurchaseOrder.query.order_by(PurchaseOrder.order_date.desc()).all()
	return render_template('lists/purchase_orders.html', pos=pos, title='Purchase Orders')

@app.route('/purchase-orders/new', methods=['GET', 'POST'])
def po_new():
	if request.method == 'POST':
		order_date_str = request.form.get('order_date')
		supplier_id = int(request.form.get('supplier_id') or 0) or None
		total_cost = float(request.form.get('total_cost') or 0)
		order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date() if order_date_str else date.today()
		db.session.add(PurchaseOrder(order_date=order_date, supplier_id=supplier_id, total_cost=total_cost))
		db.session.commit()
		return redirect(url_for('po_list'))
	suppliers = Supplier.query.all()
	return render_template('forms/po_form.html', suppliers=suppliers, title='New Purchase Order')

@app.route('/delivery-notes')
def dn_list():
	dns = DeliveryNote.query.order_by(DeliveryNote.delivery_date.desc()).all()
	return render_template('lists/delivery_notes.html', dns=dns, title='Delivery Notes')

@app.route('/delivery-notes/new', methods=['GET', 'POST'])
def dn_new():
	if request.method == 'POST':
		delivery_date_str = request.form.get('delivery_date')
		purchase_order_id = int(request.form.get('purchase_order_id') or 0) or None
		notes = request.form.get('notes')
		delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date() if delivery_date_str else date.today()
		db.session.add(DeliveryNote(delivery_date=delivery_date, purchase_order_id=purchase_order_id, notes=notes))
		db.session.commit()
		return redirect(url_for('dn_list'))
	pos = PurchaseOrder.query.all()
	return render_template('forms/dn_form.html', pos=pos, title='New Delivery Note')

# APIs for dashboard and reports
@app.route('/api/dashboard/summary')
def api_dashboard_summary():
	# Pending counts
	pending_count = PendingItem.query.filter(PendingItem.status != 'Closed').count()
	# Low stock (quantity_on_hand <= reorder_level and > 0)
	low_stock = InventoryItem.query.filter(InventoryItem.quantity_on_hand <= InventoryItem.reorder_level).count()
	# Inventory value
	items = InventoryItem.query.join(Product, InventoryItem.product_id == Product.id).all()
	total_value = sum((item.quantity_on_hand or 0) * (item.product.cost_price or 0) for item in items)

	# Last 6 months PO cost
	now = date.today().replace(day=1)
	labels = []
	data = []
	for i in range(5, -1, -1):
		month = (now - timedelta(days=30 * i))
		start = month
		end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
		labels.append(start.strftime('%b %Y'))
		cost = db.session.query(db.func.sum(PurchaseOrder.total_cost)).filter(PurchaseOrder.order_date >= start, PurchaseOrder.order_date <= end).scalar() or 0
		data.append(round(cost, 2))

	# Last 14 days deliveries count
	labels_daily = []
	data_daily = []
	start_day = date.today() - timedelta(days=13)
	for i in range(14):
		day = start_day + timedelta(days=i)
		labels_daily.append(day.strftime('%d %b'))
		cnt = DeliveryNote.query.filter(DeliveryNote.delivery_date == day).count()
		data_daily.append(cnt)

	return jsonify({
		'pendingCount': pending_count,
		'lowStockCount': low_stock,
		'totalInventoryValue': round(total_value, 2),
		'totalInventoryValueFormatted': currency(total_value),
		'monthly': {'labels': labels, 'data': data},
		'daily': {'labels': labels_daily, 'data': data_daily},
	})

@app.route('/reports/daily')
def daily_report():
	return render_template('reports/daily.html', title='Daily Report')

@app.route('/reports/monthly')
def monthly_report():
	return render_template('reports/monthly.html', title='Monthly Report')

# Seed sample data

def seed():
	if Supplier.query.count() > 0:
		return
	s1 = Supplier(name='Acme Supplies', contact_email='sales@acme.test', contact_phone='123-456')
	s2 = Supplier(name='Global Parts', contact_email='info@global.test', contact_phone='555-0100')
	db.session.add_all([s1, s2])
	db.session.flush()

	p1 = Product(sku='SKU-1001', name='Widget A', cost_price=12.5, selling_price=20.0, supplier_id=s1.id)
	p2 = Product(sku='SKU-1002', name='Widget B', cost_price=7.2, selling_price=12.0, supplier_id=s2.id)
	db.session.add_all([p1, p2])
	db.session.flush()

	i1 = InventoryItem(product_id=p1.id, quantity_on_hand=50, reorder_level=20)
	i2 = InventoryItem(product_id=p2.id, quantity_on_hand=10, reorder_level=15)
	db.session.add_all([i1, i2])

	e1 = Equipment(name='Forklift', serial_number='FL-001', status='Active')
	e2 = Equipment(name='Conveyor', serial_number='CV-002', status='Maintenance')
	db.session.add_all([e1, e2])

	pend1 = PendingItem(title='Follow up with supplier', description='Pending quotation', status='Open', due_date=date.today() + timedelta(days=2))
	pend2 = PendingItem(title='Arrange delivery', description='Schedule truck', status='Open', due_date=date.today() + timedelta(days=1))
	db.session.add_all([pend1, pend2])

	po1 = PurchaseOrder(order_date=date.today() - timedelta(days=40), supplier_id=s1.id, total_cost=1200)
	po2 = PurchaseOrder(order_date=date.today() - timedelta(days=10), supplier_id=s2.id, total_cost=800)
	db.session.add_all([po1, po2])
	db.session.flush()

	dn1 = DeliveryNote(delivery_date=date.today() - timedelta(days=5), purchase_order_id=po2.id, notes='Delivered on time')
	dn2 = DeliveryNote(delivery_date=date.today() - timedelta(days=1), purchase_order_id=po2.id, notes='Partial delivery')
	db.session.add_all([dn1, dn2])

	db.session.commit()

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)