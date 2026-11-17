# Yakala security update (#299 / #302)

This update closes the gaps between address parsers. Percent-encoding in the host, non-ASCII
characters and alternative numeric IP notations are rejected. When content is processed, all DNS
results are checked before the Defuddle or YouTube helper starts; `localtest.me` and `nip.io`
addresses that resolve to a private IP are also rejected.

For file links, UNC paths, drive letters, parent directories and Windows device names are rejected
before `resolve()` runs. After a relative file path is resolved, the result is also checked to make
sure it stays inside the vault; Windows junctions cannot be used to read files outside it.

New `.ham/` records carry an opening and closing marker with a random ID unique to each file.
"Source ended" or "user instruction" headings written by the source itself do not close this
boundary. The content is still untrusted data; these markers alone are not a guarantee against
prompt injection. Old raw records are not changed; when needed, reprocess the card with
`yakala isle <id>`.

## Refresh an existing Yakala install

The Beyin update script refreshes itself; the `beyin-yakala` skill written by `yakala kur` is not
refreshed automatically. After you get this security update, run this once in the vault folder:

```powershell
py -3 beyin.py yakala kur
```

On macOS / Linux use `python3 beyin.py yakala kur`. If you installed only the template and the
skill, add `--kisayol-yok` to the same command. The saved hotkey and inbox choice are kept. Skill
copies that carry the install marker receive the new untrusted-content and boundary rules; a skill
the user wrote themselves, without the marker, is not changed. A test verifies in the package
install that an old marked skill is refreshed.

## Limits

Capture does not go out to the network; under the current behavior in this PR, local/intranet URLs
are also rejected at capture. A Web Clipper content item that was already fetched is processed
without a network connection or DNS query, but the card's URL goes through the same syntax/IP check.

Defuddle and yt-dlp now go out through a short-lived protection proxy on `127.0.0.1`: every
connection and redirect step passes through the same address gate, and the socket is opened to the
IP address that was checked. An answer that changes between the DNS check and the connection
(rebinding) and a redirect to a local address cannot let the helper reach the local network. A
proxy the user configured themselves (HTTP or SOCKS) stays behind the protection: the target first
passes through the same gate, and a local hop is never asked of that proxy. Requests that
Defuddle's YouTube, Reddit, X, Bilibili and C2 wiki readers open to those sites' fixed addresses do
not go through the protection proxy. Details: [YAKALA.md](YAKALA.md) > Source security.

The file card reads only captured files in its own `dosyalar/` folder; safe-type folders inside
the vault, `.obsidian/` and other notes cannot be copied into `.ham/` through a `## Files` link.
