#!/usr/bin/env python3
"""Vault-local entry point; configuration contains no credentials."""
import importlib.util
import json
from pathlib import Path
import sys
import unicodedata
sys.dont_write_bytecode = True



JEV_MODES = {'off': 'off', 'shadow': 'shadow', 'on': 'on'}


def jev_mode(mode, provider):
    """Laya is shadow-only: a saved or hand-edited `on` still runs as shadow."""
    if provider == 'laya' and mode in ('shadow', 'on'):
        return 'shadow (only)'
    return JEV_MODES.get(mode, 'unknown')


def update_lines(result):
    status = result.get('status', 'unknown')
    if status == 'available':
        command = 'py -3' if sys.platform == 'win32' else 'python3'
        lines = ['New version: ' + result['version'],
                 'Release notes: ' + result['release_url'],
                 'Update: ' + command + ' beyin.py update']
    else:
        messages = {'disabled': 'Release notifications are off.', 'unknown': 'No release check has run yet.',
                'unavailable': 'The release check failed; whether Beyin is up to date is unverified.',
                'up_to_date': 'Beyin is up to date: ' + str(result.get('current_version', '?')),
                'ahead': 'The installed version is ahead of the official stable release.'}
        lines = [messages.get(status, 'Release information unavailable.')]
    if result.get('checked_at'):
        from datetime import datetime, timezone
        lines.append('Last check: ' + datetime.fromtimestamp(result['checked_at'], timezone.utc).isoformat())
    return lines


def jev_lines(result):
    """Shared by the jev command and the doctor summary; reads only reported fields."""
    lines = []
    laya = result.get('provider') == 'laya'
    if result.get('automatic_model_calls'):
        lines.append('Automatic context is on: every turn sends the prompt plus the title and'
                     ' first 600 characters of up to 8 candidate internal/public notes ' + ('to the local Laya server' if laya else 'to the provider') +
                     '. Private notes are not sent.')
        if result.get('context_mode_notice'):
            lines.append("Warning: automatic context works only with 'context_mode: turn'; the current setting is '" +
                         ascii_text(result.get('context_mode', '?')) + "' (to enable: beyin.py preferences --context-mode turn).")
        if laya and not result.get('auto_context_applied'):
            lines.append('Laya runs in shadow mode only: automatic context scores are only logged and do not change the context.')
    if laya:
        if result.get('mode_refused') == 'laya_shadow_only':
            lines.append('jev.json asks for on mode, but Laya runs in shadow mode only; results do not change.'
                         ' For on mode: jev on --provider typesafe.')
        if result.get('mode', 'off') != 'off':
            lines.append('Local Laya server: ' + ascii_text(result.get('laya', {}).get('base_url')) +
                         '; start it with LAYA_HOST=127.0.0.1. Scores are logged for measurement and do not change results.')
    elif result.get('mode', 'off') != 'off' and not result.get('key_present'):
        lines.append('TYPESAFE_API_KEY is not set: calls fall back to local results.')
    server = result.get('server')
    if isinstance(server, dict) and server.get('checked'):
        if server.get('reachable') and server.get('pinned_model_loaded'):
            lines.append('Laya server ready (' + ascii_text(server.get('device')) + ').')
        elif server.get('reachable'):
            lines.append('The Laya server responds, but the pinned model is not loaded.')
        else:
            lines.append('Laya server unreachable: calls fall back to local results.')
    elif isinstance(server, dict) and server.get('reason') == 'not_applicable':
        lines.append('--check probes the server only for the laya provider.')
    return lines


def ascii_text(value):
    """Human lines stay ASCII even if a field ever carries something else."""
    return str(value if value is not None else '?').encode('ascii', 'replace').decode('ascii')


# Bidirectional overrides can reorder what a terminal shows (Trojan Source); category Cc covers ESC/BEL.
_BIDI_CONTROLS = frozenset('\u061c\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069')


def plain_text(value):
    """One terminal line from stored text: newlines fold, control and bidi characters become '?'."""
    text = str(value if value is not None else '?').replace('\r\n', '\n')
    return ''.join(' / ' if ch in '\n\r\u2028\u2029\x85' else ' ' if ch == '\t' else
                   '?' if unicodedata.category(ch) == 'Cc' or ch in _BIDI_CONTROLS else ch for ch in text)


def state_location_lines(location):
    """Doctor lines for the state_location warnings (#113); information only, never a status."""
    if not isinstance(location, dict):
        return []
    codes = {str(warning).split(':', 1)[0] for warning in location.get('warnings') or []}
    prefix = 'State location (info): '
    lines = []
    if 'state_split' in codes:
        lines.append(prefix + 'this vault has installed state on both sides of the package redirection (' +
                     ', '.join(plain_text(root) for root in location.get('sibling_state_roots') or []) +
                     '). Which half a session reads depends on whether it runs inside the package;'
                     ' pick the current one and move it: https://github.com/uy4nik-droid/avenoxbeyin-english/blob/main/docs/v3/UPDATE.md')
    if 'pinned_in_package_container' in codes:
        lines.append(prefix + 'the pinned state root is inside the MSIX package container (Packages\\...\\LocalCache);'
                     ' if the package is reset or installed under another identity, this path is lost. Moving it: https://github.com/uy4nik-droid/avenoxbeyin-english/blob/main/docs/v3/UPDATE.md')
    if 'pin_resolves_elsewhere' in codes:
        lines.append(prefix + 'the pinned path resolves to a different directory in this process (' +
                     plain_text(location.get('pinned_resolves_here_to')) +
                     '). Run doctor inside and outside the package and compare.')
    if 'pinned_state_not_absolute' in codes:
        lines.append(prefix + 'the state path in .beyin-runtime.json is not an absolute path on this machine; it may have been'
                     ' synced from another operating system. beyin.py is using the default state directory'
                     ' of this machine. Installation files are machine-specific; syncing: https://github.com/uy4nik-droid/avenoxbeyin-english/blob/main/docs/v3/MULTI-MACHINE.md')
    if 'pinned_state_empty' in codes:
        lines.append(prefix + 'no installation was found in the pinned state root. If the state was moved, rerun the installer'
                     ' with the new --state.')
    if 'effective_state_differs' in codes:
        lines.append(prefix + 'this run reads a different state directory instead of the pinned root.')
    return lines


def receipt_line_endings_lines(report):
    """Doctor line for the receipt line-ending warning (#205); information only, never a status."""
    if isinstance(report, dict) and report.get('status') == 'warning':
        return ['Receipt line endings (info): core.autocrlf=true and receipts/ is not pinned; a receipt from another machine'
                ' can be checked out with CRLF and make the same receipt report "event id collision".'
                ' Add "receipts/** -text" to .gitattributes: https://github.com/uy4nik-droid/avenoxbeyin-english/blob/main/docs/v3/MULTI-MACHINE.md']
    return []


def sync_copy_lines(result):
    """Sync lines for file-sync copies (#205): a stamped copy is out of the index, a numbered one is only listed."""
    lines = []
    stamped = [w for w in result.get('warnings') or [] if isinstance(w, dict) and str(w.get('reason', '')).startswith('file sync')]
    for warning in stamped:
        lines.append('Sync conflict copy left out of the index: ' + plain_text(warning.get('source')) +
                     '. Compare it with the original note, keep the correct version, delete the other.')
    for candidate in result.get('sync_copy_candidates') or []:
        same = candidate.get('same_content')
        lines.append('Possible sync copy: ' + plain_text(candidate.get('source')) + ' / ' + plain_text(candidate.get('original')) +
                     {True: ' (same content)', False: ' (different content)'}.get(same, '') +
                     '. Both are indexed; if it is a real note, rename it; if it is a copy, delete one of them.')
    extra = (result.get('sync_copy_candidate_count') or 0) - len(result.get('sync_copy_candidates') or [])
    if extra > 0:
        lines.append('+' + str(extra) + ' more possible copies; see --json for details.')
    return lines


def supersedes_lines(issues, count):
    """Present existing sync/doctor findings only; do not guess or remember a target."""
    issues = issues or []
    count = max(count or 0, len(issues))
    if not count:
        return []

    def field(value):
        text = plain_text(value)
        return text[:157] + '...' if len(text) > 160 else text

    reasons = {'ambiguous supersedes reference': 'matches more than one note',
               'unresolved supersedes reference': 'target not found',
               'supersedes reference points to the note itself': 'points to the note itself',
               'supersedes reference is part of a cycle': 'part of a cycle'}
    lines = ['Supersedes warning: ' + str(count) + ' references currently retire no note; '
             'notes retired earlier can enter the context again.']
    for issue in issues[:3]:
        reason = issue.get('reason')
        lines.append('  - ' + field(issue.get('source')) + ' -> ' + field(issue.get('value')) +
                     ' (' + field(reasons.get(reason, reason)) + ')')
    if count > min(3, len(issues)):
        lines.append('+' + str(count - min(3, len(issues))) + ' more references.')
    lines.append('Check the target and direction; name the right note by explicit id or full vault path. Details: --json.')
    return lines


def index_exclusion_lines(report, pruned=False):
    """Lines for the user's index exclusions (state/index.json); shared by doctor, sync and preferences."""
    if not isinstance(report, dict):
        return []
    if report.get('status') == 'unavailable':
        return ['Index scope could not be checked (' + plain_text(report.get('error', 'unknown')) +
                '); index exclusion settings and folder hints could not be verified.']
    lines = []
    if report.get('excluded_dirs'):
        lines.append('Folder names excluded from the index (your list, at any depth): ' +
                     ', '.join(plain_text(name) for name in report['excluded_dirs']) +
                     (' (' + str(report.get('pruned', 0)) + ' folders skipped in this scan)' if pruned else '') + '.')
    if report.get('error'):
        lines.append('index.json is invalid (' + plain_text(report['error']) +
                     '); the folder exclusion list is not applied, everything is indexed.')
    return lines


def megabytes(value):
    return '%.1f' % ((value or 0) / 1048576)


def rewrite_note(entry):
    """#168: the rewrite instruction, said only once the full text is safe in the archive."""
    if entry.get('backup') in ('written', 'exists'):
        return ' (full text backed up to the archive: ' + str(entry.get('archive')) + '); rewrite the file within the limit.'
    if entry.get('backup') == 'planned':
        return '; first run without --dry-run so the full text is backed up to the archive; then rewrite the file within the limit.'
    return '; rewrite the file within the limit.'


def human_result(result, command, installed_version=None):
    status = result.get('status', '')
    if command == 'scheduled-check' and 'status' in result:
        # Exit 4 (needs attention) prints here like a finished check: the check ran and found something.
        texts = {'ok': 'Scheduled check: healthy.',
                 'needs_attention': 'Scheduled check: there is a problem that needs attention; see beyin.py doctor for details.',
                 'already_running': 'Scheduled check: another check is still running; this run was skipped.',
                 'error': 'Scheduled check could not finish (' + ascii_text(result.get('error')) + '); check with beyin.py doctor.'}
        lines = [texts.get(status, 'Scheduled check: ' + ascii_text(status))]
        notification = {'shown': 'Notification sent.',
                        'failed': 'Notification could not be sent.',
                        'unavailable': 'No notification tool on this machine.'}
        if result.get('notification') in notification:
            lines.append(notification[result['notification']])
        if status == 'needs_attention' and result.get('session_notice_pending') is True:
            lines.append('It will also be reported in one line when the next agent session opens.')
        return '\n'.join(lines)
    if result.get('error'):
        return ('Operation failed: ' + str(result.get('message', result['error'])) +
                ('\n' + ascii_text(result['hint']) if result.get('hint') else ''))
    if command == 'hook-reconcile':
        status = result.get('status')
        if status in ('ok', 'noop'):
            return 'Hook paths are already current; no file was changed.'
        if status == 'not_installed':
            return 'No installed hook file found in this vault.'
        lines = ['Hook reconciliation finished: ' + str(len(result.get('files', []))) + ' files updated (' +
                 str(result.get('reconciled_count', 0)) + ' hook commands adapted to this machine).']
        for entry in result.get('files', []):
            lines.append('- ' + entry['file'] + ' (backup: ' + entry.get('backup', '') + ', ' +
                         str(entry.get('reconciled', 0)) + ' hooks renewed)')
            for change in entry.get('changes', []):
                lines.append('  * ' + change['event'] + ':')
                lines.append('    Old: ' + plain_text(change.get('old_summary', change.get('old_command', ''))[:80]))
                lines.append('    New: ' + plain_text(change.get('new_summary', change.get('new_command', ''))[:80]))
        lines.append('Old commands were replaced with the Python and vault paths of this machine.')
        return '\n'.join(lines)
    if command == 'triage':
        try:
            from beyin_v3_triage import format_human
            return format_human(result)
        except Exception:
            return json.dumps(result, ensure_ascii=False, indent=2)
    if command == 'audit':
        try:
            from beyin_v3_audit import format_audit_human
            return format_audit_human(result)
        except Exception:
            return json.dumps(result, ensure_ascii=False, indent=2)
    if command == 'jev':
        features = result.get('features', {})
        provider = result.get('provider')
        lines = ['Jev: ' + jev_mode(result.get('mode'), provider) +
                 (' (saved: ' + jev_mode(result.get('saved_mode'), provider) + ')'
                  if result.get('kill_switch') else ''),
                 'Features: ' + (', '.join(name + ' ' + ('on' if value else 'off')
                                             for name, value in features.items()) or 'none')]
        if result.get('provider') == 'laya':
            lines += ['Provider: laya (local, model ' + ascii_text(result.get('laya', {}).get('model')) + ')',
                      'Key: not needed' + (' (LAYA_API_KEY is set)' if result.get('key_present') else '')]
        else:
            lines.append('Key: ' + ('set' if result.get('key_present') else 'not set'))
        lines += ['Kill switch: ' + ('on' if result.get('kill_switch') else 'off'),
                  'Last 24 hours: ' + str(result.get('last_24h', {}).get('calls', 0)) + ' calls']
        if not result.get('config_valid', True):
            lines.append('The settings file is corrupt; jev.json must be fixed by hand.')
        return '\n'.join(lines + jev_lines(result))
    if command == 'preferences':
        prefs = result['preferences']
        lines = ['Automatic check: ' + ('on' if prefs['auto_sync'] else 'off'),
                 'Check interval: ' + str(prefs['interval_minutes']) + ' minutes (0 = every event)',
                 'Automatic context: ' + prefs['context_mode'],
                 'Context limit: ' + str(prefs['context_chars']) + ' characters',
                 'Secret filter: ' + ('on' if prefs['secret_filter'] else 'off'),
                 'Release notifications: ' + ('on' if result.get('update_notifications', {}).get('effective') else 'off'),
                 'Project session-start context: ' + ('on' if result.get('project_context') == 'on' else 'off')]
        if result.get('daily_layout') in ('flat', 'v3'):
            layout = result['daily_layout']
            lines.append('Daily layout: ' + layout + ' (' +
                         ('daily/YYYY-MM-DD.md' if layout == 'flat' else 'daily/v3/YYYY-MM-DD.md') + ')')
        opening = (result.get('companion_context') or {}).get('context_chars')
        if opening is not None:
            lines.append('Session-start memory context: ' + (str(opening) + ' characters' if opening else 'up to the context limit'))
        if result.get('companion_context_notice'):
            lines.append(result['companion_context_notice'])
        for name, value in (result.get('companion_limits') or {}).items():
            lines.append('Memory file limit, ' + name + ': ' + (str(value) + ' characters' if value else 'off'))
        hygiene = result.get('hygiene') or {}
        if hygiene:
            lines.append('Hygiene signals (off by default): word cap warning ' +
                         ('on (' + str(hygiene.get('max_words')) + ' words)' if hygiene.get('word_cap_warning') else 'off') +
                         ', folder questions ' + ('on' if hygiene.get('folder_questions') else 'off') +
                         ', promotion report ' + ('on' if hygiene.get('promotion') else 'off'))
        if result.get('hygiene_notice'):
            lines.append(result['hygiene_notice'])
        inbox = result.get('inbox_report') or {}
        if inbox:
            lines.append('Inbox report (off by default): ' +
                         ('on (' + str(inbox.get('max_items')) + ' notes / ' + str(inbox.get('max_days')) + ' days; ' +
                          ('folders: ' + ', '.join(plain_text(name) for name in inbox['folders'])
                           if inbox.get('folders') else 'recognized by folder name') + ')'
                          if inbox.get('enabled') else 'off'))
        if result.get('inbox_report_notice'):
            lines.append(result['inbox_report_notice'])
        if result.get('parallel_sessions'):
            lines.append('Parallel session notice: ' + ('on' if result['parallel_sessions'] == 'on' else 'off'))
        if result.get('parallel_sessions_notice'):
            lines.append(result['parallel_sessions_notice'])
        if result.get('context_dedupe'):
            lines.append('In-session repeat prevention: ' + ('on' if result['context_dedupe'] == 'on' else 'off'))
        if result.get('context_dedupe_notice'):
            lines.append(result['context_dedupe_notice'])
        hermes_p = result.get('hermes_platforms') or {}
        if hermes_p.get('attended') or hermes_p.get('unattended'):
            h_parts = []
            if hermes_p.get('attended'):
                h_parts.append('attended: ' + ', '.join(hermes_p['attended']))
            if hermes_p.get('unattended'):
                h_parts.append('unattended: ' + ', '.join(hermes_p['unattended']))
            lines.append('Hermes platform settings: ' + '; '.join(h_parts))
        if result.get('hermes_platforms_notice'):
            lines.append(result['hermes_platforms_notice'])
        if result.get('excluded_components'):
            lines.append('Excluded components: ' + ', '.join(result['excluded_components']))
        if result.get('exclusion_notice'):
            lines.append(result['exclusion_notice'])
        lines += index_exclusion_lines(result.get('index_exclusions'))
        if result.get('index_exclusions_notice') and not (result.get('index_exclusions') or {}).get('error'):
            lines.append(result['index_exclusions_notice'])
        lines.append('When on, GitHub release information is read at most once a day; notes are not sent.')
        lines.append('Local checks make no model calls. No scheduler is installed.')
        return '\n'.join(lines)
    if command == 'recap':
        # --since/--until select local calendar days (as daily/v3 is named); the --days window stays UTC.
        local = result.get('timezone') == 'local'
        lines = ['Sourced activity: ' + (result['from'] or 'no start limit') + ' - ' + result['through'] +
                 (' (local days; ' if local else ' (UTC; ') + 'agent records, not independently verified facts)']
        if not result['items']:
            lines.append('No dated records in this range.')
        for item in result['items']:
            lines.append('\n' + (item.get('day') or item['created_at'][:10]) + '  ' + plain_text(item['summary']))
            lines.append('Source: ' + plain_text(item['source']))
            for ref in item.get('refs', []):
                lines.append('  - ' + plain_text(ref))
            withheld = item.get('refs_withheld') or {}
            if withheld.get('private'):
                lines.append('  (' + str(withheld['private']) + ' private source links hidden)')
            if withheld.get('missing'):
                lines.append('  (' + str(withheld['missing']) + ' sources no longer exist)')
        if result['truncated']:
            lines.append('Showing only the newest ' + str(result['shown']) + '/' + str(result['total']) +
                         ' records; raise this with --limit.')
        if result['undated_omitted']:
            lines.append(str(result['undated_omitted']) + ' undated/old-format records skipped.')
        if result.get('missing_source_omitted'):
            lines.append(str(result['missing_source_omitted']) + ' records skipped: their receipt file no longer exists.')
        if result.get('partial') or result.get('source_sync', {}).get('status') == 'degraded':
            lines.append('Warning: source sync is partial; use --json for details.')
        if any(w.get('kind') == 'receipt_view' for w in result.get('source_sync', {}).get('warnings', [])):
            lines.append('Warning: a local edit to a receipt view was kept; to archive and regenerate it, use beyin.py sync --recover-views.')
        return '\n'.join(lines)
    if command == 'companion-compact':
        lines = []
        for name, entry in result.get('files', {}).items():
            if entry.get('status') in ('compacted', 'planned'):
                lines.append(name + ': ' + str(entry.get('chars')) + ' -> ' + str(entry.get('chars_after')) + ' characters' +
                             (' (planned)' if entry['status'] == 'planned' else '') + ', ' + str(entry.get('moved_chars')) +
                             ' characters ' + ('will move to the archive' if entry['status'] == 'planned' else 'moved to the archive') + '.')
                if not entry.get('within_limit_after'):
                    lines.append(name + ' is still above the limit (' + str(entry.get('limit')) + ')' + rewrite_note(entry))
            elif entry.get('status') == 'needs_rewrite':
                lines.append(name + ': no old dated entries to move' + rewrite_note(entry))
            elif entry.get('status') == 'conflict':
                lines.append(name + ': the file changed during the operation; nothing was moved, try again.')
            elif entry.get('status') == 'needs_attention':
                lines.append(name + ': ' + str(entry.get('reason', 'needs attention')) + '.')
            elif entry.get('status') in ('within_limit', 'limit_off'):
                lines.append(name + ': within the limit, no change.')
        if result.get('status') == 'needs_attention' and not result.get('files'):
            lines.append('The limit setting could not be read; nothing was moved.' if result.get('limits_file') == 'invalid'
                         else 'There is more than one companion folder; nothing was moved.')
        return '\n'.join(lines + ['No text was deleted; no model was called.'])
    if command == 'state-compact':
        if status == 'planned':
            return ('Old event records: ' + str(result.get('events_prunable', 0)) + ' (about ' +
                    megabytes(result.get('event_bytes_prunable', 0)) + ' MB), old temp files: ' +
                    str(result.get('stale_temp_files', 0)) + ', expired Jev cache: ' +
                    str(result.get('expired_jev_cache', 0)) + '. Nothing changed.')
        lines = ['Old event records deleted: ' + str(result.get('events_removed', 0)) + ', old temp files: ' +
                 str(result.get('temp_files_removed', 0)) + ', expired Jev cache: ' +
                 str(result.get('jev_cache_removed', 0)) + '.']
        if result.get('vacuum') == 'done':
            lines.append('Local index ' + megabytes(result.get('database_bytes_before', 0)) + ' MB -> ' +
                         megabytes(result.get('database_bytes_after', 0)) + ' MB.')
        elif result.get('vacuum') == 'busy':
            lines.append('The index is in use right now; VACUUM could not run. Try again when open sessions end.')
        else:
            lines.append('VACUUM did not finish: ' + ascii_text(result.get('vacuum')))
        return '\n'.join(lines + ['Vault files were not touched.'])
    if command == 'mutation-queue':
        if isinstance(result.get('enabled'), bool):
            return ('Offline mutation queue: ' + ('on' if result['enabled'] else 'off (to turn on: beyin.py mutation-queue --enable)') +
                    '; ' + str(result.get('pending_count', 0)) + ' pending, ' + str(result.get('conflict_count', 0)) +
                    ' conflicts, ' + str(result.get('failed_count', 0)) + ' failed.')
        if 'replayed' in result:
            text = ('Queue replayed: ' + str(result.get('applied', 0)) + ' applied, ' +
                    str(result.get('conflicts', 0)) + ' conflicts, ' + str(result.get('failed', 0)) + ' failed.')
            if result.get('source_sync', {}).get('status') in ('error', 'degraded', 'conflict'):
                text += ('\nSource sync needs attention; to diagnose it and refresh the index, '
                         'run beyin.py sync. Do not queue the applied records again.')
            return text
        if 'pruned' in result:
            return 'Removed ' + str(result['pruned']) + ' records from the queue; ' + str(result.get('remaining', 0)) + ' records remain.'
        if result.get('mutation_id'):
            return ('Queue record ' + plain_text(result['mutation_id']) + ': ' + plain_text(result.get('status', '')) +
                    (' (already queued)' if result.get('duplicate') else '') + '.')
    if command == 'doctor':
        labels = {'never_seen': 'No real client session observed yet.',
                  'observed_metadata': 'Session events are being observed.',
                  'pending': 'There is pending work.', 'needs_attention': 'There is a problem that needs attention.'}
        lines = ['Beyin ' + (installed_version or 'version unknown'), labels.get(status, 'Health check finished.'),
                 'Pending work: ' + str(result.get('pending_events', 0))]
        for name, details in result.get('lifecycle', {}).items():
            lines.append(name + ': ' + ('event seen' if details.get('status') == 'observed_metadata' else 'not verified yet'))
        jev = result.get('jev') or {}
        if jev.get('mode', 'off') == 'off':
            lines.append('Jev: off')
        else:
            lines.append('Jev: ' + jev_mode(jev['mode'], jev.get('provider')) +
                         (', provider: laya (' if jev.get('provider') == 'laya' else ' (') + 'automatic context: ' +
                         ('on' if jev.get('automatic_model_calls') else 'off') + '), last 24 hours ' +
                         str(jev.get('last_24h', {}).get('calls', 0)) + ' calls')
            if jev.get('context_mode_notice'):
                cm = ascii_text(jev.get('context_mode', (result.get('preferences') or {}).get('context_mode', '?')))
                lines.append("Jev automatic context works only with 'context_mode: turn'; currently in '" +
                             cm + "' mode. To enable: beyin.py preferences --context-mode turn")
        if result.get('secrets_redacted'):
            lines.append('Secret filter wrote ' + str(result['secrets_redacted']) + ' matches as [REDACTED].')
        cov = result.get('receipt_coverage')
        if isinstance(cov, dict) and cov.get('total', 0) > 0:
            ratio = cov.get('ratio')
            pct = int(round(ratio * 100)) if ratio is not None else 0
            d7 = cov.get('last_7d', {})
            d7_text = ''
            if d7.get('total', 0) > 0 and d7.get('ratio') is not None:
                d7_text = ', last 7 days: ' + str(int(round(d7['ratio'] * 100))) + '%'
            # A question-only session needs no receipt; name how many of the missing ones saw no edit (#212).
            unobserved = cov.get('missing_no_observed_edit')
            unobserved_text = ('; ' + str(unobserved) + ' of the missing sessions showed no edit'
                               if isinstance(unobserved, int) and unobserved > 0 else '')
            lines.append('Receipt coverage: ' + str(pct) + '% (' + str(cov['covered']) + '/' + str(cov['total']) + ' sessions' + d7_text + ')'
                         + unobserved_text)
        kf = result.get('knowledge_freshness')
        if isinstance(kf, dict) and kf.get('status') == 'unavailable':
            lines.append('Last knowledge distillation: not measurable (' + str(kf.get('error') or 'error') + ')')
        elif isinstance(kf, dict):
            if kf.get('last_distilled_at') is not None:
                days = kf.get('days_ago', 0)
                time_text = 'today' if days == 0 else ('1 day ago' if days == 1 else str(days) + ' days ago')
                lines.append('Last knowledge distillation: ' + time_text + ' (' + str(kf.get('receipts_since', 0)) + ' receipts since then)')
            else:
                lines.append('Last knowledge distillation: no concept note distilled yet (' + str(kf.get('receipts_since', 0)) + ' receipts in total)')
        scheduled = result.get('scheduled_check') or {}
        if scheduled.get('status') in ('ok', 'needs_attention', 'error'):
            lines.append('Scheduled check (info): last run ' + str(scheduled.get('age_hours', '?')) + ' hours ago, ' +
                         {'ok': 'healthy', 'needs_attention': 'needs attention', 'error': 'check did not finish'}[scheduled['status']] + '.')
        for conflict in result.get('instruction_conflicts', []):
            lines.append('Instruction conflict: ' + conflict['file'] + ' contains a V2 compiler statement ("' + conflict.get('snippet', '') + '"). This text conflicts with V3 agent distillation; remove the old compiler instructions.')
        if result.get('receipt_view_conflicts'):
            lines.append('Receipt view conflict: ' + ', '.join(plain_text(c['source']) for c in result['receipt_view_conflicts']) +
                         '. To archive and regenerate the views: ' +
                         ('py -3' if sys.platform == 'win32' else 'python3') + ' beyin.py sync --recover-views')
        if result.get('skill_conflicts'):
            lines.append('Skill copies diverged: ' + ', '.join(result['skill_conflicts']) + '. Both versions were kept.')
        if result.get('skill_unmanaged'):
            lines.append('Unmanaged entries in the skill folder (info): ' + ', '.join(result['skill_unmanaged']) + '.')
        if result.get('excluded_components'):
            lines.append('Excluded components: ' + ', '.join(result['excluded_components']) + '.')
        if result.get('pending_exclusions') or result.get('exclusions_pending'):
            lines.append('Exclusion change pending (' + ', '.join(result.get('pending_exclusions', [])) +
                         '): applied at the next install or update.')
        if result.get('exclusions_error'):
            lines.append('.beyin-exclusions.json is invalid; updates stop until it is fixed: ' + result['exclusions_error'])
        hygiene = result.get('companion_hygiene') or {}
        for name in hygiene.get('over_limit', []):
            entry = hygiene['files'][name]
            lines.append('Memory hygiene: ' + name + ' ' + str(entry['chars']) + ' characters (limit ' + str(entry['limit']) +
                         '). Ask your agent to run "' + ('py -3' if sys.platform == 'win32' else 'python3') +
                         ' beyin.py companion-compact"; old entries move to the archive, no text is deleted.')
        storage = result.get('state_storage') or {}
        if storage.get('compact_suggested'):
            lines.append('Local index (info): ' + megabytes(storage['database_bytes']) + ' MB, of which ' +
                         megabytes(storage['free_bytes']) + ' MB is free pages. To return the space to disk: ' +
                         ('py -3' if sys.platform == 'win32' else 'python3') + ' beyin.py state-compact')
        rules_opening = result.get('companion_rules_opening') or {}
        if rules_opening.get('status') == 'stale':
            lines.append('Kurallar.md source verification is out of date (info); run beyin.py sync to measure the opening.')
        if rules_opening.get('status') == 'clipped':
            lines.append('Kurallar.md is clipped at session opening (info): the rules text is ' + str(rules_opening['chars']) +
                         ' characters; with these settings the Claude Code opening (' + str(rules_opening['budget']) +
                         ' characters) shows at most ' + str(rules_opening['share']) + ' characters of it whole, and the rules in between are skipped' +
                         (' (reasons were also left out)' if rules_opening.get('reasons_omitted') else '') +
                         '. Keep the rules short; move long reasons and details to a separate note (e.g. Kurallar-Detay.md).')
        references = result.get('instruction_references') or {}
        if references.get('status') == 'unavailable':
            lines.append('Instruction and skill link check could not finish (info): ' +
                         plain_text(references.get('error', 'unknown')) + '.')
        elif references.get('dead_count'):
            shown = ', '.join(entry['file'] + ':' + str(entry['line']) + ' -> ' + entry['target']
                              for entry in references['dead'][:3])
            more = references['dead_count'] - min(3, len(references['dead']))
            lines.append('Broken links in instruction and skill files (info): ' + shown +
                         (' and ' + str(more) + ' more' if more > 0 else '') + '.')
        supersedes = result.get('supersedes') or {}
        lines += supersedes_lines(supersedes.get('dead'), supersedes.get('dead_count'))
        boundary_report = result.get('boundary') or {}
        boundary_lines = {
            'parent_obsidian_index': 'Root boundary (info): the parent folder also has a .obsidian; Obsidian may open the parent folder and treat this vault as a subfolder.',
            'no_root_obsidian': 'Root boundary (info): there is no .obsidian in the vault root; open exactly this folder in Obsidian.',
        }
        for finding in boundary_report.get('findings') or []:
            code = str(finding).split(':', 1)[0]
            if code == 'kasa_excluded':
                lines.append('Sensitive folders (info): ' + ', '.join(plain_text(name) for name in boundary_report.get('sensitive_excluded') or []) +
                             '; hygiene scans skip them; for a full guarantee, add visibility: private to their sources.')
            elif code == 'code_inside_vault':
                lines.append('Root boundary (info): there are code folders inside the vault (' + ', '.join(plain_text(name) for name in boundary_report.get('code_dirs', [])[:5]) +
                             '); keep the code repository outside the memory vault.')
            elif code == 'nested_git_repository':
                lines.append('Root boundary (info): there is a separate git repository inside the vault (' + ', '.join(plain_text(name) for name in boundary_report.get('nested_repositories', [])[:3]) + ').')
            elif code == 'backup_artifacts':
                lines.append('Root boundary (info): the root holds backup or sync copies (' + ', '.join(plain_text(name) for name in boundary_report.get('backup_artifacts', [])[:5]) +
                             '); they may carry a private copy.')
            elif code in boundary_lines:
                lines.append(boundary_lines[code])
        review = result.get('review') or {}
        if review.get('due_count'):
            shown = ', '.join(plain_text(entry['source']) + ' (' + str(entry['days_overdue']) + ' days)' for entry in review['due'][:3])
            more = review['due_count'] - min(3, len(review['due']))
            lines.append('Notes due for review (review_at, info): ' + shown +
                         (' and ' + str(more) + ' more' if more > 0 else '') + '.')
        if review.get('invalid_count'):
            lines.append('review_at values that are not real dates (info): ' +
                         ', '.join(plain_text(entry['source']) for entry in review['invalid'][:3]) + '.')
        closed = result.get('closed_tasks') or {}
        if closed.get('closed_count'):
            shown = ', '.join(plain_text(entry['source']) + ' (' + str(entry['days_old']) + ' days)' for entry in closed.get('closed')[:3])
            more = closed['closed_count'] - min(3, len(closed.get('closed') or []))
            lines.append('Closed tasks older than ' + str(closed.get('days', 30)) + ' days are still under tasks/ (info, moving them is your call): ' + shown +
                         (' and ' + str(more) + ' more' if more > 0 else '') + '.')
        cap = result.get('word_cap') or {}
        if cap.get('over_count'):
            shown = ', '.join(plain_text(entry['file']) + ' (' + str(entry['words']) + ' words)' for entry in cap.get('over', [])[:3])
            more = cap['over_count'] - min(3, len(cap.get('over') or []))
            lines.append('Notes over the word cap (' + str(cap['cap']) + ') (info): ' + shown +
                         (' and ' + str(more) + ' more' if more > 0 else '') + '.')
        promo = result.get('promotion') or {}
        if promo.get('hot'):
            lines.append('Hot folders (touches in the last ' + str(promo.get('window_days', 30)) + ' days): ' +
                         ', '.join(plain_text(entry['folder']) + ' (' + str(entry['touches']) + ')' for entry in promo['hot'][:3]))
        if promo.get('cold'):
            lines.append('Cold folders (promotion is your call): ' +
                         ', '.join(plain_text(entry['folder']) + ' (' + str(entry['days_quiet']) + ' days)' for entry in promo['cold'][:3]))
        waiting = [entry for entry in (result.get('inbox') or {}).get('folders') or []
                   if entry.get('attention') or entry.get('error')]
        if waiting:
            lines.append('Waiting in inbox folders (info, processing is your call): ' + ', '.join(
                plain_text(entry['folder']) + (' (unreadable: ' + plain_text(entry['error']) + ')' if entry.get('error') else
                                               ' (' + str(entry['notes']) + ' notes, oldest ' + str(entry['oldest_days']) + ' days)')
                for entry in waiting[:3]) + (' and ' + str(len(waiting) - 3) + ' more folders' if len(waiting) > 3 else '') + '.')
        parallel = result.get('parallel_sessions') or {}
        if parallel.get('enabled'):
            lines.append('Parallel session notice: on (' + str(parallel.get('active', 0)) + ' session markers active in the last 45 minutes)')
        elif parallel.get('valid') is False:
            lines.append('parallel-sessions.json is invalid; the parallel session notice is treated as off.')
        dedupe = result.get('context_dedupe') or {}
        if dedupe.get('enabled'):
            lines.append('In-session repeat prevention: on (' + str(dedupe.get('sessions', 0)) + ' session ledgers)')
        elif dedupe.get('valid') is False:
            lines.append('context-dedupe.json is invalid; in-session repeat prevention is treated as off.')
        queue = result.get('mutation_queue') or {}
        if queue.get('valid') is False:
            lines.append('mutation-queue-settings.json is invalid; the offline queue is treated as off.')
        if queue.get('enabled') or queue.get('queue_exists'):
            lines.append('Offline mutation queue: ' + ('on' if queue.get('enabled') else 'off') +
                         (' (queue file unreadable)' if queue.get('status') == 'invalid' else
                          ' (' + str(queue.get('pending_count', 0)) + ' pending, ' + str(queue.get('conflict_count', 0)) +
                          ' conflicts, ' + str(queue.get('failed_count', 0)) + ' failed)'))
        index_scope = result.get('index_exclusions') or {}
        lines += index_exclusion_lines(index_scope)
        hint = index_scope.get('vendored_hint') or {}
        if hint.get('notes'):
            more = len(hint.get('dirs') or []) - 3
            lines.append('Index scope (info): folders that look like code copies of other projects have ' + str(hint['notes']) +
                         ' notes indexed (' + ', '.join(plain_text(entry['dir']) + ': ' + str(entry['notes'])
                                                       for entry in (hint.get('dirs') or [])[:3]) +
                         (' and other folders' if more > 0 or hint.get('truncated') else '') +
                         '). If they are not your notes, keep them out of the index: ' + ('py -3' if sys.platform == 'win32' else 'python3') +
                         ' beyin.py preferences ' + ' '.join('--index-exclude-dir ' + plain_text(name)
                                                            for name in hint.get('names') or []))
        arch_hint = index_scope.get('archive_hint') or {}
        if arch_hint.get('notes'):
            more = len(arch_hint.get('dirs') or []) - 3
            py_cmd = 'py -3' if sys.platform == 'win32' else 'python3'
            exclude_args = ' '.join('--index-exclude-dir ' + (('"' + plain_text(name) + '"') if ' ' in name else plain_text(name))
                                    for name in arch_hint.get('names') or [])
            lines.append('Archive scope (info): notes in archive folders that are not retired count as live; ' + str(arch_hint['notes']) +
                         ' notes indexed (' + ', '.join(plain_text(entry['dir']) + ': ' + str(entry['notes'])
                                                       for entry in (arch_hint.get('dirs') or [])[:3]) +
                         (' and other folders' if more > 0 or arch_hint.get('truncated') else '') +
                         '). To keep them out of the context, write "status: archived" in the notes or keep the folder out of the index: ' +
                         py_cmd + ' beyin.py preferences ' + exclude_args)
        lines += state_location_lines(result.get('state_location'))
        lines += receipt_line_endings_lines(result.get('receipt_line_endings'))
        backup = result.get('backup') or {}
        if backup.get('status') == 'remote_configured':
            lines.append('Backup (info): a Git remote is set; a current, restorable second copy was not verified. docs/v3/BACKUP.md')
        elif backup:
            lines.append('Backup (info): no second copy of this vault could be verified; a backup you make another way does not show here. Keep a separate copy in case of disk failure. docs/v3/BACKUP.md')

        paths = result.get('hook_paths') or {}
        if paths.get('status') == 'stale':
            lines.append('Hook paths point to another installation (' + str(len(paths.get('stale', []))) + ' old paths). ' +
                         'To update: ' + ('py -3' if sys.platform == 'win32' else 'python3') + ' beyin.py hook-reconcile')
        tracked = result.get('tracked_machine_files') or {}
        bridges = result.get('global_bridge_paths') or {}
        if bridges.get('status') == 'stale':
            harnesses = sorted({row.get('harness') for row in bridges.get('stale', [])
                                if row.get('harness') in ('claude', 'codex', 'antigravity', 'opencode')})
            commands = ', '.join('bridge --harness ' + harness + ' ... --install' for harness in harnesses)
            lines.append('Global bridge paths point to an old installation (info): ' + commands +
                         '. Reinstall them from inside the new vault, keeping the earlier --project-root, --event and --context-chars choices'
                         '. Global settings were not changed.')
        if tracked.get('status') == 'warning':
            lines.append('Git tracks machine-specific installation files (info): ' +
                         ', '.join(plain_text(name) for name in tracked.get('tracked', [])) +
                         '. Keeping a backup for each machine, read the docs/v3/MULTI-MACHINE.md guide; nothing was changed automatically.')
        elif tracked.get('status') in ('unavailable', 'skipped'):
            lines.append('Git installation file check (info): ' + plain_text(tracked.get('status')) +
                         ' (' + plain_text(tracked.get('reason', 'unknown')) + ').')
        scopes = result.get('project_scopes') or {}
        if scopes.get('status') == 'error' and scopes.get('error'):
            lines.append('Project scopes (.beyin-projects.json) are invalid: ' + plain_text(scopes['error']))
        elif scopes.get('status') in ('error', 'warning'):
            # Entry-level problems: name each entry instead of a bare "error" (#419).
            details = []
            if scopes.get('missing_folders'):
                details.append('folders not found in the vault: ' + ', '.join(plain_text(f) for f in scopes['missing_folders']))
            if scopes.get('duplicate_folders'):
                details.append('folders assigned to more than one project: ' + ', '.join(plain_text(f) for f in scopes['duplicate_folders']))
            if scopes.get('invalid_entries'):
                details.append('invalid entries: ' + ', '.join(plain_text(f) for f in scopes['invalid_entries']))
            if scopes.get('duplicate_folders') or scopes.get('invalid_entries'):
                details.append('these entries are skipped, and the vault folders they name are open to no project' +
                               (' and shared_unscoped is off until they are fixed' if scopes.get('shared_unscoped') else ''))
            lines.append('Project scopes (.beyin-projects.json) need attention: ' + '; '.join(details) +
                         '. To fix or clean up: ' + ('py -3' if sys.platform == 'win32' else 'python3') +
                         ' beyin.py project-scope prune')
        if status in ('needs_attention', 'pending'):
            lines.append('Say "beyin doktor" to your agent to have the details examined.')
        return '\n'.join(lines + update_lines(result.get('updates', {})))
    if result.get('verification') == 'metadata_only':
        return '\n'.join(update_lines(result) + ['Only release information was checked; no package install was attempted.'])
    if status == 'updated':
        message = 'Beyin updated: ' + str(result.get('from_version', installed_version or '?')) + ' -> ' + str(result['version'])
        if result.get('removed'):
            message += '\nExcluded components removed: ' + ', '.join(result['removed']) + '.'
        if result.get('preserved_excluded'):
            message += '\nExcluded but modified files were kept: ' + ', '.join(result['preserved_excluded']) + '.'
        if result.get('orphaned_legacy_state'):
            message += ('\nThere are ' + str(len(result['orphaned_legacy_state'])) + ' interrupted V2 flush records (status inflight,'
                        ' and the writing process no longer runs); not treated as a blocker, the files were not touched.'
                        ' The summaries of those sessions may not have been written to daily/.')
        if result.get('stale_legacy_locks'):
            message += ('\nThere are ' + str(len(result['stale_legacy_locks'])) + ' orphaned V2 lock folders (prompt_count.*.lock,'
                        ' older than eight days); not treated as a blocker, not touched.')
    elif status == 'available':
        message = 'New version available: ' + str(result.get('current_version', '?')) + ' -> ' + str(result['version']) + '\nTo update: python beyin.py update'
    elif status == 'noop':
        message = 'Beyin is up to date: ' + str(result.get('version', installed_version or '?'))
    elif status == 'dismissed':
        message = 'Session notice muted for this version: ' + result['version']
    elif status == 'uninstalled':
        message = 'Installation removed. User notes were kept.'
    elif status == 'rolled_back':
        message = 'Rolled back to the previous version: ' + str(result.get('version', '?'))
    elif status == 'recovered':
        message = 'Interrupted operation recovered. Version: ' + str(result.get('version', '?'))
    elif command == 'context':
        records = result.get('records', [])
        message = '\n\n'.join(str(r.get('source', '')) + '\n' + str(r.get('text', '')) for r in records) or 'No matching source found.'
    elif command == 'project-scope':
        action = result.get('action', 'list')
        if action == 'list':
            if result.get('status') == 'absent':
                return 'Project scopes (.beyin-projects.json) not found.'
            if result.get('error'):
                return 'Project scopes (.beyin-projects.json) are invalid: ' + plain_text(result['error'])
            lines = ['Project scopes (.beyin-projects.json):']
            folders = result.get('folders', {})
            missing = set(result.get('missing_folders', []))
            for f, p in sorted(folders.items()):
                extra = ' (not found in the vault)' if f in missing else ''
                lines.append('  ' + plain_text(f) + ' -> ' + plain_text(p) + extra)
            for f in result.get('missing_folders', []):
                if f not in folders:
                    lines.append('  ' + plain_text(f) + ' (not found in the vault)')
            # Skipped entries (#419): named here, closed to every project until fixed.
            for entry in result.get('invalid_entries', []) + result.get('duplicate_folders', []):
                lines.append('  ' + plain_text(entry) + ' (skipped)')
            shared = result.get('shared_unscoped')
            if shared and result.get('shared_unscoped_effective') is False:
                lines.append('  shared_unscoped: off (until the skipped entries are fixed)')
            else:
                lines.append('  shared_unscoped: ' + ('on' if shared else 'off'))
            return '\n'.join(lines)
        elif action == 'add':
            # add is the only command that changes shared_unscoped (#607): show the saved value.
            return ('Folder added to project scope: ' + plain_text(result.get('folder', '')) + ' -> ' +
                    plain_text(result.get('project', '')) +
                    '\n  shared_unscoped: ' + ('on' if result.get('shared_unscoped') else 'off'))
        elif action == 'remove':
            return 'Folder removed from project scope: ' + plain_text(result.get('folder', ''))
        elif action == 'prune':
            pruned = result.get('pruned', [])
            if not pruned:
                return 'No missing folders to clean up; all folders exist in the vault.'
            return 'Removed ' + str(len(pruned)) + ' folders that no longer exist in the vault from the project scope: ' + ', '.join(plain_text(f) for f in pruned)
    elif command == 'bridge':
        status = result.get('status')
        harness = result.get('harness', 'unknown')
        if status == 'installed':
            lines = ['Global bridge installed (' + harness + '):']
            if result.get('hook_file'):
                lines.append('  Hook settings: ' + plain_text(result['hook_file']))
            if result.get('gemini_md'):
                lines.append('  Global instructions: ' + plain_text(result['gemini_md']))
            if result.get('project_roots'):
                lines.append('  Covered project roots: ' + ', '.join(plain_text(r) for r in result['project_roots']))
            lines.append('Existing user settings were kept; a .bak backup was made.')
            return '\n'.join(lines)
        elif status == 'uninstalled':
            lines = ['Global bridge removed (' + harness + '):']
            if result.get('hook_file'):
                lines.append('  Hook settings: ' + plain_text(result['hook_file']))
            lines.append('  Bridge entries removed: ' + str(result.get('removed_count', 0)))
            lines.append('Other user settings were kept.')
            return '\n'.join(lines)
    else:
        message = 'Result: ' + str(status or 'done')
        if command in ('sync', 'recover-views'):
            if result.get('recovered_views'):
                recovered_lines = ['Conflicting receipt views were archived and regenerated:']
                for item in result['recovered_views']:
                    recovered_lines.append('  - ' + plain_text(item['source']) + ' -> ' + plain_text(item['archive']))
                message = '\n'.join([message] + recovered_lines)
            message = '\n'.join([message] + index_exclusion_lines(result.get('index_exclusions'), pruned=True) +
                                (sync_copy_lines(result) if command == 'sync' else []) +
                                supersedes_lines(result.get('supersedes_issues'), result.get('supersedes_issue_count')))
    if result.get('trust_review_required'):
        message += '\n' + trust_review_line(result.get('trust_review_files'))
    if result.get('view_conflicts'):
        message += '\nReceipt views kept: ' + ', '.join(plain_text(c['source']) for c in result['view_conflicts']) + '. Recovery: beyin.py sync --recover-views'
    return message


# Hook definition file -> the step its client needs before the new hooks run (SETUP-V3.md step 5).
TRUST_REVIEW = {
    '.codex/hooks.json': 'Codex: /hooks trust review',
    '.kiro/hooks/beyin-v3.json': 'Kiro: review in the Agent Hooks panel or with CLI /hooks',
    '.agents/hooks.json': 'Antigravity: trust the vault folder',
    '.claude/settings.local.json': 'Claude Code: no extra review',
}


def trust_review_line(files):
    """Name only the clients whose hook definitions changed; an older updater gives no list."""
    changed = [name for name in TRUST_REVIEW if name in (files or ())]
    if not changed:
        return 'Hook definitions changed: complete the trust review in the client you use and open a new session.'
    return ('Hook definitions changed (' + ', '.join(changed) + '). ' +
            '; '.join(TRUST_REVIEW[name] for name in changed) + '. Then open a new session.')


def print_error(error):
    """--json error on stderr with real characters as UTF-8 (#587), like the CLI's print_error.
    Kept here because a broken .beyin-runtime.json fails before the CLI module is loaded."""
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except (OSError, ValueError):
            pass
    # Control characters (DEL, C1), bidi and other format controls, line separators and lone
    # surrogates stay escaped.
    text = ''.join(json.dumps(ch)[1:-1] if unicodedata.category(ch) in ('Cc', 'Cf', 'Cs', 'Zl', 'Zp') else ch
                   for ch in json.dumps(error, ensure_ascii=False))
    try:
        print(text, file=sys.stderr)
    except UnicodeEncodeError:
        print(json.dumps(error, ensure_ascii=True), file=sys.stderr)


def load_cli(directory):
    """The installed CLI module, loaded from its file like every other entry-point command."""
    spec = importlib.util.spec_from_file_location('beyin_installed_cli', directory / 'beyin_v3_cli.py')
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return cli


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    force_json = '--json' in argv or '--print-config' in argv
    human = ('--human' in argv or sys.stdout.isatty()) and not force_json
    argv = [arg for arg in argv if arg not in ('--human', '--json')]
    if human:
        # A piped or redirected Windows console uses a legacy code page (cp1252 has no s-cedilla);
        # write redirected human output as UTF-8 so stored text and paths survive intact.
        # Keep the interactive terminal's encoding and replacement behavior.
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, 'reconfigure'):
                if stream.isatty():
                    stream.reconfigure(errors='replace')
                else:
                    stream.reconfigure(encoding='utf-8', errors='replace')
    command = argv[0] if argv else 'doctor'
    if command in ('note-read', 'note-edit'):
        human = False  # These commands have a JSON contract, including on a terminal.
    vault = Path(__file__).resolve().parent
    stamp = vault / '.beyin-version'
    installed_version = None
    try:
        installed_version = stamp.read_text(encoding='utf-8').strip() if stamp.is_file() else None
        config_path = vault / '.beyin-runtime.json'
        if not config_path.is_file():
            raise ValueError('Installation settings are missing; finish installing this vault with the official V3 installer.')
        try:
            config = json.loads(config_path.read_text(encoding='utf-8'))
        except ValueError as exc:  # JSONDecodeError or UnicodeDecodeError: name the file (#587)
            raise ValueError('Installation settings could not be read: .beyin-runtime.json is not valid JSON (' + str(exc) + ').') from None
        directory = vault / '.claude/scripts'
        sys.path.insert(0, str(directory))
        cli = None
        raw_state = config.get('state') if isinstance(config, dict) else None
        if isinstance(raw_state, str) and raw_state and Path(raw_state).expanduser().is_absolute():
            cli = load_cli(directory)
            state = cli.resolve_state(vault, Path(raw_state))
            try:
                pinned_state = Path(raw_state).expanduser().resolve()
            except (OSError, ValueError, RuntimeError):
                pinned_state = None
            if state != pinned_state:
                print('Warning: a foreign default state path was resolved to the local state folder of this machine: ' +
                      plain_text(state) + '. Permanent fix: install with install_v3.py on this machine.', file=sys.stderr)
        else:
            # The installer always pins a resolved absolute path. A pin that is not absolute
            # here came from another OS through a synced vault (a Windows C:\ path on POSIX,
            # a /home path on Windows, #249) or was edited by hand. Read as a relative path it
            # would put the state under the working directory, so this machine's default
            # state is used instead; doctor reports the pin it could not use, and every command says
            # so on stderr (#205): stdout stays the command's own result, JSON included.
            cli = load_cli(directory)
            state = cli.default_state(vault)
            print('Warning: the state path in .beyin-runtime.json (' + plain_text(raw_state) + ') is not an absolute path '
                  'on this machine; the vault may have been synced from another operating system. Using the default '
                  'state folder of this machine: ' + plain_text(state) + '. Permanent fix: install with '
                  'install_v3.py on this machine; that also binds the hook commands to this machine.', file=sys.stderr)
        if argv and argv[0] == 'yakala':
            # Optional capture tool: its own small CLI, no index or sync engine.
            import beyin_v3_yakala as yakala
            return yakala.main((['--json'] if force_json else []) + argv[1:], vault=vault, state=state)
        if argv and argv[0] == 'web':
            # Optional local web view; only this explicit command ever starts it.
            import beyin_v3_web as web
            return web.main((['--json'] if force_json else []) + argv[1:], vault=vault, state=state, cli=cli)
        if argv and argv[0] in ('update', 'rollback', 'recover'):
            import argparse
            import beyin_v3_update as updater
            class _UpdateArgumentParser(argparse.ArgumentParser):
                def error(self, message):
                    if force_json:
                        print_error({'error': 'SystemExit', 'message': message})
                        self.exit(2)
                    super().error(message)

            parser = _UpdateArgumentParser()
            parser.add_argument('command', choices=('update', 'rollback', 'recover'))
            parser.add_argument('--check', action='store_true')
            parser.add_argument('--package', type=Path)
            parser.add_argument('--metadata-only', action='store_true')
            parser.add_argument('--dismiss')
            args = parser.parse_args(argv)
            if args.command != 'update' and (args.check or args.package or args.metadata_only or args.dismiss is not None):
                parser.error('update options require the update command')
            if args.metadata_only and (not args.check or args.package or args.dismiss is not None):
                parser.error('--metadata-only requires --check and cannot use --package or --dismiss')
            if args.dismiss is not None and (args.check or args.package):
                parser.error('--dismiss cannot use --check or --package')
            if args.command == 'update':
                import beyin_v3_releases as releases
                if args.metadata_only: result = releases.check(vault)
                elif args.dismiss is not None: result = releases.dismiss(vault, state, args.dismiss)
                else: result = updater.update(vault, state, args.package, args.check)
            elif args.command == 'rollback': result = updater.rollback(vault, state)
            else: result = updater.recover(vault, state)
            print(human_result(result, command, installed_version) if human else json.dumps(result, ensure_ascii=True, indent=2))
            return 0
        cli = cli or load_cli(directory)
        cli_args = ['--vault', str(vault), '--state', str(state)] + (['--json'] if force_json else []) + (argv or ['doctor'])
        if not human:
            return cli.main(cli_args)
        if hasattr(cli, 'main') and 'return_result' in getattr(getattr(cli, 'main'), '__code__', {}).co_varnames:
            result, code = cli.main(cli_args, return_result=True)
            try:
                message = human_result(result, command, installed_version)
            except (ValueError, TypeError, AttributeError):
                # A result human_result cannot shape (history returns a list) prints as the JSON
                # the captured path below shows, not as a failed command.
                message = ('Operation failed; run the same command with --json for details.' if code
                           else json.dumps(result, ensure_ascii=True, indent=2))
        else:
            from contextlib import redirect_stdout, redirect_stderr
            import io
            output, error = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(error):
                code = cli.main(cli_args)
            value = output.getvalue() if not code else error.getvalue()
            try:
                result = json.loads(value)
                message = human_result(result, command, installed_version)
            except (ValueError, TypeError, AttributeError):
                message = 'Operation failed; run the same command with --json for details.' if code else value.strip()
        print(message, file=sys.stderr if code else sys.stdout)
        return code
    except Exception as exc:
        error = {'error': type(exc).__name__, 'message': str(exc)}
        if human:
            print(human_result(error, command, installed_version), file=sys.stderr)
        else:
            print_error(error)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
