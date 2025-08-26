-- Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	contact TEXT,
	email TEXT,
	phone TEXT,
	address TEXT,
	created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE IF NOT EXISTS products (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	sku TEXT UNIQUE NOT NULL,
	name TEXT NOT NULL,
	description TEXT,
	unit_price REAL NOT NULL DEFAULT 0,
	cost_price REAL NOT NULL DEFAULT 0,
	supplier_id INTEGER,
	FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Inventory movements (positive for in, negative for out)
CREATE TABLE IF NOT EXISTS inventory_movements (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	product_id INTEGER NOT NULL,
	quantity INTEGER NOT NULL,
	note TEXT,
	source TEXT,
	moved_at TEXT DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Equipment
CREATE TABLE IF NOT EXISTS equipment (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	serial TEXT,
	status TEXT DEFAULT 'active',
	location TEXT,
	created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Purchase Orders
CREATE TABLE IF NOT EXISTS purchase_orders (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	order_no TEXT UNIQUE NOT NULL,
	supplier_id INTEGER NOT NULL,
	status TEXT DEFAULT 'pending',
	ordered_at TEXT DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS purchase_order_items (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	purchase_order_id INTEGER NOT NULL,
	product_id INTEGER NOT NULL,
	quantity INTEGER NOT NULL,
	unit_price REAL NOT NULL,
	cost_price REAL NOT NULL,
	FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id),
	FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Delivery Notes
CREATE TABLE IF NOT EXISTS delivery_notes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	dn_no TEXT UNIQUE NOT NULL,
	supplier_id INTEGER,
	received_at TEXT DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS delivery_note_items (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	delivery_note_id INTEGER NOT NULL,
	product_id INTEGER NOT NULL,
	quantity INTEGER NOT NULL,
	unit_price REAL NOT NULL,
	cost_price REAL NOT NULL,
	FOREIGN KEY (delivery_note_id) REFERENCES delivery_notes(id),
	FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Action Plans / Pendings
CREATE TABLE IF NOT EXISTS pendings (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	title TEXT NOT NULL,
	description TEXT,
	status TEXT DEFAULT 'open',
	due_date TEXT,
	created_at TEXT DEFAULT CURRENT_TIMESTAMP
);