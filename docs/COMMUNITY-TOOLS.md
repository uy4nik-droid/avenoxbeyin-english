# Community tools

The tools on this page are third-party community tools; they are built and maintained by their owners. The avenoxbeyin project
does not support them, does not audit them for security and does not verify their behavior. Being listed is not an endorsement or
a recommendation. Review them yourself before installing.

Inclusion criteria: the tool reads the vault according to the [Markdown contract](v3/MARKDOWN.md), does not
assume that particular folders exist, and shows how to verify its claims in its own repository.

## Beyin (macOS)

[yigit2015/beyin-mac](https://github.com/yigit2015/beyin-mac) · MIT · macOS 26+ · third-party, not audited

A read-only app that shows the vault as a network, a globe and an overview. It does not contain or run avenoxbeyin code.

- It follows [MARKDOWN.md](v3/MARKDOWN.md) for the reading rules; what it reads and what it skips:
  [docs/UYUMLULUK.md](https://github.com/yigit2015/beyin-mac/blob/main/docs/UYUMLULUK.md).
- It is said not to write to the vault and not to go onto the network. These claims have not been independently audited; you can
  check them yourself with
  [`Scripts/verify_offline.sh`](https://github.com/yigit2015/beyin-mac/blob/main/Scripts/verify_offline.sh).
- The tool's README states that the app does not use the App Sandbox (macOS does not restrict its network access) and that the distributed
  build is not approved by Apple (not notarized); check the current status there.
- The folder contract is being discussed in [#478](https://github.com/avenoxai/avenoxbeyin/issues/478); if the contract changes,
  keeping up with it is the responsibility of the tool's owner.
- For problems: [beyin-mac issues](https://github.com/yigit2015/beyin-mac/issues).
