# Session Log: YouTube OAuth Recovery & Live Performance Analytics Audit

- **Date**: 2026-11-26 (01:42 IST)
- **Channel**: `@baerozgaarmard` (`95` subscribers, `27,979` total channel views, `63` total videos)

## 1. OAuth Token Recovery
- Diagnosed why `youtubeAnalytics` and reporting stalled: `youtube_token.pickle` hit Google's `invalid_grant` 7-day Testing expiration.
- Re-authenticated via local OAuth callback (`reauth_youtube.py`) with all 4 scopes saved (`youtube.upload`, `youtube.readonly`, `yt-analytics.readonly`, `youtube.force-ssl`).

## 2. Live Performance & Retention Audit
- **Channel Traffic Cliff**: Shorts Feed views dropped from **10,038** (`Nov 14–19`) to **386** (`Nov 20–26`) — a **96.2% drop** triggered immediately after the Nov 16 (9 simultaneous releases) and Nov 20 (5 uploads in 17h) bursts alongside low-retention misfires on Nov 18–21.
- **Retention Proof on Cosmic Shorts** (through settled Analytics window `Nov 23–24`):
  - `tv5mM-wvckI` (*The 330-Million-Light-Year Void*, Nov 22): **12 views**, **43s AVD**, **85.3% retention**
  - `Z-dbFcIpcVo` (*Creepiest Sound In The Universe*, Nov 24): **40 live views** (`20` settled in Analytics), **45s AVD**, **82.3% retention**
  - `0liXjBNq9UI` (*The Cosmic Bruise*, Nov 22): **16 views**, **2 likes**, **32s AVD**, **69.7% retention**
  - Contrast with misfires: `oj3CFAQADy8` (`12.1%` ret), `4hlM4HsfQdU` (`6.9%` ret / 3s AVD), `gDOcCnPJd3M` (`0` engagedViews).
- **Scheduled Queue Verified**: All **14 upcoming Shorts** (`4` Batch 1 + `10` Batch 2) are `private` + `processed` with exact `publishAt` timestamps intact (`Nov 26 – Dec 02`).
