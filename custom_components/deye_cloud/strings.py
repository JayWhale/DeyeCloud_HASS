{
  "config": {
    "step": {
      "user": {
        "title": "Set up Deye Cloud",
        "description": "Enter your Deye Cloud API credentials. You can obtain these from the [Deye Cloud Developer Portal](https://developer.deyecloud.com/app).",
        "data": {
          "app_id": "App ID",
          "app_secret": "App Secret",
          "scan_interval": "Update interval (seconds)"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect to Deye Cloud API",
      "invalid_auth": "Invalid App ID or App Secret",
      "unknown": "Unexpected error occurred"
    },
    "abort": {
      "already_configured": "This Deye Cloud account is already configured"
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Deye Cloud Options",
        "data": {
          "scan_interval": "Update interval (seconds)"
        }
      }
    }
  }
}
