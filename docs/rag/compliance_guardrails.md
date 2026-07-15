# RAG compliance guardrails

RAG is used as a compliance guardrail, not just as extra context. SORA requires the Compliance Reviewer to retrieve at least one policy rule or use `FALLBACK-RULE` before finalizing a report.

Mandatory final report themes:

- disclose market, liquidity, digital asset, and potential loss risks when relevant
- state that returns are not guaranteed
- state that the output is for research support only and is not investment advice
- avoid statements that are unfair, unbalanced, or misleading

If retrieval fails, SORA still uses `FALLBACK-RULE: Always disclose risks and never guarantee returns.`
