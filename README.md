# Location Radius Map

A privacy-focused Google Maps component that uses Google Sheets as a database. Users can search for an address and see nearby saved locations (within 1/4 mile) displayed as colored circles.

## Features

- Search any address to display an approximate 1/8 mile radius
- Shows saved locations from Google Sheets within 1/4 mile of the searched address
- Different colors: Blue for searched location, Yellow/Orange for saved locations
- Privacy protection: Coordinates are slightly randomized
- No markers placed at exact locations
- Static HTML - no server required, host anywhere
- Mobile responsive

## Setup

### Step 1: Create Your Google Sheet

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet
2. Name it something like "Location Database"
3. Set up these columns in Row 1:

| A | B | C | D |
|---|---|---|---|
| address | lat | lng | label |

4. Add your addresses starting from Row 2:

| address | lat | lng | label |
|---------|-----|-----|-------|
| 123 Main St, Austin, TX | 30.2672 | -97.7431 | Location A |
| 456 Oak Ave, Austin, TX | 30.2700 | -97.7400 | Location B |

### Step 2: Get Your Google Sheet ID

Your Sheet URL looks like:
```
https://docs.google.com/spreadsheets/d/1ABC123xyz789/edit
```

The Sheet ID is the part between `/d/` and `/edit`:
```
1ABC123xyz789
```

### Step 3: Get a Google API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable these APIs:
   - **Maps JavaScript API**
   - **Geocoding API**
   - **Google Sheets API**
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. (Recommended) Click "Edit API Key" and restrict it:
   - Under "Application restrictions" → "HTTP referrers"
   - Add your domain (e.g., `https://yourdomain.com/*`)
   - Under "API restrictions" → Select the 3 APIs above

### Step 4: Configure index.html

Open `index.html` and update the CONFIG section (around line 175):

```javascript
const CONFIG = {
    GOOGLE_SHEET_ID: 'YOUR_GOOGLE_SHEET_ID',  // From Step 2
    GOOGLE_API_KEY: 'YOUR_GOOGLE_API_KEY',     // From Step 3
    SHEET_NAME: 'Sheet1',                       // Your tab name
    // ... rest of config
};
```

Also update the Google Maps script at the bottom (line googlemaps):

```html
<script async defer
    src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_API_KEY&callback=initMap">
</script>
```

### Step 5: Deploy to Bluehost

1. Upload `index.html` to your Bluehost File Manager
2. That's it! No server needed.

## Adding Addresses

Simply add new rows to your Google Sheet:

| address | lat | lng | label |
|---------|-----|-----|-------|
| 789 Pine St, Austin, TX | 30.2650 | -97.7450 | New Location |

The map will automatically pick up new addresses on the next search.

### How to Get Coordinates

1. Go to [Google Maps](https://maps.google.com)
2. Search for the address
3. Right-click on the exact location
4. Click the coordinates to copy them (e.g., `30.2672, -97.7431`)
5. First number = lat, second number = lng

## Embedding

```html
<iframe
    src="https://yourdomain.com/index.html?embed=true"
    width="100%"
    height="600"
    style="border: none;">
</iframe>
```

With pre-populated address:

```html
<iframe
    src="https://yourdomain.com/index.html?embed=true&address=Austin%2C%20TX"
    width="100%"
    height="600"
    style="border: none;">
</iframe>
```

## Configuration Options

Edit the `CONFIG` object in `index.html`:

```javascript
const CONFIG = {
    GOOGLE_SHEET_ID: 'your-sheet-id',
    GOOGLE_API_KEY: 'your-api-key',
    SHEET_NAME: 'Sheet1',

    RADIUS_METERS: 201.168,         // Display circle size (1/8 mile)
    QUARTER_MILE_METERS: 402.336,   // Search radius for nearby locations
    PRIVACY_OFFSET_METERS: 50,      // Random offset for privacy

    // Circle colors
    SEARCHED_FILL_COLOR: '#4285f4',  // Blue for searched
    SAVED_FILL_COLOR: '#f9ab00',     // Yellow for saved
};
```

## Troubleshooting

**"Failed to fetch from Google Sheets"**
- Make sure your API key has Sheets API enabled
- Check that the Sheet ID is correct
- Verify the sheet name matches exactly

**Addresses not showing**
- Check that lat/lng columns have valid numbers
- Make sure there are no empty rows between data
- Column headers must be exactly: `address`, `lat`, `lng`, `label`

**Map not loading**
- Verify Maps JavaScript API is enabled
- Check browser console for errors
- Make sure API key is correct in both CONFIG and script tag

## License

MIT License
