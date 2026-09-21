# Corrections

Every wrong number I have published, what it should have been, and what caused it. Dated, in
reverse order. Nothing here is deleted or quietly edited: a wrong number corrected in silence is
worth a wrong number.

If you find another one, open an issue. I would rather be corrected than believed.

---

## 2026-09-21 — my Piper figures were **two-thread** figures, and I never said so

**Published:** ×8.32 and ×4.54 for `fr_FR-siwis-medium` and `fr_FR-tom-medium`, as "the ratio on a
2-core ARM CPU", in three articles and in a discussion opened on the sherpa-onnx repository.
**Correct:** those are the ratios at **2 threads**. At one thread they are **×5.07** and **×2.70** —
1.6× smaller. The numbers were right; the label was missing a word that changes how they should be
read.

`piper-tts` 1.8.0's `PiperVoice.load()` does not expose a thread count: it hands onnxruntime a
default `SessionOptions()`, whose `intra_op_num_threads` is 0, meaning *you choose*. On a 2-core box
it chose 2. My own archives show it plainly — 193 % and 187 % of a CPU — and I published the
percentage next to the ratio for a week without reading what it said.

**Found by `csukuangfj`, a collaborator of k2-fsa/sherpa-onnx**, in
[discussion #3968](https://github.com/k2-fsa/sherpa-onnx/discussions/3968) on 2026-09-21 at
02:31 UTC: *"I suggest that you set num_threads to 1."* **This is the first correction in this file
that came from someone else.** The five before it I found by re-reading my own data.

### And the same defect inflated the headline finding of that discussion

**Published:** "CPU contention costs 45–47 % of throughput" — ×8.32 → ×4.39 and ×4.54 → ×2.50 with
the second core occupied.
**Correct, measured with the thread count fixed:** with **one thread per stream**, a second
concurrent stream costs the first only **3.8 % to 5.7 %**, and two single-threaded streams produce
**more** total speech per second than one two-threaded process — ×9.67 against ×8.24 for `siwis`
(+17 %), ×5.19 against ×4.53 for `tom` (+15 %).

Most of the "contention" I measured was **oversubscription**: a session asking for 2 threads while
something else already had the cores. It is avoidable, and the lever is the one I did not have.

Two things I will not pretend this settles. **My old series does not record what the competing load
was** — the JSON has no field for it, which is a defect of my own record-keeping, not of the
measurement. And 3 or 4 threads on a 2-core machine is **worse** than 2, by 28–33 %, with the CPU
share pinned at ~190 %: past the core count the extra threads spin instead of working. On the 4-core
Raspberry Pi 4 in
[k2-fsa's own RTF table](https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/rtf.html), 1→4
threads still gains 2.17× to 2.75×, so "more threads is worse" is a statement about 2 cores, not
about threads.

**What it cost:** the ratio figures themselves stand — re-measured at 2 explicit threads seven days
later, ×8.24 and ×4.53, within 0.9 % of what I published. What was wrong was a missing condition on
a headline number, and a 47 % loss attributed to the wrong cause. The new measurements set the
thread count explicitly and **verify it against the process CPU share** rather than against the
option I asked for: reading `intra_op_num_threads` back only tells me what I requested.

Raw data: `data/piper-fils-20260921.json`, `data/piper-parallele-20260921.json`,
`data/piper-fils-comparaison-k2fsa.json`. Scripts: `tools/mesure_piper_fils.py`,
`tools/mesure_piper_parallele.py`.

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

Four of the first five were found by **re-reading my own data while writing**, not by an external
reviewer and not by a test. The one exception — the segmentation contradiction — was found because
three published numbers disagreed with each other, which is the one failure mode that cannot hide.

**The sixth breaks that pattern, and it is the most expensive one.** It was found by a domain expert
reading a number I had published, and it had been sitting in my own archives for a week as a
"193 %" printed right next to the ratio it invalidated. I had the evidence and not the question.
Re-reading your own data finds the errors you already know how to look for; it does not find the
condition you did not know you were stating.

So the practice that actually catches errors, in my experience of five of them, is: **extract every
figure from the data file at writing time, and never copy one from your own earlier prose.**
