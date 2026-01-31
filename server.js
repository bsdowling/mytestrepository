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

// Haversine formula to calculate distance between two points in meters
function getDistanceInMeters(lat1, lng1, lat2, lng2) {
    const R = 6371000; // Earth's radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

const QUARTER_MILE_METERS = 402.336;

// API Routes

// GET addresses near a location (within 1/4 mile)
app.get('/api/addresses', (req, res) => {
    const { lat, lng } = req.query;

    try {
        const allAddresses = db.prepare('SELECT * FROM addresses ORDER BY created_at DESC').all();

        // If lat/lng provided, filter to only nearby addresses
        if (lat && lng) {
            const targetLat = parseFloat(lat);
            const targetLng = parseFloat(lng);

            const nearbyAddresses = allAddresses.filter(addr => {
                const distance = getDistanceInMeters(targetLat, targetLng, addr.lat, addr.lng);
                return distance <= QUARTER_MILE_METERS;
            });

            return res.json(nearbyAddresses);
        }

        // If no lat/lng, return all (for admin purposes)
        res.json(allAddresses);
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
