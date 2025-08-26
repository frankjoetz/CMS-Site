import { Router } from 'express';
import db from '../db/index.js';

const router = Router();

router.get('/reports/summary', (req, res) => {
	const monthlyOrders = db.prepare("SELECT COUNT(1) as c FROM purchase_orders WHERE strftime('%Y-%m', ordered_at)=strftime('%Y-%m','now')").get().c;
	const monthlyDeliveries = db.prepare("SELECT COUNT(1) as c FROM delivery_notes WHERE strftime('%Y-%m', received_at)=strftime('%Y-%m','now')").get().c;
	const monthlyRevenue = db.prepare("SELECT IFNULL(SUM(quantity*unit_price),0) as s FROM delivery_note_items dni JOIN delivery_notes dn ON dn.id=dni.delivery_note_id WHERE strftime('%Y-%m', dn.received_at)=strftime('%Y-%m','now')").get().s;
	const monthlyCost = db.prepare("SELECT IFNULL(SUM(quantity*cost_price),0) as s FROM delivery_note_items dni JOIN delivery_notes dn ON dn.id=dni.delivery_note_id WHERE strftime('%Y-%m', dn.received_at)=strftime('%Y-%m','now')").get().s;

	res.json({
		daily: {
			orders: db.prepare("SELECT COUNT(DISTINCT id) as c FROM purchase_orders WHERE DATE(ordered_at)=DATE('now')").get().c,
			deliveries: db.prepare("SELECT COUNT(DISTINCT id) as c FROM delivery_notes WHERE DATE(received_at)=DATE('now')").get().c,
			pendings: db.prepare("SELECT COUNT(1) as c FROM pendings WHERE status!='closed'").get().c
		},
		monthly: {
			labels: ['Week 1','Week 2','Week 3','Week 4'],
			orders: [monthlyOrders],
			deliveries: [monthlyDeliveries],
			costs: [monthlyCost],
			revenues: [monthlyRevenue]
		}
	});
});

router.get('/products', (req, res) => {
	const rows = db.prepare('SELECT * FROM products ORDER BY name ASC').all();
	res.json(rows);
});

router.post('/products', (req, res) => {
	const { sku, name, description, unit_price, cost_price, supplier_id } = req.body;
	try {
		const stmt = db.prepare(`INSERT INTO products (sku, name, description, unit_price, cost_price, supplier_id)
		VALUES (?, ?, ?, ?, ?, ?)`);
		const info = stmt.run(sku, name, description || null, unit_price || 0, cost_price || 0, supplier_id || null);
		return res.status(201).json({ id: info.lastInsertRowid });
	} catch (e) {
		return res.status(400).json({ error: e.message });
	}
});

router.get('/suppliers', (req, res) => {
	const rows = db.prepare('SELECT * FROM suppliers ORDER BY name ASC').all();
	res.json(rows);
});

router.post('/suppliers', (req, res) => {
	const { name, contact, email, phone, address } = req.body;
	try {
		const stmt = db.prepare(`INSERT INTO suppliers (name, contact, email, phone, address)
		VALUES (?, ?, ?, ?, ?)`);
		const info = stmt.run(name, contact || null, email || null, phone || null, address || null);
		return res.status(201).json({ id: info.lastInsertRowid });
	} catch (e) {
		return res.status(400).json({ error: e.message });
	}
});

export default router;