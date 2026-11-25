---
name: youtube-breakdown
description: Break down a YouTube video into a ranked "top 3 actions" briefing without watching it. Pulls the transcript (the video never plays), extracts every claim, tactic and tip with its timestamp, checks product and feature claims against official docs, and ranks what is worth doing for this user. Use when the user pastes a YouTube link and asks to break it down, summarise it, "is this worth watching", "what should I take from this", or "check what this video claims".
---

# YouTube Breakdown

Turn a YouTube video into action, not reading. The output is a short briefing: what the video says, what is actually true, and the three things worth doing.

The video link is in the user's message or here: $ARGUMENTS

## 1. Get the transcript (never play the video)

The script lives in this skill's own folder: `scripts/transcript.py` (in a plugin install that is `${CLAUDE_PLUGIN_ROOT}/skills/youtube-breakdown/scripts/transcript.py`). Use the full path. Try these in order and stop at the first that works:

1. **Bundled script** (preferred):
   `uv run <skill folder>/scripts/transcript.py "<url>"`
   `uv run` fetches the open-source youtube-transcript-api library on first use. If `uv` is not installed, tell the user the script needs that library and ask before running `pip install youtube-transcript-api`, then use `python3 <skill folder>/scripts/transcript.py "<url>"`.
   Options: `--lang <code>` for another language, `--list` to see the caption tracks, `--plain` for text with no timestamps.
   The first three lines give title, channel, upload date, length, caption language and whether captions are auto-generated.
   Exit codes: 0 ok; 2 no transcript for this video (captions off, private, members-only or blocked); 3 library missing; 4 the input is not a YouTube link or ID (ask the user to check the link, do not say captions are off).
2. **A YouTube transcript tool**, if the user has one connected (for example an MCP tool named like `get_transcript`).
3. **Ask the user** to paste the transcript (YouTube: "...more" under the video, then "Show transcript"). Do not open the video in a browser to read it yourself unless the user asks, and if you do, pause and mute it first.

If no transcript exists, say so plainly and stop. Never invent content for a video you could not read. If the header says "not captured" for a field, write "not captured" in the briefing rather than guessing.

## 2. Extract the claims

Go through the whole transcript, not just the start. List every concrete feature, tactic, tip or factual claim, one line each, with the timestamp where it starts (m:ss). Merge repeats. Skip filler, sponsor reads and calls to subscribe (note a sponsor once if there is one).

Tag each line as one of:
- **Product claim**: a tool or feature does something, costs something, is available somewhere, or was released.
- **Tactic**: a method or workflow the viewer could copy.
- **Stat**: a number presented as fact.
- **Opinion**: the creator's view.

Auto-generated captions mangle names (products, people, brands). When a name looks garbled or a tool is referred to but not named, flag it as "unclear in captions" and work out what it is only from an official source. Never guess a name.

## 3. Check the claims

**Scope.** Check every product claim about the main products the video is about. Side mentions (other tools, competitors) only need checking if they make the top 3 or the user asks.

**Where.** Only the **official** source, opened in this run: the vendor's docs, help centre, changelog, release notes or pricing page. Not a blog, not another video. Plan limits and regions are usually on help pages, not the pricing page: check there too. Record the exact link you opened and today's date. If a page is cut off before the part you need, try the page's section link or a more specific page; if you still cannot see it, mark the claim Unverified and say the page was too long to read.

**Status** for each:
- **Verified**: the official source says so.
- **Partly true**: true, but with limits the video leaves out (plan, region, platform, waitlist, beta). Name the limits.
- **Changed**: it was true but the docs now differ. Say how.
- **Unverified**: no official source found, or you could not open it.
- **Wrong**: the official source contradicts it.

**Stats.** If the creator names a source, open it and read the figure. If they don't, do one quick search for the original; if you find it, report what it actually says (wording mismatches matter: "3% of a bank's customers" is not "3% of Americans"). If you can't find or open it, mark it Unverified and never repeat the number as fact.

If you have no web access in this environment, say so at the top of the briefing and mark every product claim Unverified. Never recommend an unverified feature as if it works.

## 4. Fit it to the user

Use what you already know about the user from this conversation and their project instructions: tools, plan, business, goals, and **country** (features are often region-locked). If you know nothing, ask one short question before ranking: "What do you want from this video, and where are you based? (for example: tools to try, marketing ideas, a fact check)". If they skip it, rank for a general audience and say so.

Drop anything that does not fit their setup, plan or region. Be honest when a video is mostly hype: "nothing here worth acting on" is a valid result.

## 5. Rank the top 3 actions

At most three. For each:
- **Action**: one sentence, starting with a verb.
- **Why**: the outcome it buys.
- **Cost**: money, plan tier, credits, platform or region as the official source states it ("free on all plans", "needs a paid plan and the Mac app", "unknown"). Do not estimate hours.
- **Source**: the timestamp it came from and the doc link if it is a product claim.

Rank by value to this user over effort. Anything that costs money or changes a plan is flagged, never switched on. If the video is pushing a shiny new tool that would replace something the user already has working, say so in one line ("shiny object check"). Everything else goes under **Parked**, one line each.

## 6. Output

Reply in chat with this shape. Keep it scannable.

```
# <Video title>
<Channel> | uploaded <date> | <length> | <link>
Transcript: <manual or auto-generated>, <language> | Checked: <today's date> | Ranked for: <who, or "general audience">
<If no web access: "No web access here, so every product claim is Unverified.">

**TL;DR:** two lines on what the video is and whether it is worth the user's time.

## Top 3 actions
| # | Action | Why | Cost | Source |
|---|--------|-----|------|--------|

## Claims checked
| Time | Claim | Status | Official source |
|------|-------|--------|-----------------|

## Stats and opinions
- m:ss  the stat or opinion, and what you found (stats) or "opinion" (no check needed)

## Tactics worth knowing
- m:ss  one line each

## Parked
- one line each, with why

**Unclear in captions:** names you could not confirm, or "none".
**Shiny object check:** one line, or "none".
```

If the user wants it saved, write it to `youtube-breakdowns/<today's date YYYY-MM-DD>-<short-slug>.md` inside the folder Claude is currently working in (create the folder if needed) and give the full path.

## Rules
- Summarise in your own words. Never paste the transcript or long quotes: one quote under 15 words at most.
- Every product claim and stat carries the official link you opened, or is marked Unverified.
- Separate what the video says from what you checked and from your own judgement. Never present inference as a finding.
- Do not buy, subscribe, sign up or change any setting the video recommends. Flag it for the user.
- Long videos (over about an hour): work through the transcript in sections so the later parts are covered too; say if anything was skipped.
- Match the user's spelling conventions (for example Australian or British English if that is what they use).
