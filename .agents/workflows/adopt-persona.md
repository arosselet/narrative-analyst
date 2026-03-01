---
description: Initiate the 3-stage Actor-Narrative Framework pipeline
---

# The Actor-Narrative Framework Pipeline (`/adopt-persona`)

This workflow initiates the 3-stage pipeline to deconstruct and analyze an article, then synthesize a new blog post from the findings. 

**Inputs:**
1. The source article content or URL.
2. A short, URL-friendly topic name (e.g., `2028-intelligence-crisis`).

**Execution Steps:**

**1. Setup Workspace**
- Run the command to create the necessary directories: `mkdir -p ./analysis/<topic_name>` and `mkdir -p ./blog/<topic_name>`
- Save the raw source article content to `./analysis/<topic_name>/source_article.txt`.

**2. Stage 1: The Publication Deconstructor**
- Read the instructions in `./prompts/publication_analyst.md` using the `view_file` tool.
- Adopt this persona and process `source_article.txt`.
- Save your analysis to `./analysis/<topic_name>/extracted_controversies.md`.

**3. Stage 2: The Narrative Analyst**
- Read the instructions in `./prompts/narrative_analyst.md` using the `view_file` tool.
- Adopt this persona and process `extracted_controversies.md`.
- Save your analysis to two files: `./analysis/<topic_name>/narrative_analysis.md` and `./analysis/<topic_name>/positioning_comparison.md`.

**4. Stage 3: The Narrative Journalist (Article Writer)**
- Read the instructions in `./prompts/article_writer.md` using the `view_file` tool.
- Adopt this persona and process `positioning_comparison.md` and the context of the analysis to generate a publishable blog post.
- Ensure the article incorporates 4-5 relevant keywords at the end (as per previous refinements).
- Save the final output to `./blog/<topic_name>/article.md`.
- Generate a unique visual metaphor using the `generate_image` tool that captures the deep structural essence of the controversy. Name the image intuitively, and ensure it lands in a location you can link to from the blog post.

**5. Completion**
- Update any necessary `task.md` or tracker files.
- Notify the user with links to the generated artifacts (`article.md` and the visual metaphor).