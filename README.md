# Email to Telegram Service

## Local Development Setup

### 1. Install Dependencies

Make sure your virtual environment is activated:
```bash
.venv\Scripts\activate
```

Install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Run the FastAPI Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 3. Expose Local Server to Internet

You have two main options to expose your local development server:

#### Option A: Using ngrok (Recommended for Quick Testing)

1. **Download ngrok**: Visit [ngrok.com](https://ngrok.com/) and download for Windows
2. **Sign up** for a free account to get an auth token
3. **Install and authenticate**:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```
4. **Expose your local server**:
   ```bash
   ngrok http 8000
   ```
5. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`) and use it in the Cloudflare Worker

#### Option B: Using Cloudflare Tunnel (Better for Long-term Development)

1. **Install cloudflared**:
   ```bash
   winget install --id Cloudflare.cloudflared
   ```
   Or download from [Cloudflare's website](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)

2. **Authenticate** (first time only):
   ```bash
   cloudflared tunnel login
   ```

3. **Create a tunnel**:
   ```bash
   cloudflared tunnel create email-webhook
   ```

4. **Run the tunnel**:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
   
   Or for a named tunnel with custom domain (requires DNS setup):
   ```bash
   cloudflared tunnel route dns email-webhook your-subdomain.yourdomain.com
   cloudflared tunnel run email-webhook
   ```

5. **Copy the tunnel URL** and use it in the Cloudflare Worker

### 4. Configure Cloudflare Email Worker

1. Go to your Cloudflare Dashboard
2. Navigate to **Email Routing** → **Email Workers**
3. Create a new worker or edit existing one
4. Copy the contents of `cloudflare-worker.js`
5. **Replace** `YOUR_NGROK_OR_CLOUDFLARE_TUNNEL_URL` with your actual tunnel URL (e.g., `https://abc123.ngrok.io`)
6. Save and deploy the worker
7. Set up email routing rules to use this worker

### 5. Test the Setup

Send a test email to your catch-all email address. You should see:
- Detailed output in your FastAPI console showing all parsed email data
- The Cloudflare Worker logs showing successful forwarding

## Project Structure

```
email2telegram/
├── .venv/                  # Virtual environment
├── main.py                 # FastAPI webhook server
├── cloudflare-worker.js    # Cloudflare Email Worker code
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## API Endpoints

- `GET /` - Health check endpoint
- `POST /webhook/email` - Receives raw MIME email from Cloudflare Worker

## Next Steps

After confirming the email parsing works:
1. Set up database models (SQLAlchemy)
2. Implement Telegram bot integration
3. Add user management and credit system
4. Implement email logging
