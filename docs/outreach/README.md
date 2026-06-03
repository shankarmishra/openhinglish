# OpenHinglish — Outreach Posting Playbook

> **Read this before posting anything.** The V0.1 lexicons are tiny and real-world coverage is near-zero. Posting before the GitHub repo is public, or overclaiming capability before V1, will burn the first-impression opportunity. This playbook is staged accordingly.

---

## Files in this directory

| File | Platform | Audience |
|---|---|---|
| `show-hn.md` | Hacker News (Show HN) | Technical, international, skeptical |
| `reddit.md` | r/developersIndia, r/india, r/MachineLearning | Three different audiences — use the right version for each |
| `linkedin.md` | LinkedIn | Professional network, Indian AI ecosystem |
| `x-thread.md` | X / Twitter | Developer community, Indian ML/AI circle |
| `devto-article.md` | Dev.to / Hashnode | Long-form technical audience, good for SEO |

---

## Posting order and rationale

Post in this sequence. Each step is gated on the previous completing successfully.

### Stage 0 — Prerequisites (do before any posting)

- [ ] GitHub repo is public with a complete README (one-liner demo, honest state note, contribution instructions)
- [ ] At minimum the `pip install` route works OR the README clearly explains that PyPI is coming at V1
- [ ] The GitHub link in every post below is updated from `[placeholder]` to the real URL
- [ ] You have reviewed every draft for overclaiming — nothing in any post claims audio output or production-ready coverage

### Stage 1 — Developer-facing first (highest trust, highest signal)

**1a. Dev.to article** — Publish first. It is indexable, linkable, and provides a canonical long-form reference you can link from everything else. Title: "Why Hinglish breaks Indian AI (and an open-source fix I'm building)". Publish with the `nlp`, `opensource`, `india`, `python`, `machinelearning` tags.

**1b. Show HN** — Post within 1–2 days of the Dev.to article going live. The best submission windows for HN are weekday mornings (US Eastern time, roughly 8–10am ET) but Indian-dev-relevant posts can also do well on weekday evenings IST when the audience is online. Post once, do not resubmit if it doesn't trend — resubmitting is flagged as spam.

**1c. r/MachineLearning** — Post the ML-specific version. r/ML readers are technical and international. Lead with the architecture, be honest about V0.1 status. Do not post here without the Dev.to article live — you need something to link to for credibility.

### Stage 2 — Indian community (48–72 hours after Stage 1)

**2a. r/developersIndia** — Post the dev-specific version. This subreddit is high-engagement for Indian developer projects. Check the subreddit rules before posting (some require flair or specific formatting). Respond to all comments within the first 2 hours — that window is when the post has the most algorithmic lift.

**2b. LinkedIn** — Post the LinkedIn version. Best posting windows for Indian professional audience: Tuesday–Thursday, 9–11am IST or 7–9pm IST. Use all listed hashtags. Tag 0 people in the post text itself — it looks promotional. If contacts engage, reply.

**2c. r/india** — Post the general-audience version. Lower technical density than r/developersIndia. Emphasize the user experience (mispronounced app audio) rather than the architecture. Do not post the code block in this version.

### Stage 3 — X thread (after Stage 1 and 2 have settled)

Post the X thread 3–5 days after the Reddit/LinkedIn wave. By then you will have gathered real feedback and can incorporate it ("people have been asking about X — here's why I designed it this way"). Post the thread as a single connected thread, not 8 separate unrelated tweets. Best time: weekday mornings IST (8–10am) or evening (8–10pm IST) for Indian reach.

---

## Timing guidance for Indian developer audience

| Day | Best window (IST) | Notes |
|---|---|---|
| Monday | Avoid | Start-of-week, lower engagement |
| Tuesday | 9–11am, 7–9pm | Strong engagement |
| Wednesday | 9–11am, 7–9pm | Peak mid-week |
| Thursday | 9–11am, 7–9pm | Good |
| Friday | 9–11am | Morning only; afternoon/evening drops off |
| Saturday | 11am–1pm | Good for r/developersIndia |
| Sunday | Avoid for HN; ok for Reddit/LinkedIn | |

For Hacker News: US morning time (8–10am ET = 6:30–8:30pm IST) is the standard advice. The HN audience is predominantly US/EU — the Indian developer angle is interesting and human but HN rewards technical substance over regional relevance.

---

## Do's

- **Engage with every substantive comment** within the first 2–4 hours of posting. This is the highest-leverage activity after posting. Answer technical questions directly. If someone points out a flaw, acknowledge it — do not get defensive.
- **Be honest about limitations** in your replies, not just the post text. If someone asks "does it handle Tamil?" the answer is "Not yet — V0.1 is Hindi-only."
- **Welcome criticism.** People who say "I tried this and it broke on X" are doing you a favor. Thank them, ask for the input string, open an issue.
- **Update posts if something significant changes.** If you publish and then fix a major bug, edit the Dev.to article with a note at the top.
- **Cross-link.** Your Dev.to article should link to the GitHub. Your Show HN should link to the Dev.to article for depth. Your LinkedIn post can link to all of them.

## Don'ts

- **Do not post before the repo is public.** A link that goes to a 404 kills trust.
- **Do not spam multiple subreddits on the same day.** Reddit tracks posting patterns. Post one subreddit per day at minimum.
- **Do not cold-DM people** to promote the project. If someone engages with your post, replying in the thread is fine. Sliding into their DMs to ask them to try your library is not.
- **Do not overclaim the benchmark score.** The 1.000 n-best on the 6-row IndianTTSBench-mini is not evidence of production quality. Do not cite it without the methodology disclaimer.
- **Do not claim audio output.** OpenHinglish produces text. The TTS engine produces audio. These are two separate systems. Any post that implies OpenHinglish "generates speech" or "creates voice" is technically incorrect.
- **Do not post to AI4Bharat or Sarvam communities before V1.** Those communities have high technical expectations. A V0.1 demo with near-zero real-world coverage will not land well and is not the right first impression.
- **Do not delete negative comments** or engage combatively. Transparent moderation builds trust; defensive behavior destroys it.
- **Do not buy followers, upvotes, or engagement.** Obvious, but worth stating.

---

## Engagement after posting

### What counts as success at V0.1

Realistic success metrics for a V0.1 launch of a solo project with near-zero real-world coverage:

- 5–10 GitHub stars in the first week (not a vanity metric — it shows real developer attention)
- 2–3 people reporting UNKNOWN tokens on their own text (signal that actual users tried it)
- 1 TSV PR from someone not you (the flywheel taking one turn)
- One substantive comment from someone who has built Hinglish normalization before

Do not measure success by post views, impressions, or upvote counts. Measure it by meaningful signal: GitHub stars, issues opened, PRs submitted, DMs with specific technical questions.

### Responding to common questions

**"Why not just use an LLM to normalize it?"**
Latency, cost, and non-determinism. An LLM preprocessing call adds 300–1000ms and a per-token cost to every TTS request. OpenHinglish is deterministic and CPU-only — it adds microseconds, not seconds. An LLM will also hallucinate brand pronunciations. The trade-off is explicit: lower coverage now, community-growable, auditable, free.

**"This exists already — [IndicXlit / some internal tool]"**
IndicXlit handles transliteration but not abbreviation expansion, brand gazetteers, or the display/tts split. Internal tools are not community-maintained and are not sharable. If you know of a public library that covers this gap, share it — the goal is the problem being solved, not being the one who solves it.

**"The lexicons are tiny — when will this actually work?"**
V1 target: 10,000+ Roman-Hindi entries, 500+ brand forms, 5,000+ names, 300-row benchmark. Timeline depends on lexicon contribution pace. The honest answer is: it's limited now, and the timeline shortens with every TSV PR.

**"Will you add [Tamil / Telugu / Marathi]?"**
V2 roadmap, language maintainer required. Interested in maintaining a language? Open an issue.

---

## Checklist before first post

- [ ] GitHub repo is public
- [ ] README has: one-liner demo, honest state note ("V0.1, limited coverage"), contribution instructions
- [ ] All GitHub links in drafts are updated to the real URL
- [ ] Every draft has been reviewed — no claim of audio output anywhere
- [ ] The 1.000 benchmark score is not cited anywhere without its disclaimer
- [ ] You have time to monitor and respond to comments for the first 4 hours after posting
- [ ] Dev.to article is published and indexed before Show HN post goes up
