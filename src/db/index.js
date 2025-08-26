import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dbPath = path.join(__dirname, 'app.db');
const db = new Database(dbPath);

db.pragma('journal_mode = WAL');

const schemaSql = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8');
db.exec(schemaSql);

// Seed only if fresh
const row = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='products'").get();
const count = row ? db.prepare('SELECT COUNT(1) as c FROM products').get().c : 0;
if (count === 0) {
	const seedSql = fs.readFileSync(path.join(__dirname, 'seed.sql'), 'utf8');
	db.exec(seedSql);
}

export default db;