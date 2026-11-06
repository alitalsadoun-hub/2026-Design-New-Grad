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
