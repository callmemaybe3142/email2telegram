# Cloudflare Tunnel Deployment Guide

Deploy Email2Telegram using Cloudflare Tunnel (no port forwarding, no public IP exposure)

## 🌟 Why Cloudflare Tunnel?

- ✅ No need to open ports (firewall stays closed)
- ✅ No public IP exposure
- ✅ Free HTTPS automatically
- ✅ DDoS protection
- ✅ Works behind NAT/firewall
- ✅ No domain DNS configuration needed

## 📋 Prerequisites

- VPS with Ubuntu/Debian
- Cloudflare account (free)
- Domain added to Cloudflare (free)

## 🚀 Step-by-Step Setup

### 1. Initial VPS Setup

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv git curl

# Create user (optional but recommended)
sudo adduser email2telegram
sudo usermod -aG sudo email2telegram
su - email2telegram
```

### 2. Install Cloudflare Tunnel (cloudflared)

```bash
# Download and install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

sudo dpkg -i cloudflared.deb

# Verify installation
cloudflared --version
```

### 3. Setup Your Application

```bash
# Clone/upload your project
cd ~
git clone <your-repo> email2telegram
# OR upload via SCP

cd email2telegram

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Create .env file
nano .env
```

Add:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_GROUP_ID=your_admin_group_id
KPAY_PHONE=09XXXXXXXXX
KPAY_NAME=Your Name

# Important: Use localhost since tunnel handles external access
FASTAPI_HOST=127.0.0.1
FASTAPI_PORT=8000

DATABASE_URL=sqlite+aiosqlite:///./email2telegram.db
```

### 5. Setup Database

```bash
# Initialize database
python scripts/manage_domains.py

# Add your domains
# Example: mail.yourdomain.com
```

### 6. Create Systemd Service for Application

```bash
sudo nano /etc/systemd/system/email2telegram.service
```

Add:
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

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable email2telegram
sudo systemctl start email2telegram

# Check status
sudo systemctl status email2telegram
```

### 7. Authenticate Cloudflare Tunnel

```bash
# Login to Cloudflare (opens browser)
cloudflared tunnel login

# This will:
# 1. Open a browser window
# 2. Ask you to select your domain
# 3. Save credentials to ~/.cloudflared/cert.pem
```

### 8. Create Tunnel

```bash
# Create a tunnel (choose a name, e.g., "email2telegram")
cloudflared tunnel create email2telegram

# Note the Tunnel ID shown (you'll need it)
# Example: Created tunnel email2telegram with id abc123-def456-ghi789
```

### 9. Configure Tunnel

```bash
# Create config directory
mkdir -p ~/.cloudflared

# Create tunnel configuration
nano ~/.cloudflared/config.yml
```

Add the following:
```yaml
tunnel: email2telegram  # Your tunnel name
credentials-file: /home/email2telegram/.cloudflared/abc123-def456-ghi789.json  # Replace with your tunnel ID

ingress:
  # Route for email webhook
  - hostname: mail.yourdomain.com  # Replace with your subdomain
    service: http://127.0.0.1:8000
  
  # Catch-all rule (required)
  - service: http_status:404
```

**Important:** Replace:
- `email2telegram` with your username if different
- `abc123-def456-ghi789.json` with your actual tunnel ID
- `mail.yourdomain.com` with your chosen subdomain

### 10. Create DNS Record

```bash
# Create DNS record pointing to your tunnel
cloudflared tunnel route dns email2telegram mail.yourdomain.com

# Replace:
# - email2telegram: your tunnel name
# - mail.yourdomain.com: your subdomain
```

This automatically creates a CNAME record in Cloudflare DNS.

### 11. Create Systemd Service for Tunnel

```bash
sudo nano /etc/systemd/system/cloudflared.service
```

Add:
```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=email2telegram
ExecStart=/usr/bin/cloudflared tunnel --config /home/email2telegram/.cloudflared/config.yml run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start tunnel
sudo systemctl daemon-reload
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# Check status
sudo systemctl status cloudflared
```

### 12. Update Cloudflare Email Worker

Update your `cloudflare-worker.js`:
```javascript
const WEBHOOK_URL = "https://mail.yourdomain.com/webhook/email";
```

Deploy the worker to Cloudflare.

## ✅ Verification

### Test Your Setup

```bash
# Check if application is running
sudo systemctl status email2telegram

# Check if tunnel is running
sudo systemctl status cloudflared

# View application logs
sudo journalctl -u email2telegram -f

# View tunnel logs
sudo journalctl -u cloudflared -f
```

### Test Webhook

```bash
# From your local machine or another server
curl https://mail.yourdomain.com/

# Should return:
# {"status":"Email2Telegram Service Running",...}
```

### Send Test Email

Send an email to one of your configured addresses and check if it arrives in Telegram.

## 🔧 Troubleshooting

### Tunnel Not Connecting

```bash
# Check tunnel status
cloudflared tunnel info email2telegram

# Test tunnel manually
cloudflared tunnel --config ~/.cloudflared/config.yml run

# Check logs
sudo journalctl -u cloudflared -n 50
```

### Application Not Accessible

```bash
# Verify app is running on localhost:8000
curl http://127.0.0.1:8000/

# Check if port is in use
sudo lsof -i :8000

# Restart services
sudo systemctl restart email2telegram
sudo systemctl restart cloudflared
```

### DNS Not Resolving

```bash
# Check DNS record
nslookup mail.yourdomain.com

# Should show Cloudflare IP (not your VPS IP)

# Recreate DNS record if needed
cloudflared tunnel route dns email2telegram mail.yourdomain.com
```

## 🔐 Security Benefits

With Cloudflare Tunnel:
- ✅ **No open ports** - Firewall can block everything except SSH
- ✅ **No IP exposure** - Your VPS IP stays hidden
- ✅ **Free HTTPS** - Automatic SSL/TLS
- ✅ **DDoS protection** - Cloudflare's network protects you
- ✅ **No port forwarding** - Works behind any firewall/NAT

### Firewall Configuration (Optional)

```bash
# You can now block everything except SSH
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable

# Port 8000 stays closed - tunnel handles it!
```

## 📊 Monitoring

### View Logs

```bash
# Application logs
sudo journalctl -u email2telegram -f

# Tunnel logs
sudo journalctl -u cloudflared -f

# Combined view
sudo journalctl -u email2telegram -u cloudflared -f
```

### Restart Services

```bash
# Restart application
sudo systemctl restart email2telegram

# Restart tunnel
sudo systemctl restart cloudflared

# Restart both
sudo systemctl restart email2telegram cloudflared
```

## 🔄 Updates and Maintenance

### Update Application

```bash
cd ~/email2telegram
git pull  # or upload new files
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart email2telegram
```

### Update Cloudflared

```bash
# Download latest version
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

sudo dpkg -i cloudflared.deb
sudo systemctl restart cloudflared
```

## 🌐 Multiple Tunnels (Optional)

You can create multiple tunnels for different services:

```bash
# Create another tunnel
cloudflared tunnel create another-service

# Add to config.yml
nano ~/.cloudflared/config.yml
```

```yaml
tunnel: email2telegram
credentials-file: /home/email2telegram/.cloudflared/abc123.json

ingress:
  - hostname: mail.yourdomain.com
    service: http://127.0.0.1:8000
  
  - hostname: admin.yourdomain.com
    service: http://127.0.0.1:8001
  
  - service: http_status:404
```

## 📋 Quick Reference

### Useful Commands

```bash
# List all tunnels
cloudflared tunnel list

# Get tunnel info
cloudflared tunnel info email2telegram

# Delete tunnel (if needed)
cloudflared tunnel delete email2telegram

# Test configuration
cloudflared tunnel --config ~/.cloudflared/config.yml ingress validate

# Run tunnel manually (for testing)
cloudflared tunnel --config ~/.cloudflared/config.yml run
```

## ✅ Deployment Checklist

- [ ] VPS setup complete
- [ ] cloudflared installed
- [ ] Cloudflare authenticated
- [ ] Tunnel created
- [ ] DNS record created
- [ ] Application running
- [ ] Tunnel running
- [ ] Both services auto-start on boot
- [ ] Webhook URL updated in Email Worker
- [ ] Test email sent and received
- [ ] Bot commands working

---

**Your service is now accessible at:**
`https://mail.yourdomain.com`

**No ports exposed, no IP visible, fully secure!** 🔒

## 🎯 Advantages Over Traditional Setup

| Feature | Traditional | Cloudflare Tunnel |
|---------|------------|-------------------|
| Port Forwarding | Required | Not needed |
| Public IP | Exposed | Hidden |
| SSL Setup | Manual | Automatic |
| DDoS Protection | None | Included |
| Firewall Config | Complex | Simple |
| Works Behind NAT | No | Yes |
| Cost | Varies | Free |

**Cloudflare Tunnel is the modern, secure way to deploy!** 🚀
