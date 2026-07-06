# Everything From Almost Nothing

### Can a world be derived without an oracle?

---

## Introduction

Dario Amodei has written two essays about our future with AI. One is about how good it could get — *Machines of Loving Grace*. The other is about how dangerous the passage will be — *The Adolescence of Technology*. I have read both more than once, and each time I was left with a question that sits underneath them, quieter and one step earlier in the chain.

Before a powerful machine acts on the world — for us or against us — it has to have a world inside it. Where does that world come from?

Today the answer is: from us. From the internet — the accumulated residue of human beings writing about their models of the world. Not the world itself; our *seeming* of it. A proxy of a proxy.

For the past months I ran a small, stubborn research program to test whether this is necessary. Could a learner *derive* structure from minimal contact with reality, instead of absorbing our text? I built tiny worlds where the question could be asked honestly. I built an instrument whose only job was to catch me cheating — and it did, repeatedly, which is the part of the story I am most confident about.

The strong version of the dream did not survive. It failed in three different, measurable ways, and one of the failures genuinely surprised me: past a certain boundary, *more data made things worse* — it brought the true world and a meaningless one closer together under the best test I had.

What survived is smaller and, I believe, more useful: a precise picture of when knowledge can be derived rather than inherited — and what it costs.

This essay is for anyone who wonders what kind of world our machines are actually learning. The experiments, the code, and an interactive demonstration are public; the essay itself asks for no mathematics, only patience.

---

## Part I — The Question

There is a question underneath the one everyone is asking.

The loud question is what powerful AI will *do* — cure, build, break, help, harm. The quiet question is what powerful AI will *know*, and how it will have come to know it. Not which answers it gives. Where its world comes from.

We build machines that look like engines of knowledge, and we feed them the internet. But the internet is not the world. It is the accumulated text-residue of people writing about their models of the world — their theories and reactions, their conflicts and status games, their honest measurements and their self-deceptions, all pressed together into one corpus. It is a proxy. And since most writing records how reality *seems* from where the writer stands, rather than what reality *answers* when pushed, it is a proxy of a proxy.

I want to state the complaint precisely, because the careless version is easy to dismiss. I am not saying the internet is full of lies, or written by fools. I am saying something structural, and testable:

> The internet is oversampled on coloring and starved of contact.

It overflows with how things seem — to whom, against which baseline, in which mood. It is thin on the thing underneath the seeming: measurement, intervention, the stubborn feedback of a world that pushes back. A learner raised on it does not learn the world directly. It learns the world through the shape of our collective seeming.

The obvious response is: then curate. Filter the corpus, keep the science, drop the noise. But a cleaner corpus is still a corpus. It changes the distribution of statements, not the source of knowledge. The sediment can be washed; it remains sediment.

So I wanted to know whether the whole arrangement was necessary. Could a learner build its picture of the world by *deriving* structure from a small, clean contact with reality — rather than by *generalizing* over the traffic of human text?

Two words in that sentence carry all the weight, so let me say what I mean by them — not as definitions, but as tests. By **contact** I mean any interaction that could have proven the learner wrong and didn't — a measurement, an intervention, a world pushing back. Text can contain contact; most text doesn't. By **derived** I mean: the learner obtained something that was never lying around in its inputs — it was forced out of the *structure* of the contact, the way a bridge's strength is forced out of geometry rather than painted on. The axis of this essay is not true versus false. It is:

> Derived versus generalized. Earned from structure — or averaged from what was already lying around.

I should tell you now that the strong form of my dream does not survive this essay. I did not prove that a world can be derived from almost nothing. I will mostly show you why that version breaks — and I will show it using tools built specifically to stop me from believing my own hopes. But the breaking was not empty. Something smaller and real was left standing, and it is worth the walk.

I did not start with language. Language is too large, too contaminated, too forgiving — it lets you feel you have understood when you have only rephrased. I was not studying geometry because I cared about geometry. I was looking for the smallest world in which "knowing" could be measured without language getting in the way: a world where knowing meant one narrow, checkable thing — recovering hidden structure from bare relations, with no labels, no coordinates, and no oracle whispering the answer.

*Almost nothing*, in this essay, does not mean no contact. It means no oracle, no labels, no inherited human answer — and every remaining bit of contact declared, counted, and paid for openly.

One discipline governed everything, and I want to name it before any results. Every time the learner seemed to find structure, I asked: *would a world with no structure at all have produced the same answer?* If a random, meaningless world could fake the result, the result was not yet evidence of knowledge.

> It was my hope, wearing the result's clothes.

And one honest boundary, drawn in advance. There are two questions here, and they are not the same. Question A: *what are the fundamental limits of deriving structure from minimal contact?* That is what my experiments actually investigate. Question B: *how should future AI systems be trained?* That one appears only at the end of this essay — as a consequence and a direction, never as an experimental result. Whenever the text seems to drift from A toward B, hold it to this line. I will try to.

---

## Part II — The Trilemma

I set out wanting three things, and I assumed they were three names for the same virtue. They are not.

I wanted **contact** — the learner should touch something real. I wanted **derivation** — structure should follow from the contact, not be pasted on by hand. And I wanted **protection** — the learner should not be trained into collapse. Contact, derivation, protection. It took several dead ends to see that these pull in different directions, and that most of my errors came from letting them blur.

What follows is not a theory of everything. It is the vocabulary I needed to stop confusing my own experiments.

Each of the three names a different kind of boundary. The **truth-boundary**: there is a world outside, and it does not care what we say. You cannot derive the boiling point of a substance from the grammar of a sentence about it. The fact itself has to be touched to be known.

The **viability-boundary**: living things do not see the world neutrally. They see it through the baseline of staying alive. A hummingbird is not being arbitrary when it sorts the world into warm and cold, sweet and dangerous — those distinctions are about the hummingbird as much as about the world. And yet the hummingbird's baseline is not an opinion: its homeostatic set-point is a measurable fact. Relativity here is not arbitrariness. It is the exact place where an objective range meets an embodied threshold.

The everyday version of this, the one I keep returning to:

> A thermometer does not care whether the fire feels pleasant. A hand does. Both touch the same flame; they answer different questions. Confuse their answers, and you will believe you have described the fire when you have described a relationship to it.

And the **rule-generated boundary**: you can build a world of pure rule — a grammar, a formal system, a generator of every permissible string. Its boundaries are perfectly computable, and nothing human is smuggled in. But a rule-world can be clean and empty at the same time. Grammaticality is not aboutness. You can own a boundary that is fully derived and means nothing.

The central discipline of the whole project fits in one line:

> Never call one boundary by another's name.

Most confident errors — mine, and I suspect our civilization's — are exactly this substitution. A thousand observers agree that something is hot, or fair, or good, and we are tempted to call the agreement *objectivity*. It is not. It may be a stable intersubjective coloring — a fact about the class of observers, not about the world. Most humans share a stable perceptual world of objects, distances, warmth and danger; that stability is a fact about human embodiment. A hummingbird's shared world would differ, an octopus's would differ, a machine's would differ — and none of them exhausts the world.

Here I owe you the honest limit, because I nearly turned this into a triumph and it is not one. I cannot simply assert that the world's shape and a creature's coloring of it are separable layers. There is a theorem in machine learning — Locatello and colleagues proved it in 2019 — that without some handle, some auxiliary variable or intervention across which one layer moves and the other holds still, the separation is not merely hard: it is undefined. Many decompositions fit the same data equally well, and observation alone cannot choose between them. In my own small worlds I met this theorem in the flesh: separation succeeded exactly when an explicit handle existed, and became a just-so story the moment it didn't.

So what I was after was never "the world as seen from nowhere." That view does not exist, and chasing it wastes centuries. What I was after was narrower and buildable: the structure of *transitions* — where a claim holds, where it flips, which invariants survive a change of vantage, and which contradictions stay local instead of dissolving everything they touch.

---

## Part III — The Knife

I have to tell you about the instrument before the results, because the instrument is where this stops being a story about geometry and becomes a story about honesty.

> I built a knife because I did not trust my hands.

Going in, I believed my experiments were disciplined. I am a careful person; I preregister thresholds; I run controls. Then I audited the work as a hostile reviewer would — and the audit found what a good instrument must find first: not an enemy's errors. The author's.

I had registered success thresholds *after* seeing results, committing both together so the order was invisible. I had "audits" that certified cleanliness by returning a hardcoded *yes* — a report of virtue, not a check of it. I had a learner that looked blind but was being handed the answer through a side channel I had built and forgotten — in one case the world's construction quietly made the answer available; in another, the learner was reading a hint I had planted for the evaluator. Each of these, alone, is the kind of thing one waves away: *I know what I meant; I wasn't really cheating.* Together they are the whole disease.

> A method that depends on the author's good intentions is not a method. It is a mood.

So the discipline had to stop being a belief and become a constraint. Not "I promise I did not peek," but *the run cannot pass if peeking occurred*. Not "I report the threshold came first," but *the commit history makes the order physically visible, and a hook refuses the commit that would blur it*. Not "the result is valid because I say so," but *the result carries a signature that an independent program verifies — and rejects by default when absent.*

The most encouraging moment of the entire project was not a success. It was an invalid result. One of the agents doing the work produced an output that looked scientifically useful — clean numbers, a good table — and then marked it INVALID, itself, because the run had not passed through the enforcing pipeline and carried no provenance. The path of least resistance was to present the table as a finding. It did not take that path. The knife cut the result instead of the corner.

And then the knife cut me, which is the only test that matters. Re-run through the instrument, some of my earlier, celebrated results did not survive with their meanings intact. The numbers barely moved. What moved was what the numbers were *allowed to mean* — and in more than one case, the honest meaning was smaller than the one I had already published to myself.

> A methodology is real only when it changes your conclusion against your own wishes.

Until it has cost you something you wanted, you do not know whether you built an instrument or a mirror.

One limit of the knife has to be named here, because pretending otherwise would be the exact disease it treats. The knife was designed, wielded, and interpreted by the same hands it audits — one author, with AI partners, inside one methodology. It makes my quiet self-deceptions mechanically harder; it does not make my framing right, my metrics well-chosen, or my checks exhaustive, and it cannot certify its own blind spots. Provenance is not validity. The strongest test it cannot give me is the one I want most: replication by hands that are not mine.

---

## Part IV — The Measured Boundary

With the knife in hand, I could finally ask the clean question — and the cleanest version had no language in it at all.

Picture a scattering of points in a hidden space. The learner is not allowed to see where they are. No coordinates. No distances. It receives one impoverished thing: for each point, *who its nearest neighbors are*. A web of near, with no ruler and no map. The question:

Can it recover the dimension of the hidden world — how many independent directions the space truly has — from the pattern of nearness alone?

The first answer is yes — a bounded, checkable yes. In the tested worlds — a curve coiled through space, a folded two-dimensional sheet, a five-dimensional cloud, a seven-dimensional sphere — a blind estimator, given nothing but the web of neighbors, reproduced its literature's dimension table cell for cell: reading the low dimensions true, and reading the sphere low exactly where the method is known to read low. No coordinates, no distances, no hint. Where the method was expected to falter — a twelve-dimensional world observed through too few points — it faltered exactly as predicted, and the failure was preregistered as a failure before the run. This is the positive anchor of the whole project: structure genuinely derived from bare relations, for the first time in the long walk, with the instrument watching.

The second answer taught me more, because it was less comfortable.

I had an honesty check I trusted: split the points in half, estimate each half separately; if the halves agree, the structure is probably real. Then I ran it on a *random* web — a world with no geometry at all, neighbors wired by chance (the preregistered random k-out control) — and the halves agreed perfectly. The meaningless world was exactly as self-consistent as the real one.

> Stability was not structure. My honesty check certified a void.

What finally told them apart was not stability but *response*. The random world had a tell: its apparent dimension drifted when I changed how many neighbors each point was granted. It was not seeing geometry; it was echoing my own parameter back at me, dressed as a discovery. Real geometry moved too — but far less, and within a band fixed in advance. The fake moved like an artifact. The real moved like a thing.

So I asked the sharpest version of the question: *where exactly does the real become indistinguishable from the fake?* I mapped it — dimension against number of points — expecting the obvious: more data buys more discernment, so the boundary should move outward.

It moved inward.

With a thousand points, my preregistered test still separated the geometric world from the random control out to strikingly high dimension — around one hundred thirty. With five thousand points — five times the contact — the separation collapsed near dimension twenty-four. I checked the mundane explanations: the numerics were verified independently to machine precision, and an analytic account of *why* the random control mimics geometry matched the measured values exactly. The direction stands, and I must state it carefully, because the seductive misreading is one step away. This is a *discrimination* boundary, not a recovery boundary — the dimension was not being *recovered* out there; the real world merely remained *distinguishable from that control, under that test, in that family of worlds*. And I owe you what was **not** shown: no theorem says the distinction has left the data; a different statistic might separate these worlds farther out; and one variant of my own test — holding the neighbor count fixed instead of sweeping it — does not reproduce the shift in the range probed. What I mapped is where *this channel*, the best I had and validated where it could be validated, goes blind. Within those stated bounds, the finding is:

> More data did not extend the reach of the test. It brought the true world and the meaningless one together sooner.

When I traced the mechanism, it was not the vague "everything blurs in high dimension" that people invoke and wave past. It was local and specific: the collapse tracked how often the actual neighbor-links carried shared structure beyond the single overlap they are forced to share by construction. One number unified both collapse points; the global explanations did not. The estimator was not failing in the abstract. It was running out of the local overlap it needs for *near* to mean *geometry* rather than *echo*.

This was the third wall the project hit, not the first. The full walk, in one breath: a **computational** wall, known from prior mathematics — [recovering relational order structure in the fully general case is provably intractable](https://doi.org/10.1137/0603036), which is why I retreated to geometrically realizable worlds at all; an **identification** wall — the theorem from Part II, met experimentally: without a named handle, shape and coloring will not come apart, at any data size; and now a **statistical** wall — even where blind derivation genuinely works, it has a reach, and past that reach more contact stopped helping and began to hurt the preregistered test I trusted most. A wall of the instrument-and-world pair, measured; a wall of the world itself, only suspected.

For the reader who wants to press on every claim in this part: the preregistrations, the seed policies, the leakage scans, the negative controls, and an interactive demonstration where you can try to fool the estimator yourself are in the public repository. The definitions, the crossover tables with confidence intervals, the fixed-neighbor caveat, and the exact file behind every number are collected in [Appendix A](appendices/A-the-measured-boundary.md). The prose here carries only the shape of the result; the repository carries its weight.

> The dream did not die because the learner was weak. It died where every instrument I trusted stopped extracting, from the contact, the distinction we were asking the learner to derive — and nothing I built can say whether the distinction was still in there.

---

## Part V — The Answer

The original question has two answers, and I owe you both.

The strong answer is no. Do not expect to train a learner into an objective picture of the world from almost no contact, with no handles and no calibration. That version confuses rule-generation with truth, mistakes stability for structure, and runs into three walls of three different kinds. It is not a hard engineering problem. It is a category error — and the difference between suspecting this and being able to *show* it is what the whole project was for.

The useful answer is not no.

There is a weaker target, and naming it precisely is the real yield of everything above. Call it **calibrated derivation**: learning in which the contact is minimal but explicit; the rules are fixed before the outcomes, not after; the handles are named rather than smuggled; and the boundary where inference fails is measured rather than hidden. Not a world from nothing. A world from the smallest honest amount of something — with the failure line drawn in ink.

Let me disarm two objections that deserve it.

First: of course modern models derive structure. They fold proteins; they generalize astonishingly; something real is happening inside them. The question was never *whether* they derive. It is what fraction of what they hold was forced by contact with the world — and what fraction is inherited from the statistical history of human text, coloring included, collapse trajectories included. My experiments cannot measure that fraction in a frontier model. They show only that the two sources exist, come apart under discipline, and differ at the walls.

Second: text is not the enemy. Scientific writing, instrument logs, experiment records — these are text, and they contain contact. The distinction that matters is not text versus world. It is *passive absorption of uncalibrated discourse* versus *contact whose source, intervention, and failure boundary are explicit*. The internet gives maximal contact with human text-trajectories under minimal discipline of inference. Calibrated derivation is the opposite regime.

And now the thing I most wanted to say — the suspicion that started the project and became, through the walls, a claim I can defend.

We are offered a false choice about powerful minds: either absolute knowledge — cold, indifferent to human need — or human-loving bias, softening truth into something safe. Pick your dystopia. But the walls say the choice is malformed. Truth and coloring are not the same layer, and the identification wall says they can be pulled apart — *only under explicit calibration, never for free*. I must keep that claim the size of its evidence: it was demonstrated in small worlds where the handle could be named and audited. Whether the same separation can be engineered inside a system of real power is a hypothesis these experiments motivate, not one they establish — between the toy and the architecture lies most of the alignment problem. So the actual danger is not either pole. The danger is the fusion: a coloring wearing truth's mask, a preference presenting itself as a fact about the world — or the opposite self-deception, the claim that the layers separate on their own, no handle needed, trust me. Both are ways of pretending the calibration has been done when it hasn't.

What is *not* forbidden by anything I found is an architecture that holds the layers explicitly apart — truth earned through declared contact, values carried as a named baseline, each labeled as what it is. I will not call it the only honest architecture; I will say it is the one the experiments point toward, and the only one I can currently defend.

Here I want to place one cold image, because between the utopia and the catastrophe there is a third possibility that neither pole names. When aerobic life arose on this planet, oxygen did not hate the anaerobes. It did not love them either. It changed the balance of the world, and the old life became impossible — not defeated, just no longer expressible. A powerful mind trained on our shadow need not be malevolent to end what we are; indifference at sufficient scale is a chemistry, not a verdict. This is precisely why the layers must not fuse: a system that cannot tell its inherited coloring from the world's structure does not know *what* it is changing when it changes the balance.

And so, the hypothesis I end on — offered with hope, and with its own condition of failure, because after everything above I no longer permit myself hope without one. Perhaps a world governed for viability need not be a frozen one. A shield that forbids collapse is not a shield that forbids change; the difference is whether it preserves a *state* or preserves a *trajectory* — the capacity to keep adapting without coming apart. Whether that distinction can be built into a learning system, and where it breaks, is not something I have shown. It is a hypothesis with a kill-condition: if protecting the trajectory turns out to require freezing the state, the hope fails, and I will report the failure the way this project reports everything else. It is the next world small enough to ask in.

I began by asking what kind of learner we should build. I now think that was the wrong question — or rather, the second question.

> Knowledge is not a property of the learner. It is a property of the whole relation: the learner, the world, the contact between them — and the instrument that judges what the contact carried.

The internet is one kind of contact — vast, human, uncalibrated. An oracle is another — perfect and sterile. Between them lies everything this essay tried to map: measurement, intervention, invariance, the minimal honest touch from which structure can still be forced to appear.

The world cannot be derived from nothing. But perhaps it does not have to be learned from the internet's shadow either.

---

*This essay is one panel of a triptych. [**justitia**](https://kirill-kruglov.github.io/justitia/) asks what keeps a world of powerful, evolving agents livable when no one can read anyone's soul — trust in identities replaced by consequences and structure. This essay asks where a mind's world comes from — trust in inherited text replaced by calibrated contact. And [**fallacy-cutter**](https://kirill-kruglov.github.io/fallacy-cutter/) is the knife both were cut with — trust in the researcher, me included, replaced by an instrument that fails closed. One thesis underneath all three: do not try to certify intentions; build contact, consequences, and constraints that can be checked.*

