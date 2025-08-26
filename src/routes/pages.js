import { Router } from 'express';
import db from '../db/index.js';

const router = Router();

router.get('/equipment', (req, res) => {
	const items = db.prepare('SELECT * FROM equipment ORDER BY created_at DESC').all();
	res.render('equipment', { title: 'Equipment', items });
});

router.get('/pendings', (req, res) => {
	const items = db.prepare('SELECT * FROM pendings ORDER BY status DESC, due_date ASC NULLS LAST').all();
	res.render('pendings', { title: 'Pendings', items });
});

router.get('/suppliers', (req, res) => {
	const items = db.prepare('SELECT * FROM suppliers ORDER BY name ASC').all();
	res.render('suppliers', { title: 'Suppliers', items });
});

router.get('/products', (req, res) => {
	const items = db.prepare(`
		SELECT p.*, s.name as supplier_name
		FROM products p
		LEFT JOIN suppliers s ON s.id = p.supplier_id
		ORDER BY p.name ASC`).all();
	res.render('products', { title: 'Products', items });
});

router.get('/inventory', (req, res) => {
	const items = db.prepare(`
		SELECT p.id, p.sku, p.name,
		IFNULL((SELECT SUM(quantity) FROM inventory_movements im WHERE im.product_id = p.id), 0) as stock
		FROM products p
		ORDER BY p.name ASC`).all();
	res.render('inventory', { title: 'Inventory', items });
});

router.get('/purchase-orders', (req, res) => {
	const items = db.prepare(`
		SELECT po.*, s.name as supplier_name,
		IFNULL((SELECT SUM(quantity) FROM purchase_order_items poi WHERE poi.purchase_order_id = po.id),0) as total_items
		FROM purchase_orders po
		LEFT JOIN suppliers s ON s.id = po.supplier_id
		ORDER BY po.ordered_at DESC`).all();
	res.render('purchase-orders', { title: 'Purchase Orders', items });
});

router.get('/delivery-notes', (req, res) => {
	const items = db.prepare(`
		SELECT dn.*, s.name as supplier_name,
		IFNULL((SELECT SUM(quantity) FROM delivery_note_items dni WHERE dni.delivery_note_id = dn.id),0) as total_items
		FROM delivery_notes dn
		LEFT JOIN suppliers s ON s.id = dn.supplier_id
		ORDER BY dn.received_at DESC`).all();
	res.render('delivery-notes', { title: 'Delivery Notes', items });
});

export default router;