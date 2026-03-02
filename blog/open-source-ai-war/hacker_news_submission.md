# Hacker News Submission Draft

**Title:** Show HN: A deterministic LLM pipeline for extracting subtext from corporate PR

**URL:** `[Link to the blog post / README]`

**First Comment (OP):**
Hey HN,

I got tired of asking LLMs to analyze controversies only to get polite, "both-sides" summaries. Because of their RLHF safety training, models are fundamentally consensus engines. If you give them a corporate PR statement, they just restate the dominant narrative with better grammar.

I wanted an X-ray scanner for public relations, so I built the Actor-Narrative Framework. It's a deterministic prompt pipeline that forces the model to stop summarizing and instead reconstruct the underlying power dynamics and economic incentives.

To test it, I ran Meta and the OSI's statements regarding the "Open Source AI" definition war through the pipeline. 

A standard LLM prompt (the control) gave me a boring summary about licensing technicalities. 
The pipeline extracted the actual strategic knife fight:
- Meta isn't "democratizing" AI; they are using developers as unwitting lobbyists against the EU AI Act. By wrapping their product in the "open source" flag, they achieve **regulatory capture** and **liability externalization** (via the AUP), while maintaining an anti-competitive moat against Google/Apple (the 700M clause).
- The OSI isn't just defending a definition; they are fighting a proxy war for their donors (Microsoft/Google) by demanding an impossible standard (full training data transparency, which no frontier model can legally provide).

The framework runs in 3 stages (Extraction -> Narrative Analysis -> Synthesis). The prompts are all open source in the repo. Would love to hear your thoughts on using structured decomposition to break neutrality conditioning!
