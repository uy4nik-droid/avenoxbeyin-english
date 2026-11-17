---
name: gecmis-import
description: Converts old chat history (ChatGPT, Claude, Gemini Takeout exports) into the brain vault's daily log format and writes it under daily/. Triggers - "import chat history", "import my history", "takeout", "ChatGPT history", "load my old chats into the brain", "geçmiş import", "geçmişimi aktar", "ChatGPT geçmişi", "eski sohbetlerimi beyne yükle". Do not use - saving a single note or searching the vault (beyin), health check (beyin-doktor).
---

# History Import

Feeds an old chat archive into the brain's normal pipeline. The export file is read locally,
the chats are split by month and written to `daily/import-YYYY-MM-part-NNN.md` files.
The evening compiler reads the content of these files like normal daily logs and sends it to
Claude through the user's own Claude subscription for summarisation. The export file
itself is not uploaded and the data is not sent anywhere else.

Private or sensitive chats are included in the import and in the later compilation unless the
user excludes them with a date or keyword filter.

## Mandatory approval gate

The agent MUST complete the steps below in order. Opening the export file, parsing it or
writing files under `daily/` without the user's permission is FORBIDDEN.

1. The agent MUST explain the data flow clearly: the export is read locally, the selected chats
   are written to local `daily/` files, and the evening compiler sends the content of these files to
   Claude through the user's own Claude subscription for summarisation. Nothing is uploaded or
   sent anywhere else.
2. The agent MUST say that private and sensitive chats are included by default.
   It MUST offer the user a start and end date limit and an exclusion list made of one or more
   keywords. Matching is case-insensitive and the whole matching
   conversation is skipped.
3. The agent MUST ask the user for the path of the export file and take the path only as text.
   It may not guess the path or open the file yet. It MUST then ask for explicit permission for a
   local, read-only preview scan only and wait for the answer. Without explicit permission it may not
   open the file. If permission is given, it runs the script with `--preview` and the chosen filters. This mode
   writes no output files.
4. The agent MUST show the user the number of chats to be imported from the preview, the date range,
   and the counts that will be skipped for date, keyword, empty content or invalid record reasons.
5. The agent MUST also tell the user the honest ways to back out: they can choose never to compile
   the imported files, or they can delete a monthly part file they do not want before the evening
   compilation. If the user backs out, the process stops.
6. The agent MUST restate the chosen date range and keyword list and ask for this explicit
   approval: `Yes, import with this preview and these filters.` Unless the user explicitly says yes,
   the import and writing may not start. An ambiguous answer does not count as approval.

This approval instruction is for the agent. Do not add automatic approval, interactive approval or a
flag that skips approval to the script.

## Steps

1. Complete the approval gate and use the export path you got from the user. Do not guess.
2. Verify the file type.
   - ChatGPT: `conversations.json` inside the export zip. If the zip has not been extracted, ask the user to
     extract it or use `unzip` locally with explicit permission.
   - Claude: `conversations.json` inside the export.
   - Gemini: `My Activity/Gemini Apps/MyActivity.json` inside Google Takeout.
3. Measure the file size with `wc -c < <path>`. If it is over 50 MB, the script applies the last 12 calendar months
   as an automatic limit. Say this in the preview. If the user has a narrower date limit,
   the narrower limit applies.
4. Write the matching script below to a temporary path such as `.claude/scripts/.state/import-chatgpt.py`.
   Run it with `--preview` first. After the second explicit approval, run it with the same filters without
   `--preview`.
5. Use a separate `--exclude-keyword` for each keyword. Dates are inclusive days.

```text
python3 .claude/scripts/.state/import-chatgpt.py conversations.json \
  --preview --start 2025-01-01 --end 2025-12-31 \
  --exclude-keyword "health" --exclude-keyword "private project"
```

6. Relay the script's summary output to the user verbatim. If a target file already exists, the script refuses to
   overwrite it. In that case ask the user to explicitly choose a new output folder or to deal with the existing
   files themselves. Do not delete, merge or overwrite the file.
7. Explain the compilation plan according to the `What happens next` section below.

## ChatGPT script

In a ChatGPT export each chat is a `mapping` tree. If there is branching, all reachable
nodes are written once in source order. System and tool messages are not written to the daily file.
Message and conversation texts are not truncated. When the monthly limit is reached, conversations move to a new
part file instead of being dropped. If a single conversation is larger than the limit, that part may exceed
the limit so that no content is lost.

```python
#!/usr/bin/env python3
"""Convert a ChatGPT conversations.json archive into local daily part files."""

import argparse
import datetime as dt
import json
import os
import sys

MAX_EXPORT_BYTES = 50 * 1024 * 1024
RECENT_MONTHS = 12
MAX_FILE_CHARS = 200000


def iso_date(value):
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be YYYY-MM-DD: %s" % value) from exc


def arguments():
    parser = argparse.ArgumentParser(description="Import ChatGPT history locally")
    parser.add_argument("source", help="conversations.json file or the folder containing it")
    parser.add_argument("--preview", action="store_true", help="preview only, do not write files")
    parser.add_argument("--start", type=iso_date, help="inclusive start date, YYYY-MM-DD")
    parser.add_argument("--end", type=iso_date, help="inclusive end date, YYYY-MM-DD")
    parser.add_argument(
        "--exclude-keyword",
        action="append",
        default=[],
        help="skip matching chats, can be used more than once",
    )
    parser.add_argument("--out-dir", default="daily", help="output folder, default daily")
    args = parser.parse_args()
    if args.start and args.end and args.start > args.end:
        parser.error("start date cannot be after end date")
    return args


def load_export(path):
    if os.path.isdir(path):
        path = os.path.join(path, "conversations.json")
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        data = data.get("conversations", [])
    if not isinstance(data, list):
        raise ValueError("export is not a list of chats")
    return path, data


def content_parts(message):
    if not isinstance(message, dict):
        return []
    content = message.get("content") or {}
    if content.get("content_type") not in ("text", "multimodal_text", None):
        return []
    texts = []
    for part in content.get("parts") or []:
        if isinstance(part, str) and part.strip():
            texts.append(part)
        elif isinstance(part, dict) and isinstance(part.get("text"), str):
            if part["text"].strip():
                texts.append(part["text"])
    return texts


def message_text(message):
    if not isinstance(message, dict):
        return None, None
    role = (message.get("author") or {}).get("role")
    if role not in ("user", "assistant"):
        return None, None
    metadata = message.get("metadata") or {}
    if metadata.get("is_visually_hidden_from_conversation"):
        return None, None
    parts = content_parts(message)
    if not parts:
        return None, None
    return role, "\n".join(parts)


def walk_nodes(mapping):
    roots = [
        node_id
        for node_id, node in mapping.items()
        if isinstance(node, dict) and not node.get("parent")
    ]
    seeds = roots + [node_id for node_id in mapping if node_id not in roots]
    seen = set()
    for seed in seeds:
        stack = [seed]
        while stack:
            node_id = stack.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            node = mapping.get(node_id)
            if not isinstance(node, dict):
                continue
            yield node
            children = node.get("children") or []
            for child in reversed(children):
                stack.append(child)


def conversation_turns(mapping):
    turns = []
    for node in walk_nodes(mapping):
        role, text = message_text(node.get("message"))
        if role:
            turns.append((role, text))
    return turns


def conversation_time(conversation, mapping):
    stamp = conversation.get("create_time") or conversation.get("update_time")
    if isinstance(stamp, (int, float)) and stamp > 0:
        return float(stamp)
    for node in walk_nodes(mapping):
        message = node.get("message") or {}
        stamp = message.get("create_time")
        if isinstance(stamp, (int, float)) and stamp > 0:
            return float(stamp)
    return None


def searchable_text(conversation, mapping):
    values = [str(conversation.get("title") or "")]
    for node in walk_nodes(mapping):
        values.extend(content_parts(node.get("message")))
    return "\n".join(values).casefold()


def recent_cutoff(today):
    month_number = today.year * 12 + today.month - 1 - (RECENT_MONTHS - 1)
    year, month_index = divmod(month_number, 12)
    return dt.date(year, month_index + 1, 1)


def select_conversations(conversations, size, start, end, keywords):
    stats = {
        "source": len(conversations),
        "invalid": 0,
        "date": 0,
        "keyword": 0,
        "empty": 0,
    }
    automatic_start = None
    if size > MAX_EXPORT_BYTES:
        automatic_start = recent_cutoff(dt.datetime.now(dt.timezone.utc).date())
    effective_start = start
    if automatic_start and (effective_start is None or automatic_start > effective_start):
        effective_start = automatic_start
    folded_keywords = [word.casefold() for word in keywords if word.strip()]
    selected = []
    for conversation in conversations:
        if not isinstance(conversation, dict):
            stats["invalid"] += 1
            continue
        mapping = conversation.get("mapping") or {}
        if not isinstance(mapping, dict):
            stats["invalid"] += 1
            continue
        stamp = conversation_time(conversation, mapping)
        if stamp is None:
            stats["invalid"] += 1
            continue
        moment = dt.datetime.fromtimestamp(stamp, dt.timezone.utc)
        day = moment.date()
        if (effective_start and day < effective_start) or (end and day > end):
            stats["date"] += 1
            continue
        haystack = searchable_text(conversation, mapping)
        if any(word in haystack for word in folded_keywords):
            stats["keyword"] += 1
            continue
        turns = conversation_turns(mapping)
        if not turns:
            stats["empty"] += 1
            continue
        selected.append(
            {
                "title": str(conversation.get("title") or "untitled"),
                "moment": moment,
                "turns": turns,
            }
        )
    selected.sort(key=lambda item: item["moment"])
    return selected, stats, automatic_start, effective_start


def conversation_block(record):
    moment = record["moment"]
    title = record["title"].replace("\r", " ").replace("\n", " ").strip()
    heading = "### Session (%s UTC) ChatGPT: %s\n\n" % (
        moment.strftime("%Y-%m-%d %H:%M"),
        title or "untitled",
    )
    lines = []
    for role, text in record["turns"]:
        label = "**User:**" if role == "user" else "**Assistant:**"
        lines.append("%s %s\n" % (label, text))
    return heading + "\n".join(lines)


def part_header(month, part_number):
    return (
        "# Daily Log: %s (import, part %03d)\n\n"
        "Source: ChatGPT export. This file was written by a machine.\n\n"
        "## Sessions\n\n" % (month, part_number)
    )


def build_parts(selected, out_dir):
    months = {}
    for record in selected:
        month = record["moment"].strftime("%Y-%m")
        months.setdefault(month, []).append(conversation_block(record))
    plans = []
    for month in sorted(months):
        part_number = 1
        header = part_header(month, part_number)
        blocks = []
        total = len(header)
        for block in months[month]:
            separator = "" if not blocks else "\n"
            if blocks and total + len(separator) + len(block) > MAX_FILE_CHARS:
                text = header + "\n".join(blocks)
                name = "import-%s-part-%03d.md" % (month, part_number)
                plans.append((os.path.join(out_dir, name), text, len(blocks)))
                part_number += 1
                header = part_header(month, part_number)
                blocks = []
                total = len(header)
                separator = ""
            blocks.append(block)
            total += len(separator) + len(block)
        if blocks:
            text = header + "\n".join(blocks)
            name = "import-%s-part-%03d.md" % (month, part_number)
            plans.append((os.path.join(out_dir, name), text, len(blocks)))
    return plans


def write_exclusive(plans):
    claimed = []
    try:
        for path, text, count in plans:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            claimed.append([path, descriptor, text, count])
    except OSError:
        for path, descriptor, _text, _count in claimed:
            os.close(descriptor)
            os.unlink(path)
        raise
    try:
        for item in claimed:
            with os.fdopen(item[1], "w", encoding="utf-8", newline="\n") as handle:
                handle.write(item[2])
            item[1] = None
    except OSError:
        for path, descriptor, _text, _count in claimed:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass
        raise


def print_selection(selected, stats, automatic_start, effective_start, preview):
    skipped = stats["invalid"] + stats["date"] + stats["keyword"] + stats["empty"]
    print("PREVIEW" if preview else "IMPORT")
    print("source chats: %d" % stats["source"])
    print("chats to write: %d" % len(selected))
    if selected:
        print(
            "date range: %s .. %s"
            % (selected[0]["moment"].date(), selected[-1]["moment"].date())
        )
    else:
        print("date range: none")
    print(
        "skipped chats: %d (date: %d, keyword: %d, empty: %d, invalid: %d)"
        % (skipped, stats["date"], stats["keyword"], stats["empty"], stats["invalid"])
    )
    if automatic_start:
        print("50 MB limit: last 12 calendar months, automatic start %s" % automatic_start)
    if effective_start:
        print("effective start date: %s" % effective_start)


def main():
    args = arguments()
    try:
        path, conversations = load_export(args.source)
        size = os.path.getsize(path)
        selected, stats, automatic_start, effective_start = select_conversations(
            conversations, size, args.start, args.end, args.exclude_keyword
        )
        print_selection(selected, stats, automatic_start, effective_start, args.preview)
        if args.preview:
            print("no files written")
            return 0
        plans = build_parts(selected, args.out_dir)
        if not plans:
            print("files written: 0")
            return 0
        os.makedirs(args.out_dir, exist_ok=True)
        try:
            write_exclusive(plans)
        except FileExistsError as exc:
            print(
                "ERROR: existing import file was not overwritten: %s" % exc.filename,
                file=sys.stderr,
            )
            return 3
        print("files written: %d" % len(plans))
        print("chats written: %d, chats skipped: %d" % (
            sum(count for _path, _text, count in plans),
            stats["invalid"] + stats["date"] + stats["keyword"] + stats["empty"],
        ))
        for output, text, count in plans:
            print("  %s  %d chats  %d characters" % (output, count, len(text)))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
```

## Claude script

The Claude export schema is flat. Use the same approval gate, `--preview`, date and keyword
filters, lossless part generation and `write_exclusive` writing. Instead of the ChatGPT-specific
`conversation_turns`, call the parser below. Do not write system records.

```python
def claude_turns(conversation):
    turns = []
    for message in conversation.get("chat_messages") or []:
        role = {"human": "user", "assistant": "assistant"}.get(message.get("sender"))
        if not role:
            continue
        texts = []
        for block in message.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    texts.append(text)
        fallback = message.get("text")
        if not texts and isinstance(fallback, str) and fallback.strip():
            texts.append(fallback)
        if texts:
            turns.append((role, "\n".join(texts)))
    return turns
```

Resolve the timestamp with the stdlib only, like this:

```python
created = str(conversation.get("created_at") or "")
moment = dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
if moment.tzinfo is None:
    moment = moment.replace(tzinfo=dt.timezone.utc)
stamp = moment.timestamp()
```

## Gemini Takeout

The Takeout archive has a `My Activity/Gemini Apps/` folder. If JSON was chosen,
`MyActivity.json` is a list of records. This format does not preserve chat integrity; each record is a single
prompt. Write the Gemini import like a prompt log: gather the records of the same day into a single
`### Session (YYYY-MM-DD) Gemini` block and make each record a `**User:**` line. The same approval,
preview, filter, part and collision rules apply. If the Takeout is HTML, ask the user to export again in
JSON format.

## What happens next

When the import is done, give the user an honest summary:

- Show the written and skipped chat counts separately. Relay the chat and character
  count of each part file from the script output.
- The `daily/import-*.md` files are local. The evening compiler sends their content to Claude through
  the user's own Claude subscription for summarisation. Nothing is sent anywhere else.
- The compiler runs one round each evening and processes the changed logs in each round. A large archive may be spread
  over several evenings.
- If the user does not want to wait, first `python3 .claude/scripts/compile.py --dry-run`, then with their explicit
  approval `python3 .claude/scripts/compile.py` can be run. Each round uses up part of the subscription
  limit.
- If the user does not want to send the content to Claude, they should not run the compiler and should delete the relevant monthly part
  files before the evening compilation.
- If an older archive was skipped because of the 50 MB limit, say so clearly and ask whether they want a
  second round with a separate date range.

As the last step, suggest running `beyin-doktor`. Progress can be followed from the compile status line.
