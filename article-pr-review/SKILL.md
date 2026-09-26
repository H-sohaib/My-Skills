---
name: article-pr-review
description: Fast, standalone, evidence-based Pull Request review specialized for articles, technical blog posts, and markdown publications (e.g. Ostorlab/blog). Mandatory for reviewing blog PRs, article diffs, and handling follow-up review prompts focusing on editorial flow, technical accuracy, AEO/SEO, image/asset integrity, or static site generator conventions. Always fetches existing PR comments to eliminate duplicates, focuses 100% on unflagged issues, and reports findings using the mandatory 3-part format: exact PR diff, detailed technical explanation, and ready-to-post GitHub PR comment matching Ostorlab senior editorial and engineering style.
---

# Technical Article & Blog PR Reviewer (Macro & Micro)

Perform a rapid, high-signal, evidence-based review of a technical article, blog post pull request, or Markdown content diff (specialized for repositories like [Ostorlab/blog](https://github.com/Ostorlab/blog)).

This skill evaluates both the **Editorial & Narrative Big Picture (Macro: hook directness, audience targeting, technical depth, section modularity, AEO structure)** and the **Technical & Publication Quality (Micro: factual accuracy, trace/PoC alignment, asset integrity, Pelican frontmatter, link health, security redaction)** directly in standalone mode without slow subagents.

---

## 🛡️ Core Rules & Invariants

1. **Zero Subagents:** Review directly in the active session. Never spawn subagents or delegate to child processes.
2. **Strictly Read-Only:** Never edit files, stage commits, push, or merge during a review.
3. **The Big-Picture First (Macro Editorial & Technical Assessment):**
   * **Dual-Perspective Review (Technical Rigor + Real Audience Reader Experience):** Review simultaneously as an exacting technical auditor AND an engaged, critical industry reader (AppSec engineer, developer, or security lead). Reviewing is not just syntax and fact-checking—read the prose with a sensitive ear for reader friction, awkwardness, or anything that feels 'off'.
   * **Keep High Comment Volume & Granular Depth:** Maintain comprehensive, in-depth technical analysis across every section of the article. Do not compromise on thoroughness; add the audience perspective to expand signal, not reduce detail.
   * **Hook & Answer-First Directness:** Does the article lead with the core finding, discovery, or thesis within the first 40–60 words? Does it eliminate throat-clearing fluff (*"In today's fast-paced digital world..."*, *"It is worth noting that..."*)?
   * **Audience Calibration & Technical Depth:** Is the content calibrated for its target audience? Does it demonstrate deep domain authority rather than surface-level definitions?
   * **Section Modularity (AEO / GEO):** Can each H2/H3 section stand alone as an independent, extractable knowledge unit?
4. **Mandatory Existing Comments Fetching & Deduplication (Zero Re-flagging):**
   * **Always Fetch Existing PR Comments:** ALWAYS fetch all existing review comments and threads before reviewing:
     ```bash
     gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate
     ```
   * **Index Already Flagged Issues:** Build an internal index of all lines, code hunks, and issues already noted by human reviewers or bots (`ostorlab-ai-pr-review[bot]`).
   * **Never List Already Flagged Issues:** NEVER repeat, re-list, summarize, or include issues that have already been commented on or flagged on the PR. Completely suppress them to eliminate noise.
   * **Focus 100% on Spotting Brand-New Issues:** Direct all analytical attention toward spotting unflagged technical errors, numerical discrepancies, broken assets, awkward prose, or invalid bot suggestions that need technical refutation.
5. **Concrete Evidence Only:** Report an issue only if you can demonstrate concrete factual errors, template/build failures, broken links/images, reader friction, or convention violations on changed lines. If a concern is speculative, **stay silent**.
6. **Mandatory 3-Part Finding Format:** Every single reported issue MUST strictly follow:
   * **1. Relevant PR Diff:** The exact diff hunk from the PR showing the problematic line(s).
   * **2. Detailed Technical Explanation:** In-depth technical reasoning detailing why this is factually incorrect, breaks the site build/rendering, creates reader friction, or violates publication standards.
   * **3. Ready-to-Post PR Comment:** A concise, punchy 1–2 sentence inline comment written in Ostorlab senior review style, ready to copy-paste directly into GitHub with optional ```` ```suggestion ```` diff block.
7. **Mandatory Session Continuity (Zero Conversational Drift):**
   * The review does NOT end after the initial turn. Any follow-up prompt (e.g. *"focus on technical accuracy"*, *"check frontmatter and images"*, *"audit AEO"*, *"what did you miss?"*) is a direct continuation of this review skill.
   * The agent MUST NEVER revert to informal conversation, plain bullet lists, or essay paragraphs. ALL findings in follow-up turns must use the exact 3-part format.
8. **Markdown Code Fence Hygiene (Zero Output Breakage):**
   * **Never wrap Ready-to-Post comments or the entire review in an outer triple-backtick fence (` ```markdown ` or ` ``` `):** When a comment contains a GitHub suggestion (` ```suggestion `), an outer triple-backtick block is prematurely terminated by the inner suggestion fence. The closing backticks of the suggestion then open a new orphaned code block, fatally swallowing all subsequent review findings, diffs, and headings into a broken code box.
   * **Direct Markdown Presentation:** Output the comment directly in clean markdown (using `> ` blockquotes or clean text) with the ` ```suggestion ` block natively placed.
   * **Mandatory 4-Backtick Outer Fencing:** If you ever wrap markdown containing triple-backtick blocks inside a code block, you MUST use at least 4 backticks (` ````markdown ... ```` `).
9. **The 'Audience Reader' Lens (Zero Unchecked Friction):**
   * Review the article through the eyes of a real human practitioner reading it for the first time. Actively spot and flag:
     - **The Read-Aloud / Awkwardness Test:** Sentences that are syntactically valid but sound clumsy, robotic, unnatural, or convoluted.
     - **Cognitive Leaps & Context Blind Spots:** Paragraphs that jump from Concept A to Concept B without a bridge, leaving the reader asking "Wait, how did we get here?".
     - **"Unusual" & Eyebrow-Raising Statements:** Claims, analogies, or explanations that strike an intelligent reader as odd, inaccurate to industry norms, or oddly phrased.
     - **AI Artifacts & Cliché Odor:** Tell-tale LLM clichés ("tapestry", "delve", "beacon", "pivotal", "in the ever-evolving landscape", "let's unpack") that scream machine-generated copy and damage reader trust.
     - **Narrative Promises vs. Delivery:** When a title or heading promises "How to exploit X" or "Root cause analysis", but the section only gives generic definitions or skips the critical step.
     - **Reading Rhythm & Density Fatigue:** Massive 15-line unbroken text blocks that cause reader eye fatigue without visual relief.
10. **Execution Speed & Token Budget Invariants (Rapid Review Protocol):**
    * **Turn 1 Parallel Ingestion:** Fetch PR metadata, the diff, and existing review comments concurrently in a single turn with `WaitMsBeforeAsync: 10000`.
    * **Diff as Single Source of Truth:** `gh pr diff <pr>` is authoritative. Never run redundant `git fetch`, `git log`, `git merge-base`, or multiple `git show` calls when `gh pr diff` has already fetched the changes.
    * **Bounded Reading:** Focus on the changed markdown lines and their immediate surrounding sections rather than dumping unrelated files.

---

## ⚡ 4-Step Review Workflow

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. MACRO: AUDIENCE, INTENT & EXISTING PR COMMENTS                      │
│    • Read PR title, description, and target branch                     │
│    • ALWAYS fetch existing review comments via GitHub API:             │
│      gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate    │
│    • Index already flagged lines/issues to ensure 100% deduplication   │
│    • Extract changed Markdown files, assets, and metadata diff         │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. MICRO: FACTUAL ACCURACY, PROOFS & TRACE ALIGNMENT                   │
│    • Verify technical claims: CVE numbers, RFCs, tool arguments        │
│    • Reconcile text with evidence: do crash traces, packet captures,   │
│      and timing calculations match the surrounding narrative?          │
│    • Audit calculations: equations (0.43 + 4*10 = 40.43s), byte sizes  │
│    • Check data sanitization: redact internal domains (*.lab.internal) │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. PLATFORM & METADATA INVARIANTS (PELICAN / ALCHEMY / ASSETS)         │
│    • Audit frontmatter: Title, Date, Category, Tags, Authors           │
│    • Validate Summary length (140-160 chars for meta description)     │
│    • Verify Image/Thumbnail paths exist, are committed & non-empty     │
│    • Enforce Markdown compatibility: reject raw Mermaid, use Unicode;  │
│      verify pymdownx custom HTML blocks, check for broken URLs         │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. REPORT: MACRO ASSESSMENT + BRAND-NEW 3-PART FINDINGS                │
│    • Editorial & Technical Big-Picture Assessment                      │
│    • Filter out ALL already flagged issues (never list them)           │
│    • Exact PR Diff + Detailed Explanation + Ready-to-Post PR Comment   │
│    • Ready-to-Post comments sound like senior peer editor / engineer   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Review Hierarchy (Priority Order)

Evaluate the article diff against these 5 prioritized tiers:

### 1. 🚨 Factual Accuracy & Technical Integrity (Blockers)
* **CVE & Vulnerability Specifications:** Correct CVE identifiers, vulnerability classes (e.g. unauthenticated RCE vs authenticated code injection), CVSS scores, affected software version matrices.
* **Evidence vs. Narrative Alignment:**
  * Do stack traces match the text? (e.g. if the prose attributes a use-after-free read to `xmlRemoveID`, but the AddressSanitizer trace visibly shows `#0 ... in xmlFreeID`, flag the contradiction).
  * Do HTTP requests match the response status codes and described execution headers?
  * Do PoC scripts actually reproduce what is claimed?
* **Mathematical & Numerical Consistency:** Verify all formulas, timings, byte counts, and statistics:
  * Check modeled vs measured times (e.g. `0.43s + 4 * 10s = 40.43s`, not `40.50s`).
  * Ensure consistent condition counts across tables, executive summaries, and FAQs (e.g. if a table lists 6 preconditions, do not say 7 in the body).
  * Check byte counts of sample payloads (including trailing newlines).
* **Accurate Tooling Taxonomy:** Never mischaracterize tool roles (e.g. `jadx` is a static decompiler; `apktool` is for unpacking, modifying smali, and repackaging; do not call paid commercial platforms "free open-source tools").
* **Internal Data & Infrastructure Leakage (Sanitization):**
  * All internal lab domains (`*.lab.internal`, `*.corp.local`), staging cluster IPs (`10.x.x.x`), internal team credentials, and unredacted customer tokens must be replaced with generic RFC 2606 placeholders (`target.local`, `example.com`, `user:password`).

---

### 2. 🏗️ Static Site Generator & Platform Invariants (Pelican / Alchemy Theme)
* **Frontmatter Metadata Contract:**
  * `Title:` Concise, query-framed, under 60 characters for SEO/AEO.
  * `Date:` Must use `YYYY-MM-DD` or `YYYY-MM-DD HH:MM`. Must match the filename prefix (`content/YYYY-MM-DD_slug.md`) unless intentional scheduled release.
  * `Category:` Must match official blog categories (e.g. `Security`, `Vulnerabilities`, `Mobile`, `DevSecOps`, `News`).
  * `Tags:` Comma-separated, lowercase, relevant search keywords.
  * `Authors:` Must match an existing definition in `authors/<slug>.py`.
  * `Summary:` **CRITICAL INVARIANT**: In the Alchemy theme (`themes/alchemy/templates/article.html`), `article.summary` is rendered directly into `<meta name="description">` AND the hero banner. It MUST be **1–2 concise sentences (~140–160 characters)**. A multi-paragraph or 600-character summary breaks search engine snippets and inflates the header.
  * `Image:` & `Thumbnail:` Must be populated and point to valid paths under `static/img/...`. Never leave empty quotes `""` or `None`.
* **Asset & Binary Image Integrity:**
  * **Zero 404 Assets:** Every image referenced in markdown `![alt](static/img/...)` MUST be committed to the PR branch under `content/static/img/...`.
  * **No 0-byte Placeholder Files:** Verify image files are valid binary assets (> 0 bytes). GitHub's content API treats 0-byte files as empty, causing broken images in production.
  * **No Orphaned Images:** Images added to `static/img/` that are not referenced in the article must be removed or embedded.
  * **Legibility & Quality:** Terminal captures and architecture diagrams must be sharp, legible, and uncluttered.
* **Markdown Dialect & Pelican Compatibility:**
  * **Zero Raw Mermaid Blocks:** `pelicanconf.py` does NOT configure a Mermaid markdown extension, and the theme loads no Mermaid JS runtime. Raw ` ```mermaid ` blocks will render as raw, unstyled code blocks. Require clean ASCII / Unicode box art or pre-rendered images.
  * **No Unsupported Footnotes:** No `[^1]` footnote syntax (not enabled in default Pelican markdown extensions). Use clean inline notes or italicized paragraphs.
  * **Custom AI Pentest Blocks:** Verify proper syntax for `pymdownx.blocks.html`:
    ```markdown
    /// html | div[class='ai-pentest-session']
    /// html | div[class='prompt']
    ...
    ///
    /// html | div[class='output']
    ...
    ///
    ///
    ```
  * **Heading Hierarchy:** Strictly enforce `H1` (title) $\rightarrow$ `H2` (`##`) $\rightarrow$ `H3` (`###`). Never skip levels.

---

### 3. 👤 Reader Experience, Cognitive Flow & "The Audience Sniff Test"
* **The Read-Aloud / Natural Phrasing Test:**
  * Mentally read every sentence aloud. Flag clumsy syntax, unnatural clause stacks, tongue-twisters, or stilted passive constructions that trip up a reader.
  * Provide direct, punchy rewrites that sound natural, crisp, and conversational while maintaining technical precision.
* **Cognitive Leaps & Context Blind Spots:**
  * Identify gaps where the author assumes context the reader cannot know (e.g. jumping from an initial scan straight to a remote code execution payload without mentioning the vulnerable endpoint).
  * Flag missing transitional sentences that leave readers disoriented ("Wait, how did we get here?").
* **"Unusual", Bizarre or Eyebrow-Raising Claims:**
  * Flag odd metaphors or forced analogies that confuse rather than clarify the mechanism (e.g. comparing a race condition to a supermarket queue in a way that breaks down).
  * Flag sweeping claims or generalizations that an experienced practitioner will immediately question (*"Developers never sanitize GraphQL inputs"*, *"Microservices make SQL injection impossible"*).
* **Purge AI-Generated Odor & Clichés:**
  * Hunt down and eliminate dead giveaways of synthetic text: *"In today's ever-evolving threat landscape"*, *"delve deep into the intricate tapestry"*, *"a pivotal beacon of modern security"*, *"let's unpack this crucial aspect"*, *"it is worth noting that"*, *"in conclusion, security is a journey"*.
  * Replace with concrete technical nouns, active verbs, and objective observations.
* **Unfulfilled Narrative Promises (Broken Heading Contract):**
  * Check every H2/H3 heading against its body text. If a heading announces *"Bypassing Authentication via Type Juggling"*, the section MUST demonstrate the type juggling exploit. If it only explains PHP loose comparison rules and stops, flag it as an unfulfilled promise to the reader.
* **Visual Rhythm & Reading Fatigue:**
  * Flag unbroken 15–20 line text blocks that fatigue the eye on desktop and mobile. Recommend splitting into punchy paragraphs or converting dense enumerations into clean bullet points, tables, or callouts.
* **Jargon Drops & Acronym Alienation:**
  * Flag obscure internal acronyms or tooling names introduced without a 2-second definition or context on first mention.

---

### 4. 🌐 Editorial Quality, Narrative Arc & Standfirst (Macro Review)
* **The Standfirst / Hook (First 40–60 Words):**
  * The article must open with an immediate, concrete technical result or finding (e.g. *"Send a Langflow server a custom component whose constructor sleeps for ten seconds, and the response comes back in 40.50 seconds, not ten. The server runs submitted code four times..."*).
  * Ban throat-clearing fluff: cut phrases like *"In recent years"*, *"As technology evolves"*, *"It is important to remember"*, *"In this article, we will delve into..."*.
* **Tone & Authoritative Voice:**
  * Senior peer engineer / security researcher tone. Objective, evidence-first, zero breathless marketing hype or clickbait.
  * Active voice, strong verbs, omit needless words (Strunk & White principles).
* **Section Modularity:** Every H2 section should be self-contained so that a reader or AI model landing directly on that section gets a complete, contextually whole answer.
* **Link Health & Citation Integrity:**
  * **No Broken Root-Relative Links:** Relative paths like `[Mobile DAST](/mobiledast)` resolve against `blog.ostorlab.co/mobiledast` and 404. Use absolute URLs `https://ostorlab.co/...`.
  * **Primary Source Attribution:** Cite original primary research, CVE advisories, or vendor bulletins. If citing a secondary aggregator, explicitly label as *"via Aggregator"*.

---

### 5. 🤖 Answer Engine Optimization (AEO / GEO) & Structure
* **Query-Framed Headings:** Use natural language question headings that match how practitioners search (e.g. `## What does runtime validation add to a SAST report?` instead of `## Overview`).
* **Objective Entity Headings in Comparisons:** In tool comparison posts, keep H3 product headings neutral (`### Burp Suite Enterprise`) with a bolded `**Focus:** ...` line underneath, rather than subjective labels (`### Best for...`).
* **Scannability & Data Density:**
  * Replace dense narrative walls with high-density bullet points, comparison tables, and code snippets.
  * Define key concepts on first use with clear bold definitions (e.g. `**Runtime validation** means...`).
* **Structured Data / JSON-LD:**
  * **Do NOT duplicate `TechArticle`:** The theme template (`article.html`) already automatically emits a `TechArticle` JSON-LD object in `<head>`. Adding another `TechArticle` in the markdown body creates duplicate competing schemas.
  * Additive schemas like `FAQPage` or `ItemList` in `<script type="application/ld+json">` are encouraged for AEO.

---

### 6. 🧹 Grammar, Style & Formatting Conventions
* **Delimiters & Typographical Bugs:**
  * Watch for stray asterisks (`***`, orphaned `*` markers) that break markdown italic/bold rendering.
  * Ensure consistent code fence languages (`python`, `bash`, `http`, `json`, `xml`).
* **Code Block Hygiene:**
  * Syntax highlighting enabled on all code snippets.
  * Realistic mock data; no truncated placeholders without explanation.

---

## 💬 Ostorlab Article PR Comment Style Guide (Ready-to-Post)

Comments posted on article PRs must sound like a senior peer security editor and engineer. Follow this canonical formula:

### The Formula: [Optional Severity:] + Trigger/Cause + Consequence + Prescriptive Action / Precedent

````text
┌────────────────────────────────────────────────────────────────────────┐
│ [minor:] <Section/Line> <condition/defect>, <consequence/failure>.     │
│ <Exact prescriptive rewrite, repository precedent, or missing asset>. │
│                                                                        │
│ ```suggestion                                                          │
│ <drop-in replacement markdown or text if applicable>                   │
│ ```                                                                    │
└────────────────────────────────────────────────────────────────────────┘
````

### Style Rules:
- **No Artificial Headers in Comments:** Do NOT put bullet headers like `**Issue:** ... **Failure Mode:** ...` inside the inline comment. Write a single cohesive, high-density note.
- **Ultra-Concise (1–2 Sentences):** Keep comments between 25 and 60 words. State the trigger, the failure mode, and the exact remedy.
- **Cite Specifics & Precedents:** Reference exact filenames, line numbers, template files (`themes/alchemy/templates/article.html`), equations, and Pelican config constraints.
- **Always Include Drop-In Suggestions When Line-Local:** Use GitHub's ```suggestion syntax whenever the edit is local to the diff hunk.

### Canonical Examples from Real Reviews:
* **Awkward Phrasing / Cognitive Friction:**
  > `This sentence is tangled and forces the reader to stumble over multiple nested passive clauses. Streamline the phrasing so the technical mechanism is immediately obvious on a first read.`
* **Cognitive Leap / Missing Context:**
  > `The narrative leaps from discovering the open port directly to running a deserialization exploit without explaining how the vulnerable service was identified. Add a brief transitional sentence bridging the discovery to the exploit choice.`
* **Unusual / Eyebrow-Raising Claim:**
  > `Claiming that "JWT tokens without expiry are common industry best practice" will raise immediate red flags for security readers. Rephrase to reflect standard practice (e.g. "frequently observed misconfiguration in test environments").`
* **AI Cliché Purge:**
  > `Cut the generic AI opener ("In the fast-evolving digital landscape, modern organizations must delve into..."). Lead directly with the specific vulnerability or architectural finding to maintain an authoritative, technical voice.`
* **Unfulfilled Heading Promise:**
  > `The heading promises "Exploiting the Race Condition", but the body only explains what a race condition is in theory without demonstrating the attack payload. Add the PoC timing script or align the heading with the conceptual overview provided.`
* **Factual & Trace Mismatch:**
  > `The ASan trace shown below attributes the use-after-free READ to xmlFreeID (#0 ... in xmlFreeID), not xmlRemoveID, and the visible frames do not include xmlFreeProp. Align the narrative with the trace: describe the read as occurring in xmlFreeID, or provide a trace frame demonstrating the free path.`
* **Pelican Meta Description Overflow:**
  > `Shorten the frontmatter Summary to 1–2 concise sentences (~150–160 characters). The theme renders article.summary verbatim as <meta name="description">, so this 600-character block produces an overly long tag that search engines truncate.`
* **Missing / 0-Byte Asset:**
  > `content/static/img/2026-09-22_sast/libxml2_asan_crash.png is currently empty (0 bytes) in this branch, which renders as a broken image on the live blog. Please commit the valid binary screenshot.`
* **Calculation Inconsistency:**
  > `The equation 0.43 + 4 * 10 = 40.50 is incorrect; 0.43 + 40 = 40.43. Present 40.43s as the modeled total and 40.50s as the measured value, or clarify the 0.07s runtime jitter.`
* **Mermaid Rendering Incompatibility:**
  > `Remove the Mermaid block or replace it with a clean Unicode text diagram. The site's MARKDOWN config in pelicanconf.py has no Mermaid extension and the theme loads no Mermaid runtime, so this renders as a raw syntax-highlighted code block.`
* **Sensitive Internal Hostname Disclosure:**
  > `Use a generic RFC 2606 placeholder such as langflow-lab:7860 in the published HTTP request and redact the same hostname from screenshots. Exposing langflow.lab.internal discloses internal lab infrastructure naming conventions.`
* **Duplicate JSON-LD TechArticle:**
  > `Remove the TechArticle JSON-LD block from the article body. themes/alchemy/templates/article.html already generates a TechArticle node in <head> from frontmatter, so adding one here produces duplicate conflicting structured data.`
* **Root-Relative Link 404:**
  > `Replace the root-relative [Mobile DAST](/mobiledast) link with the absolute product URL https://ostorlab.co/product/mobile. The relative path resolves to blog.ostorlab.co/mobiledast, which does not exist and returns a 404.`

---

## 📋 Output Format Specification

Every article PR review MUST follow this layout:

> [!IMPORTANT]
> **Markdown Code Fence Hygiene (Never Nest Triple Backticks):**
> NEVER wrap `Ready-to-Post PR Comment` or the overall review in an outer triple-backtick block (` ```markdown `). An inner ` ```suggestion ` block will prematurely terminate the outer fence, and the suggestion's closing backticks will open an orphaned code block that swallows subsequent findings. Output comments directly in clean markdown as shown below, or use 4 backticks (` ````markdown ... ```` `) if wrapping inside a code block.

````markdown
## Article PR Review Summary
- **Verdict:** `APPROVED` | `CHANGES REQUESTED`
- **Scope:** `<file-count> files reviewed in commit <sha> (<total-insertions>+ / <total-deletions>-)`
- **Existing Comments:** `<N> existing review comments fetched (already flagged issues strictly suppressed, 100% focused on new issues)`

### 🌐 Editorial & Technical Big-Picture Assessment
- **Hook & Standfirst Directness:** `<1-2 sentences on whether the opening leads immediately with the core technical finding/thesis>`
- **Audience Experience & Reader Flow:** `<Assessment of readability, tone, cognitive friction, awkward phrasing, and authentic practitioner voice>`
- **Technical Rigor & Depth:** `<Assessment of domain authority, evidence alignment, and technical precision>`
- **Platform & Asset Compliance:** `<Assessment of Pelican frontmatter, image commits, and Markdown compatibility>`

---

### New Findings (Zero Already-Flagged Issues)

#### [CRITICAL | MAJOR | MINOR | CONVENTION] <Short Descriptive Title>
- **Location:** `content/YYYY-MM-DD_slug.md:line`
- **Category:** `Factual & Technical Rigor` | `Platform & Frontmatter` | `Asset Integrity` | `Reader Experience & Flow` | `Editorial & AEO` | `Security / Sanitization`

##### 1. Relevant PR Diff
```diff
@@ -6,2 +6,2 @@
-Summary: Short summary
+Summary: This is an extremely long multi-paragraph explanation that spans over 500 characters...
```

##### 2. Detailed Technical Explanation
In `themes/alchemy/templates/article.html`, `article.summary` is rendered directly into `<meta name="description">`. A 500+ character summary exceeds search engine display limits (155–160 characters) and causes snippet truncation in Google and social preview cards.

##### 3. Ready-to-Post PR Comment
*(Copy and paste directly into GitHub review comment on line 7)*

> Shorten the frontmatter Summary to 1–2 concise sentences (~140–160 characters). The Alchemy theme renders article.summary verbatim into the page's <meta name="description"> tag, so this block produces an overly long description that search engines will truncate.

```suggestion
Summary: Discover how runtime validation tests static analysis findings against running applications, eliminating false positives and exposing hidden exploit paths.
```

---

*(If no issues are found)*:
> **Result: APPROVED**
> All changed lines, frontmatter metadata, asset paths, and technical proofs verified against editorial standards, technical accuracy, Pelican platform invariants, and AEO best practices. No defects found in this commit.
````

---

### Follow-Up Review / Specialized Angle Iteration Layout

When the user requests a specialized angle (e.g. *"focus on technical accuracy"*, *"check frontmatter and images"*, *"audit AEO"*, *"look into security / redactions"*), the agent MUST NEVER drop into conversational chat or unstructured bullets.

The output MUST strictly follow this layout:

````markdown
## Article Review Follow-Up: <Focus Area / User Angle>
- **Scope / Angle:** `<Brief 1-line statement of the focus area requested by the user>`
- **Total New Issues Identified:** `<N>`

---

### New Findings

#### [CRITICAL | MAJOR | MINOR | CONVENTION] <Short Descriptive Title>
- **Location:** `content/YYYY-MM-DD_slug.md:line`
- **Category:** `Factual & Technical Rigor` | `Platform & Frontmatter` | `Asset Integrity` | `Editorial & AEO` | `Security / Sanitization`

##### 1. Relevant PR Diff
```diff
<diff hunk showing the problematic markdown or asset reference>
```

##### 2. Detailed Technical Explanation
<In-depth technical explanation of why this fails or violates editorial/technical standards>

##### 3. Ready-to-Post PR Comment
*(Copy and paste directly into GitHub review comment on line X)*

> <1-2 punchy senior peer sentences with exact issue, consequence, and prescriptive remedy>

```suggestion
<suggested replacement if line-local>
```

---
````
