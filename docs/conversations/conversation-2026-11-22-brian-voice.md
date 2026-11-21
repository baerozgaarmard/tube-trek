# Session Log: 10-Short Batch Production & YouTube Scheduling

- **Date**: 2026-11-22
- **Channel**: Baerozgaarmard
- **Voice Engine**: Microsoft Edge TTS (`en-US-BrianMultilingualNeural`)
- **Acoustic Profiling**: Warm American baritone (`-2Hz` pitch, `-3%` conversational tempo)
- **Status**: 10/10 Videos Rendered & Scheduled Successfully on YouTube

---

## 1. Context & User Directives
1. **Voice Selection**: User verified the audition studio ([dan_voice_audition_studio.html](file:///C:/Users/ayush/.gemini/antigravity/brain/bf2b5cb8-abb7-4975-aae7-8a7e07e3c970/dan_voice_audition_studio.html)) and selected **Brian (Multilingual Neural)** as the studio-grade, uncompressed conversational narrator.
2. **Quality Standards**:
   - Zero recycled scripts (peer-reviewed astronomy, quantum anomalies, genetics, neuroscience).
   - Zero repeated visual assets via `used_media_registry.json` deduplication.
   - 45–56s duration matching YouTube Shorts retention sweet spot.
   - Word-level kinetic subtitle styling and tension sub-bass audio beds.
   - 12-hour spaced scheduling cadence (08:00 AM & 08:00 PM IST) to avoid spam filters and audience cannibalization.

---

## 2. Production Manifest & Scheduled YouTube Links

| # | Title | Scheduled Release (IST) | YouTube Link | Local Master File |
|---|---|---|---|---|
| 1 | **Are Dinosaur Fossils Orbiting On The Moon? 🦖🌙** | Mon, Nov 23 @ 08:00 AM | [Watch on YouTube](https://www.youtube.com/watch?v=gDOcCnPJd3M) | `output/dinosaur_fossils_on_the_moon/final_short.mp4` |
| 2 | **The Ghost Force Haunting NASA Spacecraft 🚀** | Mon, Nov 23 @ 08:00 PM | [Watch on YouTube](https://www.youtube.com/watch?v=4hlM4HsfQdU) | `output/the_flyby_anomaly_gravity_kick/final_short.mp4` |
| 3 | **The Creepiest Sound In The Universe Is 57 Octaves Deep 🌌** | Tue, Nov 24 @ 08:00 AM | [Watch on YouTube](https://www.youtube.com/watch?v=Z-dbFcIpcVo) | `output/perseus_black_hole_lowest_sound/final_short.mp4` |
| 4 | **We Are Living In The Universe's Only Golden Age 🔭** | Tue, Nov 24 @ 08:00 PM | [Watch on YouTube](https://www.youtube.com/watch?v=LsiVg2dk-9c) | `output/the_end_of_starlight_lonely_future/final_short.mp4` |
| 5 | **The Man Who Woke Up Seeing Cats On Every Human Face 🐱** | Wed, Nov 25 @ 08:00 AM | [Watch on YouTube](https://www.youtube.com/watch?v=XodNc-6TSfI) | `output/the_man_who_saw_cats_in_faces/final_short.mp4` |
| 6 | **The Real-Life Wolverine: The Family With Unbreakable Bones 🦴** | Wed, Nov 25 @ 08:00 PM | [Watch on YouTube](https://www.youtube.com/watch?v=F3ZMOSSpKxM) | `output/unbreakable_skeleton_lrp5_mutation/final_short.mp4` |
| 7 | **The Appalachian Family That Was Born Bright Indigo Blue 💙** | Thu, Nov 26 @ 08:00 AM | [Watch on YouTube](https://www.youtube.com/watch?v=DJt1ULQMAUw) | `output/the_blue_people_of_kentucky/final_short.mp4` |
| 8 | **The 4% Measurement Error That Broke Modern Physics ⚛️** | Thu, Nov 26 @ 08:00 PM | [Watch on YouTube](https://www.youtube.com/watch?v=c6lV-2Lfasc) | `output/the_proton_radius_puzzle/final_short.mp4` |
| 9 | **NASA Detected Particles Shooting Up Out Of Antarctica 🧊** | Fri, Nov 27 @ 08:00 AM | [Watch on YouTube](https://www.youtube.com/watch?v=hjCHTu-uBMI) | `output/the_anita_cosmic_ray_inversion/final_short.mp4` |
| 10 | **The Last Physical Object That Will Ever Exist 🌌** | Fri, Nov 27 @ 08:00 PM | [Watch on YouTube](https://www.youtube.com/watch?v=ssLcxm7LpIk) | `output/the_iron_star_era_last_object/final_short.mp4` |

---

## 3. Engineering & Bugfixes Implemented
- **Bugfix**: Guarded against `None` image paths in `video/creator.py` (`paths = (image_map or {}).get(sid) or []`).
- **Clean State**: Deleted previous failed test uploads from YouTube before launching full batch.
- **Deduplication**: Verified that all visual queries across the 10 videos pulled unique assets logged in `used_media_registry.json`.
