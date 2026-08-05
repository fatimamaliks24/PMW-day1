# Week 1 Reflection — PMW Ice-Breaker Review

**Fatima Malik** | AI & 3D Reconstruction Intern, Preserve My World
Repo: `PMW-day1` | Live site: https://fatimamaliks24.github.io/PMW-day1/

---

## 1. What prompt worked

I gave the AI reviewer everything at once, upfront: the actual `index.html` and `README.md` files, plus the module's own grading criteria (branding, GitHub setup, clarity, consistency, mission fit) and the explicit instruction to score and rank fixes by impact — not give generic praise.

This worked because it removed room for vague feedback. Instead of "looks good, maybe add more detail," I got a scorecard with specific numbers and a ranked list of five concrete fixes, in priority order. Framing it as a *strict* review, per the "strict weekly audit" prompt pattern, mattered — a softer prompt like "can you check this?" tends to get politeness instead of critique.

## 2. What failed / needed a second pass

The first attempt to add a live GitHub Pages link **guessed the URL** from the README's title (`PMW-Day-1`) instead of pulling it from the actual repo settings. That produced a broken link: 404 not found.

The real repo slug was `PMW-day1` (lowercase "d," no hyphen before "1") — a small casing/formatting difference that GitHub Pages treats as a completely different URL. The fix required going back to the actual Pages settings screen, copying the exact URL, and correcting the README rather than trusting an inference from the repo name mentioned in prose.

**Lesson:** any AI-generated link, path, or identifier that depends on an external system (a live URL, a filename, a branch name) needs to be pulled from the source of truth, not inferred from context clues in a document.

## 3. What I verified manually

- Confirmed the actual repo name and exact casing via GitHub Settings → Pages, rather than trusting the README title.
- Confirmed GitHub Pages was enabled and pointed at the `main` branch, with `index.html` at the root (not nested in a subfolder).
- Clicked the corrected live link myself to confirm it resolved before treating the fix as done.
- Read through both the portfolio page and README edits line by line to confirm nothing was changed outside what I asked for (no unintended content, no broken HTML).

## 4. What I'll do differently next week

- Provide the exact repo URL/slug upfront when asking AI to reference it, instead of letting it infer the name from a README title or casual mention.
- Ask for an explicit verification checklist *before* committing any AI-suggested change involving external links, filenames, or paths — not just after something breaks.
- Test every generated link personally before considering a task finished, since a broken link is invisible in the code itself and only shows up when clicked.

---

## 5. Before → After: what actually changed

| # | Before (original submission) | Mistake | After (improved) |
|---|---|---|---|
| 1 | README described the portfolio page but gave no way to view it | Reviewer had to clone the repo to see any output | Added a live GitHub Pages link at the top of the README, verified against actual Pages settings |
| 2 | Portfolio contact section listed only Email and LinkedIn | Missing GitHub link is a real gap for a CS student's site | Added a GitHub contact link (`fatimamaliks24`) alongside Email and LinkedIn |
| 3 | Stats section read "Actively seeking internships & projects" right next to an "● Active" internship badge | Contradicted itself — implied I was both actively interning and actively job-hunting for the same thing | Reworded to "Open to research collaborations & new projects," removing the contradiction |
| 4 | README's "About" and "What I Learned" sections used generic onboarding language ("I learned how to create a GitHub repo") | Could have described any first Git commit by anyone — not specific to this deliverable | Rewrote both sections to describe the actual build (custom CSS-variable theming, sticky nav, hero section, PR workflow) and why documentation/live links matter |
| 5 | Skills section listed generic "Machine Learning / Computer Vision" while Experience mentioned COLMAP, NeRF, and Gaussian Splatting | Mission-relevant work (3D reconstruction) wasn't visible where a reviewer looks first | Added "3D Reconstruction" as a Skills tag to align with the Experience section |
| 6 | First fix attempt introduced a broken (guessed) live link | Assumed a URL instead of verifying it | Corrected the link to the exact repo URL (`PMW-day1`) after checking GitHub Pages settings directly |

---

## Summary

The core lesson from this round wasn't about HTML or CSS — it was about **verification discipline**. AI review caught real, specific gaps (missing link, missing GitHub reference, contradictory copy) fast. But the one mistake introduced *by* AI assistance — a guessed URL — only got caught because I actually clicked the link instead of assuming it worked. Going forward, the checklist step isn't optional polish; it's the difference between a fix that looks done and one that actually is.
