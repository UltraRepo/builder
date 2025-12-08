# Dell DGX Spark Remote Desktop Setup Guide

Complete guide for secure remote desktop access to Dell DGX Spark Ubuntu GNOME machine from macOS.

---

## Table of Contents

1. [System Information](#system-information)
2. [Current Status](#current-status)
3. [Quick Start - Local Network Access](#quick-start---local-network-access)
4. [Cloudflare Zero Trust - Remote Access Anywhere](#cloudflare-zero-trust---remote-access-anywhere)
5. [Alternative Methods](#alternative-methods)
6. [Security Best Practices](#security-best-practices)
7. [Troubleshooting](#troubleshooting)

---

## System Information

- **Hostname:** `promaxgb10-70dc`
- **Username:** `cogitari`
- **Wired IP:** `192.168.1.70` (primary)
- **WiFi IP:** `192.168.1.74` (backup)
- **Domain (for remote access):** `vpn.clincentric.net`

---

## Current Status

✅ **GNOME Remote Desktop (RDP)** is enabled and running
- Service: `gnome-remote-desktop.service` (active)
- Port: 3389 (listening)
- Protocol: RDP (Remote Desktop Protocol)

✅ **Docker** is installed (v28.5.1)

❌ **SSH server** needs to be enabled for secure tunneling

---

## Quick Start - Local Network Access

### Enable Remote Desktop (Already Done)

The RDP service is already running. If you need to enable it manually:

```bash
# Enable RDP
gsettings set org.gnome.desktop.remote-desktop.rdp enable true

# Set screen sharing mode
gsettings set org.gnome.desktop.remote-desktop.rdp screen-share-mode 'mirror-primary'

# Enable and start the service
systemctl --user enable gnome-remote-desktop.service
systemctl --user start gnome-remote-desktop.service

# Verify it's running
systemctl --user status gnome-remote-desktop.service
ss -tlnp | grep 3389
```

### Connect from macOS (Local Network)

**Using Microsoft Remote Desktop:**

1. Install [Microsoft Remote Desktop](https://apps.apple.com/us/app/microsoft-remote-desktop/id1295203466) from Mac App Store

2. Open the app and click **"Add PC"**

3. Enter connection details:
   - **PC name:** `192.168.1.70` (or `promaxgb10-70dc.local`)
   - **User account:**
     - Username: `cogitari`
     - Password: (your Ubuntu password)

4. Click **"Add"** and double-click to connect

---

## Cloudflare Zero Trust - Remote Access Anywhere

Access your DGX Spark from anywhere via `vpn.clincentric.net` without exposing ports or setting up traditional VPN.

### Benefits

- ✅ No port forwarding required
- ✅ No public IP exposure
- ✅ Built-in DDoS protection
- ✅ Zero Trust authentication
- ✅ Encrypted tunnel
- ✅ Auto-restart on power failure
- ✅ Free tier (up to 50 users)

### Prerequisites

1. **Cloudflare account** with domain `clincentric.net` configured
2. **Cloudflare Zero Trust** account (free tier available)
3. **Docker** installed (✅ already installed)

---

### Step 1: Cloudflare Zero Trust Setup (Web Dashboard)

#### 1.1 Create Zero Trust Account

1. Go to [Cloudflare Zero Trust](https://one.dash.cloudflare.com/)
2. Sign in with your Cloudflare account
3. Create a team name (e.g., `clincentric`)

#### 1.2 Create a Tunnel

1. Navigate to **Access** → **Tunnels**
2. Click **Create a tunnel**
3. Choose **Cloudflared**
4. Name your tunnel: `dgx-spark-desktop`
5. Click **Save tunnel**
6. **Copy the tunnel token** (you'll need this for Docker)

#### 1.3 Configure Public Hostnames

Add two public hostnames for your tunnel:

**For RDP Access:**
- **Subdomain:** `vpn`
- **Domain:** `clincentric.net`
- **Service:** `rdp://localhost:3389`

**For SSH Access (backup):**
- **Subdomain:** `ssh`
- **Domain:** `clincentric.net`
- **Service:** `ssh://localhost:22`

#### 1.4 Configure Access Policies (Optional but Recommended)

1. Go to **Access** → **Applications**
2. Click **Add an application**
3. Choose **Self-hosted**
4. Configure:
   - **Application name:** DGX Desktop
   - **Subdomain:** `vpn`
   - **Domain:** `clincentric.net`
5. Add access policy (e.g., email-based authentication)

---

### Step 2: Docker Container Setup

#### 2.1 Create Directory and Docker Compose File

```bash
# Create directory
mkdir -p ~/cloudflare-tunnel
cd ~/cloudflare-tunnel

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cloudflared-tunnel
    restart: unless-stopped
    command: tunnel --no-autoupdate run --token YOUR_TUNNEL_TOKEN_HERE
    network_mode: host
    environment:
      - TUNNEL_TOKEN=YOUR_TUNNEL_TOKEN_HERE
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF
```

**Replace `YOUR_TUNNEL_TOKEN_HERE` with your actual tunnel token from Step 1.2**

#### 2.2 Start the Tunnel

```bash
cd ~/cloudflare-tunnel
docker compose up -d
```

#### 2.3 Verify Tunnel is Running

```bash
# Check container status
docker ps

# View logs
docker logs cloudflared-tunnel

# You should see:
# INF Connection registered connIndex=0
# INF Connection registered connIndex=1
# INF Connection registered connIndex=2
# INF Connection registered connIndex=3
```

---

### Step 3: Enable Auto-Restart on Boot

Docker containers with `restart: unless-stopped` automatically:
- ✅ Start on system boot
- ✅ Restart if they crash
- ✅ Restart after power failure

Ensure Docker itself starts on boot:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

### Step 4: Enable SSH Server

```bash
# Install SSH server
sudo apt update
sudo apt install openssh-server

# Enable and start SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Verify SSH is running
sudo systemctl status ssh
```

---

### Step 5: Connect from macOS via Cloudflare

#### Option A: RDP via Cloudflare Tunnel

**Using Microsoft Remote Desktop:**

1. Install [Microsoft Remote Desktop](https://apps.apple.com/us/app/microsoft-remote-desktop/id1295203466) from Mac App Store

2. If you configured Cloudflare Access (authentication):
   - Open browser and go to `https://vpn.clincentric.net`
   - Authenticate (email verification, etc.)

3. Open Microsoft Remote Desktop
4. Click **Add PC**
5. Enter:
   - **PC name:** `vpn.clincentric.net`
   - **User account:**
     - Username: `cogitari`
     - Password: (your Ubuntu password)
6. Click **Add** and connect

#### Option B: SSH via Cloudflare Tunnel

**From macOS Terminal:**

```bash
# Direct SSH (if no Access policy)
ssh cogitari@ssh.clincentric.net

# If you have Cloudflare Access enabled:
# Install cloudflared on macOS
brew install cloudflare/cloudflare/cloudflared

# Configure SSH to use cloudflared
cat >> ~/.ssh/config << 'EOF'
Host ssh.clincentric.net
  ProxyCommand /opt/homebrew/bin/cloudflared access ssh --hostname %h
  User cogitari
EOF

# Now SSH normally
ssh ssh.clincentric.net
```

#### Option C: RDP via SSH Tunnel (Most Secure)

```bash
# Create SSH tunnel through Cloudflare
ssh -L 3389:localhost:3389 cogitari@ssh.clincentric.net

# Then connect Microsoft Remote Desktop to localhost:3389
```

---

## Alternative Methods

### VNC (Alternative to RDP)

VNC provides better compatibility with macOS's built-in Screen Sharing but may have slightly lower performance than RDP.

#### Install and Configure x11vnc

```bash
# Install x11vnc
sudo apt update
sudo apt install x11vnc

# Set VNC password
x11vnc -storepasswd

# Create systemd service for auto-start
mkdir -p ~/.config/systemd/user/
cat > ~/.config/systemd/user/x11vnc.service << 'EOF'
[Unit]
Description=x11vnc Remote Desktop
After=display-manager.service

[Service]
Type=simple
ExecStart=/usr/bin/x11vnc -auth guess -forever -loop -noxdamage -repeat -rfbauth %h/.vnc/passwd -rfbport 5900 -shared -display :0
Restart=on-failure

[Install]
WantedBy=default.target
EOF

# Enable and start
systemctl --user enable x11vnc.service
systemctl --user start x11vnc.service
```

#### Connect from macOS via VNC

**Method 1: Finder (built-in Screen Sharing):**
1. Open Finder
2. Press `Cmd+K`
3. Enter: `vnc://192.168.1.70`
4. Enter the VNC password you set

**Method 2: Terminal:**
```bash
open vnc://192.168.1.70
```

---

### SSH with X11 Forwarding

For individual applications rather than full desktop:

```bash
# On macOS, install XQuartz first
brew install --cask xquartz

# SSH with X11 forwarding
ssh -X cogitari@192.168.1.70

# Then run GUI apps, e.g.:
firefox &
```

---

## Security Best Practices

### 1. Enable Cloudflare Access Authentication

Add authentication to prevent unauthorized access:
- Email OTP
- Google/GitHub OAuth
- SAML/SSO

### 2. SSH Tunnel for Local Network RDP/VNC

Instead of exposing RDP/VNC directly on local network, tunnel through SSH:

```bash
# From macOS - Create SSH tunnel for RDP
ssh -L 3389:localhost:3389 cogitari@192.168.1.70

# Then connect RDP to localhost:3389
```

### 3. Firewall Configuration (if needed)

```bash
# For RDP (port 3389) - local network only
sudo ufw allow from 192.168.1.0/24 to any port 3389

# For VNC (port 5900) - local network only
sudo ufw allow from 192.168.1.0/24 to any port 5900

# For SSH (port 22)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### 4. Use Strong Passwords

Ensure Ubuntu user password is strong since it's accessible remotely.

### 5. Enable 2FA on Cloudflare Account

Protect your Cloudflare account with two-factor authentication.

### 6. Enable Audit Logs

Monitor all access attempts in Cloudflare Zero Trust dashboard.

---

## Troubleshooting

### Check Services Status

```bash
# Check GNOME Remote Desktop
systemctl --user status gnome-remote-desktop.service

# Check x11vnc (if using VNC)
systemctl --user status x11vnc.service

# Check SSH
sudo systemctl status ssh

# Check Cloudflare tunnel
docker ps | grep cloudflared
docker logs cloudflared-tunnel
```

### Check Listening Ports

```bash
# Check all listening ports
ss -tlnp

# Check specific ports
ss -tlnp | grep -E "3389|5900|22"
```

### View Logs

```bash
# GNOME Remote Desktop logs
journalctl --user -u gnome-remote-desktop.service -f

# x11vnc logs
journalctl --user -u x11vnc.service -f

# SSH logs
sudo journalctl -u ssh -f

# Cloudflare tunnel logs
docker logs -f cloudflared-tunnel
```

### Test Local Connections

```bash
# Test RDP locally
curl -v telnet://localhost:3389

# Test SSH locally
ssh localhost

# Test VNC locally
vncviewer localhost:5900
```

### Cloudflare Tunnel Issues

```bash
# View container logs
docker logs cloudflared-tunnel

# Check if tunnel is connected
docker exec cloudflared-tunnel cloudflared tunnel info

# Restart tunnel
docker restart cloudflared-tunnel

# Check Cloudflare dashboard
# Go to Zero Trust → Access → Tunnels
# Verify tunnel status shows "Healthy"
```

---

## Maintenance

### Update Cloudflared

```bash
cd ~/cloudflare-tunnel
docker compose pull
docker compose up -d
```

### Restart Services

```bash
# Restart GNOME Remote Desktop
systemctl --user restart gnome-remote-desktop.service

# Restart Cloudflare tunnel
docker restart cloudflared-tunnel

# Restart SSH
sudo systemctl restart ssh
```

---

## Quick Reference Commands

### Cloudflare Tunnel

```bash
# Start tunnel
cd ~/cloudflare-tunnel && docker compose up -d

# Stop tunnel
docker stop cloudflared-tunnel

# View status
docker ps | grep cloudflared

# View logs
docker logs -f cloudflared-tunnel

# Restart tunnel
docker restart cloudflared-tunnel

# Update tunnel
cd ~/cloudflare-tunnel && docker compose pull && docker compose up -d
```

### Local Services

```bash
# Check RDP status
systemctl --user status gnome-remote-desktop.service

# Check SSH status
sudo systemctl status ssh

# Check listening ports
ss -tlnp | grep -E "3389|22"
```

---

## Cost

**Cloudflare Zero Trust:**
- Free tier: Up to 50 users
- Unlimited bandwidth
- No additional cost for tunnels

**Perfect for personal/small team use!**

---

## Summary

**For Local Network Access:**
- Use Microsoft Remote Desktop with IP `192.168.1.70`
- Simple and fast for same-network access

**For Remote Access from Anywhere:**
- Use Cloudflare Zero Trust tunnel with `vpn.clincentric.net`
- Secure, no port forwarding, auto-restart on power failure
- Free tier available

**Most Secure Setup:**
- Cloudflare tunnel with Access authentication
- Strong passwords
- 2FA on Cloudflare account
- Audit logging enabled
