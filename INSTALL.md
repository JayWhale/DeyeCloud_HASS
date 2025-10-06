# Deye Cloud Integration - Installation Guide

## Quick Start

### Step 1: Create Directory Structure

SSH into your Home Assistant instance or use the File Editor add-on, then create the integration folder:

```bash
mkdir -p /config/custom_components/deye_cloud
```

### Step 2: Copy Files

Copy all the integration files into the `deye_cloud` folder:

```
/config/custom_components/deye_cloud/
├── __init__.py
├── api.py
├── config_flow.py
├── const.py
├── manifest.json
├── sensor.py
├── switch.py
├── select.py
└── strings.json
```

**All files have been provided above in separate artifacts.**

### Step 3: Restart Home Assistant

1. Go to **Settings** → **System** → **Restart**
2. Click **Restart Home Assistant**
3. Wait for Home Assistant to restart

### Step 4: Get Your Deye Cloud API Credentials

1. Go to [https://developer.deyecloud.com/app](https://developer.deyecloud.com/app)
2. Log in with your Deye Cloud account
3. Create a new application (if you haven't already)
4. Copy your **App ID** and **App Secret**

### Step 5: Add the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Deye Cloud"
4. Enter your credentials:
   - **App ID**: Your application ID from the developer portal
   - **App Secret
