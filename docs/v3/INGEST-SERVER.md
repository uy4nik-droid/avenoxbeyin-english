# Mobile and External Capture Server (`ingest-server`)

The second brain works very fast at your desk, with hotkeys, the CLI and hooks. But when you get up
from the desk and want to send an idea that comes to you on the road, on mobile (iOS / Android) or
on an external device, or an article or tweet you are reading, straight to the vault, `beyin.py ingest-server` comes into play.

This server is designed around the principles of **local-first and absolute privacy**:
- **One-way (append-only):** Data arriving from outside is written directly into the `000-Inbox/` (or the existing inbox) folder as timestamped Markdown files.
- **Zero data leakage:** The server does not serve any file inside the vault over HTTP. Only the health check (`GET /health`) and data intake (`POST /ingest` or `POST /yakala`) are exposed.
- **Zero extra dependencies:** It runs on the Python standard library (`http.server`); it needs no pip or extra packages.
- **Hardened security:** It works with constant-time token verification against timing attacks (`hmac.compare_digest`), a 1 MB upper limit, frontmatter injection protection and an `untrusted: true` trust label.

---

## 1. Starting the Server

### Local Test (This computer only)
```bash
python3 beyin.py ingest-server --port 8484
# Windows:
py -3 beyin.py ingest-server --port 8484
```

### Access over a Home Network or Tailscale (Token Protected)
To reach it from your phone or an external device, bind to the local network interface and be sure to set a Bearer token:
```bash
python3 beyin.py ingest-server --host 0.0.0.0 --port 8484 --token "COK_GIZLI_PAROLANIZ"
```
*(The token can also be given as an environment variable: `export BEYIN_INGEST_TOKEN="COK_GIZLI_PAROLANIZ"`)*

> [!TIP]
> **Secure network recommendation (Tailscale / WireGuard):** Instead of exposing the server port directly to the public internet (through modem port forwarding), we recommend using [Tailscale](https://tailscale.com/), a free mesh VPN. This way only your own devices (your phone and your computer) communicate, over an encrypted tunnel.

---

## 2. API Endpoints

### `GET /health`
Checks whether the server is up.
```json
{
  "status": "ok",
  "service": "beyin-ingest-server",
  "version": "1.0.0",
  "inbox": "ready"
}
```

### `POST /ingest` or `POST /yakala`
Drops a new note into the inbox.

**Request Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>` *(If a token has been set)*

Malformed JSON and invalid UTF-8 bodies sent with `application/json` are rejected with HTTP 400; no file is written to the inbox. To send plain text, use `Content-Type: text/plain`.

**Example JSON Body:**
```json
{
  "title": "SQLite Locks in Distributed Systems",
  "url": "https://example.com/sqlite-locking",
  "text": "Even in WAL mode, open handles on Windows lock delete operations.",
  "tags": ["sqlite", "architecture", "mobile"]
}
```

**Successful Response (HTTP 201 Created):**
```json
{
  "status": "accepted",
  "file": "000-Inbox/20261012-073000-sqlite-locks-in-distributed-systems.md",
  "bytes": 284,
  "message": "Capture added to the inbox."
}
```

When plain text (raw text) is sent, it is also parsed automatically, its first line is used as the title, and it is saved to the inbox.

---

## 3. Apple Shortcuts (iOS Shortcuts) Integration

To send any text you select, or a page you are browsing in Safari on your iPhone or iPad, to your second brain with one tap:

1. Open the **Shortcuts** app and create a **+ (New Shortcut)**.
2. Tap the settings icon in the bottom right corner and turn on **"Show in Share Sheet"**.
3. Add these actions:
   - **Text:** `{"text": "[Shortcut Input]", "title": "Mobile Share"}`
   - **Get Contents of URL:**
     - URL: `http://<computer-tailscale-ip>:8484/ingest`
     - Method: `POST`
     - Headers:
       - `Content-Type`: `application/json`
       - `Authorization`: `Bearer COK_GIZLI_PAROLANIZ`
     - Request Body: `JSON`
4. Save the shortcut. Now you can pick any link or text from the iOS share menu and send it straight to your vault.

---

## 4. Android Integration (HTTP Shortcuts / Termux)

- You can download the free **HTTP Shortcuts** app from Google Play and add a capture widget to your home screen with one tap.
- Or a simple alias through Termux:
```bash
yakala() {
  curl -X POST "http://100.x.y.z:8484/ingest" \
    -H "Authorization: Bearer COK_GIZLI_PAROLANIZ" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$*\"}"
}
```

---

## 5. Processing What Was Captured (Digestion)

Entries collected from mobile or external devices pile up in the `000-Inbox/` folder. When you are back at your desk:
1. Run `python3 beyin.py triage` to see how many sources are in the inbox and the oldest ones.
2. Tell your agent `"Process what's in the inbox"` or `"beyin-yakala"` to have the raw records turned into permanent `knowledge/` notes and tasks.

Security: listening on the local network requires a Bearer token. The token is accepted only in the Authorization header; it is never written into the URL query. A 5-second read timeout is applied per connection.

In tokenless loopback mode, browser write requests that carry an Origin and cross-site Fetch Metadata are rejected; local CLI captures work. Browser CORS access requires token-protected mode.
