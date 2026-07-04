# How this was made

This project was built by one person, in extended dialogue with several AI
systems — Codex (OpenAI, GPT-5.5), Claude (Anthropic, Opus 4.8), and Fable. I want
to be clear about that, and clear about what it did and did not mean, because "made
with AI" now covers everything from honest collaboration to hiding the absence of
work.

It was not used to write this for me.

It was used to argue against me — and, more importantly, to build an instrument
that could catch me cheating even when the arguing failed.

## The working method

The shape of the work was adversarial on purpose. I would bring a hypothesis —
that a learner could derive structure from minimal contact, that a stability check
proved a result was real, that more data would extend the reach of a test — and the
job of the models was to try to break it. Most hypotheses broke. The strong version
of the central dream broke in three different, measurable ways. What survived being
attacked is what made it into the essay and the experiments.

Concretely, the division of labour looked like this:

- **Claude** was the reasoning partner — used to stress-test ideas, find where an
  argument quietly assumed its own conclusion, surface prior work I should have
  known (the Locatello identifiability theorem, the Kleindessner–von Luxburg
  estimator), and push on the writing until it said what I actually meant. When a
  claim in the essay is careful — "this looks like a limit, not a proof"; "a
  discrimination boundary, not a recovery boundary" — that caution is usually the
  residue of an argument I lost to it first.

- **Codex** was the engineering partner — used to build, run, and audit the
  experiments: the tiny worlds, the blind estimators, the preregistrations, the
  leakage scans, the negative controls, and the thousands of seeded runs behind
  every reported number. It also extracted this repository from the larger research
  forge, keeping the harness-valid results physically separate from the
  superseded-invalid ones.

## The knife

The part of this I am most confident about is not a result. It is the instrument.

Going in, I believed my experiments were disciplined. Then I audited the work as a
hostile reviewer would, and the audit found the author's own errors first:
thresholds registered *after* seeing results, an "audit" that certified cleanliness
by returning a hardcoded yes, a learner reading an answer through a side channel I
had built and forgotten. So the discipline had to stop being a belief and become a
constraint — a gate harness that refuses to certify a result lacking provenance,
and a commit hook that makes the order of preregistration physically visible.

The most encouraging moment of the project was an *invalid* result: a run that
produced clean numbers and then marked itself `INVALID`, because it had not passed
through the enforcing pipeline. That is why this repository keeps its
[`superseded_invalid/`](https://github.com/Kirill-Kruglov/proxylimen/tree/main/experiments/superseded_invalid)
experiments in plain sight. They are not clutter. They are the evidence that the
method found and marked my own mistakes — and made them physically hard to cite.

Neither model was treated as an authority. A claim survived only when it was still
standing after repeated attempts to break it — sometimes by me, sometimes by the
models, often by both — and, for the empirical claims, only when the harness signed
off on it.

## What stayed mine

The questions were mine, and so were the constraints. The framing — derived versus
generalized, contact as the thing text usually lacks, the failure line drawn in ink
— was mine. The decisions about what counted as a result, what to keep, and what to
throw away were mine. And the responsibility for every claim on these pages is mine:
if something here is wrong, it is wrong because I let it through, not because a
model said it.

I think that is the honest way to describe this kind of work right now — not
authored by AI, not done without it. Built by a person who used very capable tools
to be wrong less often, and who remains accountable for whatever wrongness survives.

— Kirill Kruglov
