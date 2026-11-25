# YouTube Breakdown for Claude

Paste a YouTube link. Get a ranked **top 3 actions** briefing, without watching the video.

Claude reads the transcript (the video never plays), pulls out every claim, tactic and tip with its timestamp, checks product claims against the vendor's official docs, and ranks what is worth doing for you. Anything that costs money is flagged, never switched on.

A free tool from [MCP Academy](https://mcpacademy.co/tools/youtube-breakdown). MCP Academy is independent and not affiliated with Anthropic or YouTube.

## What you get

```
# <Video title>
<Channel> | <date> | <link> | transcript: auto-generated, en

TL;DR: two lines on what it is and whether it's worth your time.

Top 3 actions      Action | Why | Cost | Source (timestamp + doc link)
Claims checked     Time | Claim | Verified / Changed / Unverified / Wrong | Official source
Tactics            m:ss one line each
Parked             everything else, one line each
Shiny object check
```

## Install

### Option A: Claude Code plugin (recommended)

In Claude Code, run:

```
/plugin marketplace add GITHUB_OWNER/mcp-academy-tools
/plugin install youtube-breakdown@mcp-academy
```

Pick a scope when asked (user is the usual choice). If Claude Code says "Run /reload-plugins to apply", run `/reload-plugins`. Restarting Claude Code also works. Auto-update is off for community marketplaces, so run `/plugin marketplace update mcp-academy` now and then for new versions.

### Option B: Claude Code, manual

Unzip `youtube-breakdown-skill.zip` into `~/.claude/skills/` so the folder lands whole and you have:

```
~/.claude/skills/youtube-breakdown/SKILL.md
~/.claude/skills/youtube-breakdown/scripts/transcript.py
```

### Option C: claude.ai (web or desktop app)

1. Settings > Capabilities: turn on code execution ("Create and edit files"). On Team and Enterprise, an owner may need to allow skills.
2. Customize > Skills > **+** > Create skill > Upload a skill, and choose `youtube-breakdown-skill.zip`.

On claude.ai the transcript step runs in Claude's sandbox, which may not be able to reach YouTube. If Claude says it can't fetch the transcript, open the video, click **...more > Show transcript**, copy it and paste it in. Everything else works the same.

## The one requirement: Python

The transcript step uses the open-source [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/) Python library.

- If you have [uv](https://docs.astral.sh/uv/), nothing else to do: `uv run` installs it on the fly.
- Otherwise: `pip install youtube-transcript-api` (Claude will ask before installing anything).

## Use it

Just paste a link and ask:

> Break down this video: https://www.youtube.com/watch?v=...

or in Claude Code, call it directly: `/youtube-breakdown:youtube-breakdown <link>` (plugin install) or `/youtube-breakdown <link>` (manual install).

Tell Claude what you want from the video (tools to try, marketing ideas, a fact check) and what you already use, and the top 3 gets much sharper.

## Limits

- Needs captions. Videos with captions turned off, members-only or age-restricted videos can't be read.
- Fact checks need web access. Without it, every product claim is marked Unverified.
- YouTube sometimes blocks transcript requests from cloud servers. On your own computer this is rarely a problem.

## Licence

MIT. Use it, change it, share it.
