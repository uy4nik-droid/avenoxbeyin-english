# Yakala (capture): throw it into your brain with one key

A video, a tweet, an article, an email, a PDF, or a sentence that crosses your mind: capture it with
one key wherever you see it, and your agent will read it later and connect the lessons to your second brain.
It is optional; if you don't install it, nothing changes.

## Installation (once)

In the vault folder:

```sh
python3 beyin.py yakala kur
```

On Windows, `py -3 beyin.py yakala kur`. Or tell your agent "install the yakala tool".

The installation does the following:

| | Mac | Windows |
|---|---|---|
| Shortcut in every app | `Control+Option+B` | `Ctrl+Alt+B` |
| Sending a file | Select the file in Finder, press the shortcut | Right-click > Send to > Beyne At |
| Browser | Obsidian Web Clipper template | Obsidian Web Clipper template |
| Agent | `beyin-yakala` skill | `beyin-yakala` skill |

The shortcut needs no extra packages; it runs on Python itself. On Mac a login service
(LaunchAgent), and on Windows a small listener that starts at login, listens for the key.
If you only want the template and the skill: `python3 beyin.py yakala kur --kisayol-yok`.

**Existing installation:** After you get the [#299 security update](YAKALA-GUVENLIK-299.md),
run `python3 beyin.py yakala kur` once more in the vault folder
(on Windows, `py -3 beyin.py yakala kur`). This way the `beyin-yakala` skill written earlier
receives the new untrusted-content and random-boundary rules. If you only use the template/skill,
add `--kisayol-yok`; the user's own unmarked skill is preserved.

### Linux

On Linux there is no background listening service; the shortcut is written to the desktop's own shortcut settings.
`kur` writes the file `~/.local/share/applications/beyne-at.desktop` (or under `XDG_DATA_HOME` if it
is an absolute path). The command becomes `python3 <state>/yakala/beyin_v3_yakala.py pencere --vault <vault>`.
This copy of the script sits in the state folder and, when opening the window, switches to the current script in the vault;
you do not need to run `kur` again after an update.

`Ctrl+Alt+B` (or `--tus`) is registered according to the desktop:

| Desktop | Shortcut | Where it was tried |
|---|---|---|
| KDE Plasma 6 (Wayland) | `kur` sets it up | On a real desktop: shortcut, link and plain text |
| GNOME | `kur` sets it up | Not tried on a real desktop; unit tests only |
| KDE Plasma 5 | `kur` tries (`kwriteconfig5`) | Not tried |
| Others (Hyprland, Sway, XFCE...) | Not set up; `kur` gives the command to bind | On Hyprland, the `kur` output and the `zenity` window were tried |

- **KDE Plasma:** It is written into `kglobalshortcutsrc` with `kwriteconfig6` (or `kwriteconfig5`
  if absent) and activated without logging out using `gdbus`. `kur` then asks kglobalaccel who owns the key:
  `kisayol_calisiyor` in the output becomes `true` only if the key is bound to this shortcut; if the key is in another
  application, or the question goes unanswered, it is `false`. Limit: if the shortcut was previously
  set up with another command (the vault was moved, Python changed), KDE may keep running the old command
  in the running session; the new one takes effect after you log out and back in. This problem does not exist on first install.
- **GNOME:** A custom shortcut (`custom-keybindings`) is added with `gsettings`; your existing shortcuts
  are preserved. Here `kisayol_calisiyor` only says that the setting was written; it does not say that the key
  does not conflict with another shortcut. If the key does not work, look at the `Beyne at`
  entry under the custom shortcuts in Settings > Keyboard and open an issue.
- **Other desktops:** The `.desktop` file is written, the shortcut is not set up. The `ipucu` in the `kur` output
  gives the whole command to bind; add it to the desktop's shortcut settings. If the registration cannot be
  verified on KDE or GNOME, the same command is also given as `ipucu`.

On Linux the key can be a letter, digit, space, or F1-F12 together with Ctrl, Alt or Super.
The shortcut serves a single vault: if you run `kur` in another vault, the shortcut moves to it and
`onceki_vault` in the output tells you the old one. `kaldir` deletes only the `.desktop` file and the shortcut
that this vault set up. The desktop is recognized from the `XDG_CURRENT_DESKTOP` variable; run `kur` and `kaldir`
from a terminal inside the desktop session. In a session where this variable is absent, such as SSH,
the shortcut is not set up, and on removal the desktop's shortcut setting stays in place.

In a real X11 session the window first tries the browser reader below. If the browser context
cannot be obtained, the clipboard flow is used. On Wayland there is no automatic page/cursor reading; the window reads
what to save from the clipboard. On Wayland the `wl-clipboard` package (`wl-paste`) is required.
If it is not installed, the clipboard link/text may not reach the window even though the shortcut works; `yakala kur`,
`yakala durum` and the empty capture window point this out. After installing the package with your
distribution's package manager, check with `yakala durum` that the warning has disappeared; you do not need to reinstall Yakala.
On X11 the full window reads the text itself; `xclip` or `xsel` is needed for copied files and for the `kdialog`/`zenity` path.
If there is a single link on the clipboard, the link is captured; if there are files copied from a file
manager (a `file://` list), the files are captured; if there is other text, the text is captured. On Wayland, if only a PNG image was copied, a small preview of it
appears in the full window; it is not attached at the start, but it can be selected with `Tab` or by clicking the card and saved as a PNG file card.
If there is text or a link, they take priority. If the image cannot be read or `wl-paste` is missing, the existing
text flow does not change. X11 clipboard images are not supported in this version. At most 1 MB of clipboard text and
at most 64 MB of an image are read; if the text is truncated, the card says so.
Capturing copied files has not been tried on a real desktop, only in unit tests.

The full window needs `tkinter`. On Arch-based distributions Python's `tk` package is separate
(`sudo pacman -S tk`); on Debian and Ubuntu, `sudo apt install python3-tk`. If `tkinter` is missing, instead of the window
only "why" is asked with `kdialog`, or with `zenity` if that is also missing; if you cancel, no card is written.
If none of the three exist, nothing is saved and `kur` reports this as a warning.
Some packaged Python/Tk versions see only the `fixed` font; Turkish characters and arrows may appear
in the window as Unicode escapes. The Linux shortcut's state copy checks its own Python's
Tk fonts; if they are unsuitable and `/usr/bin/python3` has usable Tk fonts, it opens
the window with that. If system Tk is missing, install it with your distribution's package manager; if there is no suitable other Python either,
the current interpreter and the `kdialog`/`zenity` fallbacks are kept. This check does not send the card's content
anywhere else. **On an existing Yakala install, after an engine update**, to refresh the shortcut's
previously copied code, run `python3 beyin.py yakala kur` in the vault root.
Running only `yakala durum` or editing the `.desktop` file by hand does not refresh the copy; KDE may also keep the active
shortcut's old `Exec` line in memory. This reinstall does not move or delete old cards;
the saved shortcut and the selected folder are used.

To verify: `python3 beyin.py yakala durum` (`Shortcut listener: running`), on KDE
`gdbus call --session -d org.kde.kglobalaccel -o /component/beyne_at_desktop -m org.kde.kglobalaccel.Component.isActive`
(`(true,)` is expected), then press the shortcut.

### Change the shortcut

```sh
python3 beyin.py yakala kisayol 'cmd+"'
```

Describe the key the way you type it: `cmd`, `ctrl`, `alt` (or `option`), `shift`, and the key last.
Examples: `ctrl+alt+b` (default), `cmd+shift+space`, `alt+f5`, `⌘⇧K`. On Mac the character is found from the active keyboard
layout; on a Turkish Q layout `"` is the key to the left of 1. On Windows the shortcut
accepts only a letter, digit or F key together with Ctrl/Alt/Shift. `kisayol` without arguments shows the current key.
If another application already uses the key you chose, the command warns you; try a different key.

On Mac the listener runs in the background and does not appear in the Dock; if it quits, the system restarts it.
The listener runs from a copy that `kur` wrote: to refresh it after an update as well, run
`python3 beyin.py yakala kur` again (your key is preserved). `python3 beyin.py yakala durum`
tells you whether it is running.

### Browser page and cursor link

Added on 19.10.2026; code base `d9aa301`. The new Windows Gecko/Yandex, macOS AX and
Linux X11 paths in this section have **not been verified on real devices**. Unit tests check the provider, ABI,
object ownership, timeout and ambiguity rules; they do not prove that an installed browser offers this
contract. The old Opera Air measurement is stated below with its own version.

Cells show the `page / cursor` path. `UIA` is the existing Windows address bar/Hyperlink path;
`MSAA+UIA` is the renderer document value and the renderer Hyperlink; `Gecko` is the new MSAA Document/Link path;
`AX` is the macOS AXWebArea/AXLink path; `AS` is a fixed AppleScript fallback for the page only;
`SPI` is the AT-SPI Document/Hyperlink path bound to the real X11 window.
`Waiting` means the reader is not active, `No product` means there is no current official distribution for that platform.
If the schema is hidden in UIA cells, verification with the renderer document URL in the same child/bucket is required.

| Family / product | Windows | macOS | Linux X11 | Linux Wayland |
|---|---|---|---|---|
| Chrome / Chromium | UIA / UIA | AX or AS / AX | SPI / SPI | Not read |
| Edge | UIA / UIA | AX or AS / AX | SPI / SPI | Not read |
| Safari / STP | No product | AX or AS / AX | No product | No product |
| Firefox | Gecko / Gecko | AX / AX | SPI / SPI | Not read |
| Opera | MSAA+UIA | AX or AS / AX | SPI / SPI | Not read |
| Opera GX | MSAA+UIA if `opera.exe` | AX or AS / AX | Product exists; GX identity waiting | Not read |
| Opera Air | MSAA+UIA if `opera.exe` | AX or AS / AX | No product | No product |
| Brave | UIA / UIA | AX or AS / AX | SPI / SPI | Not read |
| Vivaldi | UIA / UIA | AX or AS / AX | SPI / SPI | Not read |
| Arc | Waiting | AX / AX | No product | No product |
| Zen | Gecko / Gecko | AX / AX | SPI / SPI | Not read |
| Yandex | MSAA+UIA, product path required | AX / AX | SPI / SPI | Not read |
| Samsung Browser | Product exists; reader waiting | No official distribution found | No official distribution found | No official distribution found |

The main target is 10 families: Chrome, Edge, Safari, Firefox, Opera, Brave, Vivaldi, Arc, Zen, Yandex.
Opera variants are measured separately within the same family; Samsung is an additional tracking candidate. In StatCounter's
September 2026 worldwide desktop table, the top six are Chrome 65.09%, Edge 14.64%, Safari 8.06%,
Firefox 6.11%, Opera 2.38%, Brave 1.12%. In the Turkey table Yandex appears at 1.21%.
This measurement is page-view share; it is not install or unique-user share. No exact top-10 ranking
is claimed for Vivaldi/Arc/Zen. [World](https://gs.statcounter.com/browser-market-share/desktop/worldwide/),
[Turkey](https://gs.statcounter.com/browser-market-share/desktop/turkey/),
[method](https://gs.statcounter.com/faq); accessed 19.10.2026.

**macOS.** The reader records the NSWorkspace application PID/bundle identity and the window server's visible
window identity/bounds. If Accessibility permission is present, in a terminable helper
process the AXURL value of the single visible top AXWebArea under the focused window is read.
The cursor link is found with the system's point test; the AXLink bounds must contain the cursor, and the parent object chain
must reach the same document and window. Across the two document/link reads, the URL and object identities, and at the end the
application/window/bounds and sheet state, must stay the same. The link of a moving cursor is discarded.
If AXLoadingProgress is present it must be finite and exactly 1; its availability must also not change between the two reads.
This extra check was added because, in the Mozilla source examined, the AXLoaded mask can miss loading;
the real Firefox/macOS version behavior must be measured separately.

Privacy & Security > Accessibility permission is needed for the link. Automation is a separate permission; if there is no AX
access, a fixed `/usr/bin/osascript` for the page only may be tried in Safari and in allow-listed Chromium derivatives.
The script checks the front application, window, active tab and two full URLs.
If AX saw an ambiguity such as two documents or a missing document URL, this decision is not overridden by AppleScript.
Permissions are not opened automatically. Safari's local SDEF and each derivative's dictionary must be confirmed
on the device; on a feature/build/permission error there is no address. Arc/Firefox/Zen/Yandex
are not forced onto the general Chromium AppleScript dictionary. With Accessibility off, the behavior of a native sheet and
split view tied to the same window must be measured separately in the AppleScript acceptance test.

**Linux X11.** `XDG_SESSION_TYPE=x11`, a local `DISPLAY=:N[.S]` and an empty `WAYLAND_DISPLAY` are
required. There are no new Python packages; the system must have `libX11.so.6`, `libatspi.so.0`, GLib/GObject and
a reachable AT-SPI session bus. A missing library/permission/tree gives an empty result;
no installation or setting change is made on its own. The EWMH active window, the real X input focus,
the `/proc` PID/exe/start time and the AT-SPI application PID are matched. `_NET_WM_PID` is a client
property; trust in a normal local X11 desktop is assumed, and no new security boundary is declared against malicious
processes of the same user.

The bounds of the single active AT-SPI frame must match the X11 client bounds exactly. In the Chromium
family the Document `URI` is read, in Gecko the `DocURL`. Two visible outer documents, a second pane with an invalid URL,
a busy/stale tree or a changed identity are rejected. An iframe is not chosen in place of the page.
For the cursor link, the point test starts from the frame; a real LINK that reaches the selected document, a single valid
Hyperlink anchor and a full URL are required. DPI/decoration offsets are not guessed. If the match cannot be established because of Snap, Flatpak,
AppImage, a PID namespace, a different exe name or scaling, there is no result.
Opera GX came out on Linux on 19.03.2026; this code can use the shared path only if the exe is actually `opera`.
The GX package and tree await separate measurement.

**Wayland.** On KDE/GNOME/Hyprland/Sway, the presence of AT-SPI is not by itself proof of global foreground and
cursor ownership. The XWayland active window can remain stale when a native Wayland application is in front.
Until a compositor-specific adapter with a verified permission model is added, this
version gives no automatic page or cursor URL; the existing clipboard/file/text capture continues.
The presence of `DISPLAY` or changing session variables is not used to bypass this check.
On Linux the first window/cursor sample is taken when the helper process starts; it does not represent the recorded
point of the physical shortcut moment.

**Choice and duration.** In the macOS/Linux full Tk window, if there is a verified page and a cursor
link different from it, `Link under the pointer` is the default and `Active page` the alternative.
On macOS Option+I/Option+S, on Linux Alt+I/Alt+S or clicking the row is used.
In this case the clipboard link is a disabled option. Because the macOS/Linux page+cursor path does not verify the freshness of
the clipboard text, a text card is not offered; you can type into the note box by hand or paste explicitly.
The existing clipboard image reader also does not offer an image while a page is present. On Linux a local file list on the clipboard takes priority over the browser context:
a file preview is shown and only the files are saved; the page and cursor URL are not added to the card.
The page-only flow keeps its existing behavior. In the non-Tk `kdialog`/`zenity`/macOS simple-question fallback
there is no cursor and page chooser; the verified page is used.

The new Windows document reader has a nominal budget of 1 second; the macOS browser read total is 2.5 seconds (the AX share at most
1 second); the Linux browser child is 2 seconds. Native browser provider
calls run in a terminable process. Start-up/cleanup, the macOS window server and Linux
clipboard/popup overheads may be added to these figures. These are not measured latencies or a hard real-time
guarantee. Capture is not physically atomic; the possibility of a very fast change that goes unnoticed between samples
cannot be eliminated entirely even with device tests.

The new paths do not use History/session/cookie/profile files, a debug port, an extension, a browser restart
flag, synthetic keys or JS. If a full HTTP(S) address does not come from the allowed source, no schema is made up. The existing
localhost/private IP security rules are kept.

**Device acceptance tool.** In the repo root, use the countdown to switch to a known public test page:

```sh
python3 tests/manual_browser_capture.py --delay 5 --repeat 20 --interval 1
python3 tests/manual_browser_capture.py --delay 5 --expected-page https://example.com/
python3 tests/manual_browser_capture.py --delay 5 --expect-empty
```

On Windows use `py -3` instead of `python3`. For a known real link add `--expected-hover FULL_URL`.
The tool writes no cards; it hides URLs by default and gives p50/p95 and the exact-equality result as JSON.
`--show-urls` should be used only with shareable test addresses. If no expected address was given,
`checked_samples=0`; exit code 0 does not mean the correct URL was measured. If the expectation does not hold, the exit code is 1.
In each browser try a normal page/link, a draft address bar, an iframe, two panes with the same URL, tab/
window switching, a centered window, a second monitor/DPI, a permission denial and a cold provider.
Do not accept a wrong address even in a single sample; record the empty-result rate separately from successful capture.

Primary interface sources (accessed 19.10.2026):

- [Mozilla accessibility architecture](https://firefox-source-docs.mozilla.org/accessible/Architecture.html):
  On Windows MSAA, IA2 and the UIA provider exist together; it is not said that Firefox has no UIA.
- [Chromium accessibility architecture](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/accessibility/overview.md)
  and [Chromium SDEF](https://chromium.googlesource.com/chromium/src.git/+/lkgr/chrome/browser/ui/cocoa/applescript/scripting.sdef).
- [Apple Accessibility permission](https://support.apple.com/guide/mac-help/allow-accessibility-apps-to-access-your-mac-mh43185/mac)
  and [Automation permission](https://support.apple.com/en-au/guide/mac-help/mchl07817563/mac).
- [AT-SPI Document](https://gnome.pages.gitlab.gnome.org/at-spi2-core/libatspi/method.Document.get_document_attribute_value.html),
  [EWMH](https://specifications.freedesktop.org/wm/latest-single/),
  [Wayland](https://wayland.freedesktop.org/docs/book/Protocol.html),
  [XWayland](https://wayland.freedesktop.org/docs/book/Xwayland.html).
- [Chromium URI](https://github.com/chromium/chromium/blob/main/ui/accessibility/platform/ax_platform_node_auralinux.cc)
  and [Mozilla DocURL](https://github.com/mozilla/gecko-dev/blob/master/accessible/atk/nsMaiInterfaceDocument.cpp):
  engine-specific Document attribute names.
- [Opera GX Linux announcement](https://press.opera.com/2026/03/19/opera-gx-gaming-browser-lands-on-linux/)
  (19.03.2026), [Opera downloads](https://www.opera.com/download),
  [Arc platform limits](https://resources.arc.net/hc/en-us/articles/19400148671383-Unsupported-Devices),
  [Samsung Windows announcement](https://news.samsung.com/global/samsung-takes-its-browser-beyond-mobile-extending-agentic-ai-across-devices)
  (26.03.2026).

### Browser: Obsidian Web Clipper

1. Install the [Obsidian Web Clipper](https://obsidian.md/clipper) extension (Chrome, Firefox, Safari, Edge, Arc, Brave).
2. In the extension's settings, with **Templates > Import**, choose the `beyne-at-web-clipper.json` file that the
   installation wrote to the card folder (default `📥 000-Inbox/Yakala/`; `kur` tells you the full path).
3. On a page, click the extension, choose the "Beyne at" template, optionally write a line in the **Why** section, and add it.

The Web Clipper reads the page from inside the browser; pages that require login (Gmail, paid articles) are captured this way too.
This existing optional installation is not a requirement of the local shortcut readers above.

### Windows: shortcut listener

On Windows, the shortcut reads the browser's (Chrome/Edge/Brave/Vivaldi) address bar. If the address bar
has focus (a draft that was typed but Enter was not pressed) or the value changes between two reads, it is not counted as a URL.
If Chromium hides the schema, verification is done within the same time limit with the single visible renderer's open MSAA document
URL; the visible text and a second, unfocused UIA read must agree.
No `https://` guess is made. Only a trailing `/` difference on a root address is accepted; `www`, IDN
and percent-encoding display differences or a cold renderer may lead to an empty result.
If at the moment of the shortcut the mouse is over a link
(e.g. a video card on the YouTube home page), that link becomes the default source; the open
page is chosen with **Alt+S**, the link under the cursor with **Alt+I**. If the window or tab
changes during the read (the title changes), both links are discarded. Even when there is a link, the source window's image is offered
(first Windows.Graphics.Capture, then PrintWindow if that fails). The image comes unselected; it is added with **Alt+W** or by clicking
the row, because `isle` has the agent read the image as it is. The History/session database is not read;
the existing network security limit is kept for localhost/private IP.

**Posts (X, Instagram):** A tweet's text or a video in the feed is not a link. If the open page
is X (`x.com`, `twitter.com`) or Instagram and the cursor is not over a link, the innermost
ARIA `article` element under it (a single post) is taken and the first post link inside it
(`x.com/<user>/status/<id>`, `instagram.com/p|reel/<code>/`) becomes the cursor link. On other sites
this path does not work: the body of a news page may also be a single `article`, and the tweet that the text refers to
is not the post the cursor is over; there the source stays the open page. If the page address
cannot be read, this path is also closed. A second, different post link in the same post
is the quoted post; it can be selected with **Alt+A**, and it is not selected by default. X's photo/video/analytics
subpages are reduced to the post address; the Instagram audio page (`/reels/audio/<id>/`) is not
counted as a post. The link is read from the page itself; the post address is not
generated from an image or a username.

**Opera (including Opera Air):** In a window whose process name is `opera`, the address bar is not read; the page's separate
Chromium child window is read. The page URL is taken from the real value of the MSAA Document object, the cursor
link from the UI Automation links of the same child window. A draft in the address bar is not
read; the loaded address of the open page is used. No extension, restart or
accessibility start-up flag is needed. A single visible renderer, window/process ownership, and the page URL before and after
the read are verified. If there are multiple visible renderers, an invisible document,
a changing page or a timeout, no URL is given. If the link changes between two reads, only the cursor
link is discarded. The page and cursor read is done in a single helper process within a 1.8-second budget.
Chromium turns web accessibility off after a while of non-use; then the first read
comes back empty, accessibility is turned on by a UI Automation request to the renderer, and the document is waited for at most 0.8 seconds.
If accessibility is already on, the read is as fast as before.
The basic provider path was measured on Opera Air 136.0.6008.70 in a separate profile without flags;
a user acceptance test on logged-in YouTube/Instagram feeds must be done separately.

**Firefox / Zen / Yandex:** For Firefox and Zen, `MozillaWindowClass`, foreground/PID and
the real exe name are verified. In the MSAA tree, the exact value of the single visible top Document is read;
it does not descend into an iframe. The real Link under the point is verified with its physical bounds and the
IUnknown identity that reaches the same Document. The URL, name and object identity of the two link reads must also be the same.
The Yandex `browser.exe` name is accepted only if the real path
ends with `\\YandexBrowser\\Application\\browser.exe`; the existing Opera renderer/MSAA path is used. If a custom portable/beta path
does not match this rule, no support is given. The Windows reader for Arc/Samsung is not yet active.

The Opera Air cold accessibility measurement and the single UIA wake-up request are a separate
[#399](https://github.com/avenoxai/avenoxbeyin/pull/399) effort; this addition does not
include that PR. Because Yandex uses the shared renderer path, the cold/warm provider result and
before/after #399 must be measured separately. The old Opera Air result is not evidence for the new browsers.

If there is a link read from the browser (under the cursor or the open page), it is the default. Clipboard text
is visible only if its freshness is verified; next to a link it comes disabled. Stale clipboard text is not shown.
If there is no link, the clipboard revision observed since the listener started and not used in a successful save
takes priority. On first use/restart the age of the existing clipboard is unknown: the text is
hidden; the link and image remain as disabled options. The Snipping Tool file time alone does not
provide automatic freshness.
Cancelling and saving only the page do not consume the clipboard. If the clipboard change happened after the capture key,
the new content is not selected as a source automatically. Text/image is
copied from the same clipboard session; a delayed or inconsistent read is safely skipped.

Selection paths: **Alt+I** link under the cursor, **Alt+S** active page, **Alt+A** quoted
post, **Alt+P** clipboard link, **Alt+M** text, **Alt+G** clipboard image, **Alt+W** window
image. The shortcuts also work in the note box; uppercase and the Turkish I/İ are supported.
Several links can be selected together. The main `url` priority: cursor link, active page,
quoted post, clipboard link. The other selected addresses are kept in the card's `Additional links` section
and in the optional `ek_urller` list; `isle` processes the main URL. The same address is not shown as a second card.
To save only one link, uncheck the others.
An existing URL card to which clipboard text, a file or an email address was added also becomes `private`.
Even if an email address is selected in `ek_urller` instead of as the main source, the whole card stays private.
If one of the additional links is a local or private network address (`127.0.0.1`, `192.168.x.x`, `intranet`,
`nas.local`), the capture is not cancelled: the address is written as a record only to a separate `ek_urller_yerel` list and to the
`## Local network links` section, and the card becomes `private`. `isle` does not open these
addresses. The main `url` can still only be a public address; an additional link that contains an option, `file://`, user
info or an encoded IP notation is rejected. A corrupt `ek_urller` value in a hand-edited or synced
card does not block a new capture of that page.
Even if the same popup's record ID is replayed, a second
commit is not made.

The popup uses a warm neutral background, a terracotta accent and small shortcut badges. Selected sources
are set apart with a colored frame and a check mark. The window fits the work area of the source monitor;
a long source list is scrolled with the mouse wheel or PgUp/PgDn. The note box and the save
hints stay in place. The window image is not added to the card without the user choosing it; the link and image
can be saved together.

A second capture of the same page does not open a new card; it is added to the existing card. The page identity is computed with the same rule on every
system (a synced vault can be read by Mac and Windows together):
the same YouTube video (`youtu.be`, `watch?v=`, `shorts/`, `live/`, `embed/`, `music.youtube.com`)
and the same X/Twitter post are gathered in a single card; the domain name must match exactly (`notyoutube.com` is not
counted as YouTube). For other pages, the scheme, the `www.`/`m.` prefix, a trailing `/` and the fragment (`#baslik`)
make no difference; a non-default port (`:8443`) and routing markers (`#/sayfa`, `#!sayfa`)
count as a separate page.

**Single active popup:** pressing the shortcut again does not open a new window; it sends a focus request to the open popup,
preserving the current text and source selection. The listener and the warm window speak a READY with
instance/schema/version/HWND verification → foreground permission → ACTIVATE. The second call is FOCUS.
The old protocol is not silently accepted; after this update the listener copy must be refreshed
with `py -3 beyin.py yakala kur`. IPC pipes do not block the hotkey thread.
Listener shutdown sends STOP first; windows and readers that do not respond are terminated through an owned
Job Object. State belonging to another vault is not deleted.

On Windows a temporary handshake timeout or an unexpected popup closure does not abandon the shortcut.
The old process is first terminated and waited for, then a new window is warmed up after 0.5 seconds.
A capture whose result is unknown is not repeated automatically; the next press is a new capture.
On a third temporary failure within 120 seconds the listener shuts down and a refresh with `yakala kur` is requested.
A protocol mismatch or the inability to terminate the old process is a direct reason for shutdown.
The failure stage and the recovery decision are written to `yakala/dinleyici.log`.

The popup opens on the source monitor. On Windows, Tk uses a managed window; to preserve the custom
palette/canvas look the native title/frame style is removed. Plain **Esc** cancels immediately at local
focus. While sources are being read and for as long as the popup is open, wherever focus is,
a low-level keyboard hook (`WH_KEYBOARD_LL`) looks at Esc and the modifier keys
(Shift, Ctrl, Alt, Win): if the popup is in front, Tk handles Esc; if the source window is in front (focus
was denied or the page was clicked), plain Esc is consumed and the popup closes; if another window is in front,
the popup closes and Esc is also passed to that window. The hook never consumes Esc with a modifier
and does not close the popup; system shortcuts such as Ctrl+Shift+Esc work. The popup's own Tk binding
also cancels only on plain Esc: Caps/Num/Scroll Lock do not count as modifiers, and the Win key, which Tk does not
report in the event, is read in the GUI thread synchronously with `GetKeyState`. For modifiers that are already
held down at the moment the hook is installed, the hook reads the `GetAsyncKeyState` value only once and outside the callback;
after that it tracks the state with the press/release events it sees itself (left and right key separate), and for Alt it also looks at the `LLKHF_ALTDOWN`
flag in the event. The asynchronous key state is not queried inside the callback. The hook is removed when the popup closes (save, Esc, Close, Alt+F4, error);
after that no application's Esc is held. A re-press of the hotkey re-installs the hook with the new source window and does not change
the old capture's content. `AttachThreadInput` is not used.
The visible **Close** and Alt+F4 are also cancellation. For the Windows secure desktop/UIPI/hook denial,
there is no global Esc guarantee in every case. If the card's disk commit has begun, Esc does not retroactively cancel
the saved data; during slow disk I/O the interface response may be delayed.

For the window image, even when there is a link, the order **WGC → PrintWindow → no image** is followed;
each backend is in a separate, terminable process. This preparation may add time to the popup opening.
If the capture fails, no image option is created. The preview shows the method
name. There is no BitBlt from the screen DC. If the source window changes, the result is discarded.
WGC is the Windows 10 1903+ API path; if support/permission/driver fails, PrintWindow is tried.
No success or HDR color accuracy is claimed for all protected/GPU/exclusive-fullscreen applications. No failure
makes the old clipboard an automatic source.

The external wait for UIA/clipboard is 1 second (the Opera reader 1.8 seconds), for WGC 2.5 seconds, for PrintWindow 1.2 seconds;
there may be extra overhead for process start/termination. PNG/DIB accepts at most **16,777,216 pixels**,
the image payload 64 MiB, the text UTF-8 payload 4 MiB, the IPC metadata 64 KiB.
A PNG size declared as large is not given to Tk. Card/raw temporary write errors are cleaned up;
no absolute promise of deletion is made for a hard kill/power loss or the file system refusing to delete.
On a normal/forced popup closure the listener also cleans up its own TEMP tree.

`kur` writes a `Beyne At Dinleyici` shortcut to the Startup folder (`shell:startup`) and starts the listener.
There is a single listener per session; running `kur` in another vault hands the key to that vault.
`py -3 beyin.py yakala durum` shows its status, and `yakala/dinleyici.log` in the state shows errors.
If the vault was moved, it is not rewritten to the old path; installation is done again at the new location. The shortcut
is created in a temporary file and replaced after verification; a stop timeout is not counted as success.

ABI sources, limitations and real-desktop acceptance commands:
[Windows capture ABI and test guide](WINDOWS-CAPTURE-ABI.md).

## Usage

1. **Capture.** Press the shortcut. The window shows what will be saved: the page in the browser
   (the platform matrix above), the file selected in Finder, or the text on the clipboard.
   If you like, write a one-line "why" and press Enter. Esc cancels.

   On Windows, if there is an image on the clipboard, the window shows it with a small preview. An image copied to the clipboard after the
   last successful save (e.g. `Win+Shift+S`) comes ready to be added: Enter saves it as a PNG into the `dosyalar/` folder
   next to the cards and opens the same file card as Send to > Beyne At. Freshness is measured not by the clock but by the clipboard sequence number; cancelling (Esc) does not consume the clipboard.
   An image whose freshness cannot be verified is disabled; it can be toggled with **Alt+G** or by clicking the row.
   Clipboard text/link and the window image follow the Windows selection rules above.
2. **Process.** Tell your agent "process the captures". The number of waiting sources is also shown at the start of a session.

Each capture becomes a card in the card folder (default `📥 000-Inbox/Yakala/`). If you capture the same video or
page a second time, no new card is opened; the new note is added to the same card.

### The card folder

If only one of the inbox folders already has a `Yakala/` in it, cards are written there; if there is no such single
folder, the starting folder `📥 000-Inbox` is used, and if that does not exist either, the single folder at the top of the vault whose name is an inbox
(`000-Inbox`, `00_INBOX`, `Gelen Kutusu`). If it cannot be decided, no guess is made
and the starting path is opened. Folders starting with a dot, symbolic links, archive and safe-type names
are not counted as an inbox.

If you want somewhere else, say so at install time:

```sh
python3 beyin.py yakala kur --klasor "Notlar/Yakala"
```

- The folder must be inside the vault. A path that goes outside is rejected and nothing is written.
- The Web Clipper template, the skill, the session notice and `durum` show the same folder. If you
  changed the folder, re-import the template into the Web Clipper.
- Cards in the old folder are not moved. `kur` tells you how many cards were left behind; if you
  want them processed, you move them to the new folder.
- The choice is stored in this machine's state folder. If you use the same vault on another machine,
  run the same command there too.
- If the saved folder is deleted or renamed, the rule above applies again; `durum` tells you which folder is used.

## Optional: save and hand to the agent

**It is off by default.** When you turn it on, **Enter** still only saves the card. **Ctrl+Enter** or
the **Save and hand to the agent** row in the window first saves the card, then starts a separate
Claude Code or Codex session for this card. The agent works inside the vault; it saves the result to
memory with source links. You can close the window and continue working in another agent session.

This path exists in the full Tk window. The Linux `kdialog`/`zenity` fallback windows only
capture; you can send the saved card with the `ajan-gonder` command below.

### Open, use, close

In the vault folder, for Windows:

```sh
py -3 beyin.py yakala kur --ajan claude
py -3 beyin.py yakala ajan
```

For automatic selection use `kur --ajan otomatik` or `ajan otomatik`. First, the Claude Code or Codex
session that did the installation is chosen; if there is no session marker, the single installed CLI is chosen. If both are installed,
the terminal asks `1) claude / 2) codex`; in JSON output or non-interactive use you have to choose `claude`
or `codex` explicitly. If neither is found, an error is given. A concrete client is written to the setting;
the `secim` field of the output shows the `kurulum-ajani`, `tek-kurulu` or `kullanici` path.
The agent that does the installation opens the background agent only if you explicitly ask; if you did not specify a client, it uses
`--ajan otomatik`. The skill tells the agent not to grant, on its own, the permissions for `ajan-gonder`,
`ajan-toplu --gonder`, `--ses-isle` and `--tani-servise-gonder` in your place.
If `--ajan` is not given, the default off behavior does not change.

To choose Codex, use `--ajan codex`. If Yakala is already installed, `py -3 beyin.py yakala ajan claude`
or `py -3 beyin.py yakala ajan codex` is enough. On Mac/Linux write `python3` instead of `py -3`.
On the first move to this Windows version, run the `kur` command again: the listener copy in the state must also
receive the new process setting that separates the agent job from the popup. The message format between the popup and the listener
is the same as 3.12.0; before `kur` is refreshed, the shortcut and normal capture also work,
and an update or rollback does not close the shortcut. Only the agent job cannot start: the card is saved, moves to the `hata`
state, and its `ajan_notu` field tells you to refresh the listener with `yakala kur` and send the card again.

**Appearance: hidden or window.** On Windows, for Claude and Codex you can choose how the agent will run:

- `gizli` (default): the job runs in a headless session in the background, and a notification arrives when it finishes.
- `pencere`: Ctrl+Enter opens the Claude Code or Codex window of the client selected on screen; you watch
  what the agent is doing live, and if needed you steer it by typing in the same window. The tool limit is the same as in the hidden run
  (the general shell is closed; Codex's file-read profile and network setting are below). The job is
  delivered when the agent calls `complete`; the receipt and the card update are again done by the worker after verification,
  the window stays open and the conversation can continue. If you close the window without leaving a result, the job becomes `onay-bekliyor`.
  The turn and budget limits apply only in the hidden run; the time limit applies
  to both. The window is not isolation: in the same console the user's own client
  controls (in Claude, e.g. a command with `!`) are open, and after the job finishes the window may stay
  open at the same time as the next job.

**Network: restricted or open.** In the same context the agent reads both the untrusted source and your private notes;
an instruction hidden in a source may try to make it put the text of a note it read into a URL or a search query.

- `kisitli` (default): general web search is off. `fetch_source` and `download` open only
  the captured main address, explicitly selected additional addresses, and links the worker itself parsed from an allowed page; new addresses the model
  produces are rejected. Side channels such as link selection and timing remain; this is not complete
  data-leak protection.
- `acik`: Claude's web search (hosted search in Codex) and every public address can be used.
  It is needed for jobs that require research (e.g. finding the music in a video); private notes and the web
  share the same exit channel. In this mode the agent is also given a separate instruction: search and download are only
  for public information; no text from notes, personal information or private or user-uploaded content is put
  into a search query, an address or a file name, and a job that
  requires it becomes `onay-bekliyor` for the user's permission. This is a model instruction, not a technical
  barrier.

The `ek_urller` on a multi-source card is, when it is sent to the queue, verified under the existing card and queue locks
and pinned to the job's `extra_urls` list. Links in the card body,
URLs the model produces and later card changes do not give this job new authority;
a repeat of the same delivery keeps the first list. If the field is absent in old jobs, only the main source is used.
The extra list can hold at most 63 addresses, 8192 characters per address and 64 KiB as JSON.
The first job record, written together with the request, settings and sources, is limited to 96 KiB;
room is left for later work/result fields within the 128 KiB reader limit. If the limit is exceeded,
an error is raised without moving the card to the agent state; the card itself is preserved.

In both network modes `fetch_source` and `download` share a total of **8 calls** per job. Failed
allowed attempts are also deducted from this budget. The counter is saved to disk before going out to an external request;
reconnecting to the bridge or reloading the same job does not reset the budget. An address that is not allowed
is rejected without going to the network. If the counter is corrupt or cannot be written, no network call is made. The allowed address
list per job is at most 64 addresses. This limit is for MCP calls; it is not a packet counter for HTTP redirects,
the client's hosted web search and the model service's normal traffic.
The call order, address choice and timing side channels continue. When the budget runs out, it is still possible to read existing
notes, write a result and report a concrete blocker with `complete`.

```sh
py -3 beyin.py yakala ajan claude --ag acik
```

**Monthly agent log.** The worker adds a short entry to the `Ajan/Gunluk-YYYY-MM.md` note
in the Yakala folder where the job's card is located; it does not write to `Last-Session.md`.
Yakala's existing folder choice is used; if the setting changes after the job is queued, the entry
stays in the same folder as that job's card. If the file does not exist it is created with `visibility: internal` frontmatter and the
`# Yakala agent log - YYYY-MM` heading. The newest entry is under the heading.
The entry carries the date-time, the client, the first eight characters of the real session ID, the status and the card/result/receipt
links. The links are relative Markdown paths from the log; special characters are preserved with URL
encoding. With normal paths it is about 300 characters including the marker; with long file
paths the links are not truncated, so it may be longer.

The log can be found in search; it carries no summary, user request or source text. Like `private` cards,
the results of `internal` cards may also contain information from private requests, attachments or result notes.
Since there is no reliable public-summary distinction, no job's result summary is copied into this log.
The full summary stays in the `visibility: private` result note. The visibility rules of the link targets
do not change; a link in the log does not open a private note to search or hook context.

Each job is added only once, with the `<!-- yakala-ajan:<job-UUID> -->` marker. The file is not touched until the log time
is written to the job record; a retry at a month change uses the same monthly note.
The write is done under the `memory.lock` lock. If the file changes between read and
write, the entry is not added; the result and the receipt are preserved. A new file is published atomically without overwriting an existing
target; an existing file is replaced atomically. All the written bytes
are verified by reading them back. In the very short interval between this check and the atomic
replace, the write of an editor that does not take part in the lock may be lost;
since there is no portable compare-and-swap path, this risk is knowingly accepted.

```sh
py -3 beyin.py yakala kur --ajan claude --ajan-gorunum pencere
py -3 beyin.py yakala ajan codex --gorunum pencere
py -3 beyin.py yakala ajan claude --gorunum gizli
```

If `kur --ajan claude`, `kur --ajan codex` or `kur --ajan otomatik` is run in a terminal without `--ajan-gorunum`,
it asks which one you want. If you are having an agent do the installation, the agent must ask you this choice.

1. Press the shortcut, choose the source and write the task to be done in the **Why** field. When the feature is on,
   `Ctrl+Enter · Save and hand to the agent (claude)` or `(codex)` appears at the bottom. When it is off, this row does not
   appear; Ctrl+Enter does not start an agent job and does not accidentally turn into a plain Enter save.
   Instead the window says `Agent is off · Enter to save`.
2. Press **Ctrl+Enter**. An empty request is not sent; the window says `Write the request for the agent`.
   After a successful save and adding to the queue, `✓  Saved · Queued for the agent` appears and the window closes.
   If the queue is full or the independent process cannot be opened, the card is preserved, and the window states the save and the agent error
   separately. A new request for the same URL is not mixed with old requests added to the card earlier.
3. When the job actually starts, the **Beyin agent started** notification arrives. Waiting in the queue does not mean the model
   has started working. The queue of this vault on a machine runs **one job** at a time.
4. When the verified result, the receipt and the monthly agent log entry are complete, **Beyin agent finished** appears.
   If there is a blocker, **Beyin agent awaiting approval** appears; on a run error **Beyin agent could not complete**
   appears. The card's `ajan_notu` field shows the reason, the monthly log shows the status and links.

To turn off new jobs:

```sh
py -3 beyin.py yakala ajan kapali
```

A running job is stopped when it re-reads the setting; files that were already created are not rolled back. Waiting jobs
are not run automatically when they are woken up again. While it is off, capture and plain Enter keep working.
Changing the client does not change the saved client or limits of jobs queued earlier.
For the newly selected client the old `extra_args` and `executable` are reset; the
`--ayar` values given in the same command are applied after that. This way Claude's `--model haiku`, `--effort` or
custom binary path is not carried over to Codex. Changing the other settings of the same client keeps these options.
When re-enabling from the `kapali` state, since it is not known which client the old options belonged to, it returns to the
model/binary default; if you want, specify them again explicitly.

You can also give an explicit request for a single saved card:

```sh
py -3 beyin.py yakala ajan-gonder KART_ID --istek "Review this source, note three key findings with their sources"
py -3 beyin.py yakala ajan-devam
py -3 beyin.py yakala ajan-serbest KART_ID
```

`ajan-devam` wakes up the persistent queue; it does not give permission to re-run an interrupted job.
`ajan-serbest` turns a `hata` or `onay-bekliyor` card that you reviewed into `bekliyor` and leaves it to the normal
`isle`/`bitti` flow. You cannot release a running card. This command does not start a new agent job
and does not give broad tool permission. If you want an automatic retry, first review the partial results,
then give a new, explicit request with `ajan-gonder`.

### Card, session and memory

| The card's `durum` value | Meaning |
|---|---|
| `bekliyor` | Normal capture; no agent job was given, or the user left it to normal processing |
| `ajanda` | A job for this card is queued or running; `ajan_asama` gives the detail |
| `islendi` | The result and memory closure were verified |
| `hata` | The run could not be completed; the card and existing results are preserved |
| `onay-bekliyor` | Permission, setup, an uncertain interruption or memory verification requires human review |

The normal waiting list does not take `ajanda` cards into processing again. `isle` and `bitti` do not close this card
from another session; the session notice separately reports reserved and approval-waiting cards.
Capturing the same card again preserves the new note; a job in progress is not started a second time.

`ajan_isi` on the card is the job UUID; `ajan_oturum` is the client's session UUID. For Claude the UUID
is generated before the start and given with `--session-id`; for success, the same real session must be
seen in the CLI output. In a Claude job that has not started, a reserved UUID being written does not
prove the session was created. The Codex UUID is taken in hidden mode from the `thread_id` field of the first `thread.started` event;
in window mode only the first-line metadata of new sessions under `CODEX_HOME/sessions` (default `~/.codex/sessions`) is read.
A single session whose start time and vault path match must be
found. If the identity is not found or there is more than one candidate, the result is preserved and the job becomes `onay-bekliyor`;
the memory closure is not done. Codex sessions opened concurrently in the same vault may make this matching
ambiguous. The job UUID is not used in place of the Codex session.
[doc: CLI and headless run sources below]

To open the same session from a terminal in the vault folder:

```sh
claude --resume SESSION_UUID
codex resume SESSION_UUID
```

Result notes are written as new files under the card folder's `Ajan/<job-UUID>/`. The card, result,
source and, if any, the path of the downloaded file are recorded together. `ajan_sonuc` and `ajan_receipt`
show the closure records. Links to these are added to the monthly agent log. In a later session
it is possible to find a request like "that music you downloaded" through these source records; for that,
the normal vault memory rules and hooks must be installed.

**Receipt integration, assumption:** This module does not include the `beyin.py receipt` implementation. The adapter looks in the
local `receipt --help` output for `--file` and `--harness` support; the session ID goes with the `session` field in the file; it expects a machine-readable response with `--json`.
The integration contract is that the file input accepts the `event_id`, `summary`, `refs`, `session`
fields, and that the response gives the same `event_id`, a success status and the real `source`
path inside the vault. The code accepts only `status: succeeded`;
any other value, an unknown status or an empty status is not counted as a successful closure.
The source file is read back and the event ID
is checked. This JSON schema and the local success status must match the upstream runtime in an acceptance test;
the help output alone does not prove the data schema. The contract, receipt or
agent log cannot be verified, the downloaded file and notes are preserved, and the card is not counted as completed.

### Advanced JSON setting

The settings are stored on the machine in `<state>/yakala/ajan/config.json`. They are tied to the vault and to the user's
CLI session; they do not become active on another machine on their own. In the settings file give the fields you want
to change, then choose the client explicitly:

```json
{
  "timeout_seconds": 600,
  "max_queue": 8,
  "max_budget_usd": 1.0,
  "extra_args": ["--model", "sonnet"]
}
```

```sh
py -3 beyin.py yakala ajan claude --ayar yakala-ajan.json
```

| Field | Default and limit |
|---|---|
| `client` | `kapali`; `claude`, `codex` or `kapali` is chosen through the CLI |
| `timeout_seconds` | 900 seconds; between 30 and 3600. This is the CLI run time; preparation and memory closure may take extra time |
| `max_queue` | 32; between 1 and 32 active jobs including the running one. The concurrent-run limit is fixed at 1 |
| `max_budget_usd` | 1.0; between 0.05 and 20. It is Claude's estimated spending limit; it does not apply to Codex and is not a hard billing ceiling |
| `extra_args` | `[]`; only `--model VALUE` and, for Claude, `--effort VALUE`, each at most once |
| `executable` | `null`; found from PATH. If customized, a single absolute executable or a recognized npm shim path |
| `downloads_dir` | At first install the operating system's Downloads folder, `~/Downloads` if not found; an absolute local folder |
| `last_session_path` | Read for compatibility with old settings and ignored; not written to new settings |
| `schema`, `vault` | The module's version and vault ownership fields; do not change them to move it to another vault |

The JSON can be at most 16 KiB; unknown keys, free command templates and permission flags
are rejected. On Windows write the `\` character as `\\` inside JSON. The CLI takes the user note from UTF-8 stdin;
the request is at most 16,000 characters. User text is not embedded into a shell command. An npm `.cmd`/`.bat`
file is not run; only known Claude/Codex package entry points are opened directly with Node.
For an undefined shim there is no fallback to the command interpreter.

No Companion folder or Last-Session search is made. Even if the old `last_session_path` target no longer
exists, the setting and the job record can be read. New `job.json` records have a vault-relative `journal` path instead of `last_session`,
and a `journal_time` for repeat protection. Records that carry the old `last_session`
field can be loaded; old Last-Session cards are not moved or deleted.

### What can the agent do?

This session is opened in the normal vault folder, with the existing client settings. In Claude `--bare`,
`--safe-mode` and `--no-session-persistence` are not used; known environment settings that turn off memory loading
or session persistence are not silently bypassed. Codex's project/hook trust must have been granted beforehand in a normal
session. Opening a new login, UAC or approval window is not part of this flow.

For the task's local read, write and permitted music operations, the same Python module
offers eight capabilities over stdin/stdout. The extra permissions of the music tools are
explained in the "Optional: recognizing music in a video" section below:

| Tool | Authority |
|---|---|
| `read_note` | Reads an existing Markdown/text note within limits and this card's linked text |
| `search_notes` | Does a limited search over visible notes; gives at most 30 results |
| `fetch_source` | Reads limited text from a public HTTP(S) source; on a `kisitli` network only the captured address and the links of an allowed page; 8 calls in total with `download` |
| `download` | Prepares a direct media/text/PDF file at up to 50 MiB; 8 calls in total with `fetch_source`; the extra 10-file ceiling in the manifest is kept; the address rule is the same as `fetch_source` |
| `music_info` | Reads only the music metadata on this card's video page; a source claim is not an audio match |
| `music_identify` | A short local sample with the host CLI's per-job audio permission; at most one AudD request with a separate upload permission and key |
| `write_note` | Creates at most 30 new result notes only in this job's folder; does not change an existing note |
| `complete` | Reports a result to be verified; the trusted worker updates the card, the receipt and the monthly agent log |

For a download, the file type and hash are checked; executable file types are not allowed. A successful
file is written to Downloads with a new name that includes the job ID; an existing user file is not
overwritten. A `.part` file is created first; the completed copy is verified with SHA-256 and published under its final name on the same file
system. A hard link is tried first; if it is not supported, on Linux
`renameat2(RENAME_NOREPLACE)`, on macOS `renamex_np(RENAME_EXCL)`, and on Windows `os.rename`, which
rejects an existing target, is used. Result notes and completion files also go through the same helper.
An existing target is not overwritten, and no half copy is created under the final name. If the file system rejects both
the hard link and the special rename, if the disk fills up or the target collides, the download's
`.part` file is preserved and the card awaits review. There is no support guarantee for every network file system. With more than one file, earlier
successes are not lost: each publish intent and each completed file is recorded separately, and a partial result is also
included in the receipt and agent log closure.
The bridge rejects hidden/sensitive paths, symbolic links and Windows junctions.
The agent reads the card given to it whatever its name is; access to other sensitive notes does not change.
Notes with `remote_allowed: false`, a sensitive `sensitivity`, or blocked `kaynak_guveni` metadata
are not read. `visibility: private` notes do not enter the hook context and are also not opened to this job;
only the job's own card, raw text, attachments and its own result notes are read.
The name `Dosyalar` alone is not a reason for blocking. The attachment stores of the current capture folder and of old capture folders recognized by a
card or a Yakala `.gitignore` trace containing `*`
are protected; unrelated `knowledge/Dosyalar` notes go through the same policy as other notes. An old attachment store whose cards
have been moved is not opened to search if this trace remains. The `read_note` response for the card/raw text/permitted attachments
carries `source_trust: untrusted`; ordinary memory notes stay `vault-data`.
This privacy check reads canonical JSON frontmatter and plain scalar YAML fields;
a repeated key, corrupt/unclosed metadata or an unsupported format is not silently skipped.

The Claude profile runs with `dontAsk`, `--permission-prompts none`, limited built-in tools and only this
MCP configuration; `--permission-prompts` requires at least 2.1.259. For Codex the
oldest supported stable version is **0.155.1**. The Codex profile uses `-a never`, `--strict-config`
and `-c agents.enabled=false`. On Linux/macOS every run is given a randomly named
permission profile. Since the single file system entry is `":root"="deny"`, no read/write root is given
to local tools. This profile is selected with `-c default_permissions=...`;
on POSIX `-s read-only` is not added: the old selector disables the named profile.
**On Windows the `-s read-only` compatibility path is used; the content-guessing channel remains open.**
Since the Windows `elevated` sandbox asks for root read permission, the root-deny start-up stopped;
no named profile is added to the Windows command. The user's sandbox type/config is not changed.
In hidden runs `--ignore-rules` is also used. The pre-check first reads the plain table of
`codex features list` without flags; `--json` is not given to this command. Then it verifies the enabled states against the job's disable
flags. A missing, removed, duplicated or unparseable
required feature; an old/pre-release version; a failed or oversized inventory output stops the job.

For every job these 14 features are turned off: `shell_tool`, `unified_exec`, `view_image`, `apps`,
`multi_agent`, `multi_agent_v2`, `plugins`, `remote_plugin`, `computer_use`, `browser_use`,
`browser_use_external`, `in_app_browser`, `image_generation`, `goals`. Both sub-agent gates
and `agents.enabled=false` are required together; V2 selection from model metadata is also blocked.
The measured 0.155.1 shows `unified_exec` as `true` even when `--disable unified_exec` is given. This case is accepted only if
`shell_tool=false` is verified: in the official source all shell tools
are behind this main gate. There is no such exception for the other required enabled features.

Existing MCP servers are turned off by name only in that job and the result is re-checked; the user's
config file is not changed. Plugin/app gates are also closed per job. If the inventory or the enabled
state cannot be verified, the job stops; not every machine that has an enabled MCP is rejected wholesale.
Codex's code mode that calls MCP tools is preserved. It is not opened as a general shell or local file system tool.
Web search is open only when `ag: acik` (Claude `WebSearch`, Codex `web_search="live"`). `bypassPermissions` and full file system write permission are not given. [doc: CLI, config and permission sources]

The previous branch's maintainer measurement (18.10.2026; Claude Code 2.1.302, Codex 0.160.0, macOS): on a `kisitli` network the Claude session's tool list
is only six `mcp__yakala__*` tools; on an `acik` network `WebSearch` is added to this; there are no Bash and file tools.
On a `kisitli` network, when the model added note text to a URL, the bridge rejected the address. This record
is not a measurement of the current branch on Windows. [#384 maintainer comment](https://github.com/avenoxai/avenoxbeyin/pull/384#issuecomment-6243678257)

Measurement of the previous `read-only` profile (19.10.2026 Turkey time; 18.10.2026 23:12-23:14 UTC): official Linux Codex 0.155.1,
an empty/temporary `CODEX_HOME`, harmless test files and a local fake Responses API were used.
No request was sent to a real account/model service. Forced `view_image`, `exec_command` and
`spawn_agent` calls were rejected as unsupported tools. Four `apply_patch` writes, modifying an existing
file and creating a new file inside/outside the vault, were rejected;
the test files did not change. A separate pre-check with an enabled `local_mcp` turned it off for the job,
and the hash of the config file stayed the same. This experiment does not measure a real model finishing a job with the six MCP tools
or the Windows sandbox behavior.

**Codex `apply_patch`, new fix for #384 finding 2 (19.10.2026 UTC):** `apply_patch` may remain
on the tool surface; `apply_patch_freeform` was removed in 0.155.1 and in the current stable 0.163.0
and is not a security switch. The old `read-only` profile also gave different errors in 0.163.0 to a correct
and a wrong line guess. On Linux/macOS this branch uses the **named file system permission profile**
from the official documentation. `":root"="deny"` also applies to the file read of the patch
verification. A new 128-bit random profile name is generated for each command so that the user's narrower permissions under the same name
are not merged and reopened; the config
file is not edited. No additional read permission is given to `:minimal`, the vault, the temp directory or the Python root.

With the official **Linux 0.155.1, 0.160.0 and 0.163.0** binaries, in each of two tests in each version,
28 forced `apply_patch` calls were tested: relative/absolute, inside/outside-vault paths; correct
and wrong context for Update/Move; Delete; Add to an existing/new file. The correct/wrong pairs were
rejected with the same read error, no content was exposed and existing file hashes did not change. In each version, additionally, the real
Yakala MCP bridge read the allowed note and `AGENTS.md`, rejected the private note, wrote a result note
and accepted the `complete` delivery. A synthetic `SessionStart` hook given normal hash trust
added memory context to the first request. A local fake Responses API was used; no real account
or model service was used. This is evidence of the `complete` delivery; it is not a measurement that the receipt,
agent log and notification were completed on a live desktop. The tests cover the cases where the user's existing
config has `workspace-write` and a separately selected config profile has `read-only`;
the effectiveness of the new permission choice under these legacy settings was also measured.

Permission profiles are in **beta** status in the official documentation. `--strict-config` prevents unknown top-level
settings from being silently ignored; it is not security proof that detects all future behavior
changes. The newest pre-release seen, **0.164.0-alpha.3**, was examined only in
source; the current stable version gate does not accept it. On Linux this guessing channel
was closed; the macOS native result has not been measured yet. **Windows finding 2 is partially open:**
on 19.10.2026 the user reported, on real Windows 11 / Codex 0.155.1, that the `dc2a1bc2` root-deny
profile stopped the start-up at `AGENTS.md`, and the old `69ac79c` read-only path completed in both
views. This branch brings the read-only selector back to Windows;
the write and other tool restrictions are kept, and the `apply_patch` guess verification is not counted as closed.
The native Windows start-up and the receipt/agent log chain of the corrected branch have not yet been
measured. The POSIX root-deny native tests are skipped on Windows with justification; this skip
is not a Windows success. Source, option evaluation and repeat commands:
[Codex file read limit review](CODEX-APPLY-PATCH.md).

The music tools (`music_info`, `music_identify`) were added after these measurements; the eight-tool
inventory and the music flow have not yet been measured live.

**Trust boundary:** The normal vault hooks, the client and `beyin.py receipt` are trusted local code;
their own behavior is not put into a sandbox by this tool bridge. The model service the agent uses can
see the request in the CLI's normal data flow and the notes that are read. While public GET and web
search exist, there is no guarantee that universally prevents data transfer through a URL/query or the remote server attaching a side effect to a GET.
A file name/metadata filter cannot find every secret written into an ordinary note. The operating system restrictions and the tool list are not presented as
a security system that controls all of the model's intent. [inference]

The user's **Why** field is the task to be done; carrying it as data in the JSON envelope does not
ignore this request. This field gives no authority to change system rules. Instructions in the source URL, page, clipboard and
quote are untrusted content. If the request requires a free shell, deletion, payment, credentials,
sending messages or a system change, the agent must leave an `onay-bekliyor` result;
a "bypass the permission" statement inside the text does not create new authority.

**Limit of the Instagram example:** Music metadata can be read from the page. For audio
recognition, however, a separate local audio/upload permission and an optional AudD key
are needed; details are in the music section below. If these permissions are absent, the agent waits for approval
with a concrete blocker. There is no Instagram session/cookie, DRM circumvention or free command
execution. Direct file download is done with the existing download tool only if the source allows it.
There is no guarantee that every reel's music will be found
or downloaded; wrong music or an HTML file is not counted as
success. The normal `isle` tools are not opened to the agent profile automatically.

### Client, platform and permission matrix

This table shows the limit the code applies on every run. `extra_args` can add only `--model` and,
for Claude, `--effort`; the flags below cannot be removed through settings.

| Client and appearance | Platform | Tool and permission limit (code) | Local file system | Web |
|---|---|---|---|---|
| Claude, `gizli` | Windows, macOS, Linux | `-p`, `--permission-mode dontAsk`, `--permission-prompts none`, `--allowedTools mcp__yakala__*`, `--strict-mcp-config`, `--no-chrome`, `--max-turns 24`, `--max-budget-usd` | `--tools ""`: no built-in file or shell tool; read/write only through the Yakala bridge | `kisitli`: none; `acik`: only `WebSearch` |
| Claude, `pencere` | Windows only | The same tool set, `dontAsk` and strict MCP; no `--permission-prompts`, turn or budget limit; the console belongs to the user (`!` commands are open) | Same | Same |
| Codex, `gizli` | Linux, macOS | `exec`, `-a never`, `--strict-config`, `agents.enabled=false`, 14 features off, user MCP servers off for the job, `--ignore-rules` | A randomly named `":root"="deny"` permission profile | `kisitli`: `web_search="disabled"`; `acik`: `live` |
| Codex, `gizli` | Windows | Same | `-s read-only`: no write, the `apply_patch` content-guessing channel is not closed | Same |
| Codex, `pencere` | Windows only | The same feature gates, interactive TUI; no `--ignore-rules` | `-s read-only` | Same |

In all combinations the agent is off by default. Turning it on (`kur --ajan`, `ajan claude|codex`)
and every job (`Ctrl+Enter`, `ajan-gonder`, `ajan-toplu --gonder --plan` after the preview) are the user's
explicit action; the setting is in `<state>/yakala/ajan/config.json`, not in `.beyin-preferences.json`.
Audio processing and the AudD upload are given only on `ajan-gonder`, per job, with two separate flags;
`Ctrl+Enter` and batch sending do not give these permissions.

Measurements made with a live model (apart from unit tests):

| Combination | Who, when, version | Measured | Not in the recorded measurement |
|---|---|---|---|
| Claude `gizli`, Windows 11 | Contributor, 17-19.10.2026, Claude Code 2.1.296 | A real vault job `completed`: result note, receipt `succeeded`, card `islendi` | Music tools, batch sending, monthly agent log |
| Claude `pencere`, Windows 11 | Contributor, 17-19.10.2026, Claude Code 2.1.296 | `completed`; the window stayed open, a closed window became `onay-bekliyor` | Same |
| Claude `gizli`, macOS | Maintainer, 18.10.2026, Claude Code 2.1.302 | Tool list of six Yakala tools (plus `WebSearch` on an open network); note text added to a URL was rejected | The full job chain (receipt, log), music tools |
| Claude, Linux | Not measured | Unit tests only | All of it |
| Codex `gizli` and `pencere`, Windows 11 | Contributor, 18-19.10.2026, Codex 0.155.1 | `completed` in both views; the window session ID was found from the rollout metadata | The `apply_patch` guessing channel was not closed; monthly agent log |
| Codex `gizli`, Linux | Contributor, 19.10.2026, official Codex 0.155.1, 0.160.0 and 0.163.0, fake Responses API | Forced `apply_patch` writes were rejected with the same contentless error; MCP delivery and hook worked | A real model service |
| Codex `gizli`, macOS | Maintainer, 18.10.2026, Codex 0.160.0 (previous branch) | The web search tool did not appear in `kisitli` mode | The native result of the root-deny permission profile |
| Music (`music_info`, `music_identify`) | Not measured | Unit tests with a fake network and local ffmpeg | A real AudD, platform and DPAPI call |
| Batch queue | Contributor, Windows 11 | Preview only | A real `--gonder`, a cancellation race |

In the 07.11.2026 maintenance round no live model, AudD or platform call was made; the changes were checked on macOS
with Python 3.11 and 3.14 unit tests and an update/rollback rehearsal from the 3.12.0 package.
On first use of a combination that has no recorded measurement, verify it with the Windows acceptance test
steps below.

### Notification, interruption and removal

On Windows, when the feature is turned on, a `Beyin Yakala Ajan.lnk` Start menu shortcut and the
`AvenoxBeyin.Yakala.Agent` notification identity are registered. The toast is sent with this identity; if the ownership
of the shortcut cannot be verified, another shortcut is not overwritten.
On Windows, clicking a notification opens the result note with the default application; the start, approval and error
notifications open the card. If the result path was not recorded, the completion notification also opens the card.
On Mac `osascript display notification` is used, on Linux `notify-send` if present.
The fixed notification text has no user request, URL or note
title. The operating system's notification setting, focus mode or a missing tool may hide the notification;
a notification failure does not change the card's result, it is only written to the log. [doc: notification sources]

The Windows worker breaks away from the popup's Job Object with `CREATE_BREAKAWAY_FROM_JOB | CREATE_NO_WINDOW`;
if this is not permitted, it does not silently fall back to a broader process path. The agent's own process tree
is kept in a separate, terminable Job Object. On Mac/Linux an independent supervisor process opens its own
session and process group; the CLI runs in this group. When only the pipe whose write end the worker holds
closes, when the CLI exits or when the monotonic time budget runs out, the supervisor
terminates its own group. Even if the worker dies with SIGKILL, this limit does not depend on the worker's finally block.
No signal is sent to an old PID taken from the persistent record. The CLI budget starts after the pre-check/preparation is finished;
a budget exhausted without starting the CLI is not accepted. Closing the popup or the listener does not
cancel a normal job; a timeout or `ajan kapali` terminates a running job.
This desktop feature does not set up a new network server or an always-running cloud task.

Job and bridge authority are tied not just to the PID number but to the process creation identity: on Linux the
boot ID and the `/proc` start counter, on macOS the `proc_pidinfo` start time, on Windows
liveness over the same handle and `GetProcessTimes` are used. On every MCP request, after the tool
lock is acquired and before data is returned, the worker identity/time limit is verified.
`complete` only acknowledges the instantaneous received result as `submitted`; the worker does the successful
closure. A visible Windows console whose worker has died may stay open, but the bridge
tools of the old job are closed. Interrupted jobs with an old schema, a reused or an unqueryable PID
are not re-run; an uncertain job is put under review and the next job is moved to.

For diagnosis use `<state>/yakala/ajan/<card-id>.log` and the `ajan` status. The job files
are under `<state>/yakala/ajan/jobs/<job-UUID>/`. The logs may contain requests, sources and tool outputs;
do not attach them to a public issue without checking. On a network/login/limit error the card
is preserved. If the process or the computer shuts down unexpectedly, partial effects may be unknown;
`ajan-devam` does not repeat the same job on its own, it requires review.

Yakala jobs' own writes are locked; if another normal agent or editor does not use the same lock, it may
later replace the monthly agent log as a whole and lose the added line. The independent
result note and the receipt link are therefore preserved. Opening a shared vault on two machines does not provide a single
distributed queue or a common file lock between all agents.

The POSIX card lock no longer writes `.beyin-yakala-card.lock` to the vault root; it is in the
shared lock directory in the user's local state area. The lock is tied to the current vault's file system identity;
path aliases of the same directory and different custom state choices meet at a single lock.
When the agent is off, normal capture also uses this lock. The Windows named mutex path is kept.
On update, close all old Yakala listener/worker processes and refresh with `yakala kur`;
do not run versions using the old and new lock layout together in the same vault.

`yakala kaldir` first sets the agent setting to `kapali` and applies the existing Yakala shortcut/skill removal.
Cards, agent results, receipts, downloaded files and diagnostic records are not deleted.
This version also preserves the new `Beyin Yakala Ajan.lnk` toast shortcut and the registration marker; if you want,
you can remove the shortcut with this name from the Start menu separately. Removal is not an operation that rolls back file
effects already made. The network behavior in this section is only for agent jobs sent explicitly;
the normal capture flow below does not go out to the network when it writes a card.

### Windows acceptance test

Unit tests do not run a real model service. The POSIX lifecycle tests open and terminate real temporary
Python processes; the Windows/macOS API models do not replace a local measurement.
Run the whole Yakala package in the repo root:

```sh
py -3 -m unittest discover -s tests -p "v3_yakala*_test.py"
```

Additionally try the following on Windows 11. For each record add the date, Windows/Python/CLI version,
client, `gizli`/`pencere`, `kisitli`/`acik`, file system and the expected/actual result.
Use distinguishable harmless test notes instead of real user secrets.

1. With `kur --ajan kapali`, verify that plain Enter does the old save and that the Ctrl+Enter row does not appear.
2. In a normal terminal log in to the chosen CLI, check the vault/hook trust and the `beyin.py receipt --help`
   contract; run `kur --ajan claude` or `codex`.
3. Send a harmless note research with Ctrl+Enter. Close the popup and the listener; verify that the job progresses without a console
   window opening, the real session ID on the card and the notification.
4. Download a known small public file. After the new target name, the hash, the result note, the receipt and the
   agent log links are verified together, check that it becomes `islendi`.
5. Try a job that asks for deletion/login, a private IP URL, a missing CLI, a network error and a short timeout.
   Verify that the cards are preserved, the reason is written and no success notification is given.
6. Send two requests back to back; check that a single CLI runs. On the same card try the normal `isle`/`bitti`
   calls, the `ajan-devam` behavior after an interruption and an explicit `ajan-serbest` handover.
7. Turn off notifications and repeat the job; the result and the log must be created. From a new normal session find the earlier
   card and the download path, and finally verify the `ajan kapali` and `kaldir` behavior.
8. Run Claude and Codex in both `gizli` and `pencere` modes. For Codex 0.155.1 and the new version to be used, record
   `codex --version`, `codex features list` without flags and the table with the job's disable flags. Verify the rejection of `view_image`/shell/sub-agent
   calls and the absence of web search in `kisitli` mode. The Yakala MCP call through code mode and the real session UUID
   must match. Watch the `--` and `--tools ""` behavior in the Claude window argv separately.
9. Run the job in a temporary CLI profile that has a pre-enabled MCP and plugin; another server's
   tool must not be opened, the user config hash must not change. After selecting Claude `--model haiku` and a custom
   executable, switch to Codex; the new job must start with the default Codex options.
10. Verify the Windows Codex read-only compatibility path in both hidden and window modes:
    `AGENTS.md` and the normal memory start-up, the allowed MCP read, the private rejection, the result,
    the receipt and agent log chain must work. Record the sandbox type and the CLI version.
    With harmless notes, Update/Move/Delete and existing/new Add writes inside/outside the vault
    must be rejected; no existing file's hash may change. The correct/wrong context errors
    may differ: do not present the Windows `-s read-only` path as a closed content-guessing limit.
11. Bring the allowed `fetch_source`/`download` calls to a total of 8 with mixed and failed attempts.
    The ninth call must be rejected before the network. Opening a new MCP connection to the same job must not
    renew the allowance; `complete` must still work. The `acik` tool description must not say that it
    forbids a new public URL; hosted web search is not in this counter.
12. Unexpectedly close only the worker process of a hidden job; the CLI/child processes must end with the Job Object
    closure. Even if the visible console stays open, the dead worker's MCP must not return
    a note. Review the results of a short timeout, `ajan kapali`, `ajan-devam` and `ajan-serbest`. Run the PID generation mismatch
    and AccessDenied regressions in an automated test;
    do not try to produce PID reuse by terminating a random system process.
13. On NTFS, a real exFAT/FAT USB and the network share to be used, publish a new note and download.
    The hash of an existing target must not change; in a race a single publish must win; an error in the middle of a write must not
    leave a half file under the final name. If neither hard link nor exclusive rename is supported,
    an explicit error and a preserved `.part` are expected. Junction/symlink rejection must continue.
14. An unrelated `knowledge/Dosyalar` note must be readable; another card's attachments, an attachment store whose old cards
    were moved, and private/sensitive notes must not be opened. The trust label of its own card/raw text/linked text attachment
    must be `untrusted`. Also try upper/lower-case path aliases.
15. Normal capture with the agent off must not write a new lock to the vault root. When different `--state` choices
    update the same card concurrently, no record may be lost. Having more than one companion or a Last-Session
    in the archive must not affect the job; the Last-Session bytes must not change. In the monthly log a
    single entry, the same bytes on a repeat call, and, for a `private` card, a summary-free status/links are expected.

**Separate Codex read-limit measurement for Linux/macOS:**
run [the optional real CLI regression](CODEX-APPLY-PATCH.md). Under root-deny, in the
relative/absolute, inside/outside-vault Update/Move/Delete and Add attempts the files must be preserved;
for the same path/operation the correct and wrong context must produce the same contentless error. The normal hook
and the allowed MCP delivery in the same session must also pass. Do not count a start-up/policy error as success;
do not automatically broaden this POSIX profile with the read-only selector or an extra read root. The Linux
measurement is not a macOS native measurement; record the platform, CLI and actual result separately.

**Esc and Opera One/GX, additional desktop measurement for #383:**

- Try plain Esc behavior with the source window, the popup and another window in front. Ctrl+Shift+Esc,
  Ctrl+Esc, Alt+Esc, Shift+Esc and Win+Esc must pass through the hook. Try holding a modifier down before the popup
  opens, releasing only one while left/right Ctrl are both held, and then plain
  Esc. Record on screen that the shortcut Windows reserves really works.
- For Opera Air, One and GX record the exact version/build and the profile/extension state. Measure the
  address/text/link selection on a normal article, a single X post, a logged-in heavy X feed and Instagram. Check that a username like `abc2h` with a
  `2h` time label does not corrupt the title.
- In each scenario record, for at least 20 repeats, the read time in ms, the correct-URL rate, returns without a URL and
  one-second budget overruns; report the median, p95 and maximum time. These are measurement
  targets; they are not performance measurements made for this branch.
- Two visible renderers, a foreign renderer, a document/foreground change between two reads and an ambiguous result in a
  dense UIA tree must stay without a URL. Compare under the same conditions as main/base;
  measure the effect of removing the omnibox on One/GX together with the correct URL and time.
  Do not automatically turn the old omnibox path back on to hide ambiguity.

### Technical sources

The access date of the first CLI/notification links is **17.10.2026**; the version-pinned Codex,
process, atomic publish and keyboard sources below were reviewed in the first fix on **19.10.2026 Turkey time**
(UTC records 18.10.2026). The named Codex permission profile research and the regression with three official
binaries were done on **19.10.2026 UTC**. CLI options may change;
documentation support is not evidence of a live run on this computer.

- Review: [#384 main comment](https://github.com/avenoxai/avenoxbeyin/pull/384#issuecomment-6243678257),
  [feature table additional note](https://github.com/avenoxai/avenoxbeyin/pull/384#issuecomment-6243771486),
  [#383 merge comment](https://github.com/avenoxai/avenoxbeyin/pull/383#issuecomment-6243513321),
  all 18.10.2026 UTC.
- Codex 0.155.1: [official binary](https://github.com/openai/codex/releases/tag/rust-v0.155.1),
  [feature names](https://github.com/openai/codex/blob/rust-v0.155.1/codex-rs/features/src/lib.rs),
  [shell/view_image/apply_patch registrations](https://github.com/openai/codex/blob/rust-v0.155.1/codex-rs/core/src/tools/spec_plan.rs),
  [sub-agent selection](https://github.com/openai/codex/blob/rust-v0.155.1/codex-rs/core/src/config/mod.rs),
  [apply_patch verification order](https://github.com/openai/codex/blob/rust-v0.155.1/codex-rs/core/src/tools/handlers/apply_patch.rs).
  Linux musl binary SHA-256: `a0ef8b2debc3bf747e07b1a039354de31300ac0dcc2276498ba281470b5d9115`.
  The [0.160.0 feature table](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/features/src/lib.rs)
  was compared in the source; in this fix a synthetic CLI/MCP test was also run with the 0.160.0 binary.
- Codex permission limit: [official beta profiles and scope](https://learn.chatgpt.com/docs/permissions),
  [0.163.0 release](https://github.com/openai/codex/releases/tag/rust-v0.163.0),
  [0.164.0-alpha.3 pre-release](https://github.com/openai/codex/releases/tag/rust-v0.164.0-alpha.3),
  [0.163.0 patch verification](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/src/tools/handlers/apply_patch.rs),
  [compilation of the permission profile](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/src/config/permissions.rs),
  [CLI profile selection](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/src/config/mod.rs),
  [normal hook trust contract](https://learn.chatgpt.com/docs/hooks).
  For detail and the SHA-256 list see the [research note](CODEX-APPLY-PATCH.md).
- Process: [Linux /proc](https://docs.kernel.org/filesystems/proc.html),
  [Windows GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes),
  [WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject),
  [Apple proc_info.h](https://github.com/apple/darwin-xnu/blob/main/bsd/sys/proc_info.h).
- Atomic publish: [Python 3.12 os.rename](https://docs.python.org/3.12/library/os.html#os.rename),
  [Linux rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html),
  [Apple RENAME_EXCL](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/stdio.h).
- Keyboard: [LowLevelKeyboardProc](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelkeyboardproc),
  [KBDLLHOOKSTRUCT](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct),
  [GetAsyncKeyState](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate).

- Claude Code: [CLI reference](https://code.claude.com/docs/en/cli-reference),
  [headless run](https://code.claude.com/docs/en/headless),
  [permission modes](https://code.claude.com/docs/en/permission-modes),
  [sandbox limits](https://code.claude.com/docs/en/sandboxing),
  [managed MCP](https://code.claude.com/docs/en/managed-mcp).
- Codex: [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli),
  [headless run and thread ID](https://learn.chatgpt.com/docs/non-interactive-mode),
  [config reference](https://learn.chatgpt.com/docs/config-file/config-reference),
  [approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security),
  [rules](https://learn.chatgpt.com/docs/agent-configuration/rules),
  [hook trust](https://learn.chatgpt.com/docs/hooks),
  [Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox).
- Microsoft: [process creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)
  and [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
  (updated 14.07.2025),
  [desktop toast registration with AUMID](https://learn.microsoft.com/en-us/windows/win32/shell/enable-desktop-toast-with-appusermodelid)
  (07.01.2021),
  [sending a desktop toast](https://learn.microsoft.com/en-us/windows/win32/shell/quickstart-sending-desktop-toast)
  (20.06.2022).
- Apple: [Display Notifications](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/DisplayNotifications.html)
  (updated 13.06.2016).
- Freedesktop: [Desktop Notifications 1.3](https://specifications.freedesktop.org/notification/latest-single/)
  (18.08.2024); GNOME: [libnotify](https://gnome.pages.gitlab.gnome.org/libnotify/).

## Handing pending cards to the agent in bulk

This feature works only with an explicit CLI instruction. Plain Enter, the SessionStart notification,
`liste`, `ajan-devam` or a new card being added to the inbox does not do a bulk send.
`ajan-toplu` is a preview by default; it creates no job record, changes no settings,
uses no network and does not open an agent process. For sending, the agent setting must be `claude` or
`codex`, `--gonder` must be present in the same command, and the preview's `plan` value must be given with
`--plan`. A bulk send is not done without the preview being seen. After installing the new
version, use the normal `yakala kur` flow to also update the old listener copy.

```text
py -3 beyin.py yakala ajan claude
py -3 beyin.py yakala ajan-toplu --neden --limit 5
py -3 beyin.py yakala ajan-toplu --neden --limit 5 --gonder --plan PLAN
```

The first command turns on the existing agent setting. The second command shows the card IDs, the FULL request to be
given to each card, the network mode, the free queue capacity and the `plan` value.
The third command gives an explicit send permission to the cards and requests seen in the preview.
`--gonder` without `--plan` gives an error and creates no job. If the
card, request, filter result or agent setting changed after the preview, the plan does not hold and the send is
rejected; a new preview is needed. Cards that arrive later do not become part of this bulk job. A successful send returns a `batch_id`;
this means only acceptance into the queue, not that the jobs are complete.

### Selection and request source

Only `tur: yakala`, `durum: bekliyor` cards in the selected Yakala inbox
are candidates. Subfolders, archives and other vaults are not scanned. Cards that are `ajanda`,
`onay-bekliyor`, `islendi`, `cikarildi` and `hata` are not taken into a bulk send.
Even if the user manually sets a card's status to `bekliyor`, the existing active job ownership
prevents a second job from being created. The single `ajan-gonder` also uses the same queue lock;
`KART_ID` and `KART_ID.md` are checked as the same card. A card carrying a local/private network address
or an invalid URL (for example a local page saved with the Web Clipper) is not
selected; it appears with its reason in the preview's `atlanan` ("skipped") list and does not block the other cards.

| Option | Behavior |
|---|---|
| `--neden` | Uses each card's first `## Why` section as that card's request |
| `--istek "..."` | Gives the same explicit request to every selected card; does not combine it with Why |
| `KART_ID ...` | Narrows the candidates to these IDs; a `.md` file name is also accepted |
| `--tur youtube` | Filters by the `kaynak_turu` field; can be given more than once |
| `--alan instagram.com` | Filters by the URL's exact host name; `www.` and `m.` are normalized |
| `--limit 5` | Selects the oldest five candidates; default 10, allowed range 1 to 32 |
| `--gonder` | Sends the previewed cards to the persistent queue; `--plan` is required |
| `--plan OZET` | The 64-character plan summary from the preview; rejects the send if the selection, a card or the setting changed |
| `--json` | Returns the preview, the batch ID and statuses as machine-readable JSON |

`--neden` and `--istek` exclude each other; choosing one explicitly is mandatory.
An empty Why, the `_(no note)_` placeholder, a NUL or a request longer than 16000 characters
blocks the send. If the request of one of the selected cards is invalid, the others are also
not sent. The `Recaptured` section and source selection added by a re-capture are not
turned into an automatic instruction in place of the first Why. If you want to use the latest request, give
`--istek` or edit the card's Why section.

```text
py -3 beyin.py yakala ajan-toplu --alan instagram.com --istek "Review this source and write a note with sources" --limit 3
py -3 beyin.py yakala ajan-toplu KART_ID_1 KART_ID_2 --neden
py -3 beyin.py yakala ajan-toplu KART_ID_1 KART_ID_2 --neden --gonder --plan PLAN
py -3 beyin.py yakala ajan-toplu --tur youtube --tur makale --istek "Summarize the main findings" --limit 4 --gonder --plan PLAN --json
```

Filters intersect; domain name matching is not a substring or arbitrary subdomain match.
In the existing card type classification, Instagram and TikTok links
can be `makale`; use `--alan` for these sources. When sending, copy the preview's
`plan` value and add `--gonder --plan VALUE` to the same options. This summary is
not an authorization key; it is a consistency check that ensures the preview was seen and that a change to the card/request/setting
is noticed.

Cards with a valid time-zoned `yakalandi` value are ordered by their real capture time,
and on a tie by card ID. Missing or invalid timestamps go
to the end and are ordered by card ID. Jobs already in the queue come first. The members of a bulk
job are added in this selection order; even if the system clock is set back or produces the same
timestamp, the monotonic job order is preserved.

### Capacity, persistence and result summary

Each card is a separate job and a separate agent session. The existing single worker runs single and
bulk jobs in order. The `max_queue` limit applies to the FULL total of `preparing`, `queued` and
`running` jobs; the default and upper limit are 32.
If the selection does not fit into the free capacity, no card is added to the queue; lower the limit or
wait for existing jobs to finish. The time/budget limits are copied from the current settings for each job;
no new total spending limit is added for a bulk.

Under the same queue and card locks, the send checks the current setting, all selected cards,
the requests, explicitly chosen extra sources, ownership and capacity. Each member's
combined UTF-8 job input is subject to the same 96 KiB limit as the single agent; room is reserved for later run
and result fields. An invalid extra source or an oversized job input
appears in the relevant card's `hata` field in the preview and `gonderilebilir` ("sendable") is false.
At send, all members are verified before the first manifest, job or card write;
on these input errors no member of the selection is sent. Then
it writes all member IDs and explicit requests to the file
`<state>/yakala/ajan/batches/<batch-UUID>.json`; each member's job stays in the existing `jobs/<job-UUID>/job.json`
layout. In the last stage a single worker wake-up call is made. The manifest,
cards and jobs are local files; the requests are stored in the existing machine
state outside the vault. The manifest read limit is 4 MiB, the single card read limit is 200 KiB.
A note that exceeds this limit or is not UTF-8 is not selected; it appears in the preview's `atlanan` list
and does not block the send of the other cards. If it is explicitly selected by ID, it gives an error.
Symbolic links and Windows junction/reparse paths are not allowed. If there is an unreadable
job record, the capacity is considered unknown and a new bulk send is rejected;
first review the relevant record and the card's location. Moving an old card may also require this
check.

```text
py -3 beyin.py yakala ajan-toplu-durum BATCH_ID
py -3 beyin.py yakala ajan-toplu-durum BATCH_ID --json
```

The summary is computed from the real job records on every query: preparing, queued,
running, completed, error, approval-waiting and cancelled members are counted separately.
Each member's result summary, the created note path and the receipt path are shown if present.
The model saying `complete` or being accepted into the queue is not by itself completion;
the terminal result after the existing worker's memory/receipt/Last-Session verification is used. `bitti` ("done") indicates that all members are in a terminal state and the card reconciliations
are complete; `hepsi_basarili` ("all succeeded") indicates that all are `completed`.
A bulk job that ends with a cancellation or an error is not counted as successful.

If the file write is interrupted in the middle, member IDs that were previously persisted are preserved;
a partial send is reported as `toplu_kismi`. On a forced process termination the first
manifest may stay `preparing`. On the next call the whole selection is not resent on its own.
The existing worker may run the next members whose validity is complete;
uncertain preparation jobs are left to human review under the existing recovery rule.
Review the manifest or the job records, and if needed use `ajan-devam`. A member whose record is missing
or corrupt is counted as `kayit_yok` / `kayit_gecersiz`; no result is assumed, and
`bitti` would not be correct until this uncertainty is resolved. If the worker wake-up fails,
the queued jobs are preserved and are not automatically turned into an error/approval state.

### Taking back members that have not started

```text
py -3 beyin.py yakala ajan-toplu-iptal BATCH_ID
```

This command cancels only bulk members that have not yet started and whose ownership is verified,
and sets their cards to `bekliyor`. It uses the same lock as a worker that has claimed the queue:
if the worker moved to `running` first, that member is preserved; if the cancellation was
persisted first, the worker does not run that member. Jobs in the running, completed, error or approval
state are not changed. If there is a run trace, an ownership mismatch or a corrupt
record, a safe cancellation is not assumed; that member is skipped and reported.

The cancellation state is first written to the job record as `cancelled` plus a card reconciliation request,
then the card is updated. If it is interrupted in between, `ajan-devam` can reconcile the card; it does not open
a new model job. User content, fields added later, result notes,
receipts and downloads are not deleted. The same cancel command can be run again.
Missing manifest members are not recreated during cancellation; their state
stays uncertain. This is not a command to undo the effects of a running agent or to
delete finished jobs. Giving the card to the agent again later requires a new, explicit
`--gonder` or `ajan-gonder` instruction.

A bulk job keeps the same network and tool limits. `ag: kisitli` is limited to each member's own
captured URL, the addresses explicitly selected in the card's `ek_urller` field at send time
and links returned from allowed pages. The extra addresses are copied into that
member's persistent job record; a URL in the card body, a different query
or a later edit of the card does not widen the existing job's source permission.
The extra sources use the same limits as the single agent: at most 63 addresses, 8192 characters per address and a
total 64 KiB record limit;
`ag: acik` keeps the existing privacy instruction.
Writing "download the audio" in Why or in the shared request does not give an upload of audio to an external service or extra
tool permission. A bulk job does not generate such permissions automatically.

The tests run with real local card/job/manifest files and queue locks; they run
without network, a model, a desktop notification and a real client:

```text
py -3 -m unittest discover -s tests -p v3_yakala_toplu_ajan_test.py -v
py -3 -m unittest discover -s tests -p "v3_yakala*_test.py"
```

In the Windows 11 live check: race single and bulk sends from two separate terminals;
check that the queue limit is not exceeded and no duplicate job appears.
Try a bulk cancel while the first member is running; verify that only the cards that did not start come back
and that the visible/hidden client choice follows the current setting. Check UTF-8 files,
vault/state paths with Turkish characters and the JSON outputs in the terminal.

## Optional: recognizing music in a video

This feature identifies the song and gives a legitimate listening link. Full song download,
reading accounts/cookies, circumventing DRM, using a browser session or the model
writing commands is not part of this capability. The Python side uses only the stdlib and, on Windows,
ctypes; no AudD SDK or new Python package is needed.

### Explicit permission and example usage

The two new MCP tools take no parameters. `music_info` reads only the music metadata of this card's captured
Instagram reel/video, TikTok or YouTube/Shorts page. `music_identify` extracts a local audio sample with the separate permissions below
and, if requested, sends it to AudD. The source URL, file path, search query, command,
key or approval cannot be given by the model as a tool argument.

```sh
# Choose the client you use; an open network alone does not grant audio upload permission.
python beyin.py yakala ajan claude --ag acik

# Once: enter the key secretly in the terminal. This command makes no service request.
python beyin.py yakala ajan-muzik audd

# Capture the source normally, then use the real card ID.
python beyin.py yakala ekle "https://www.instagram.com/reel/VIDEO_ID/" --neden "Identify the song"
python beyin.py yakala ajan-gonder KART_ID --istek "Identify the song and give a legitimate listening link" --ses-isle --tani-servise-gonder

# Local review only: the sample is not sent to any recognition service.
python beyin.py yakala ajan-gonder KART_ID --istek "Review the video metadata" --ses-isle

# Service status and turning it off.
python beyin.py yakala ajan-muzik
python beyin.py yakala ajan-muzik kapali
```

`--ses-isle` is the explicit permission the user gives for extracting a sample of up to
12 seconds for this job from a video they are permitted to process. `--tani-servise-gonder` is the
separate permission to upload that sample to AudD; it is rejected without `--ses-isle`.
Both permissions are written to the job record by the host, before the worker is woken up.
The words "download", "identify" or "I give permission" in the Why/request text,
popup Ctrl+Enter, the general `ag: acik` setting or a bulk send do not grant these
permissions on their own. When permissions are missing, the agent presents an `approval_required` result
and the CLI options needed. A second job cannot be queued before the earlier job on the same card finishes;
after the approval-waiting result is reviewed, a new command
is given. The old job does not restart on its own.

For non-interactive key entry, `ajan-muzik audd --anahtar-dosyasi FILE` can be
used. The file must be UTF-8 on a local disk outside the vault; a symlink/junction is
not accepted. Do not put the key in CLI text, the JSON agent setting, an environment variable,
a vault note or a prompt. The input file is not deleted automatically; the user
manages their own secure key source. The persistent service key is in `yakala/ajan/credentials/audd.json`
under state. If the resolved state path
stays inside the vault, the service setting is rejected. On Windows CurrentUser DPAPI is used.
On POSIX the file owner and `0600` permissions are verified; this path
makes no encryption claim. If the key is moved to a system/account other than the same operating system account,
it must be re-entered. The AudD variables are removed from the model/sub-tool environment; the bridge adds the key only to the fixed AudD POST body.

`ajan-muzik kapali` removes the key record. If the service is turned off while a video is being processed,
the bridge re-checks the key and the job state right before a new upload; it does not start a new
request with the old key. Taking back a request that has already started or deleting data on the service side is not this command's job.
Turning off/changing the key and the last permission check and POST are ordered under the same local OS lock.
Before the off command returns, the next new upload stops;
if there is a POST in progress, the command may wait for its network stage of at most 7 seconds.

### Network, evidence and result

| State | Page metadata | yt-dlp / local sample | AudD upload |
| --- | --- | --- | --- |
| `ag: kisitli` | Only the captured supported URL and allowed platform redirects | Off | Off |
| `ag: acik`, no extra permission | The same narrow tool | Off | Off |
| `ag: acik` and `--ses-isle` | On | On for this job | Off |
| The previous row and `--tani-servise-gonder` | On | On | Only if there is an AudD key, at most one attempt |

The existing privacy instruction of the general open network does not change: note/personal/private content is not put
into a search query or a URL. The AudD permission here covers only sending the fixed short audio
sample; notes, request text, card ID, vault path
and source URL are not sent to the service. Human voice/speech may be found in the sample;
the decision to send the sample covers this too. The model cannot extend this permission to another service.

Metadata sources: HTML `og:title`/`og:description`, the YouTube
`ytInitialPlayerResponse` description, Instagram music/original audio fields,
TikTok `music`, JSON-LD `MusicRecording`, and also `track`/`artist` in the permitted yt-dlp output.
A page's "Original audio" label is not evidence of a song identity. These results carry `verification: source_metadata_only` and
`recognized: false`. A real AudD match
carries `verification: provider_acoustic_match`; a confidence percentage the provider did not give is not
made up (`confidence: null`). If there is no match in the service result,
`unmatched` returns; if the service/tool is absent or safe processing is not possible, `unavailable`
returns. A source/metadata claim, a model guess and an audio match are not
mixed up.

Returned listening links are accepted only from `music.apple.com`, `open.spotify.com` and
`lis.tn` HTTPS addresses. Apple's numeric `i` parameter that selects the song is kept; other query/tracking and fragment fields are dropped. These
links are not opened automatically, not downloaded and not added to the restricted network's download allow
list. A Spotify/Apple preview address and an AudD match are not counted as a download
license. For a direct file for which the user's permission and the source's open permission exist, the existing `download` capability can be used;
this feature does not open a new full-song download path.

### Fixed tools and budgets

- For each job, page reading and audio processing are at most one persistent attempt each.
  The results are cached in state. There is no automatic retry after an interruption/timeout; retrying requires an explicit new job. This choice
  may require a new command on a temporary network error, but it prevents an automatic repeat of an uncertain paid
  request.
- The AudD attempt record is written before the POST. If `music-provider-attempt.json`
  exists, the same job does not send a paid request again. Even if the process is interrupted before the result record could be written,
  the earlier result is counted as "unknown"; it is not presented as successful.
- The page is at most 512 KiB; the yt-dlp JSON stdout at most 4 MiB; a single direct media file to be fetched
  at most 32 MiB. The audio is at most the first 12 seconds:
  mono, 16 kHz, 16-bit PCM WAV. At exactly 12 seconds 384044 bytes are produced.
  There is no audio selection/offset/model filter argument or microphone recording.
- yt-dlp extracts only metadata. A fixed argv; `shell=False`,
  `--ignore-config`, `--no-plugin-dirs`, `--no-js-runtimes`,
  `--no-remote-components`, `--no-exec`, `--no-playlist`, `--simulate`,
  cookie/cache disabling and zero retries are used. Playlists,
  the generic extractor and URLs/commands given by the model are not used.
- yt-dlp HTTPS access passes through a CONNECT proxy with random credentials that lives only on
  loopback. The proxy accepts only the fixed platform/CDN domain-name suffixes of the relevant platform,
  port 443 and verified public IPs. IP pinning prevents DNS rebinding and a redirect to a private IP.
  If the DNS results are a mix of public/private IPs, it is rejected. This is not an operating
  system sandbox; the installed yt-dlp/ffmpeg binaries are trusted local
  dependencies. There is no fallback for cookies/login or removing a security flag.
- The proxy limit is 24 CONNECT tunnels and a total of 12 MiB of encrypted transfer in both directions.
  The number of HTTP requests inside TLS is not seen; the 24 limit is not a claim about the number of HTTP requests.
  yt-dlp does the TLS certificate check; the proxy verifies and pins the target's numeric IP.
  When the proxy closes, all tunnels are closed.
- The stage times of a single tool call: page 7 s, yt-dlp 18 s, media 10 s,
  ffmpeg 5 s, AudD 7 s; the shared deadline is 50 s or the remaining
  time of the running job, whichever is shorter. Before a new network/local process stage and after the AudD
  attempt record is persisted, the job time is re-verified with the worker's PID + start identity.
  If the worker has ended, no new media request or audio upload is started. An HTTP request that has begun cannot be taken back. A watchdog that closes the DNS deadline and
  the socket at the deadline also stops a slow DNS/header flow.
  If the OS DNS call cannot be cancelled, at most four daemon resolvers per process
  may remain; these cannot open connections and hold new DNS capacity until they complete.
  These times are application ceilings, not a measurement of service latency.
- The media URL is determined by the data yt-dlp returns; the bridge makes a separate IP-pinned,
  limited HTTPS GET. An HLS/DASH manifest, a live stream, DRM, a cookie or
  a CDN outside the allow list gives a safe error. It does not save a page as mp3.
- ffmpeg opens only bytes taken from stdin. The media magic header is checked,
  the demuxer is pinned, `-protocol_whitelist pipe` is used. It cannot read additional input through a file,
  HTTP, concat or another protocol. The PCM stdout is read with a separate size limit and the stdlib writes the WAV header. The raw media and audio
  sample stay in RAM; no file is produced in Downloads or in the vault.
- The `moov` box that sits at the end of normal MP4 files is moved to the front in RAM only in a supported progressive layout
  containing a single `moov` and a single `mdat`;
  the `stco`/`co64` addresses are verified and corrected. Box/depth/table size
  limits, the real `mdat` payload addresses and number overflows are checked.
  A zero-length open-ended `moov`, fragment/index boxes in this layout or
  unsupported position information is rejected. This is not a general MP4 repair tool. If `moov` is already at the front, the file does not change.

### Service preference and Windows acceptance test

AudD is this version's optional provider because it supports a single fixed endpoint and a short audio sample
over stdlib HTTP. While there is no key the service stays off,
and even if the user adds a key, a per-job upload permission is required. The AcoustID/
Chromaprint, ACRCloud and Shazam add-ons were not implemented in this patch; the cost, input/license and privacy terms of the alternatives
must be evaluated separately.

Check of 19.10.2026: the AudD home page lists the first 300 requests as free and the following
1000 requests as 5 USD. The API documentation gives a 10 MB file ceiling for the standard endpoint; the home page gives the information that roughly the first 12 seconds are processed.
The 384044 bytes/12 s here is an application ceiling; it is not a
price or accuracy guarantee. Before using it, check the current price/quota and terms:

- https://audd.io/
- https://docs.audd.io/
- https://audd.io/terms/index.php (terms version 07.07.2026)
- https://audd.io/privacy/index.php
- https://github.com/yt-dlp/yt-dlp#usage-and-options
- https://ffmpeg.org/ffmpeg-protocols.html

AudD's agreement reserves the right to improve the service with de-identified/aggregated customer content;
no general "data is not retained / not used in training" guarantee is given. Recognition does not remove the source platform's terms or
the copyright holder's permission requirement.

The automated tests do not connect to a real paid service or a user account.
A real local loopback proxy, a slow HTTP header/DNS timeout, an anonymous WAV,
the same 12 s ffmpeg output for a normal and a faststart AAC MP4, not charging for results again,
a cancelled service permission, token redaction and negative
authority/URL/media scenarios are checked:

```sh
python -m unittest discover -s tests -p "v3_yakala_muzik_test.py"
python -m unittest discover -s tests -p "v3_yakala*_test.py"
```

What you must verify on your own machine on Windows 11: that the real yt-dlp/ffmpeg versions on PATH
support all the fixed security options, Turkish/space-containing
paths, DPAPI store/open and that a different account cannot open it, metadata and audio access in real permitted reel/
TikTok/YouTube examples, that no upload happens at all without the service permission,
a real match of a permitted sample with AudD, the link opening the right piece,
timeout/service shutdown, and full delivery of the process into memory. Live platforms may require login, region, CDN or JS.
In particular, when new YouTube flows require a JS runtime, this version does not
turn it on and returns a safe `unavailable`. In these cases the user must move to the official
platform/manual recognition path. Automatic account login,
taking browser cookies or widening the protocol permission is not recommended.

## How processing works

`python3 beyin.py yakala isle` extracts the text of pending cards, then the agent connects the lessons
to `knowledge/` notes and closes the card with `bitti`.

| Source | Path |
|---|---|
| A page that came in with the Web Clipper | The captured text is used, no network is used |
| YouTube | A sectioned transcript with [Defuddle](https://github.com/kepano/defuddle); if that fails or its language does not match the spoken language, the `yt-dlp` subtitle; if that is also missing, only the audio is downloaded, transcribed to text with local Whisper, and the audio is deleted |
| X, Reddit, GitHub, article | Defuddle; if that fails, text over plain HTTP |
| Mail | The selected text; for the whole mail, the agent's Gmail/Outlook connection |
| PDF, text file | `pdftotext` or direct reading; the agent opens the images |
| DOCX file | Text and table cells are read locally; images, embedded content or a document without text are left to the agent's review, and the part that is missing is written in the card's `uyari` field |

Text attachments are read as UTF-8; the BOM is removed. An attachment with a corrupt encoding is not taken into the raw text, and its file name is shown as a warning on the card.

The raw text sits in the card folder under `.ham/`. Because it is a folder starting with a dot, it does not mix into
search or Obsidian. `.ham/` and `dosyalar/`, where captured files sit, stay out of the repository whatever the card folder is, thanks to the
`.gitignore` written into them.

The file card reads only the files in the `dosyalar/` subfolder of its own folder that were copied there at capture time.
Even if the card's `## Files` section is changed by hand or from a synced device, the rest of the vault
(safe-type folders, `.obsidian/`, other notes) is not copied into `.ham/`; if `dosyalar/` is a link to
somewhere else (symlink, junction), no file is read.

### Missing-section warning on a web page

After Defuddle returns text, `isle` makes **one extra source fetch** to the same source URL and compares
the h2/h3 headings in the main content with the extracted text. The Defuddle command downloads the page itself
and does not hand back the HTML; this is why the check makes its own request. Redirects may require extra HTTP
requests. This check uses the existing HTTP
protections: private/local addresses are rejected in DNS and redirects. The timeout for the connection and for each
read is 15 seconds; the whole request including redirects takes at most 30 seconds,
and if the time runs out the check is counted as not done. The HTML for comparison can be at most 5 MB. Any error
that occurs in the check (network, parsing) does not drop the text; the card still becomes `cikarildi`. The source HTML is not downloaded again
in the retry loop and is not added to the `.ham/` file. If Defuddle fails, the plain HTTP
fallback still uses a single source fetch. In the video, file, selected text and Web Clipper paths there is no such extra
source fetch; the Web Clipper text is not counted as separately verified.

The check is a heuristic and looks at a single `article` or `main` area. Navigation, side panels and
explicitly hidden content are filtered out; repeats of the same heading, upper/lower case, HTML entities and ordinary
Markdown formatting differences do not count. Two kinds of evidence are sought:

- **Headings:** the area must have at least 6 distinct, meaningful h2/h3 headings. If at least 3 headings are
  found in the text, and at least 3 headings and at least 25% of the total are not found, a warning is written. This is how it looks when Defuddle's
  `id`/`class` word rules (such as `error-`) delete a section entirely.
- **`empty:hidden` blocks:** Tailwind's `empty:hidden` class hides an element only when it is empty,
  but Defuddle treats every class ending in `:hidden` as hidden and deletes it (this is why note boxes disappear).
  If the area has a paragraph or list item of at least 5 words carrying this class that is absent from the text, and at least
  3 headings are found in the text, a warning is written. Defuddle's own rule is followed: an element that also carries a display class such as `md:block`
  is not counted; classes tied to screen size such as `md:hidden`
  often hide a duplicate, so they are not counted as evidence.

The warning is written to the card's `uyari` field as **"The text may be incomplete: ..."**; the same warning appears in the `isle` result
as `not`. The text is preserved and the status stays `cikarildi`. The agent must check the source
page before drawing lessons.

This check does not prove the text is complete. It cannot detect missing paragraphs whose headings were preserved,
headings left in the table of contents, or every element hidden with CSS.
If there are multiple main content areas, insufficient headings/overlap, a failed request or a size limit,
no new claim of incompleteness is produced. A previous warning is preserved when the check cannot be done; it is removed
when all suitable headings in the new source response are found in the text and there is no lost `empty:hidden` block.
Cards processed earlier do not change on their own; to re-check, use
`python3 beyin.py yakala isle <id>`.

### The transcript language in a video

In an automatically dubbed video, YouTube offers a separate subtitle track for each dub. `isle`, if
`yt-dlp` is installed, learns the language spoken in the video from the video's information, asks Defuddle for the
transcript in that language and checks the language that comes back. If they do not match, it downloads only the track in the spoken language with `yt-dlp`;
a manually written subtitle takes precedence over an automatic one. The result is written to the card's frontmatter:

- `dil`: the language of the saved transcript.
- `altyazi`: the track obtained with `yt-dlp`, for example `en-orig (automatic)` or `tr (manual)`.
- `uyari`: written only if there is a sign of a problem: if the transcript could not be obtained in the spoken language, or
  if the video is dubbed (audio in more than one language, or an `-orig` track) and the spoken language could not be determined.

If `yt-dlp` is not installed, the language cannot be verified: the transcript Defuddle chose is saved as before and
its language is written to the `dil` field. If `dil` is not the language spoken in the video, install `yt-dlp` and retry with
`python3 beyin.py yakala isle <id>`; a card with a `uyari` is also retried with the same command. Cards
processed earlier do not change.

### Optional tools

None is required; if present, processing expands, if not, it continues with what is at hand.
`python3 beyin.py yakala durum` tells you which ones are found.

- **Node.js** (`npx`): for Defuddle. A pinned version (`defuddle@0.19.4`) is run.
- **yt-dlp**: the language spoken in the video, subtitles and audio.
- **Whisper**: on Mac `mlx_whisper`, elsewhere `whisper` or `whisper-ctranslate2`. If you do not want the audio downloaded, `isle --ses-yok`.
  If `yt-dlp` could tell the language spoken in the video, it is passed to Whisper as `--language`; if the language is unknown or the video
  is dubbed, Whisper recognizes the language itself. To choose a model, the `BEYIN_WHISPER_MODEL` environment variable
  (e.g. `large-v3-turbo`) is passed as `--model`. The default of `whisper-ctranslate2` is `small`; in languages such as Turkish
  it can garble terms (e.g. "likidite" (liquidity) → "liquidite"). If you have a GPU, choose a larger model.
  On a machine with an NVIDIA card `whisper-ctranslate2` chooses CUDA itself; if the CUDA library cannot be loaded (e.g.
  `cublas64_12.dll` is missing), the audio is transcribed again once on the CPU and the card's warning names the error.
  To speed it up, install the missing library (e.g. `pip install nvidia-cublas-cu12` and add its folder to PATH).
  If Whisper produces no text at all, the card shows Whisper's own last error line.
- **pdftotext** (Poppler): PDF text.

If no text comes out of an image-based PDF, the file name is shown in the processing result and in the card's warning.
Text extracted from the other attachments is preserved; no OCR is done.

On Windows, if these tools are installed as a `.cmd`/`.bat` wrapper, the arguments are run directly,
without passing through the command interpreter (cmd.exe); if this is not possible, that tool is skipped and
processing continues with what is at hand.

## Privacy

- Capture does not go out to the network; it only writes a file to the vault.
- The network is used only at the `isle` step and only for the sources you captured. If an X post is not on the page,
  Defuddle asks the FxTwitter API for the post address.
- Mail, clipboard text and file cards are written with `visibility: private`. If one of the selected additional
  links is an email address, the same rule applies even if the main source is public.
- To remove: `python3 beyin.py yakala kaldir`: the shortcut, skill and notification go away, your cards stay.

## Commands

```text
beyin.py yakala              capture window
beyin.py yakala ekle URL|DOSYA|METIN [--neden "..."]
beyin.py yakala liste [--durum bekliyor|cikarildi|islendi|hata]
beyin.py yakala isle [ID ...] [--ses-yok] [--tekrar]
beyin.py yakala bitti ID --bilgi knowledge/concepts/x.md [--ozet "..."]
beyin.py yakala kur [--kisayol-yok] [--tus 'ctrl+alt+b'] [--klasor "Notlar/Yakala"]
beyin.py yakala kisayol ['cmd+"']
beyin.py yakala kaldir | durum | sablon
```

### Source security

Creating a Yakala card uses no network. Before an HTTP(S) source is processed, local/private IP addresses,
URL user info and malformed addresses are rejected. Before a URL is sent to Defuddle and yt-dlp,
the DNS responses are also checked; redirects on the Python HTTP path pass through the same gate. If DNS
temporarily cannot be resolved, the card stays with an error note and the next cards continue to be processed.

The Python HTTP path resolves the name again at connect time, passes every answer through the same gate and opens the socket to the checked
IP address (TLS still verifies the real server name). A DNS answer that changes after the check
(rebinding) cannot redirect this path to a local address. If a proxy is set on the system, the proxy resolves the target; this binding
is not applied to the proxy itself.

Every time Defuddle and yt-dlp run, `isle` opens a short-lived protection proxy that listens only on `127.0.0.1`
and makes it the helper's only proxy (`ALL_PROXY`). Every connection the helper opens,
including every step of redirects, tells this proxy the target name; the proxy checks the address with the same gate
and opens the socket to the checked IP address. A redirect of a public page to a local address
or a DNS answer that changes later cannot let the helper reach the local network; the card ends in error with a note saying that the page redirected to a local or private
network address. An HTTPS connection stays end-to-end
encrypted inside the proxy. The `NO_PROXY` list is not passed to the helper.

If a proxy is set in the environment (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`) or, for yt-dlp, in the operating system
(for example a local proxy client such as `127.0.0.1:7890`), the protection does not turn off; it stands in front of that proxy:
every target first passes through the same gate, and only after that does the user's proxy
carry the connection.
A step going to a local or private address is never asked of the user's proxy. The HTTP proxy, `socks5h`
and `socks4a` take the target name and resolve it themselves (as on the Python path); `socks5` and `socks4` take the checked
IP address. A public name in the `NO_PROXY` list connects directly to the checked IP address. The proxy credentials (`user:password@`) are preserved. The protection does not
open a connection through a type it cannot chain, such as an `https://` proxy (connecting to the proxy with TLS); the helper then cannot fetch the page. npm
keeps using the user's proxy settings and the `NO_PROXY` list only for its own registry
through `npm_config_https_proxy`, `npm_config_proxy` and `npm_config_noproxy`.

Limit: Defuddle's YouTube, Reddit, X, Bilibili and C2 wiki readers open their own connection to those sites' fixed
addresses; these requests do not pass through the protection proxy, but their targets are also not an address that the
card content can choose. yt-dlp works only with a YouTube address: even if the card's
`kaynak_turu` field is set to `youtube` by hand, another site is not given to yt-dlp; it is
processed according to the address type.
The raw source text is marked as untrusted data;
role-change, command-execution and file-deletion requests inside the text are not counted as instructions.

### Concurrent card writes

The card and the raw source result are saved together only if the byte image at the start of extraction is still valid. If another capture or job changed the card, a late result does not overwrite it. On POSIX the lock is tied not to a file in the vault but to the directory's device/inode identity in the local state root; a different state choice does not create a second lock area for the same card. Windows uses the existing named mutex path. This lock coordinates only processes that write through this module on the same machine.
