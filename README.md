# Location Radius Map

A privacy-focused Google Maps component that displays a 1/4 mile radius around a location without revealing the exact address.

## Features

- Enter any address to display an approximate area
- Shows a 1/4 mile (400 meter) radius circle
- Privacy protection: The center point is slightly randomized so the exact address is not revealed
- No marker placed at the exact location
- Embeddable on any website
- Mobile responsive

## Setup

### 1. Get a Google Maps API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - **Maps JavaScript API**
   - **Geocoding API**
4. Go to "Credentials" and create an API key
5. (Recommended) Restrict your API key to your domain for security

### 2. Add Your API Key

Open `index.html` and replace `YOUR_API_KEY` with your actual API key:

```html
<script async defer
    src="https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY&callback=initMap">
</script>
```

### 3. Deploy

Upload `index.html` to your web server or hosting service.

## Usage

### Standalone Page

Simply open the page in a browser, enter an address, and click "Search".

### Embedding on Your Website

Use an iframe to embed the map:

```html
<iframe
    src="https://yourdomain.com/index.html?embed=true"
    width="100%"
    height="600"
    style="border: none; border-radius: 12px;"
></iframe>
```

### Pre-populated Address

You can pre-load an address using URL parameters:

```
https://yourdomain.com/index.html?address=Times%20Square%2C%20New%20York
```

Combined with embed mode:

```
https://yourdomain.com/index.html?embed=true&address=Times%20Square%2C%20New%20York
```

## Configuration

You can customize the behavior by editing the `CONFIG` object in `index.html`:

```javascript
const CONFIG = {
    RADIUS_METERS: 402.336,        // 1/4 mile in meters (change for different radius)
    DEFAULT_ZOOM: 15,              // Map zoom level
    CIRCLE_FILL_COLOR: '#4285f4', // Circle fill color
    CIRCLE_FILL_OPACITY: 0.2,     // Circle transparency
    CIRCLE_STROKE_COLOR: '#4285f4',
    CIRCLE_STROKE_OPACITY: 0.8,
    CIRCLE_STROKE_WEIGHT: 2,
    PRIVACY_OFFSET_METERS: 50     // Random offset for privacy (increase for more privacy)
};
```

### Common Radius Values

| Distance | Meters |
|----------|--------|
| 1/4 mile | 402.336 |
| 1/2 mile | 804.672 |
| 1 mile   | 1609.34 |
| 1 km     | 1000 |
| 5 km     | 5000 |

## Privacy Features

This map is designed to show an approximate area without revealing the exact location:

1. **No markers**: Unlike typical maps, no pin is placed at the exact address
2. **Random offset**: The center of the circle is randomly shifted by up to 50 meters
3. **Area display**: Only shows the general neighborhood, not the specific property

## License

MIT License - Feel free to use and modify for your projects.
