# Optional local web view

`beyin.py web` is a small local server that shows the vault's tasks, recent receipts, the size of
the memory files and the doctor summary in the browser ([#371](https://github.com/avenoxai/avenoxbeyin/issues/371),
[#423](https://github.com/avenoxai/avenoxbeyin/pull/423)). It is entirely optional: install,
update and hooks never start it; no desktop shortcut or background service is installed. It opens
only when you run the command.

```sh
python3 beyin.py web ac              # starts the server, opens the browser
python3 beyin.py web ac --read-only  # read-only: task, sync and compaction are off
python3 beyin.py web ac --no-browser # only prints the address
python3 beyin.py web durum
python3 beyin.py web durdur
```

On Windows, `py -3 beyin.py web ac`. The default port is the first free port between 7373 and 7393;
if all are taken, a free port given by the operating system is used. You can choose one with
`--port`. The server shuts itself down if it is unused for 30 minutes; `Ctrl+C` or
`beyin.py web durdur` also shuts it down. If Beyin is updated or rolled back, the running server
notices this on the next request, rejects the request and shuts down; open it again with the new
version using `beyin.py web ac`.

## What it shows, what it writes

| Section | Source | Write |
| --- | --- | --- |
| Cockpit | `doctor` summary, open task counts, recent receipts | none |
| Tasks | task records under `tasks/` (`kind: task`) | new task `task-create`, status change `task-update` |
| Search | the index agents use for context | none |
| Receipts | receipts from the last 14 days | none |
| Memory | the `companion-compact --dry-run` plan | `companion-compact` (moves old entries to the archive unchanged, does not delete) |

The **Sync** button in the top corner does the same thing as `beyin.py sync`. The web view does not
write files to the vault on its own: every write is done by running the CLI command itself in the
same process; revision checks, locks, the secret filter and projection validation are the same as
in the CLI. On a concurrent change, a task update is rejected with `revision conflict`; refresh the
page and try again.

## Privacy

Reads go through the core index's own gate: `visibility: private` notes and tasks, `trust: untrusted`
records, safe-class folders (Kasa, Şifre, Müşteri, Finans...), folders excluded from the index
and notes whose source changed after indexing do not appear in search results, the task list or the
preview; even if the ID is known, they cannot be opened or updated. A receipt summary tied to a
hidden source is not shown. No arbitrary vault path can be requested directly; the preview opens
only with the ID of a record in the index.

## Security

- The server listens only on `127.0.0.1`. On every request the `Host` header must point to this
  listener (`127.0.0.1:<port>` or `localhost:<port>`); `Origin` and `Sec-Fetch-Site`, if present,
  must point to the same origin. Another site cannot get a response, even with DNS rebinding.
- A new token is generated at every launch and is valid until the server shuts down. The token is
  in the address printed to the terminal (in the `adres` field of the `--json` output) and in the
  `web/running.json` file in the state folder; this file's permission is 0600 on macOS and Linux,
  Windows does not apply this permission. The browser arrives once with this address; the server
  issues a separate `HttpOnly; SameSite=Strict` session cookie and immediately removes the token
  from the address bar. The address with the token may stay in the browser history (and on other
  devices if history is synced); it is useless once the server shuts down.
- Every write request coming from the page must carry the session cookie, an `Origin` from the same
  origin, an `application/json` body and that session's CSRF token. The only exception is
  `beyin.py web durdur`: it sends the token in the `Authorization` header, carries no `Origin`, and
  only shuts the server down. No CORS header is ever sent.
- Cookies are not separated by port: the browser sends the session cookie to other ports on
  `127.0.0.1` as well. A request coming from another page is caught by the `Origin` and
  `Sec-Fetch-Site` check; however, a local server serving from another port on the same computer (a
  development server or a container opened to `127.0.0.1`) could take this cookie and use the
  session. While such servers are running, use `--read-only` and shut it down with
  `beyin.py web durdur` when you are done.
- The page, styles and script come from `beyin_v3_web_ui.py`; there is no CDN, web font or remote
  image. The content security policy allows only these same-origin files; vault text is always
  written to the page as plain text.

There are no dependencies outside the Python standard library; it does not connect to the outside network.
