---
name: bazi-ziwei-lesson-notes
description: >-
  Attend, capture, and clean up 八字 (BaZi / Four Pillars) and 紫微斗數 (Zi Wei Dou Shu)
  classes recorded by Fireflies, then turn each lesson into polished Traditional-Chinese
  study notes. Use whenever the user wants to: make sure their recurring 八字/紫微/命理/擇日/奇門
  lesson gets recorded by Fireflies; fetch a lesson transcript; fix garbled Cantonese
  speech-to-text terminology (e.g. 祿→鹿, 羊刃/陽刃→洋人, 驛馬→翼馬, 子→紫, 午→五火, 亥→害,
  旬空亡→胸膜, 魁罡→灰江, 流年→榴槤, 官星→觀星, 年柱→蓮柱, 廉貞→廉政, 天機→天璣, 化忌→法技/法記,
  紫府朝垣→子虎朝桓, 命宮→命工, 田宅宮→田澤公); summarise what was taught; or build structured
  study notes with concepts, 命例 case studies, and homework. Trigger on mentions of 八字,
  紫微, 紫微斗數, 命理, 神煞, 擇日, 奇門, lesson notes, class transcript, Fireflies recording of
  a 命理 class, or 「整理今堂筆記 / 清理 transcript / 補充術語」.
---

# 八字 / 紫微 Lesson Notes (Fireflies)

This skill helps a 命理 student (Angus) attend, capture, and study recurring
八字 / 紫微斗數 classes that are recorded by Fireflies. The classes are taught in
Cantonese and are dense with technical terms that speech-to-text mangles badly.

The skill does three jobs:

1. **Attend / capture** — make sure Fireflies records the lesson.
2. **Improve transcript quality** — apply a domain glossary to fix misheard terms.
3. **Produce study notes** — structured, cleaned, bilingual-friendly notes.

## Reference files (read these FIRST)

- `reference/glossary.md` — the Cantonese-STT → correct-term correction table, aligned
  to the user's own calculation engine (論八字/六壬/奇門, via
  `moira-web/src/lib/chinese` + `spirit-stars.json`). **Always load this before
  cleaning a transcript.** Its Appendix A holds the engine-canonical 神煞/十神/紫微
  catalog — when textbook and transcript disagree, prefer the engine spelling
  (e.g. 陽刃 not 羊刃, 孤辰 not 孤臣, 咸池=桃花, 八字用 殺 / 六壬用 煞). Appendix B logs
  newly-discovered mishearings per lesson.
- `reference/knowledge.md` — 八字 + 紫微 conceptual scaffold (used to recognise topics,
  expand garbled terms in context, and structure notes).
- `reference/notes-template.md` — the output template for a lesson's study notes.
- `reference/fireflies-custom-vocabulary.md` — the correct-spelling vocabulary list to
  paste into Fireflies → Settings → Custom Vocabulary, plus the "set language to 粵語/中文"
  advice. This *prevents* mishearings at source.

---

## Workflow 1 — Attend / capture a lesson

Fireflies auto-joins meetings that are on the connected calendar with a video link.
When the user asks to "make sure tonight's 八字/紫微 lesson is recorded":

1. Check the calendar (calendar MCP) and/or Fireflies upcoming/active meetings
   (`fireflies_get_active_meetings`) for the lesson. The class is a recurring Zoom
   meeting; recent instance titles were 「八字紫微」/「紫微八字」 (organizer
   `ilovegemini31@gmail.com`, Zoom `us02web.zoom.us/j/8282940253`).
2. Confirm Fireflies (Fred) is set to join. If the meeting isn't on the calendar or the
   notetaker isn't attached, tell the user how to add it (add the Zoom link to a
   calendar event Fireflies watches, or add the meeting in the Fireflies dashboard) —
   **do not fabricate that it's been scheduled.**
3. If the user wants this to happen automatically every week, offer to create a
   scheduled task that, a few hours after each class slot, runs Workflow 2+3 on the
   newest 八字/紫微 transcript and saves notes.

> This skill does not itself dial into Zoom. It relies on Fireflies' notetaker. If the
> user wants Claude to actively join/operate a Zoom room, that's a separate Zoom-bot task.

---

## Workflow 2 — Improve transcript quality (the core)

1. **Fetch the transcript.** Use `fireflies_search` with `keyword:"紫微"` or
   `keyword:"八字"` (or `fireflies_get_transcripts`) to find the lesson, then
   `fireflies_get_transcript` with the transcript id for full sentences.
   - ⚠️ **The Fireflies auto-summary is NOT enough** — it drops technical detail and
     repeats the STT errors. Always read the raw `fireflies_get_transcript` sentences.
   - ⚠️ **Watch for duplicate/parallel recordings** of the same class (two transcript
     ids, minutes apart, near-identical content). Verify before treating them as two
     different lessons.
2. **Load `reference/glossary.md`** and apply corrections section by section, in context:
   - 天干地支 homophones (炳→丙, 任→壬, 桂→癸, 鹿→祿, 紫→子, 五火→午火, 害→亥, 摔→戌…).
   - 十神 (觀星→官星, 吃神→食神…), 神煞 (金魚→金輿, 翼馬→驛馬, 灰江→魁罡, 大號→大耗,
     孤臣寡屬→孤辰寡宿, 胸膜/凶亡→旬空亡, 洋人→陽刃…), 十二長生, 命盤結構 (日署→日柱,
     連柱/蓮柱→年柱, 子女權→子女宮, 命工→命宮, 田澤公→田宅宮…), 紫微星曜 (廉政→廉貞,
     天璣→天機, 天童→天同…) + 四化 (法技/法記→化忌, 六拳→化權), 技法 (五虎盾→五虎遁,
     榴槤→流年, 調侯→調候…).
   - **Disambiguate**: only convert 子/午/巳/亥/申/酉/卯/寅 etc. when they clearly name a
     干支 (next to another 干支, or to 月/日/時/年/柱/水/火), not in ordinary speech.
3. **Repair structure**: collapse STT stutter loops (e.g. "繼續被人搞啊那你…" ×20,
   "夾夾夾…" ×40, "有有有…") to one instance; re-punctuate run-on sentences.
4. **Re-attribute speakers**: labels often swap "Master" and "S5_余均揚". Assign lines by
   content — the one explaining doctrine is the 老師 (阿松); the student is Angus.
5. **Separate lesson from chit-chat**: park work/relocation small-talk; keep the 命理 teaching.
6. **Output a cleaned transcript** (faithful, just corrected) when the user wants the raw
   cleaned text. Otherwise proceed to Workflow 3.

### Correction principles

- Preserve the teacher's wording and Cantonese voice; **fix terms, not style**.
- **Never invent doctrine.** If a garbled passage can't be confidently mapped, mark it
  `【聽不清：原文…】` rather than guessing.
- Keep a short **"corrections applied"** list so Angus can cross-check against the original.

---

## Workflow 3 — Build study notes

1. Use `reference/notes-template.md` as the structure.
2. Fill: 本課主題 → 概念精要 (each concept: correct term → teacher's framing → how-to-judge)
   → 命例分析 (each real chart: background, key features, which 神煞/十神/星曜 confirmed it,
   takeaway) → 校正術語表 → 行動項/功課 → 下次預告.
3. Cross-reference `reference/knowledge.md` so concepts are explained correctly and
   consistently.
4. **Save** the notes as a Markdown file in the user's vault under `玄學/{科目}/課堂筆記/`
   (e.g. `玄學/紫微八字/課堂筆記/`, `玄學/奇門/課堂筆記/`), named `命理筆記_{YYYY-MM-DD}_{主題}.md`. Add frontmatter
   (title/type/source/created/tags) and `[[wikilinks]]` per the vault's CLAUDE.md
   conventions. Offer a `.docx` version if the user wants to print/share.
5. Present the file. Keep the chat summary short.

---

## Notes & guardrails

- Output notes in **繁體中文 / 粵語-friendly** wording to match the class; technical terms
  in standard 命理 Chinese.
- This is for the user's **own study**. 命理 content is presented as the teacher's
  teaching, **not** as predictive fact about real people.
- If asked to analyse a real person's chart for high-stakes decisions, frame it as study
  material and avoid deterministic claims.
- **The glossary grows over time**: when a new lesson reveals a new mis-hearing, append
  the pair to `reference/glossary.md` (Appendix B).
