# Email2Telegram VPS Deployment Guide

Complete guide to deploy Email2Telegram service on a VPS (Ubuntu/Debian)

## 📋 Prerequisites

- VPS with Ubuntu 20.04+ or Debian 11+
- Root or sudo access
- Domain name (optional but recommended)
- Telegram Bot Token
- KPay payment details

## 🚀 Step-by-Step Deployment

### 1. Initial VPS Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Create a non-root user (recommended)
sudo adduser email2telegram
sudo usermod -aG sudo email2telegram
su - email2telegram
```

### 2. Clone and Setup Project

```bash
# Clone your project (or upload via SCP/SFTP)
cd ~
git clone <your-repo-url> email2telegram
# OR upload your project folder

cd email2telegram

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add the following:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_GROUP_ID=your_admin_group_id

# KPay Payment Details
KPAY_PHONE=09XXXXXXXXX
KPAY_NAME=Your Name

# FastAPI Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./email2telegram.db
```

Save and exit (Ctrl+X, Y, Enter)

### 4. Setup Database

```bash
# Initialize database and add domains
python scripts/manage_domains.py

# Choose option 2 to add your domains
# Example: yourdomain.com, mail.yourdomain.com
```

### 5. Test the Application

```bash
# Test run
python main.py

# You should see:
# ✅ Telegram bot started successfully
# Uvicorn running on http://0.0.0.0:8000

# Press Ctrl+C to stop
```

### 6. Setup Systemd Service (Auto-start on boot)

```bash
# Create systemd service file
sudo nano /etc/systemd/system/email2telegram.service
```

Add the following:
```ini
[Unit]
Description=Email2Telegram Service
After=network.target

[Service]
Type=simple
User=email2telegram
WorkingDirectory=/home/email2telegram/email2telegram
Environment="PATH=/home/email2telegram/email2telegram/.venv/bin"
ExecStart=/home/email2telegram/email2telegram/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit.

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable email2telegram
sudo systemctl start email2telegram

# Check status
sudo systemctl status email2telegram

# View logs
sudo journalctl -u email2telegram -f
```

### 7. Setup Nginx Reverse Proxy (Recommended)

```bash
# Create nginx configuration
sudo nano /etc/nginx/sites-available/email2telegram
```

Add the following:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or VPS IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/email2telegram /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 8. Setup SSL Certificate (HTTPS) - Recommended

```bash
# Only if you have a domain name
sudo certbot --nginx -d your-domain.com

# Follow the prompts
# Choose option 2 to redirect HTTP to HTTPS
```

### 9. Configure Firewall

```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Check status
sudo ufw status
```

## 🌐 Cloudflare Email Worker Setup

### Option 1: Using Domain (Recommended)

Update your Cloudflare Worker with your domain:
```javascript
const WEBHOOK_URL = "https://your-domain.com/webhook/email";
```

### Option 2: Using IP Address (Works but not recommended)

Update your Cloudflare Worker with your VPS IP:
```javascript
const WEBHOOK_URL = "http://YOUR_VPS_IP:8000/webhook/email";
```

**⚠️ Important Notes:**
- If using IP without Nginx, ensure port 8000 is open:
  ```bash
  sudo ufw allow 8000
  ```
- Using domain + HTTPS is more secure and reliable
- Cloudflare may have issues with non-HTTPS webhooks

### Deploy Worker to Cloudflare

1. Go to Cloudflare Dashboard → Email Routing → Email Workers
2. Create new worker
3. Paste the content from `cloudflare-worker.js`
4. Update `WEBHOOK_URL` with your server URL
5. Save and deploy

## 📊 Monitoring and Maintenance

### View Logs
```bash
# Real-time logs
sudo journalctl -u email2telegram -f

# Last 100 lines
sudo journalctl -u email2telegram -n 100

# Logs from today
sudo journalctl -u email2telegram --since today
```

### Restart Service
```bash
sudo systemctl restart email2telegram
```

### Update Application
```bash
cd ~/email2telegram
git pull  # or upload new files
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart email2telegram
```

### Database Management
```bash
# Manage domains
python scripts/manage_domains.py

# Backup database
cp email2telegram.db email2telegram.db.backup

# View database
sqlite3 email2telegram.db
```

## 🔧 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u email2telegram -n 50

# Check if port is in use
sudo lsof -i :8000

# Test manually
cd ~/email2telegram
source .venv/bin/activate
python main.py
```

### Emails not being received
1. Check Cloudflare Worker logs
2. Verify webhook URL is correct
3. Check service logs: `sudo journalctl -u email2telegram -f`
4. Test webhook manually:
   ```bash
   curl -X POST http://localhost:8000/webhook/email \
     -H "Content-Type: message/rfc822" \
     -d "test email content"
   ```

### Bot not responding
1. Check bot token is correct in `.env`
2. Verify service is running: `sudo systemctl status email2telegram`
3. Check Telegram API is accessible from VPS

## 🔐 Security Best Practices

1. **Use HTTPS** - Always use SSL/TLS with domain
2. **Firewall** - Only open necessary ports
3. **Regular Updates** - Keep system and packages updated
4. **Backup Database** - Regular backups of `email2telegram.db`
5. **Environment Variables** - Never commit `.env` to git
6. **Admin Access** - Restrict admin group access

## 📈 Performance Optimization

### For High Traffic
```bash
# Increase worker processes in main.py
# Edit main.py and add:
uvicorn.run(
    app,
    host=FASTAPI_HOST,
    port=FASTAPI_PORT,
    workers=4  # Add this line
)
```

### Database Optimization
```bash
# Use PostgreSQL instead of SQLite for production
# Update DATABASE_URL in .env:
DATABASE_URL=postgresql+asyncpg://user:password@localhost/email2telegram
```

## 📞 Support

- Check logs first: `sudo journalctl -u email2telegram -f`
- Test components individually
- Verify all environment variables are set
- Ensure domains are added to database

## ✅ Deployment Checklist

- [ ] VPS setup complete
- [ ] Python and dependencies installed
- [ ] Project uploaded/cloned
- [ ] `.env` file configured
- [ ] Database initialized
- [ ] Domains added to database
- [ ] Systemd service created and running
- [ ] Nginx configured (if using domain)
- [ ] SSL certificate installed (if using domain)
- [ ] Firewall configured
- [ ] Cloudflare Worker deployed
- [ ] Test email sent and received
- [ ] Bot commands working
- [ ] Payment system tested

---

**Your service will be accessible at:**
- With domain: `https://your-domain.com`
- With IP: `http://YOUR_VPS_IP:8000`

**Webhook URL for Cloudflare:**
- Recommended: `https://your-domain.com/webhook/email`
- Alternative: `http://YOUR_VPS_IP:8000/webhook/email`
