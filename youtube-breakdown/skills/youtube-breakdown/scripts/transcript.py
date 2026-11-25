#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["youtube-transcript-api>=1.0"]
# ///
"""
Fetch a YouTube transcript without playing the video.

Usage:
  uv run transcript.py <youtube-url-or-id> [--lang en] [--plain] [--list]
  python3 transcript.py <youtube-url-or-id>     (needs: pip install youtube-transcript-api)

Output: a header line, then the transcript grouped under [m:ss] stamps, one block per ~30 seconds.
--plain prints the text with no stamps. --list prints the available caption tracks.
The first lines give title, channel and upload date when YouTube returns them ("not captured" otherwise).
Exit codes: 0 ok, 2 no transcript for this video (captions off, private, blocked),
3 missing dependency, 4 the input is not a YouTube link or ID.
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    sys.stderr.write(
        "Missing dependency. Run this script with `uv run transcript.py <url>` "
        "or install it first: pip install youtube-transcript-api\n"
    )
    sys.exit(3)

ID_RE = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([A-Za-z0-9_-]{11})")


def video_id(url_or_id: str) -> str:
    s = url_or_id.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    m = ID_RE.search(s)
    if not m:
        raise ValueError(f"Could not find a YouTube video ID in: {s}")
    return m.group(1)


def stamp(seconds: float) -> str:
    s = int(seconds)
    h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


UA = {"User-Agent": "Mozilla/5.0 (youtube-breakdown skill)", "Accept-Language": "en"}


def metadata(vid: str) -> dict:
    """Title and channel from oEmbed, upload date and length from the watch page. Never raises."""
    meta = {"title": "not captured", "channel": "not captured", "uploaded": "not captured", "length": "not captured"}
    url = f"https://www.youtube.com/watch?v={vid}"
    try:
        q = urllib.parse.urlencode({"url": url, "format": "json"})
        with urllib.request.urlopen(urllib.request.Request(f"https://www.youtube.com/oembed?{q}", headers=UA), timeout=10) as r:
            d = json.load(r)
        meta["title"] = d.get("title") or meta["title"]
        meta["channel"] = d.get("author_name") or meta["channel"]
    except Exception:
        pass
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10) as r:
            html = r.read(1_500_000).decode("utf-8", "ignore")
        m = re.search(r'"uploadDate":"([0-9-]{10})', html) or re.search(r'itemprop="uploadDate" content="([0-9-]{10})', html)
        if m:
            meta["uploaded"] = m.group(1)
        m = re.search(r'"lengthSeconds":"(\d+)"', html)
        if m:
            meta["length"] = stamp(int(m.group(1)))
    except Exception:
        pass
    return meta


def main() -> int:
    p = argparse.ArgumentParser(description="Fetch a YouTube transcript.")
    p.add_argument("video", help="YouTube URL or 11-character video ID")
    p.add_argument("--lang", default="en", help="Preferred language code (default en)")
    p.add_argument("--plain", action="store_true", help="No timestamps")
    p.add_argument("--list", action="store_true", help="List available caption tracks")
    p.add_argument("--block", type=int, default=30, help="Seconds per timestamped block (default 30)")
    a = p.parse_args()

    api = YouTubeTranscriptApi()
    try:
        vid = video_id(a.video)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 4
    try:
        if a.list:
            for t in api.list(vid):
                print(f"{t.language_code}\t{t.language}\t{'auto' if t.is_generated else 'manual'}")
            return 0
        prefs = list(dict.fromkeys([a.lang, "en", "en-US", "en-GB", "en-AU"]))
        try:
            fetched = api.fetch(vid, languages=prefs)
        except Exception:
            tracks = list(api.list(vid))
            if not tracks:
                raise
            fetched = tracks[0].fetch()
        snippets = list(fetched)
        if not snippets:
            print(f"No transcript text returned for {vid}.", file=sys.stderr)
            return 2
        kind = "auto-generated" if fetched.is_generated else "manual"
        m = metadata(vid)
        print(f"Title: {m['title']}")
        print(f"Channel: {m['channel']} | Uploaded: {m['uploaded']} | Length: {m['length']}")
        print(f"Video {vid} | https://www.youtube.com/watch?v={vid} | language {fetched.language_code} | {kind} captions | {len(snippets)} lines")
        if a.plain:
            print(" ".join(s.text.replace("\n", " ") for s in snippets))
            return 0
        out, last_block = [], -1
        for s in snippets:
            block = int(s.start // a.block)
            text = s.text.replace("\n", " ").strip()
            if block != last_block:
                out.append(f"\n[{stamp(s.start)}] {text}")
                last_block = block
            else:
                out.append(" " + text)
        print("".join(out).lstrip("\n"))
        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
