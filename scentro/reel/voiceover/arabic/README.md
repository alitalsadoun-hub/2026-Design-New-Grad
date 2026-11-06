# Arabic voice-over samples (ElevenLabs, model eleven_v4) - approved script, wording unchanged
Prompt (delivery tags are not spoken): `[warmly] [softly] عطور بتحبيها... بروائح بتعرفيها. [short pause] اكتشفي مجموعتنا النسائية من ماد، مع سنترو. [short pause] [playfully] واطلبي عطرك المفضل من سنترو جو دوت كوم.`
- A: "layla - modern Arabic calm" (voice_id g3YpdjT1OTh9cunaumJs, labelled ar-jordanian) - 10.5 s, -19.6 LUFS, peak -2.8 dBFS. 173 credits.
- B: "Mimi - Lebanese (Beirut)" (voice_id NQyF5U0t336unYhQXcuv, ar-levantine) - not generated yet (ElevenLabs reported free generations busy).
Commercial-use permission NOT verified (plan/voice licence must be checked in the ElevenLabs account).

## Revised sample (Layla, eleven_v4) - final approved 3-line script, no spoken URL
Prompt: `[brightly] [warmly] عطور بتحبيها... بروائح بتعرفيها. [pause] [warmly] اكتشفي مجموعتنا النسائية من ماد، مع سِنترو. [pause] [playfully] واطلبي عطرك المفضل من سِنترو.` (163 credits; raw take 9.84 s = `layla_v2_raw_take.mp3`)
`scentro_ar_layla_v2_timed.mp3` (15.2 s, -16.1 LUFS, peak -4.8 dBFS): the same take cut at its natural pauses and placed with `place_ar_vo.py` -
lines start at 0.4 s, 6.3 s, 12.5 s; speech ends 14.8 s (CTA solo starts 16.4 s). Voice not stretched or altered.

## Continuous preview (no regeneration)
`scentro_ar_layla_v2_continuous.mp3` (10.2 s, -16.2 LUFS, peak -4.7 dBFS): the raw take as recorded (`layla_v2_raw_take.mp3`), only lead-in/tail trimmed so speech starts at 0.4 s (`make_continuous.py`).
Pauses are the take's own: 0.27 s (inside line 1), 0.43 s and 0.45 s (between lines). No stretch, no pitch change, no cuts between lines. Speech ends at 9.87 s.

## FINAL: Minimal Luxury Arabic voice-over (one take, Layla, eleven_v4) + complete Reel
Script (exact): الأناقة بتبدأ من التفاصيل. / وعطرك... واحد منها. / اكتشفي مجموعة ماد النسائية من سِنترو. / روائح متنوعة، اختيرت لتناسب أذواق مختلفة. / سِنترو... اكتشفي المزيد.
Prompt tags (not spoken): `[brightly] [warmly]` opening, `[pause]` between sentences, `[confidently]` on sentence 3, `[warmly]` elsewhere. 244 credits.
- `scentro_ar_final_layla_raw_elevenlabs.mp3` - the original ElevenLabs recording, unmodified (14.48 s).
- `make_final_vo.py` - adds only: 0.4 s lead-in, 15 ms fade-in, 40 ms fade-out, 75 Hz high-pass, loudnorm -16 LUFS/-1.5 dBTP, silence pad to 19.2 s. No stretch, no cuts.
- `../scentro_women_reel_v2_ar_final.mp4` - silent Reel V2 video stream copied bit-for-bit (md5 30add418...) + AAC 192k audio. Voice 0.4-14.8 s; CTA solo from 16.4 s.
Commercial-use permission for the ElevenLabs voice/plan NOT verified.

## v3 (refined script) - editorial cut edit
Script: الأناقة تبدأ من التفاصيل... / وعطرك، واحد من أهمها. / اكتشفي مجموعة ماد النسائية من سِنترو. / مجموعة من الروائح المميزة، لكل ذوق ولمسة مختلفة. / سِنترو... اكتشفي المزيد.
Prompt tags: `[confidently] [warmly]` (once), `[pause]` between sentences. Layla, eleven_v4, 216 credits. Original recording: `scentro_ar_v3_layla_raw_elevenlabs.mp3` (15.2 s, unmodified).
`../../scentro_women_reel_v3_ar.mp4` (19.4 s): hard cuts on phrase boundaries (render_reel_v3.py), voice 0.4-~15.5 s, CTA from 15.9 s (dissolve) / solo 16.4-19.4 s. Video stream = silent master `scentro_women_reel_v3_silent.mp4` (not tracked).
