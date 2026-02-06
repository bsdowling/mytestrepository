# One-Minute Review

A mobile-first web app that lets real-estate clients create polished Zillow/Google reviews by answering just 1-2 prompts. Agents pre-fill context via admin-generated tokenized links so clients spend under a minute.

## Quick Start (Replit)

1. Click **Run** — the `.replit` file installs dependencies and starts the server.
2. Open the app URL in your browser.
3. Go to `/admin` and log in with the password set in your `.env` file (default: `admin123`).
4. Set up your Agent Profile (name, brokerage, city, Zillow/Google URLs).
5. Create a Review Request Link with client context (buy/sell, city, property nickname).
6. Share the generated link with your client.

## Manual Setup

```bash
pip install -r requirements.txt
python3 main.py
```

The server runs on `http://0.0.0.0:8080` by default.

## Environment Variables

Create a `.env` file:

```
SECRET_KEY=your-random-secret-key
ADMIN_PASSWORD=your-admin-password
SALT=your-ip-hashing-salt
```

## How It Works

### For the Agent (Admin)

1. **Log in** at `/admin` with your `ADMIN_PASSWORD`.
2. **Set up your profile**: name, brokerage, market city, brand color, logo URL.
3. **Add platform links**: Paste your Zillow review page URL and/or Google review URL.
4. **Create review request links**: Fill in transaction details (buy/sell, city, property nickname, close date) and generate a unique tokenized URL.
5. **Share the link** via text or email using the SMS template provided.

### For the Client

1. **Open the link** (e.g., `yourapp.com/r/abcd1234`).
2. **Answer one question**: "What stood out working with [Agent Name]?"
3. **Optionally set a star rating** (1-5).
4. **Click "Generate my review"** — three review variants appear instantly.
5. **Copy** the preferred review and click the Zillow or Google button to post.

### Without a Token (Fallback Mode)

1. Visit the app root (`/`).
2. Select "Buying" or "Selling".
3. Enter a city or neighborhood.
4. Answer the same standout question and generate.

## Finding Your Google Place ID

1. Go to [Google's Place ID Finder](https://developers.google.com/maps/documentation/places/web-service/place-id).
2. Search for your business name.
3. Copy the Place ID (starts with `ChIJ...`).
4. Paste it in Admin under "Google Place ID" — the app builds the review URL automatically.

Alternatively, paste a full Google "Write a Review" URL directly.

## Creating and Sharing Tokenized Review Links

1. In Admin, click "Create Review Request Link".
2. Fill in: transaction type, city, neighborhood, property nickname, close month/year.
3. Click "Create Link" — a unique URL like `/r/abcd1234` is generated.
4. Copy the URL and share it. Use the SMS template:

> "Hey! Tap this and write 1-2 sentences about what stood out. It'll draft your Zillow/Google review for you in seconds: [link]"

## Copy/Paste Tips

- **Zillow**: Click "Copy" on your preferred review variant, then click "Post on Zillow". Paste into the review text box on Zillow.
- **Google**: Click "Copy", then click "Write a Google Review". Paste into the Google review form.

## Privacy

- Client IP addresses are hashed with a salt before logging.
- Full review text is not stored with client identity.
- The submission log records only metadata (city, transaction type, word count, rating, consent).
- All generated pages include `noindex` meta tags.

## File Structure

```
main.py                 # Flask app and routes
models.py               # SQLAlchemy database models
forms.py                # Flask-WTF form definitions
utils/review_generator.py  # Server-side review text generator
templates/
  base.html             # Base template with Tailwind CDN
  fallback.html         # No-token landing page
  review.html           # Client review form (main flow)
  results.html          # Non-JS results fallback
  admin_login.html      # Admin login page
  admin.html            # Admin dashboard
.replit                 # Replit run configuration
replit.nix              # Nix dependencies for Replit
requirements.txt        # Python dependencies
.env                    # Environment variables (not committed)
```
