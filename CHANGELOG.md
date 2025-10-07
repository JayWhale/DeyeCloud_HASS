[1.1.0] - 2025-10-07
Added

- Region selection dropdown in configuration flow
 -- EU/EMEA/Asia-Pacific region support
 -- Americas region support

- Email and password authentication (required by Deye Cloud API)
- Automatic SHA256 password hashing
- Better error messages for authentication failures

Changed

- API base URL now determined by selected region
 -- EU: https://eu1-developer.deyecloud.com/v1.0
 -- US: https://us1-developer.deyecloud.com/v1.0

- Authentication method updated to match Deye Cloud Personal User API
