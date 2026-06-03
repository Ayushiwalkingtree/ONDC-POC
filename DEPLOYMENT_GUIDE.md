# Deployment Guide: Ubuntu 22.04

This guide deploys the current FastAPI Buyer NP on an Ubuntu 22.04 VM using Python venv, Uvicorn, systemd, Nginx, and Certbot SSL.

Replace these values before running:

- `api.example.com`
- `your-buyer-subscriber-id.ondc.org`
- `your-unique-key-id`
- `/etc/ondc-buyer-np/keys/signing-private.pem`
- `https://preprod.registry.example/lookup` or the real ONDC registry URL assigned during onboarding

## 1. Install OS Packages

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git curl nginx certbot python3-certbot-nginx
```

## 2. Create Application User and Directories

```bash
sudo useradd --system --create-home --shell /usr/sbin/nologin ondc
sudo mkdir -p /opt/ondc-buyer-np
sudo mkdir -p /etc/ondc-buyer-np/keys
sudo chown -R ondc:ondc /opt/ondc-buyer-np
sudo chown -R root:ondc /etc/ondc-buyer-np
sudo chmod 750 /etc/ondc-buyer-np
sudo chmod 750 /etc/ondc-buyer-np/keys
```

## 3. Upload or Clone Code

If deploying from Git:

```bash
sudo -u ondc git clone <YOUR_GIT_REPO_URL> /opt/ondc-buyer-np
cd /opt/ondc-buyer-np
```

If uploading a release archive, extract it so `app/main.py` exists under `/opt/ondc-buyer-np`.

```bash
cd /opt/ondc-buyer-np
test -f app/main.py
```

## 4. Create Python Virtual Environment

```bash
cd /opt/ondc-buyer-np
sudo -u ondc python3 -m venv .venv
sudo -u ondc .venv/bin/python -m pip install --upgrade pip wheel
sudo -u ondc .venv/bin/pip install -r requirements.txt
```

Optional Gunicorn install if you want Gunicorn-managed ASGI workers:

```bash
cd /opt/ondc-buyer-np
sudo -u ondc .venv/bin/pip install "gunicorn>=22.0.0"
```

## 5. Configure Environment Variables

```bash
sudo tee /etc/ondc-buyer-np/ondc-buyer-np.env >/dev/null <<'EOF'
APP_NAME=ONDC MF Buyer NP
APP_ENV=production
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=INFO

SUBSCRIBER_ID=your-buyer-subscriber-id.ondc.org
UNIQUE_KEY_ID=your-unique-key-id
SIGNING_PRIVATE_KEY=/etc/ondc-buyer-np/keys/signing-private.pem
ONDC_REGISTRY_URL=https://preprod.registry.example/lookup
ONDC_REGISTRY_TIMEOUT_SECONDS=10
REQUIRE_ONDC_AUTH=true

BAP_ID=your-buyer-subscriber-id.ondc.org
BAP_URI=https://api.example.com/ondc
BAP_CALLBACK_URI=https://api.example.com/ondc
BPP_ID=
BPP_URI=

ONDC_DOMAIN=ONDC:FIS14
ONDC_VERSION=2.0.0
EOF
sudo chown root:ondc /etc/ondc-buyer-np/ondc-buyer-np.env
sudo chmod 640 /etc/ondc-buyer-np/ondc-buyer-np.env
```

## 6. Install Signing Key

```bash
sudo cp /tmp/signing-private.pem /etc/ondc-buyer-np/keys/signing-private.pem
sudo chown root:ondc /etc/ondc-buyer-np/keys/signing-private.pem
sudo chmod 640 /etc/ondc-buyer-np/keys/signing-private.pem
```

## 7. Create systemd Service Using Uvicorn

```bash
sudo tee /etc/systemd/system/ondc-buyer-np.service >/dev/null <<'EOF'
[Unit]
Description=ONDC Mutual Fund Buyer NP FastAPI service
After=network.target

[Service]
User=ondc
Group=ondc
WorkingDirectory=/opt/ondc-buyer-np
EnvironmentFile=/etc/ondc-buyer-np/ondc-buyer-np.env
ExecStart=/opt/ondc-buyer-np/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips=127.0.0.1
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable ondc-buyer-np
sudo systemctl start ondc-buyer-np
sudo systemctl status ondc-buyer-np --no-pager
```

Alternative systemd `ExecStart` using Gunicorn:

```bash
sudo sed -i 's#ExecStart=.*#ExecStart=/opt/ondc-buyer-np/.venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 2 --bind 127.0.0.1:8000 --forwarded-allow-ips=127.0.0.1#' /etc/systemd/system/ondc-buyer-np.service
sudo systemctl daemon-reload
sudo systemctl restart ondc-buyer-np
sudo systemctl status ondc-buyer-np --no-pager
```

## 8. Configure Nginx Reverse Proxy

```bash
sudo tee /etc/nginx/sites-available/ondc-buyer-np >/dev/null <<'EOF'
server {
    listen 80;
    server_name api.example.com;

    client_max_body_size 10m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 10s;
        proxy_send_timeout 60s;
    }
}
EOF
sudo ln -sf /etc/nginx/sites-available/ondc-buyer-np /etc/nginx/sites-enabled/ondc-buyer-np
sudo nginx -t
sudo systemctl reload nginx
```

## 9. Configure SSL

```bash
sudo certbot --nginx -d api.example.com --non-interactive --agree-tos -m admin@example.com --redirect
sudo systemctl reload nginx
```

## 10. Verify Service

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS https://api.example.com/health
curl -fsS https://api.example.com/docs
```

## 11. Useful Operations Commands

```bash
sudo journalctl -u ondc-buyer-np -f
sudo systemctl restart ondc-buyer-np
sudo systemctl reload nginx
sudo nginx -t
```

## 12. Deployment Readiness Notes

The current code can be hosted on a Linux VM, but it is not sufficient for ONDC UAT/production until these are implemented:

- Ed25519 Authorization header generation.
- Inbound Authorization header verification.
- Registry lookup and verification with real PreProd/Production URLs.
- Durable transaction storage.
- Outbound BPP dispatch.
- Action-specific FIS14 message validation.

