# README images

## cover.png

A conceptual cover produced specially for Second Brain. It is not a real product screen.
It was generated with the OpenAI imagegen tool on 12 November 2026; the original PNG was used.

The generation prompt is kept in [cover-prompt.txt](cover-prompt.txt). The cover contains no version
number or test result; it does not need to be regenerated when the version is updated.

## web-tasks.png

The Tasks screen of the real local web interface of V3.13.0. A sample vault created for the README,
five notes, eight tasks and five work results were used. There is no personal data.

After the package was installed, the records were created with the installed `note-create`, `task-create` and `receipt`
commands. The interface, opened with `web ac --read-only --no-browser`, was captured in a fresh
headless Chromium session at 1660 × 850. The product HTML/CSS and the
screenshot were not modified. The local server was closed at the end of the capture.

This image does not prove automatic agent/hook delivery; it shows the interface with sample data.
