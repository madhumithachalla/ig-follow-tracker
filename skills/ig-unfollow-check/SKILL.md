---
name: ig-unfollow-check
description: Find who doesn't follow you back on Instagram and who recently unfollowed you, from your Instagram data export (followers/following JSON). Use when the user asks about Instagram unfollowers, non-followers, "who doesn't follow me back", or a periodic follower check-up.
---

# Instagram unfollow check

Compares the user's official Instagram data export to report:

- **Don't follow you back**: accounts the user follows that don't follow them (minus a keep-list).
- **New unfollowers**: accounts that followed in the previous snapshot but no longer do.
- **New followers** since the previous snapshot.

Everything runs locally. Snapshots are saved to `~/.ig-follow-tracker/` so each run can be diffed against the last one.

## Hard rules

- Never ask for, accept or type the user's Instagram username/password, session cookies or API tokens.
- Never scrape Instagram, drive the Instagram app/site, or automate follow/unfollow actions. That violates Instagram's terms and risks the account. The user unfollows manually.
- Treat usernames as personal data: do not paste them into other tools, commits, issues or public repos.

## Steps

1. Get the path to the user's export folder (or the unzipped export). If they don't have one, tell them how to request it:
   Instagram → Accounts Center → Your information and permissions → Download your information → Export to device → select **Followers and following** → format **JSON** → date range **All time**. It arrives by email, usually within minutes to a day.
2. Run the analyzer (Python 3, standard library only):

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/skills/ig-unfollow-check/scripts/analyze.py" "<export_folder>"
   ```

   Useful flags: `--json` (machine-readable), `--no-save` (don't write a snapshot), `--state-dir DIR`, `--show-fans` (list followers the user doesn't follow back).
3. Present the report. Lead with new unfollowers (if a previous snapshot exists), then non-followers. Keep it concise; list usernames in a compact list.
4. Mention caveats when relevant:
   - First run has no previous snapshot, so "new unfollowers" is empty. Unfollows are detectable only between two exports.
   - Deactivated, deleted or blocked accounts also show as unfollowers.
   - Keep-list: usernames in `~/.ig-follow-tracker/keep.txt` (one per line) are excluded from "don't follow you back" (brands, celebrities, close friends you follow regardless).
5. Offer to schedule a recurring reminder (weekly or fortnightly) to export fresh data and rerun this check. See the plugin README.
