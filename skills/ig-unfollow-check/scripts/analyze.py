#!/usr/bin/env python3
"""Compare Instagram data-export follower/following lists and diff against the last snapshot.

Standard library only. Reads the JSON export (followers_*.json, following.json).
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path


def _items(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        out = []
        for v in data.values():
            if isinstance(v, list):
                out.extend(v)
        return out
    return []


def _username(item):
    sld = item.get("string_list_data") or []
    first = sld[0] if sld else {}
    name = first.get("value") or item.get("title")
    if not name and first.get("href"):
        name = first["href"].rstrip("/").rsplit("/", 1)[-1]
    return name.strip().lower() if name else None


def load_users(paths):
    users = set()
    for p in paths:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            sys.exit(f"Could not read {p}: {e}")
        for item in _items(data):
            if isinstance(item, dict):
                u = _username(item)
                if u:
                    users.add(u)
    return users


def find_files(root):
    followers = sorted(root.rglob("followers_*.json")) or sorted(root.rglob("followers.json"))
    following = sorted(root.rglob("following.json"))
    if not followers or not following:
        sys.exit(
            f"No followers_*.json / following.json found under {root}.\n"
            "Request the export in JSON format (not HTML) with 'Followers and following' selected."
        )
    return followers, following


def read_keep(state_dir):
    f = state_dir / "keep.txt"
    if not f.exists():
        return set()
    return {l.strip().lstrip("@").lower() for l in f.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")}


def latest_snapshot(snap_dir):
    snaps = sorted(snap_dir.glob("*.json"))
    return snaps[-1] if snaps else None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap =argparse.ArgumentParser(description=__doc__)
    ap.add_argument("export_dir", type=Path, help="Folder containing the unzipped Instagram export")
    ap.add_argument("--state-dir", type=Path, default=Path.home() / ".ig-follow-tracker")
    ap.add_argument("--no-save", action="store_true", help="Do not write a snapshot")
    ap.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    ap.add_argument("--show-fans", action="store_true", help="List followers you don't follow back")
    args = ap.parse_args()

    if not args.export_dir.is_dir():
        sys.exit(f"Not a directory: {args.export_dir}")

    f_files, g_files = find_files(args.export_dir)
    followers = load_users(f_files)
    following = load_users(g_files)
    keep = read_keep(args.state_dir)

    snap_dir = args.state_dir / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    prev_path = latest_snapshot(snap_dir)
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path else None

    not_back = sorted(following - followers - keep)
    fans = sorted(followers - following)
    mutual = followers & following

    report = {
        "counts": {"followers": len(followers), "following": len(following), "mutual": len(mutual),
                   "not_following_back": len(not_back), "kept_excluded": len((following - followers) & keep)},
        "not_following_back": not_back,
        "fans": fans if args.show_fans else None,
        "since": None, "new_unfollowers": None, "new_followers": None,
    }
    if prev:
        old = set(prev["followers"])
        report["since"] = prev["date"]
        report["new_unfollowers"] = sorted(old - followers)
        report["new_followers"] = sorted(followers - old)

    if not args.no_save:
        now = dt.datetime.now()
        out = snap_dir / now.strftime("%Y%m%d-%H%M%S.json")
        out.write_text(json.dumps({"date": now.isoformat(timespec="seconds"),
                                   "followers": sorted(followers), "following": sorted(following)}), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
        return

    c = report["counts"]
    print(f"# Instagram follow check\n\n{c['followers']} followers · {c['following']} following · {c['mutual']} mutual\n")
    if report["since"]:
        print(f"## New unfollowers since {report['since']} ({len(report['new_unfollowers'])})")
        print(", ".join(report["new_unfollowers"]) or "None")
        print(f"\n## New followers ({len(report['new_followers'])})")
        print(", ".join(report["new_followers"]) or "None")
    else:
        print("_No previous snapshot, so unfollow tracking starts from this export. Run again with a newer export to see who unfollowed._")
    print(f"\n## Don't follow you back ({c['not_following_back']})")
    if c["kept_excluded"]:
        print(f"_({c['kept_excluded']} more hidden by your keep-list)_")
    print("\n".join(f"- {u}" for u in not_back) or "None")
    if args.show_fans:
        print(f"\n## Follow you, you don't follow ({len(fans)})")
        print("\n".join(f"- {u}" for u in fans) or "None")


if __name__ == "__main__":
    main()
