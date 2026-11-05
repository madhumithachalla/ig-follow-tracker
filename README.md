# ig-follow-tracker

A Claude Code plugin that tells you who doesn't follow you back on Instagram and who recently unfollowed you.

It works from Instagram's **official data export**. It never logs in, scrapes, or automates follow/unfollow actions, so your account isn't put at risk. Everything runs locally; snapshots stay in a local state folder on your machine (configurable with `--state-dir`).

## Install (local)

```bash
git clone https://github.com/<your-username>/ig-follow-tracker.git
claude --plugin-dir ./ig-follow-tracker
```

Then ask Claude "who doesn't follow me back on Instagram?", or run `/ig-follow-tracker:ig-check <export_folder>`.

## Get your data

Instagram → Accounts Center → Your information and permissions → Download your information → Export to device → **Followers and following** → format **JSON** → date range **All time**. Unzip it and give Claude the folder path.

## What you get

- Accounts you follow that don't follow back (minus your keep-list)
- New unfollowers and new followers since your previous export
- Optional: followers you don't follow back (`--show-fans`)

Unfollowing is only detectable between two exports, so the first run just creates the baseline.

## Keep-list

Put usernames you follow regardless (brands, friends, creators) in a `keep.txt` file inside the state folder, one per line. They're hidden from the "don't follow you back" list.

## Run the script directly

```bash
python skills/ig-unfollow-check/scripts/analyze.py <export_folder> [--json] [--no-save] [--show-fans] [--state-dir DIR]
```

Python 3, standard library only.

## Tests

```bash
python -m unittest discover tests
```

## Making it timely

Instagram exports can't be fetched automatically, so the agent is timely by prompting you. Create a weekly reminder that asks Claude to nudge you to request a fresh export and rerun the check, for example with Claude Code's `/schedule` or `/loop` skills ("every Monday 9am, remind me to export Instagram followers and run ig-unfollow-check").

## Privacy

Exports and snapshots contain other people's usernames. Don't commit them (they're in `.gitignore`), and keep this repo **private**.
