# Windows capture: ABI map and acceptance test

Source review date: **13 October 2026**. The GUIDs and zero-based slots were compared against
Microsoft's Windows SDK headers. The `main` in the links is a moving branch; do not read this
document as a SHA-256 pin of an SDK file.
No real WGC/GPU/desktop test has been done on Linux. Pure ABI and lifecycle models do not
prove that a Windows driver successfully produces frames.

Browser addition of 19.10.2026: the Firefox/Zen MSAA and Yandex renderer paths are documented
separately below. These new paths have not been tried on a real Windows desktop. The fact that
the UIA/IA2/MSAA interface appears in the official documentation does not mean every browser
version gives this reader the expected tree. WGC/PrintWindow behavior was not changed by this
addition.

## All IIDs used

| Interface | GUID | Source |
|---|---|---|
| `IGraphicsCaptureItemInterop` | `3628e81b-3cac-4c60-b7f4-23ce0e0c3356` | [S02](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/Windows.Graphics.Capture.Interop.h) |
| `IGraphicsCaptureItem` | `79c3f95b-31f7-4ec2-a464-632ef5d30760` | [S01](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.graphics.capture.h) |
| `IGraphicsCaptureSessionStatics` | `2224a540-5974-49aa-b232-0882536f4cb5` | [S01](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.graphics.capture.h) |
| `IDirect3D11CaptureFramePoolStatics2` | `589b103f-6bbc-5df5-a991-02e28b3b66d5` | [S01](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.graphics.capture.h) |
| `IDirect3D11CaptureFramePool` | `24eb6d22-1975-422e-82e7-780dbd8ddf24` | [S01](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.graphics.capture.h) |
| `IGraphicsCaptureSession` | `814e42a9-f70f-4ad7-939b-fddcc6eb880d` | [S01](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.graphics.capture.h) |
| `IDirect3D11CaptureFrame` | `fa50c623-38da-4b32-acf3-fa9734ad800e` | [S01](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.graphics.capture.h) |
| `IDirect3DDxgiInterfaceAccess` | `a9b3d012-3df2-4ee3-b8d1-8695f457d3c1` | [S03](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/windows.graphics.directx.direct3d11.interop.h) |
| `IDirect3DDevice` | `a37624ab-8d5f-4650-9d3e-9eae3d9bc670` | [S04](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.graphics.directx.direct3d11.h) |
| `IDXGIDevice` | `54ec77fa-1377-44e6-8c32-88fd5f44c84c` | [S06](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/shared/dxgi.h) |
| `ID3D11Device` | `db6f6ddb-ac77-4e88-8253-819df9bbf140` | [S05](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/d3d11.h) |
| `ID3D11DeviceContext` | `c0bfa96c-e089-44fb-8eaf-26f8796190da` | [S05](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/d3d11.h) |
| `ID3D11Texture2D` | `6f15aaf2-d208-4e89-9ab4-489535d34f9c` | [S05](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/d3d11.h) |
| `IClosable` | `30d5a829-7fa4-4026-83bb-d75bae4ea99e` | [S07](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.foundation.h) |

The `ID3D11Device` and `ID3D11DeviceContext` addresses come from the `D3D11CreateDevice`
outputs; their IIDs are present in the map for auditing, and no extra QI is done with these
two IIDs. The frame/session/pool addresses are likewise the output of their own typed WinRT
method. No separate GUID is invented for IUnknown/IInspectable; their inherited slots are used.

## Vtable slots called

All numbers are **0-based**, including inherited slots. IUnknown: QueryInterface=0,
AddRef=1, Release=2. IInspectable additionally contains GetIids=3, GetRuntimeClassName=4,
GetTrustLevel=5; that is why the first WinRT method is usually 6.

| Interface | Slot | Method | Return / critical argument | Source |
|---|---:|---|---|---|
| IUnknown / all interfaces | 0 | QueryInterface | HRESULT; GUID*, void** | SDK interfaces |
| IUnknown / all interfaces | 2 | Release | ULONG (32-bit); not HRESULT | SDK interfaces |
| IGraphicsCaptureItemInterop | 3 | CreateForWindow | HRESULT; HWND, REFIID, void** | S02 |
| IGraphicsCaptureSessionStatics | 6 | IsSupported | HRESULT; WinRT boolean* (8-bit) | S01 |
| IGraphicsCaptureItem | 7 | get_Size | HRESULT; SizeInt32* | S01 |
| IDirect3D11CaptureFramePoolStatics2 | 6 | CreateFreeThreaded | HRESULT; device*, pixel format, buffer count, SizeInt32 **value**, pool** | S01 |
| IDirect3D11CaptureFramePool | 7 | TryGetNextFrame | HRESULT; frame** | S01 |
| IDirect3D11CaptureFramePool | 10 | CreateCaptureSession | HRESULT; item*, session** | S01 |
| IGraphicsCaptureSession | 6 | StartCapture | HRESULT | S01 |
| IDirect3D11CaptureFrame | 6 | get_Surface | HRESULT; surface** | S01 |
| IDirect3D11CaptureFrame | 8 | get_ContentSize | HRESULT; SizeInt32* | S01 |
| IDirect3DDxgiInterfaceAccess | 3 | GetInterface | HRESULT; REFIID, void** | S03 |
| ID3D11Device | 5 | CreateTexture2D | HRESULT; D3D11_TEXTURE2D_DESC*, initial-data*, texture** | S05 |
| ID3D11Texture2D | 10 | GetDesc | **void**; D3D11_TEXTURE2D_DESC* | S05 |
| ID3D11DeviceContext | 47 | CopyResource | **void**; destination*, source* | S05 |
| ID3D11DeviceContext | 14 | Map | HRESULT; resource*, subresource, map type, flags, mapped* | S05 |
| ID3D11DeviceContext | 15 | Unmap | **void**; resource*, subresource | S05 |
| IClosable | 6 | Close | HRESULT | S07 |

Slot traps: `ID3D11Texture2D` inherits the IUnknown + ID3D11DeviceChild + ID3D11Resource
methods. `ID3D11DeviceContext` also derives from ID3D11DeviceChild, so the Map/CopyResource
numbers are not simply the method's visible position in the declaration. The FramePool order
Recreate=6, TryGetNextFrame=7, add/remove_FrameArrived=8/9,
CreateCaptureSession=10 is preserved. This implementation does **not** call 8/9; it reads the
free-threaded pool with short-interval `TryGetNextFrame`. So no event delegate GUID or
DispatcherQueue is needed; no nonexistent callback API is used. [S01, S09]

## Exported functions and data layout

`combase.dll`: RoInitialize(uint32)->HRESULT, RoUninitialize()->void,
WindowsCreateString(wchar*,uint32,HSTRING*)->HRESULT,
WindowsDeleteString(HSTRING)->HRESULT,
RoGetActivationFactory(HSTRING,GUID*,void**)->HRESULT. [S23, S24]

`d3d11.dll`: D3D11CreateDevice and CreateDirect3D11DeviceFromDXGIDevice.
The latter takes an IDXGIDevice* and returns an **IInspectable***; QI to IDirect3DDevice is
done after that. The D3D11 device/context are obtained through HRESULT/out parameters. [S03, S22]

| Layout | Size / contract |
|---|---|
| GUID | 16 bytes; the first three fields little-endian, the remaining 8 bytes as is |
| HRESULT / ULONG | signed int32 / unsigned int32; the Linux `c_long` width is not copied |
| HWND / COM / HSTRING | pointer width |
| SizeInt32 | 8 bytes; two signed int32 |
| D3D11_TEXTURE2D_DESC | 44 bytes; including DXGI_SAMPLE_DESC |
| D3D11_MAPPED_SUBRESOURCE | 16 bytes on x64, 12 on x86; pointer + two uint32 |

D3D settings: hardware driver=1, BGRA_SUPPORT=0x20, SDK_VERSION=7,
DXGI_FORMAT_B8G8R8A8_UNORM=87, two frame buffers. Staging texture: Usage=3,
BindFlags=0, CPUAccessFlags=0x20000, MiscFlags=0. Map type READ=1, flags=0.
The texture and frame ContentSize are checked separately; the real `RowPitch` is used. [S01, S05, S17]

## Lifecycle / failure

`_WGCSession` runs only in a terminable helper process. If MTA RoInitialize(1) succeeds
(including S_FALSE), it is balanced with one RoUninitialize. Output pointers are registered in
scope **before** the call; even on a partial-creation failure, the references already obtained
are released. For a frame, the staging/texture/access/surface are released and the frame is
Closed/Released. Then the session, pool, item/factory and device chain are cleaned up in
reverse order. If Map succeeded, Unmap runs even if the CPU copy fails. A Close failure does
not skip the other Release calls.

A stuck native call may not return to the normal `finally` flow. At the outer deadline the
child/job is terminated; in that case it is **not claimed** that Python ran each Release.
The operating system reclaiming resources when the process dies is a separate safety boundary. [S16]

The outer WGC budget is 2.5 seconds; the inner frame-wait budget is 1.5 seconds. If WGC
fails, an independent PrintWindow child gets 1.2 seconds. Termination/startup costs are added
to these figures; they are not an end-to-end real-time guarantee. PrintWindow is synchronous,
so it too is not called on the Tk/listener thread. [S15]

## Real Windows verification

In the full repo, first place the current files on the PR branch and run the tests:

```powershell
py -3.12 -m unittest discover -s tests -p "v3_yakala_*.py" -v
$env:BEYIN_TEST_WGC = "1"
py -3.12 -m unittest discover -s tests -p "v3_yakala_wgc_test.py" -v
Remove-Item Env:BEYIN_TEST_WGC
```

The WGC test accesses only the window it draws itself. If the desktop is locked, foreground is
refused, or WGC gives no frame, do not count this test as passed. The new `BEYIN_TEST_DESKTOP`
guard has not been added to the other existing real Win32 tests. Outside the full repo, tests
that need installer/build/hygiene dependencies may fail because of missing files; those are
not successes.

In PowerShell, after running each command, switch to the target window during the countdown:

```powershell
py -3.12 tests/manual_windows_capture.py --backend wgc --delay 5 --output .\wgc-game.png
py -3.12 tests/manual_windows_capture.py --backend printwindow --delay 5 --output .\printwindow-game.png
py -3.12 tests/manual_windows_capture.py --backend auto --delay 5 --output .\auto-game.png
py -3.12 tests/manual_windows_capture.py --url --delay 5
```

`--backend wgc` does no fallback. The successful JSON must contain `method: WGC` and the
expected size; open the file and check that it is the right window/current frame. Do not
count a wrong/black image as a success just because a PNG was created. `--backend auto` writes
the two attempts and the selected method. The URL command writes the address to the console,
so do not share the output of private/tokenized addresses.
This tool does not write a card to the vault; it writes only the explicitly requested PNG file.

Then, in an installed vault, after the new script has been placed:

```powershell
py -3.12 .\beyin.py yakala kur
py -3.12 .\beyin.py yakala durum
```

Compare these scenarios: a normal Chrome page; another address typed into the Chrome address
bar but without pressing Enter; Opera Air; Notepad; a window/borderless/exclusive-fullscreen
GPU game; a second monitor; %100/%150/%200 DPI; source change; an elevated application;
Alt+Tab; two quick Enters and 10 consecutive hotkeys. A single popup must remain; pressing the
hotkey again must keep the old note/sources and bring it to the front; Esc or Close must close
without saving.

Fullscreen games, DRM/protected windows, the secure UAC desktop, UIPI/privilege differences,
screen lock and HDR color accuracy are not within the scope of universal success. The WGC path
produces SDR BGRA8; HDR tone mapping has not been added. The protection is not bypassed, and
on failure the screen does not fall back to BitBlt. [S08, S21]

## Opera Air: renderer and MSAA reading

Addition of 15 October 2026. Even though Opera's top-level window UIA tree does not show page
links, the `Chrome_RenderWidgetHostHWND` found with `EnumChildWindows` can present its own
accessibility provider. The single visible candidate is constrained by `IsChild`,
`GetAncestor(GA_ROOT)` and the window PID; the foreground and renderer identity are verified
again after reading.

`AccessibleObjectFromWindow(HWND, OBJID_CLIENT=0xfffffffc, IID_IAccessible, void**)`;
IID `618736e0-3c3d-11cf-810c-00aa00389b71`. `IAccessible` inherits IDispatch:

| Slot | Method | Argument/result |
|---|---|---|
| 10 | get_accName | CHILDID_SELF (`VARIANT VT_I4=0`), BSTR* |
| 11 | get_accValue | CHILDID_SELF, BSTR*; explicit HTTP(S) URL |
| 13 | get_accRole | CHILDID_SELF, VARIANT*; VT_I4, ROLE_SYSTEM_DOCUMENT=15 |
| 14 | get_accState | CHILDID_SELF, VARIANT*; INVISIBLE=0x8000 / OFFSCREEN=0x10000 are rejected |

VT_I4 is read only from the low 32 bits; the BSTR is released with `SysFreeString`, the VARIANT
with `VariantClear`, the object with `Release`. A successful CoInitializeEx/S_FALSE is balanced
with CoUninitialize. API and slot source: [Microsoft Windows SDK oleacc.h](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/oleacc.h).

The Opera page+cursor read is done in the same terminable `opera` helper process, within a
1.8-second budget (`OPERA_TIMEOUT`). If the first MSAA read returns the `Chrome Legacy Window`
placeholder (ROLE_SYSTEM_CLIENT), one UI Automation request is made to the renderer
(`_uia_touch`: element + Document search, nothing is read) and the document is awaited for at
most 0.8 seconds (`OPERA_WARMUP`); if the renderer changes, it gives up. The cursor's physical
coordinate is verified against the top-level window; the link search is done in the UIA tree
of the renderer HWND. The document value is verified in two reads, and the link found is also
verified in two reads. The document tree is not scanned to find the URL of another tab/iframe.

Unit model tests: `tests/v3_yakala_opera_test.py`. Live acceptance: a real video link on the
YouTube home page in Opera Air, the same card while the preview is open, an Instagram post
link, an address bar draft, window/tab switching and two monitors. No test should produce a
guess from the History database; when uncertain, the existing image path remains instead of a
link.

## Firefox and Zen: MSAA Document / Link

Addition of 19.10.2026; base `d9aa301`. The new `browser_document` protocol request for
Windows runs through `_windows_read` and the existing terminable `_process_packet`. Native
calls are not made on the Tk or hotkey thread. The HWND must be a positive integer, the
application must be on the explicit allow list, and the optional cursor must be exactly two
signed int32. The nominal budget is 1 second; process start/kill/cleanup costs are added. On
cancellation or at the deadline, the child is terminated.

`_win_document_identity` obtains the live identity with foreground/IsWindow/IsHungAppWindow,
the PID, a process handle and `QueryFullProcessImageNameW`. For Firefox/Zen, the full exe name
and `MozillaWindowClass` are required; the window title alone is not looked at. The identity
must match again at the end of the read. The process handle is cleaned up with `CloseHandle`.

Firefox's chrome shell is not confused with a Document. The official `DocAccessible::NativeRole`
produces CHROME_WINDOW for typeChrome; `RoleMap.inc` maps this to `ROLE_SYSTEM_APPLICATION=14`.
Web content is `ROLE_SYSTEM_DOCUMENT=15`. For this reason there is no special URL exception
that recognizes and skips `chrome://` text. Current Mozilla architecture lists MSAA, IA2 and
`uiaRawElmProvider` interfaces together on Windows. This implementation chooses the direct MSAA
document/link contract with stdlib/ctypes; it does not claim that Firefox does not support
UIA. [B01-B05]

ABI for `_WindowsMSAA`:

| Type / export | Contract |
|---|---|
| GUID | 16 bytes |
| HRESULT / LONG / ULONG | int32 / int32 / uint32; the host Linux `long` size is not used |
| POINT | Two int32, 8 bytes; physical screen coordinate |
| VARIANT | 8-byte header; a union containing a 64-bit scalar and two VT_RECORD pointers; Win32 16, Win64 24 bytes, 8-byte alignment |
| CoInitializeEx | MTA; S_OK and S_FALSE are balanced with one CoUninitialize |
| AccessibleObjectFromWindow | HWND, OBJID_CLIENT, IID_IAccessible, void** |
| AccessibleObjectFromPoint | POINT by value, IAccessible**, VARIANT* child |
| AccessibleChildren | IAccessible*, LONG start/count, VARIANT*, LONG* actual count |
| SysStringLen / SysFreeString | 32768 UTF-16 code-unit limit before copying a BSTR; every BSTR is freed |
| VariantClear | The returned role/state/children VARIANTs are cleared on the error path too |

IAccessible IID: `618736e0-3c3d-11cf-810c-00aa00389b71`.
IUnknown IID for identity comparison: `00000000-0000-0000-c000-000000000046`.
Slots are zero-based, including the IUnknown + IDispatch inheritance. [B06-B09]

| Slot | Method | Critical argument / result |
|---:|---|---|
| 0 | QueryInterface | GUID*, void**; identity/AddRef |
| 2 | Release | uint32, not HRESULT |
| 7 | get_accParent | IDispatch**; a separate QI is needed for IAccessible |
| 8 | get_accChildCount | int32* |
| 10 | get_accName | VARIANT child by value, BSTR* |
| 11 | get_accValue | VARIANT child by value, BSTR*; Document/Link full URL |
| 13 | get_accRole | VARIANT child by value, VARIANT*; VT_I4 |
| 14 | get_accState | VARIANT child by value, VARIANT*; VT_I4 |
| 22 | accLocation | Four int32* x/y/width/height, VARIANT child by value |

Every COM output pointer enters the owned list before the call. The IDispatch pointer is not
cast; IAccessible QueryInterface is used. The IUnknown references obtained through QI are kept
alive until the end of the snapshot; this prevents a reused address from being mistaken for the
same object. All obtained references are Released once in reverse order. If the child is
killed before a native call returns, it is not claimed that Python's finally completed; the
resources are bounded by the process lifetime.

The outer UI tree is scanned to at most 512 nodes and 32 levels. An INVISIBLE/OFFSCREEN
subtree is skipped; a missing role/state, a loop, partial child enumeration or exceeding a
limit does not yield an address. Once the single visible Document is reached, it is not
descended into; an iframe does not take the place of the main page. The result is rejected if
two visible documents have the same URL, if the second URL is empty/local, or if the document
is BUSY. In the two selections, the URL, title and retained IUnknown document identity must
be the same.

Hover starts from the real hit of `AccessibleObjectFromPoint`. The physical cursor point is
tied to the source window with `WindowFromPhysicalPoint` and `GetAncestor(GA_ROOT)`. Across at
most 64 ancestor objects, it looks for a real `ROLE_SYSTEM_LINK=30`, the link's physical
bounds and a descent chain that reaches the selected Document. A toolbar link, another
document, a busy link/iframe, two nested links, a loop or a missing value is rejected. In the
two hover reads, the URL, name and retained IUnknown/child identity must match; private
identity fields are not written to the IPC result. The Windows hotkey uses the recorded
physical point; if the cursor moved afterwards, it does not take the new point as the captured
point. This is not an atomic snapshot of the whole desktop.

## Yandex, other Chromium windows and the separate Opera wake-up PR

`_chromium_committed_url` runs inside the existing `uia` child request. An explicit HTTP(S)
omnibox value is strictly verified. If there is no scheme, the real document URL is obtained
with `_opera_snapshot` in the same child/budget; agreement with the visible text, a second
unfocused UIA read and the foreground are rechecked. There is no fallback on a focused or
unreadable box. Only a difference of a trailing root `/` is treated as equivalent; `www`, IDN
and percent-encoding display are not normalized by guesswork. `tab_url` now requires a strict
full URL. On a cold renderer or an exact display mismatch, the result may be empty.

Yandex's generic `browser.exe` name alone is not a reliable product choice. If the live exe
path ends with `\\YandexBrowser\\Application\\browser.exe`, the existing `_opera_snapshot` is
called; at the end the foreground/PID/class/path identity is checked again. If a non-standard
portable/beta installation does not satisfy this contract, there is no address. The single
visible renderer, the two document/hover reads and the existing UIA hyperlink limits are
preserved. Arc/Samsung Windows readers were not added to this allow list without measuring the
exact process and provider tree on a device. [B10]

Waking cold web accessibility in Opera Air with a single UIA request is the separate work in
[#399](https://github.com/avenoxai/avenoxbeyin/pull/399). This patch does not include that
change; no wake/retry/wait was added to the `_opera_snapshot` side. Cold/warm provider
measurements are separately needed for Yandex, which uses the shared path, and for Chromium
that needs schema verification. If #399 is merged later, all calls of the shared helper must
be measured again.

## Acceptance measurement of the new browser readers

The new test file `tests/v3_yakala_browser_windows_test.py` checks, without going to a real
Windows desktop, the native adapter ABI/ownership, fake provider trees, process identity,
physical point ownership, iframe/split view, URL/object/foreground changes and the child
protocol. The Windows x86/x64 VARIANT models do not replace a real x86 COM marshaling test.
Run all the platform tests from the repo root:

```powershell
py -3 -m unittest discover -s tests -p "v3_yakala*_test.py"
py -3 tests/manual_browser_capture.py --delay 5 --repeat 20 --interval 1
py -3 tests/manual_browser_capture.py --delay 5 --expected-page https://example.com/
py -3 tests/manual_browser_capture.py --delay 5 --expect-empty
```

Switch to the browser during the countdown. If you know the full address of the real link,
add `--expected-hover`. The probe does not write a card, and does not print URLs/titles by
default; `--show-urls` is an explicit choice. Without an expected value, exit 0 means only
that the measurement completed. Read the `checked_samples` and mismatch fields. Add the
Windows build/Python architecture/browser version, permissions, DPI/monitor and cold/warm
state to the result; measure p50/p95 with at least 20 samples.

Priority: Firefox, Zen single pane and split view, a standard Yandex installation, then the
old Chrome/Edge/Brave/Vivaldi/Opera regression. Record these scenarios separately: a draft
omnibox, HTTP and HTTPS, two tabs with the same URL, navigation with the same title, a link
inside an iframe, a new native dialog, a negative coordinate, %100/%150/%200 DPI, provider
access denial, cancellation and consecutive hotkeys. No X/Instagram ARIA article fallback was
added for Gecko; if there is no real hyperlink, an empty hover is correct. Do not combine the
absence of an address with a wrong address in the same metric. The device success rate and p95
for the new paths were not measured in this environment.

Browser sources, accessed 19.10.2026. For moving `main` links, the file blob is noted; no date
was invented for sources that have no publication date:

- **B01**: [Mozilla architecture](https://firefox-source-docs.mozilla.org/accessible/Architecture.html).
- **B02**: [MsaaAccessible.cpp](https://github.com/mozilla-firefox/firefox/blob/main/accessible/windows/msaa/MsaaAccessible.cpp),
  blob `3582dc88db83151e0a0a495c8f6c30fabcce1190`; Document accValue.
- **B03**: [DocAccessible.cpp](https://github.com/mozilla-firefox/firefox/blob/main/accessible/generic/DocAccessible.cpp),
  blob `dea5590be46e864477913934d3968b5f38f5b4ee`; chrome/content role difference.
- **B04**: [RoleMap.inc](https://github.com/mozilla-firefox/firefox/blob/main/accessible/base/RoleMap.inc),
  blob `2a56fff3f79f364af871139854420aee3106096f`; APPLICATION/DOCUMENT mapping.
- **B05**: [HTMLLinkAccessible.cpp](https://github.com/mozilla-firefox/firefox/blob/main/accessible/html/HTMLLinkAccessible.cpp),
  blob `7f50d03d7712ca28d719a7f3f027fda6674abd8f`; LINK and GetLinkLocation.
- **B06**: [Windows SDK oleacc.h](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/oleacc.h),
  blob `179b03fa7f84399055a7e6638b9d2d67c7ac75e6`.
- **B07**: [AccessibleChildren](https://learn.microsoft.com/en-us/windows/win32/api/oleacc/nf-oleacc-accessiblechildren),
  updated 13.10.2021; [AccessibleObjectFromPoint](https://learn.microsoft.com/en-us/windows/win32/api/oleacc/nf-oleacc-accessibleobjectfrompoint),
  updated 22.02.2024.
- **B08**: [get_accParent](https://learn.microsoft.com/en-us/windows/win32/api/oleacc/nf-oleacc-iaccessible-get_accparent),
  updated 22.02.2024; [accLocation](https://learn.microsoft.com/en-us/windows/win32/api/oleacc/nf-oleacc-iaccessible-acclocation),
  updated 13.10.2021.
- **B09**: [IUnknown QueryInterface](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nf-unknwn-iunknown-queryinterface(refiid_void)),
  updated 31.08.2022; [WindowFromPhysicalPoint](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-windowfromphysicalpoint),
  updated 22.02.2024.
- **B10**: [Yandex exe name](https://browser.yandex.com/help/en/troubleshooting/troubleshooting?lang=en)
  and [product path](https://browser.yandex.com.tr/help/en/troubleshooting/media). The browser
  flag advice in the source was not applied; only the installation path evidence was taken.

## Sources

The SDK and web sources below were reviewed on 13 October 2026; we do not label sources of
unknown publication date with an invented date. The CreateForWindow Learn page was last
updated on 2024-04-11; the delayed-render article is from 2022-06-09. A correct map does not
replace live testing.

- **S01** - [WGC WinRT ABI (Windows SDK)](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.graphics.capture.h)
- **S02** - [IGraphicsCaptureItemInterop (Windows SDK)](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/Windows.Graphics.Capture.Interop.h)
- **S03** - [DXGI/WinRT interop (Windows SDK)](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/windows.graphics.directx.direct3d11.interop.h)
- **S04** - [Direct3D11 WinRT interfaces (Windows SDK)](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.graphics.directx.direct3d11.h)
- **S05** - [D3D11 interfaces and structures (Windows SDK)](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/um/d3d11.h)
- **S06** - [DXGI interfaces (Windows SDK)](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/shared/dxgi.h)
- **S07** - [IClosable (Windows SDK)](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/winrt/windows.foundation.h)
- **S08** - [CreateForWindow; Windows 10 1903 / build 18362](https://learn.microsoft.com/en-us/windows/win32/api/windows.graphics.capture.interop/nf-windows-graphics-capture-interop-igraphicscaptureiteminterop-createforwindow)
- **S09** - [CreateFreeThreaded](https://learn.microsoft.com/en-us/uwp/api/windows.graphics.capture.direct3d11captureframepool.createfreethreaded?view=winrt-26100)
- **S10** - [UI Automation threading](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-threading)
- **S11** - [AllowSetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-allowsetforegroundwindow)
- **S12** - [SetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow)
- **S13** - [LowLevelKeyboardProc](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelkeyboardproc)
- **S14** - [SetWinEventHook](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook)
- **S15** - [PrintWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-printwindow)
- **S16** - [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
- **S17** - [D3D11_MAPPED_SUBRESOURCE; RowPitch](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/ns-d3d11-d3d11_mapped_subresource)
- **S18** - [CoInitializeEx](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coinitializeex)
- **S19** - [GetClipboardSequenceNumber](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getclipboardsequencenumber)
- **S20** - [Delayed clipboard rendering](https://devblogs.microsoft.com/oldnewthing/20220609-00/?p=106731)
- **S21** - [Screen capture / HDR](https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture)
- **S22** - [D3D11CreateDevice](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/nf-d3d11-d3d11createdevice)
- **S23** - [RoInitialize](https://learn.microsoft.com/en-us/windows/win32/api/roapi/nf-roapi-roinitialize)
- **S24** - [RoGetActivationFactory](https://learn.microsoft.com/en-us/windows/win32/api/roapi/nf-roapi-rogetactivationfactory)
- **S25** - [Microsoft windows-rs generated WGC projection](https://raw.githubusercontent.com/microsoft/windows-rs/master/crates/libs/windows/src/Windows/Graphics/Capture/mod.rs)
