# XChange - File Exchange & URL Shortener

XChange is a lightweight self-hosted application for sharing text snippets, links, files, and images. It features a simple web interface, URL shortening, and administrative controls.

## Features

- **Multi-format Support**: Share raw text, links, files, and images.
- **Short Names**: Choose between short Base64 IDs or human-readable 3-word combinations.
- **Access Control**: Limit items by number of accesses (1, 10, 100, or unlimited).
- **Expiration**: Set time limits for shared items (1d, 7d, 30d, or unlimited).
- **Fast Forward**: Toggle between instant redirection for links or a 5-second delay page.
- **Admin Panel**: Manage and delete items via a password-protected interface.
- **Dark Mode**: Supports both light and dark themes.
- **Self-contained**: All static assets (Tailwind, Prism.js) are hosted locally.

## Installation (Docker Compose)

1. Clone the repository.
2. Configure environment variables in `docker-compose.yml`.
3. Run:
   ```bash
   docker-compose up -d
   ```

## Environment Variables

The application uses the `XCHANGE_` prefix for configuration via environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `XCHANGE_MONGO_URI` | `mongodb://localhost:27017/xchange` | MongoDB connection URI. |
| `XCHANGE_MONGO_USER` | `None` | MongoDB username (if not in URI). |
| `XCHANGE_MONGO_PASSWORD` | `None` | MongoDB password (if not in URI). |
| `XCHANGE_ADMIN_TOKEN` | `admin-secret` | Token used to access the Admin Panel. |
| `XCHANGE_BASE_URL` | `http://localhost:5000` | The public base URL of your app. |
| `XCHANGE_MAX_FILE_SIZE` | `10485760` (10MB) | Maximum file upload size in bytes. |
| `XCHANGE_ENABLE_ADMIN_UI` | `true` | Enable or disable the Admin UI. |
| `XCHANGE_ENABLE_UNLIMITED_USAGE` | `true` | Enable or disable 'Unlimited' option for access count. |
| `XCHANGE_ENABLE_UNLIMITED_AGE` | `true` | Enable or disable 'Unlimited' option for expiration time. |
| `XCHANGE_ENABLE_FAST_FORWARD`| `true` | Enable or disable the 'Instant Redirect' feature. |
| `XCHANGE_ALLOW_CREATE_FROM` | `None` | CSV of allowed hosts for creating items (e.g. `internal.com,localhost`). |

## Storage

- **Database**: MongoDB stores item metadata.
- **Files**: Uploaded files and images are stored directly in MongoDB using GridFS.

## API Documentation

The API documentation is available at `/docs` when the application is running.
