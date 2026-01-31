const express = require('express');
const cors = require('cors');
const Database = require('better-sqlite3');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Initialize SQLite database
const db = new Database('addresses.db');

// Create addresses table if it doesn't exist
db.exec(`
    CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        label TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
`);

// API Routes

// GET all addresses
app.get('/api/addresses', (req, res) => {
    try {
        const addresses = db.prepare('SELECT * FROM addresses ORDER BY created_at DESC').all();
        res.json(addresses);
    } catch (error) {
        console.error('Error fetching addresses:', error);
        res.status(500).json({ error: 'Failed to fetch addresses' });
    }
});

// POST new address
app.post('/api/addresses', (req, res) => {
    const { address, lat, lng, label } = req.body;

    if (!address || lat === undefined || lng === undefined) {
        return res.status(400).json({ error: 'Address, lat, and lng are required' });
    }

    try {
        const stmt = db.prepare('INSERT INTO addresses (address, lat, lng, label) VALUES (?, ?, ?, ?)');
        const result = stmt.run(address, lat, lng, label || null);

        res.status(201).json({
            id: result.lastInsertRowid,
            address,
            lat,
            lng,
            label
        });
    } catch (error) {
        console.error('Error saving address:', error);
        res.status(500).json({ error: 'Failed to save address' });
    }
});

// DELETE address by ID
app.delete('/api/addresses/:id', (req, res) => {
    const { id } = req.params;

    try {
        const stmt = db.prepare('DELETE FROM addresses WHERE id = ?');
        const result = stmt.run(id);

        if (result.changes === 0) {
            return res.status(404).json({ error: 'Address not found' });
        }

        res.json({ message: 'Address deleted successfully' });
    } catch (error) {
        console.error('Error deleting address:', error);
        res.status(500).json({ error: 'Failed to delete address' });
    }
});

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
