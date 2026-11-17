# DeepSeek Harness (DSH): explicit CLI use

V3 recognizes the values `context --harness dsh` and `receipt --harness dsh`. This support
does not mean a client-specific automatic hook, a session bridge or live context delivery.
It does not need DSH's internal API or a Node dependency.

Call the installed CLI explicitly:

```sh
python3 "<vault>/beyin.py" --vault "<vault>" context "<question>" --harness dsh --project <project>
python3 "<vault>/beyin.py" --vault "<vault>" receipt --harness dsh --event-id "<unique>" --summary "<summary>" --ref "<note path>"
```

On Windows you can use `py -3` instead of `python3`. The same source, privacy and project
filters apply; there is no new automatic note transfer.

## Receipt and rollback compatibility

DSH receipts are written as `harness: manual` + `client: dsh`. The new version reads
them as `dsh`; older readers such as 3.12.0 see `manual` instead of receiving the new
`harness` value they do not support. The client preference is not saved into
`.beyin-preferences.json`. When you roll back to an older version, DSH receipts are
kept; the `--harness dsh` option is not expected to exist in the older CLI.

## Verification limit

On the installed package, the CLI, receipt repeats, re-sync and source filters are
verified with synthetic vault tests. The live DSH client, instruction/skill discovery and
hook delivery are not part of this support. The optional session bridge and session
browser in #673 are not included in this narrow change; they need a separate security
and lifecycle review. [Real client checks](LIVE-CLIENTS.md).
