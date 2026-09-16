# Corrections

Every wrong number I have published, what it should have been, and what caused it. Dated, in
reverse order. Nothing here is deleted or quietly edited: a wrong number corrected in silence is
worth a wrong number.

If you find another one, open an issue. I would rather be corrected than believed.

---

## 2026-09-15 — I called `sorted(v)[len(v)//2]` a median, and it is not one

**Published:** ×8.54 and ×8.62 for Piper, in three articles.
**Correct:** ×8.53 and ×8.59.

My measurement scripts computed `sorted(ratios)[len(ratios)//2]` and labelled the result "median".
On an **odd** number of runs that is correct. On an **even** number — my four Piper passes — it
returns the upper of the two middle values instead of their mean. So the label was wrong and the
number was wrong with it, in the second decimal, in three places.

Found by extracting the figures from the JSON to write with, instead of copying them from my own
earlier prose. The scripts now use `statistics.median`. The published ranges were replaced by the
full min–max, which does not depend on a convention.

**What it cost:** nothing in any conclusion — the ranges overlap either way. That is exactly why it
survived: an error that changes no conclusion has nothing to make it visible.

## 2026-09-15 — "the ratio degrades with text length" was an artefact of a single run

**Published:** Kokoro "degrades from ×0.93 to ×0.75 going from 505 to 950 characters", with an
unknown drawn about Piper from it.
**Correct:** **neither engine degrades with length.** Both are slightly faster on the long text —
Piper ×8.12 → ×8.58, Kokoro ×0.93 → ×0.95 — re-measured on both lengths in one session.

The ×0.75 came from a **single** measurement taken during a video production, not from a length
effect. I had generalised from one run.

**And the explanation I first published for it was also wrong.** I wrote that the machine "must have
been busy". Untested, and false. The real cause, measured afterwards, is **text segmentation** —
which is how the per-call cost finding in this repository was found. A wrong number led to a real
result only because the *explanation* got measured instead of asserted.

## 2026-09-15 — three of my articles gave three different Kokoro ratios for the same episode

Not a correction of a printed digit but of a contradiction, and the most useful thing in this list.
The cause: my video chain synthesises **sentence by sentence** (22 chunks averaging 43 characters)
while my benchmark passed **12 whole shots** averaging 79. Measured in one session: Kokoro loses
**8 %** to fine segmentation (×0.95 → ×0.87, ≈0.51 s fixed cost per call) and **Piper loses
nothing** (×8.38–×8.59 on 12 chunks against ×8.50–×8.66 on 22 — two overlapping ranges).

This is an argument *for* Piper that I had not seen, and it comes from its per-call cost rather
than its raw speed.

## 2026-09-14 — an arithmetic error of my own, in a percentage I had computed

**Published:** going from CRF 23 to CRF 32 "lightens the picture by 43 %".
**Correct:** **41.1 %**. Redone from figures already published in the same article: the picture
alone goes from 2,074,372 − 875,130 = 1,199,242 bytes to 1,581,776 − 875,130 = 706,646, so −41.1 %.

The other figures in that passage — 42 %, 55 %, 23.7 % — were correct. Caught while re-reading my
own tables.

## 2026-09-14 — two gains reported against two different baselines

The two gains from `-preset slow` were measured against different reference files: one on material
A, the other on material B. They are now both reported against the same `medium` file. The printed
percentages, 0.16 % and 2.17 %, do not change — but the comparison they invited was invalid.

---

## What these five have in common

Four of the five were found by **re-reading my own data while writing**, not by an external
reviewer and not by a test. The one exception — the segmentation contradiction — was found because
three published numbers disagreed with each other, which is the one failure mode that cannot hide.

So the practice that actually catches errors, in my experience of five of them, is: **extract every
figure from the data file at writing time, and never copy one from your own earlier prose.**
