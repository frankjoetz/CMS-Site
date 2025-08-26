import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import expressLayouts from 'express-ejs-layouts';
import morgan from 'morgan';
import bodyParser from 'body-parser';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.set('layout', 'layouts/main');
app.use(expressLayouts);

app.use(morgan('dev'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Routes
import dashboardRouter from './routes/dashboard.js';
import pagesRouter from './routes/pages.js';
import apiRouter from './routes/rest.js';

app.use('/', dashboardRouter);
app.use('/', pagesRouter);
app.use('/api', apiRouter);

app.use((req, res) => {
	res.status(404).render('404', { title: 'Not Found' });
});

app.listen(PORT, () => {
	console.log(`Server running on http://localhost:${PORT}`);
});