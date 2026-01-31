# Nginx Configuration

## Production Server
- **Host:** 193.160.208.85
- **Domain:** bankrot.denis-lab.ru

## Configuration Files

### `bankrot.denis-lab.ru.conf`
Main nginx configuration for the BankrotPro application.

**Routing:**
| Path | Backend | Port |
|------|---------|------|
| `/api/*` | FastAPI | 8000 |
| `/*` | Streamlit | 8501 |

## Deployment

The production config is deployed to:
```
/etc/nginx/sites-available/subdomains-http.conf
```

This file is part of a shared config that includes other subdomains (rss, ai).
Only the `bankrot.denis-lab.ru` server blocks from this repository should be
merged into the production file.

### Manual Deployment Steps

1. SSH to production server:
   ```bash
   ssh root@193.160.208.85
   ```

2. Backup existing config:
   ```bash
   cp /etc/nginx/sites-available/subdomains-http.conf \
      /etc/nginx/sites-available/subdomains-http.conf.bak
   ```

3. Edit the config to update the bankrot server blocks:
   ```bash
   nano /etc/nginx/sites-available/subdomains-http.conf
   ```

4. Test and reload:
   ```bash
   nginx -t && systemctl reload nginx
   ```

5. Verify routing:
   ```bash
   curl https://bankrot.denis-lab.ru/api/cases
   # Should return JSON, not Streamlit HTML
   ```

## SSL Certificate

The SSL certificate is a SAN cert covering multiple subdomains:
- ai.denis-lab.ru
- bankrot.denis-lab.ru
- rss.denis-lab.ru

Certificate path: `/etc/letsencrypt/live/ai.denis-lab.ru/`

Renewal is handled automatically by certbot.
