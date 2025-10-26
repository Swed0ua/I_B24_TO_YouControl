# I_B24_TO_YouControl - Setup and Autostart Guide

## Overview
Integration service for SmartKasa connecting YouControl, Bitrix24 CRM, Google Sheets, Facebook Ads, and SendPulse. Fetches new contractors from YouControl API, filters them by КВЕД codes, and creates deals in Bitrix24 CRM. Also syncs data to marketing platforms.

## Files
- Main entry point: `main.py`
- Configuration: `config.py`, `bitrix24_conf.py`, `youControl_conf.py`
- Bitrix24 API: `services/bitrix24/api.py`
- YouControl API: `services/youcontrol/api.py`
- Google Sheets: `services/googleService/googleSheetsService.py`
- Facebook Ads: `services/facebookAdsService/api.py`
- SendPulse: `services/SendPulseClient/api.py`

---

## Linux/Unix Autostart Setup

### 1. Create systemd service file

```bash
sudo nano /etc/systemd/system/AC_I_B24_TO_YouControl.service
```

### 2. Service file content

**Note**: Update paths below with your actual project directory.

```ini
[Unit]
Description=YouControl to Bitrix24 Integration Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/path/to/I_B24_TO_YouControl
Environment=PATH=/path/to/I_B24_TO_YouControl/venv/bin
Environment=PYTHONPATH=/path/to/I_B24_TO_YouControl
ExecStart=/path/to/I_B24_TO_YouControl/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=AC_I_B24_TO_YouControl

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/path/to/I_B24_TO_YouControl

[Install]
WantedBy=multi-user.target
```

### 3. Initialize and enable service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable autostart
sudo systemctl enable AC_I_B24_TO_YouControl

# Start service
sudo systemctl start AC_I_B24_TO_YouControl

# Check status
sudo systemctl status AC_I_B24_TO_YouControl
```

---

## Service Management Commands

### Start service
```bash
sudo systemctl start AC_I_B24_TO_YouControl
```

### Stop service
```bash
sudo systemctl stop AC_I_B24_TO_YouControl
```

### Restart service
```bash
sudo systemctl restart AC_I_B24_TO_YouControl
```

### Check status
```bash
sudo systemctl status AC_I_B24_TO_YouControl
```

### View logs
```bash
# Follow logs in real-time
sudo journalctl -u AC_I_B24_TO_YouControl -f

# View last 50 log entries
sudo journalctl -u AC_I_B24_TO_YouControl -n 50

# View all logs
sudo journalctl -u AC_I_B24_TO_YouControl
```

---

## Verification

### Check if process is running
```bash
ps aux | grep "python main.py"
```

### Check process status
```bash
systemctl is-active AC_I_B24_TO_YouControl
```

### List all services
```bash
sudo systemctl list-units --type=service
```

---

## Manual Start (Development)

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ensure config files exist with proper configuration

# Run the service
python main.py
```

---

## Configuration

Configure files in `config/` directory:

### `config.py`
```python
GOOGLE_CRED_PATH = "config/g_service_acc.json"
GOOGLE_SHEETS_ID_customers = "your_sheet_id"
FB_ACCESS_TOKEN = "your_fb_token"
FB_CUSTOM_AUDIENCE_ID = "your_audience_id"
FB_AD_ACCOUNT_ID = "your_account_id"
SP_REST_API_ID = 'your_api_id'
SP_REST_API_SECRET = 'your_api_secret'
SP_TOKEN_STORAGE = 'file'
SP_ADDRESSBOOK_ID = "your_addressbook_id"
```

### `bitrix24_conf.py`
```python
B24_WEBHOOK_URL = 'your_b24_webhook'
FOP_STAGE_ID = "your_fop_stage"
TOV_STAGE_ID = "your_tov_stage"
C22_NEW_TRADERS_STAGE_ID = "your_new_traders_stage"
C22_CLASSY_TRADERS_STAGE_ID = "your_classy_traders_stage"
```

### `youControl_conf.py`
```python
YC_API_KEY = "your_yc_api_key"
```

### `constants.py`
Contains КВЕД codes for filtering contractors:
- `NEW_TRADERS_KVED` - codes for new traders
- `CLASSY_TRADERS_KVED` - codes for classy traders

---

## Required Files

- `config/g_service_acc.json` - Google Service Account credentials for Google Sheets API
- `config/bitrix24_conf.py` - Bitrix24 configuration
- `config/youControl_conf.py` - YouControl API configuration
- `config/config.py` - General configuration
- `constants.py` - КВЕД codes configuration

---

## How It Works

1. Service runs every 3 minutes (configurable in `main.py`)
2. Fetches new contractors from YouControl API (legal and natural persons)
3. Filters contractors by КВЕД codes into categories:
   - New Traders
   - Classy Traders
   - Regular TOV/FOP
4. Creates deals in Bitrix24 CRM with appropriate stage IDs
5. For natural persons (FOP):
   - Sends emails to Google Sheets
   - Adds customers to Facebook Ads custom audience
   - Syncs contacts to SendPulse
6. Logs all operations to `logs/app.log`
7. Continues in loop with 3 minutes interval

