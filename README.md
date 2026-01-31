# Location Radius Map

A privacy-focused Google Maps component with a backend database. Users can search for an address and see nearby saved locations (within 1/4 mile) displayed as colored circles.

## Features

- Search any address to display an approximate 1/8 mile radius
- Shows saved database locations within 1/4 mile of the searched address
- Different colors: Blue for searched location, Yellow/Orange for database locations
- Privacy protection: Coordinates are slightly randomized
- No markers placed at exact locations
- Embeddable on any website
- Mobile responsive

## Project Structure

```
├── server.js          # Node.js/Express backend
├── package.json       # Dependencies
├── addresses.db       # SQLite database (created on first run)
└── public/
    └── index.html     # Frontend map interface
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Get a Google Maps API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable: **Maps JavaScript API** and **Geocoding API**
4. Go to "Credentials" and create an API key

### 3. Add Your API Key

Edit `public/index.html` and replace `YOUR_API_KEY` with your actual API key (line 412).

### 4. Run the Server

```bash
npm start
```

Server runs at `http://localhost:3000`

## Adding Addresses to the Database (Admin)

Addresses are added via the API. Users cannot add addresses - only admins can.

### Using curl

```bash
# Add a single address
curl -X POST http://localhost:3000/api/addresses \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, City, State", "lat": 40.7128, "lng": -74.0060, "label": "Location A"}'
```

### Using a REST client (Postman, Insomnia, etc.)

**POST** `http://localhost:3000/api/addresses`

```json
{
  "address": "123 Main St, City, State",
  "lat": 40.7128,
  "lng": -74.0060,
  "label": "Optional label"
}
```

### Getting coordinates for an address

You can use Google's Geocoding API or search the address on Google Maps and extract coordinates from the URL.

### View all addresses

```bash
curl http://localhost:3000/api/addresses
```

### Delete an address

```bash
curl -X DELETE http://localhost:3000/api/addresses/1
```

(Replace `1` with the address ID)

## How It Works

1. User enters an address and clicks Search
2. The frontend geocodes the address to get coordinates
3. The blue circle appears showing the searched location (1/8 mile radius)
4. The frontend queries the API for database addresses within 1/4 mile
5. Yellow/orange circles appear for any nearby saved locations

## Embedding

```html
<iframe
    src="https://yourserver.com/?embed=true"
    width="100%"
    height="600"
    style="border: none;">
</iframe>
```

With pre-populated address:

```html
<iframe
    src="https://yourserver.com/?embed=true&address=Times%20Square%2C%20New%20York"
    width="100%"
    height="600"
    style="border: none;">
</iframe>
```

## Configuration

Edit `CONFIG` in `public/index.html`:

```javascript
const CONFIG = {
    RADIUS_METERS: 201.168,        // 1/8 mile display radius
    PRIVACY_OFFSET_METERS: 50,     // Random offset for privacy
    API_BASE_URL: window.location.origin  // Change for production
};
```

Edit `server.js` for the nearby search radius:

```javascript
const QUARTER_MILE_METERS = 402.336;  // Distance to search for nearby addresses
```

## Deployment

For production, you'll need a Node.js hosting environment (Railway, Render, Fly.io, DigitalOcean, etc.) since this requires a backend server.

## License

MIT License
