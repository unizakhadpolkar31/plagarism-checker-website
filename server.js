const express = require('express');
const bodyParser = require('body-parser');
const { Pool } = require('pg');
const cors = require('cors');
const multer = require('multer');
const session = require('express-session');

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cors());
app.use(session({ secret: 'your_secret_key', resave: false, saveUninitialized: true }));

// Setup multer for file upload
const upload = multer({ dest: 'uploads/' });

// Database connection configuration
const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'postgres',
    password: 'root',
    port: 5432,
});

// Admin credentials
const adminCredentials = {
    username: 'admin',
    password: 'adminpassword' // Change this to a secure password
};

// Admin login route
app.post('/admin_login', (req, res) => {
    const { username, password } = req.body;
    if (username === adminCredentials.username && password === adminCredentials.password) {
        req.session.isAdmin = true; // Set session variable
        return res.redirect('/admin/dashboard'); // Redirect to dashboard
    }
    res.status(401).send('Invalid credentials');
});

// Admin dashboard route to display submissions
app.get('/admin/dashboard', async (req, res) => {
    if (!req.session.isAdmin) {
        return res.status(403).send('Access denied');
    }

    try {
        const result = await pool.query('SELECT * FROM submissions');
        res.json(result.rows); // You can render this data in an HTML page
    } catch (err) {
        console.error('Error fetching submissions:', err);
        res.status(500).send('Error fetching submissions');
    }
});

// Function to insert data into the database
const submit_form = async (formData, pdfFile) => {
    const { username, email, mobile, hours, pages, education } = formData;

    try {
        const queryText = 'INSERT INTO submissions(username, email, mobile, pdf, hours, pages, education) VALUES($1, $2, $3, $4, $5, $6, $7)';
        await pool.query(queryText, [username, email, mobile, pdfFile ? pdfFile.filename : null, hours, pages, education]);
        return { success: true, message: 'Form submitted successfully!' };
    } catch (err) {
        console.error('Error saving to database:', err.message, err.stack);
        return { success: false, message: 'Error saving to database' };
    }
};

// Route handler using the submit_form function
app.post('/submit_form', upload.single('pdf'), async (req, res) => {
    try {
        const { username, email, mobile, hours, pages, education } = req.body;
        const pdf = req.file;

        // Validate the received data
        if (!username || !email || !mobile || !hours || !pages || !education || !pdf) {
            return res.status(400).send('Missing form data or file');
        }

        console.log('Form Data:', { username, email, mobile, hours, pages, education });
        console.log('PDF Upload:', pdf.filename);

        // Insert into database logic
        await submit_form(req.body, pdf);

        res.send('Form submitted successfully!');
    } catch (err) {
        console.error('Error saving to database:', err.message, err.stack);
        res.status(500).send('Error saving to database');
    }
});

// Test database connection
pool.query('SELECT 1', (err, res) => {
    if (err) {
        console.error('Error connecting to the database:', err.stack);
    } else {
        console.log('Database connection test successful:', res.rows);
    }
});

// Start the server
app.listen(3000, () => {
    console.log('Server is running on port 3000');
});