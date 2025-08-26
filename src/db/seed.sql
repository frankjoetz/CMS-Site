INSERT INTO suppliers (name, contact, email, phone, address) VALUES
('Acme Supplies', 'Jane Doe', 'jane@acme.test', '+1-555-1000', '123 Elm St'),
('Global Parts', 'John Smith', 'john@global.test', '+1-555-2000', '456 Oak Ave');

INSERT INTO products (sku, name, description, unit_price, cost_price, supplier_id) VALUES
('SKU-100', 'Widget A', 'Standard widget', 25.00, 15.00, 1),
('SKU-200', 'Widget B', 'Premium widget', 40.00, 26.00, 1),
('SKU-300', 'Gadget C', 'Compact gadget', 15.00, 9.00, 2);

INSERT INTO equipment (name, serial, status, location) VALUES
('Forklift', 'FL-001', 'active', 'Warehouse A'),
('Label Printer', 'LP-112', 'active', 'Packing'),
('Conveyor', 'CV-220', 'maintenance', 'Receiving');

-- Initial inventory movements (stock in)
INSERT INTO inventory_movements (product_id, quantity, note, source) VALUES
(1, 100, 'Initial stock', 'seed'),
(2, 80, 'Initial stock', 'seed'),
(3, 150, 'Initial stock', 'seed');

-- Purchase orders
INSERT INTO purchase_orders (order_no, supplier_id, status) VALUES
('PO-001', 1, 'open'),
('PO-002', 2, 'received');

INSERT INTO purchase_order_items (purchase_order_id, product_id, quantity, unit_price, cost_price) VALUES
(1, 1, 50, 25.00, 15.00),
(1, 2, 20, 40.00, 26.00),
(2, 3, 60, 15.00, 9.00);

-- Delivery notes
INSERT INTO delivery_notes (dn_no, supplier_id) VALUES
('DN-100', 1);

INSERT INTO delivery_note_items (delivery_note_id, product_id, quantity, unit_price, cost_price) VALUES
(1, 1, 30, 25.00, 15.00),
(1, 2, 10, 40.00, 26.00);

-- Pendings
INSERT INTO pendings (title, description, status, due_date) VALUES
('Count cycle for A/B', 'Verify stock levels for Widget A/B', 'open', DATE('now','+3 day')),
('Confirm PO-001 ETA', 'Get ETA from Acme Supplies', 'open', DATE('now','+1 day')),
('Maintenance Conveyor', 'Schedule service for Conveyor CV-220', 'in_progress', DATE('now','+7 day'));