import { Router } from 'express';
import db from '../db/index.js';

const router = Router();

router.get('/', async (req, res) => {
	const today = db.prepare("SELECT DATE('now') AS d").get().d;
	const dailyOrders = db.prepare("SELECT COUNT(DISTINCT po.id) as c FROM purchase_orders po WHERE DATE(po.ordered_at)=DATE('now')").get().c;
	const dailyDeliveries = db.prepare("SELECT COUNT(DISTINCT dn.id) as c FROM delivery_notes dn WHERE DATE(dn.received_at)=DATE('now')").get().c;
	const dailyPendings = db.prepare("SELECT COUNT(1) as c FROM pendings WHERE status!='closed' AND (due_date IS NULL OR DATE(due_date) >= DATE('now'))").get().c;

	const labels = ['Week 1','Week 2','Week 3','Week 4'];
	// simple monthly agg based on items quantities
	const monthlyOrders = db.prepare("SELECT COUNT(1) as c FROM purchase_orders WHERE strftime('%Y-%m', ordered_at)=strftime('%Y-%m','now')").get().c;
	const monthlyDeliveries = db.prepare("SELECT COUNT(1) as c FROM delivery_notes WHERE strftime('%Y-%m', received_at)=strftime('%Y-%m','now')").get().c;
	const monthlyRevenue = db.prepare("SELECT IFNULL(SUM(quantity*unit_price),0) as s FROM delivery_note_items dni JOIN delivery_notes dn ON dn.id=dni.delivery_note_id WHERE strftime('%Y-%m', dn.received_at)=strftime('%Y-%m','now')").get().s;
	const monthlyCost = db.prepare("SELECT IFNULL(SUM(quantity*cost_price),0) as s FROM delivery_note_items dni JOIN delivery_notes dn ON dn.id=dni.delivery_note_id WHERE strftime('%Y-%m', dn.received_at)=strftime('%Y-%m','now')").get().s;

	res.render('dashboard', {
		title: 'Dashboard',
		daily: { orders: dailyOrders, deliveries: dailyDeliveries, pendings: dailyPendings },
		monthly: { orders: monthlyOrders, deliveries: monthlyDeliveries, pendings: dailyPendings, revenue: monthlyRevenue, cost: monthlyCost },
		charts: { labels, orders: [], deliveries: [], costs: [], revenues: [] }
	});
});

export default router;