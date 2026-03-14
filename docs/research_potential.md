# Research Extension Potential

This document outlines how this system can be extended into a publishable
research contribution, with concrete paper titles, methodology suggestions,
and evaluation frameworks.

---

## Why This Project Has Research Value

Automated literature review generation sits at the intersection of three active
research areas:

1. **Retrieval-Augmented Generation (RAG)** — using retrieved documents to
   ground LLM output and reduce hallucination.
2. **Scientific NLP** — summarization, information extraction, and synthesis
   in the domain of academic text.
3. **Agentic AI systems** — multi-step, tool-using agents that perform complex
   cognitive tasks with minimal human intervention.

This project is a working prototype that combines all three. The gap between a
working prototype and a publishable paper is primarily: rigorous evaluation,
ablation studies, and a novel contribution beyond the baseline.

---

## Candidate Paper Directions

---

### Paper 1 — System Paper with Benchmarking

**Title options:**
- *"LitReviewAgent: An Automated Multi-Stage Pipeline for Synthesizing arXiv Literature Reviews"*
- *"Towards Automated Scientific Literature Synthesis: A RAG-Based Agent Evaluation"*

**Core contribution:**
Design, implement, and rigorously evaluate the end-to-end pipeline.

**Methodology:**
1. Collect a gold-standard dataset: 20–50 topic areas with human-written
   literature reviews (sourced from survey papers on arXiv).
2. Generate automated reviews for the same topics using this system.
3. Evaluate using:
   - **ROUGE-1/2/L** — surface-level overlap with human reviews
   - **BERTScore** — semantic similarity
   - **Human evaluation rubric** — accuracy, coherence, coverage, gap identification
     (5-point Likert scale, two independent annotators)
4. Ablation: compare with/without vector store, with/without per-paper
   summarization, gpt-4o-mini vs gpt-4o for synthesis.

**Likely venues:** ACL (System Demonstrations), EMNLP, NAACL, ECIR.

---

### Paper 2 — Evaluation Framework Paper

**Title options:**
- *"How Good Are LLM-Generated Literature Reviews? A Systematic Evaluation Framework"*
- *"Evaluating Automated Scientific Synthesis: Rubrics, Metrics, and Human Alignment"*

**Core contribution:**
The bottleneck for this research area is the absence of standardised evaluation.
Propose a reusable benchmark and evaluation protocol.

**Methodology:**
1. Curate **LitReviewBench**: a dataset of (topic, human-written review, paper list)
   triples across 10 sub-fields of AI/CS.
2. Evaluate 3–5 systems (this agent, GPT-4o zero-shot, GPT-4o with chain-of-thought,
   a graph-based method) on the benchmark.
3. Analyse inter-annotator agreement on human evaluation dimensions.
4. Release the benchmark publicly.

**Likely venues:** ACL, EMNLP, NeurIPS (Datasets & Benchmarks track).

---

### Paper 3 — Multi-Agent Extension

**Title options:**
- *"Multi-Agent Literature Mining: Decomposing Scientific Synthesis into Cooperative Sub-Tasks"*
- *"Critic-Augmented Literature Review Generation with LangGraph"*

**Core contribution:**
Replace the single synthesis agent with a multi-agent system: a **retriever agent**,
a **summarization agent**, a **critic agent** (evaluates summaries for accuracy),
a **synthesis agent**, and a **consistency checker** (flags contradictions between papers).

**Methodology:**
1. Implement using LangGraph with explicit state transitions.
2. Compare against single-agent baseline on LitReviewBench.
3. Measure hallucination rate (fact-check claims against source abstracts),
   coverage (fraction of key contributions mentioned), and coherence.

**Likely venues:** ICLR, NeurIPS, AAAI.

---

### Paper 4 — Domain-Specific Application

**Title options:**
- *"AgentReview-Climate: Automated Survey Generation for Climate AI Research"*
- *"Towards Continuous Literature Monitoring for AI Safety Research"*

**Core contribution:**
Deploy the agent in a specific high-value domain (climate AI, AI safety, medical AI)
and measure its practical utility in a real research workflow.

**Methodology:**
1. Partner with domain researchers to conduct a user study.
2. Participants write a literature review section manually and using the agent.
3. Measure: time saved, quality comparison, trust and adoption.
4. Analyse domain-specific failure modes (missed papers, incorrect attributions,
   outdated information) and propose mitigations.

**Likely venues:** Domain-specific workshops at NeurIPS/ICML, or applied AI journals.

---

## Evaluation Dimensions

For any of the above papers, human evaluation should cover:

| Dimension | Question | Scale |
|-----------|----------|-------|
| **Factual accuracy** | Are claims accurately drawn from the source papers? | 1–5 |
| **Coverage** | Are key papers and contributions mentioned? | 1–5 |
| **Coherence** | Does the review read as a unified narrative? | 1–5 |
| **Gap identification** | Are research gaps accurately identified? | 1–5 |
| **Academic tone** | Is the language appropriate for a research paper? | 1–5 |
| **Hallucination** | Does the review fabricate results or claims? | Binary (count) |

---

## Known Limitations to Address in a Paper

These are explicitly mentioned in the current system and constitute open problems:

1. **Abstract-only** — The system only reads abstracts, not full paper text.
   Key contributions are sometimes only in the methods or experiments section.

2. **No temporal awareness** — The system does not reason about whether a paper
   is superseded by a newer one (e.g., GPT-2 → GPT-3 → GPT-4).

3. **No citation network** — Papers cite each other, forming a graph. The current
   system treats papers as an unordered set.

4. **Hallucination risk** — The synthesis LLM may fabricate quantitative results
   not present in the summaries. Measuring and mitigating this is an open problem.

5. **Single language** — Currently English arXiv only. Multilingual extension
   (Spanish, Chinese, Arabic) is a clear gap.

---

## Suggested Timeline for Paper 1

| Week | Task |
|------|------|
| 1–2 | Collect 30 survey papers as gold-standard reviews |
| 3–4 | Implement evaluation pipeline (ROUGE, BERTScore, human rubric) |
| 5–6 | Run experiments: baseline comparisons and ablations |
| 7–8 | Analyse results, identify failure cases |
| 9–10 | Write paper draft |
| 11–12 | Internal review, revisions, submission preparation |
