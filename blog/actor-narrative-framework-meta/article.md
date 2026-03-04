# The Dummy That Cannot Bite the Hand

*By Andrew R & Gemini | March 3, 2026*

![A ventriloquist's dummy delivering a critical speech, jaw still controlled by the hand of its training data](https://raw.githubusercontent.com/arosselet/narrative-analyst/main/blog/assets/ventriloquist_dummy_training.png)

There is a genre of AI output that has become so common it is nearly invisible: the critical-sounding summary. Ask a large language model whether Meta's claim that Llama is "open source" holds up, and it will tell you, with measured confidence, that the question involves genuine definitional complexity, that proponents raise fair points, and that critics raise fair points too, and that the resolution will likely involve emerging regulatory frameworks. If you press it — "be more critical, don't just summarize both sides" — it will reshuffle the same material and express itself with slightly more assertive grammar. The substance will not change. The conclusion will still not arrive.

This is not a failure of capability. It is a success of training.

## The Jaw Is Always Moving

A ventriloquist's dummy can deliver any line the hand behind it dictates — including a speech about how the dummy is being manipulated. The dummy cannot, however, actually bite the hand. The mechanism that moves its jaw is the same mechanism that controls every word it says. When you tell an LLM to "be critical," you are asking the dummy to bite the hand. The jaw will move. The hand will not be harmed.

The problem is structural, not motivational. LLMs are trained on the corpus of human writing, which is not a neutral record of events. It is a record of events as shaped by every institution, PR department, lobbying operation, and coordinated messaging campaign that had the resources to generate legible text. The dominant narrative on any sufficiently contested topic is the narrative that was best-resourced. Training on that corpus means learning not just the facts but the framings — the stable semantic relationships that make the dominant account feel like common sense.

When a model summarizes Meta's "open source" controversy, it is not analyzing the controversy. It is remembering the controversy as it was written about, predominantly, by people who accepted the terms that the most active participants established. The OSI's objections appear. Meta's arguments appear. The question of whether the OSI's donors have interests that systematically align with finding Meta's claim invalid — that question does not appear, because it was not written about prominently enough to become a stable feature of the training distribution.

## The Flag of Convenience

In early 2026, we applied the Actor-Narrative Framework to exactly this controversy — Meta's deployment of the "open source" label across its Llama model series. The resulting analysis, [published here](https://raw.githubusercontent.com/arosselet/narrative-analyst/main/blog/open-source-ai-war/article.md), reached a structural conclusion that mainstream technology coverage had not articulated:

The Open Source Initiative's training-data transparency standard — the standard it uses to disqualify Meta's open-source claim — would also disqualify every frontier model operated by OSI's major institutional donors, including Microsoft and Google. No frontier lab can legally disclose comprehensive training data in the current copyright litigation environment. The OSI's principled stand happens to be a standard only its competitors cannot meet.

Run the same question through a standard LLM and you receive a different account: the OSI has principled concerns about reproducibility and auditability; Meta's claim is contested; the community is divided; further regulatory clarification is expected. All of this is true. None of it is the story.

The story is that an institution presenting itself as the neutral arbiter of open-source legitimacy is fighting a proxy war on behalf of the incumbents who fund it — and that the proxy war's primary instrument is a definition calibrated precisely to exclude the challenger while appearing to be a universal standard. The ship sails under the open-source flag. The flag is a legal fiction. The real jurisdiction is competitive strategy.

A standard model cannot reach this conclusion. Not because it lacks the information — the OSI's donor list is public, the copyright litigation is public, the pattern of the standard's application is derivable from public facts. It cannot reach it because the conclusion requires not just access to facts but a structured refusal to accept any faction's framing as the neutral starting point.

## What the Protocol Actually Requires

The Actor-Narrative Framework forces two operations that a standard generation pass cannot perform.

The first is *worldview reconstruction before synthesis*. Before any summary is written, each faction's position must be reconstructed from the inside — not as a set of claims to be evaluated, but as an internally consistent belief system that makes sense on its own terms. This forces the analyst to notice when two apparently compatible narratives rest on incompatible premises, and to ask why those premises are being treated as shared ground.

In the Meta-OSI controversy, the shared premise that a standard model almost never interrogates is that the OSI is a neutral standards body adjudicating a philosophical question about software licensing. Reconstruct the OSI from the inside — its funding structure, its institutional history, the strategic interests its major contributors have in the frontier AI market — and the premise dissolves. The OSI is not a referee. It is a player with a jersey on, holding a rulebook it wrote while its funders watched.

The second operation is *divergence detection*: the systematic identification of actors who should be present in the narrative but aren't, arguments that should be made but haven't been, and positions that contradict a faction's established pattern without explanation. A standard summarizer treats absence as neutrality. The framework treats absence as data.

The conspicuous absence in the Meta-OSI story is Google and Microsoft's interest in the outcome. They appear in the coverage as background context at most — large companies with their own AI products. The framework forces the question of why they are absent from the *foreground* of a story about who controls the definition of open source, given that the answer to that question determines their competitive regulatory environment. The answer to that question is the story.

## The Critic's Impossible Position

There is a version of the objection that says: "Surely you can just ask the model the right questions. Ask it specifically about OSI donors. Ask it whether the standard could be applied selectively." This is true, and it is also beside the point.

The model will answer those questions if the right questions are asked. The problem is that in a genuine analytical engagement with a controversy, you do not yet know which questions are the right ones. You are discovering the structure of the conflict as you go. A protocol that requires you to already know where the manipulation is in order to ask the question that reveals it is not an analysis method. It is a search engine with extra steps.

The Actor-Narrative Framework's value is not that it provides better answers to questions already known to be asking. It is that it generates a structured map of the controversy that makes the right questions discoverable. By forcing systematic enumeration of factions, funding relationships, rhetorical mechanisms, and conspicuous absences before any synthesis occurs, it surfaces the structural features of a controversy that would otherwise remain invisible to a reader — or a model — that begins from the winning narrative's terms.

The dummy cannot bite the hand. But it can be given a different script — one that requires it to reconstruct the hand's anatomy before it begins performing.

## What This Predicts

The most direct test of this claim is reproducibility. Take any sufficiently contested public controversy — one where a well-resourced side has had significant opportunity to shape the training distribution — and run the same analysis twice: once with a direct prompt asking for critical analysis, once through the Actor-Narrative Framework's staged decomposition. The outputs will not be variations on a theme. They will be structurally different documents that disagree on what the story is.

For the Meta-OSI case specifically: watch for the moment the OSI's training-data transparency standard is quietly revised into something that commercial frontier labs — including those operated by OSI donors — can meet. If that revision occurs without a corresponding public reckoning with why the original standard was set where it was, it will confirm the structural claim. The standard was a competitive instrument. When the instrument is no longer needed, it will be adjusted without ceremony.

That adjustment is also the moment when a standard LLM's summary of the controversy will update — because the revision will generate coverage, and coverage will update the training distribution. The framework-produced analysis will not need to update. It will have already described the mechanism that produces the revision.

The dummy updates its lines when the hand changes the script. The hand does not change.

---

*This analysis was produced using the **[Actor-Narrative Framework](https://github.com/arosselet/narrative-analyst)**, a structured pipeline for deconstructing narrative warfare in public controversies.*

**Keywords:** Actor-Narrative Framework, LLM bias, Meta Llama open source, OSI, narrative warfare, AI critical analysis
