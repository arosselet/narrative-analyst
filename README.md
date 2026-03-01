# The Actor-Narrative Framework

**A systematic method for deconstructing controversies, identifying narrative warfare, and seeing through the stories we're told.**

---

## The Problem

Ask any large language model about a controversial topic and you'll get a confident, well-sourced synthesis. The problem is: that synthesis is often *the dominant narrative restated with better grammar*.

LLMs are trained on the internet. The internet is full of astroturfing, PR campaigns, and coordinated messaging. When one side of a controversy invests heavily in shaping public discourse, their version of events becomes the training data. The model doesn't analyze the controversy. It *reproduces the winning narrative*.

This means the more you ask an LLM to "analyze" something, the more likely you are to get a sophisticated restatement of whichever faction had the better communications strategy. The model can't tell you it's doing this, because from its perspective, it's simply summarizing consensus.

**The Actor-Narrative Framework is a protocol that forces systematic decomposition of controversies into their component parts before any synthesis occurs.** It treats every controversy as a contest between actors with distinct worldviews, strategic interests, and rhetorical toolkits. By requiring the analyst (human or LLM) to reconstruct each side's story *in that side's own words*, it makes the machinery of narrative warfare visible.

## The Framework

The Actor-Narrative Framework rests on five core operations:

### 1. Controversy Decomposition

Every complex controversy is actually a bundle of smaller fights. A proposed landfill isn't one issue: it's an environmental assessment fight, a municipal governance fight, a First Nations consultation fight, and an economic development fight, all wearing the same headline. Decomposing into sub-controversies prevents the analyst from collapsing distinct conflicts into a single "pro vs. anti" framing.

### 2. Faction Mapping and Worldview Synthesis

For each sub-controversy, identify the factions, then reconstruct their *worldview*: not just what they say, but the internally consistent belief system that makes their position seem logical to them. A mining company isn't just "pro-development." They inhabit a worldview where regulatory delay is a form of economic self-harm, where environmental assessments are a tool competitors use to block market entry, and where resource extraction is synonymous with national security.

Good worldview synthesis passes the empathy test: someone from that faction should read it and say, "yes, that's what we believe."

### 3. Rhetorical Tactic Identification

Language is the primary weapon in narrative warfare. The framework systematically identifies:

- **Elevation and denigration**: How each faction uses language to legitimize its own position and delegitimize opponents. ("Responsible stewardship" vs. "reckless obstruction.")
- **Distraction and obfuscation**: Language designed to redirect attention from inconvenient facts. (Talking about "jobs" when the question is about environmental contamination.)
- **Named tactics**: Specific rhetorical devices like Motte-and-Bailey arguments, manufactured consensus, appeals to authority, asymmetrical scrutiny, and conspicuous absence (who *should* be speaking but isn't?).

### 4. Competing Grand Narratives

The most powerful output of the framework: reconstruct each faction's story as *they would tell it*. Not a summary of their position, but their narrative. Their heroes, their villains, their moral justification, their version of cause and effect. When you force yourself to tell each side's story with full narrative coherence, you begin to see where the framing is doing the work, and where the facts are.

### 5. Divergence Detection

Once you've mapped the worldviews, you can detect when something changes. A faction's rhetoric shifts. A previously consistent actor contradicts their established pattern. An expected voice goes silent. These divergences are the signal in the noise. They tell you where to look next.

## The 7-Step Protocol

This is the structured process that operationalizes the framework. It can be applied manually, used as a prompt for any LLM, or embedded in an automated pipeline.

> **Step 1: Research and Augment Knowledge**
> Before analyzing factions, research the core controversy and key actors. Identify their historical positions, known affiliations, and prior public statements. Synthesize this background with the provided source material.

> **Step 2: Map Factions and Deconstruct Their Lexicon**
> Identify the primary factions. Deconstruct their foundational narratives (e.g., safety vs. freedom, sovereignty vs. development). Analyze their use of euphemisms, dysphemisms, and rhetorical tactics used to delegitimize opponents: Motte-and-Bailey, equivocation, loaded questions, asymmetrical scrutiny, manufactured consensus, Gish Gallop, sealioning. Scrutinize appeals to authority.

> **Step 3: Trace the Timeline to the Causal Schism**
> Investigate the conflict's history to identify the point of no return. Chronicle the events that escalated tensions. Pinpoint moments of failed compromise or perceived betrayal.

> **Step 4: Analyze the Power Structure and Economic Incentives**
> Follow the money and influence. Who funds the key players? Who controls infrastructure and communication channels? What are the economic or political incentives and potential conflicts of interest? When the text mentions factions in general terms ("the mining industry," "local communities"), identify the specific named entities that comprise them. Note when influential actors are conspicuously absent.

> **Step 5: Identify Asymmetries and Marginalized Voices**
> Look for imbalances of power. Investigate claims of censorship or control over discussion forums. Identify influential figures who were pushed out or silenced.

> **Step 6: External Corroboration and Contextualization**
> If the controversy references publicly available documents (court rulings, academic papers, official reports), reflect the context from those documents. Note where claims could be strengthened or challenged by consulting primary sources.

> **Step 7: Synthesize Competing Grand Narratives**
> Construct the most compelling, internally consistent story for each major faction. Outline their fundamental worldview. Recount their story of the conflict. Identify their heroes and villains. Articulate their ultimate moral justification.

## Using the Framework

The framework provides two distinct analysis pipelines, designed as specific Personas (or Gemini Gems/Plugins). They are located in the `prompts/` directory.

### 1. The Topic Analyst (`prompts/narrative_analyst.md`)
**Use this for:** Macro-level deconstruction of a broad topic, a controversy, or multiple sources covering the same event.
**How it works:** This persona maps the entire battlefield. It extracts all participating factions, reconstructs their internally consistent worldviews, and identifies their rhetorical strategies. 

### 2. The Publication Deconstructor (`prompts/publication_analyst.md`)
**Use this for:** Micro-level deconstruction of a *single specific document* (e.g., an article, press release, or executive memo).
**How it works:** This persona treats the document itself as an active participant in narrative warfare. It maps the baseline reality of the underlying controversies, and then analyzes how the specific document uses language, omissions, and pacing to manipulate the reader's perception. The output is a dense, whitepaper-style brief of the manipulative mechanics, providing the raw grist for further writing.

Both prompts are portable and work with ChatGPT, Claude, Gemini, or any other LLM. Simply paste the prompt as the System Instruction, provide your source material, and let the persona execute the protocol.

- **Manual analysis**: The 7-step protocols within the prompts also work as checklists for human analysts.
- **Automated pipelines**: The framework has been implemented as a multi-agent Python pipeline. If you're interested in building something similar, the methodology described here is the foundation.

## Where It Works Best

The framework is most valuable when applied to controversies where the dominant narrative is so deeply embedded that a standard LLM analysis would simply reproduce it. Some domains where this is particularly effective:

### Legislative and Regulatory Analysis
Bills, regulations, and policy proposals are presented with official narratives ("protecting the economy," "streamlining approvals"). The framework exposes the gap between stated intent and actual mechanism. It systematically identifies who benefits financially, which oversight mechanisms are weakened, and whose voices were excluded from the process. It's especially powerful for omnibus bills where significant policy changes are bundled together to avoid individual scrutiny.

### Competitive Intelligence
Companies craft deliberate public narratives through press releases, earnings calls, and thought leadership content. The framework deconstructs these narratives into worldview components, making it possible to detect when a competitor's messaging shifts, where they're positioning against you, and what their actual strategic priorities are (as opposed to what they say they are). It's particularly revealing when applied to analyst reports, short seller theses, and comparison sites, where each source has its own unstated agenda.

### Investigative Journalism
The framework generates specific, testable hypotheses and research directives. Instead of vague "look into this" guidance, it produces structured questions like: "Find payment records or contracts linking Company A and Politician B's family members between 2022 and 2024." It identifies conspicuous absences: actors who should be part of the conversation but aren't, which is often the most revealing signal of all.

### Geopolitical Analysis
International relations reporting is heavily shaped by the narratives of participating governments. The framework forces reconstruction of each state actor's worldview, making strategic calculations visible. It's particularly useful for analyzing deterrence strategies, alliance dynamics, and the gap between public diplomacy and actual policy.

### OSINT and Disinformation Research
Multi-source analysis of a single controversy is the framework's native habitat. Ingest multiple articles covering the same event, and the system maps every actor, their narrative evolution across sources, and where the factions diverge. The divergence detection capability is especially valuable: once you've established a baseline worldview for an actor, any shift in rhetoric or positioning becomes a detectable signal.

## Limitations

The framework is powerful but not magic. Be honest about what it can't do:

- **It requires source material.** The framework analyzes text. It can't investigate what isn't written down. It can identify conspicuous absences, but it can't fill them.
- **It inherits LLM limitations.** When used with an LLM, the framework is still subject to the model's training data biases. The protocol mitigates this by forcing structured decomposition, but it doesn't eliminate it. The analyst must still bring external knowledge and skepticism.
- **It doesn't tell you who's right.** The framework's power is in making each side's narrative machinery visible. It doesn't adjudicate truth. That's your job.
- **It works best on genuinely multi-sided controversies.** If there's really only one reasonable interpretation of a situation, the framework will dutifully construct two sides anyway. Use judgment.

## Background

This framework emerged from a series of conversations with Google's Gemini in 2025, where I was exploring a specific question: could I get an LLM to reliably "see through the astroturfing"? I wanted to know if a model could produce a nuanced analysis of a topic despite overwhelming bias in its training data.

The Actor-Narrative Framework was the result: a structured protocol that forces the analysis to stay grounded in specific textual evidence rather than drifting toward a potentially astroturfed consensus.

## License

MIT License. Use it, extend it, teach it. If you build something interesting with it, I'd love to hear about it.
