# Interview Talking Points — AI Agent Workflow Observability Project

**Target roles:** Data Analyst, Business Analyst, Product Analyst  
**Format:** Q&A pairs — question, then project-specific answer

---

**Q1: Tell me about a project you're proud of. What made it challenging and what did you learn?**

This project is one I initiated independently to simulate real-world AI operations analysis. What I'm most proud of is that it isn't just a cleaned dataset and some charts — it's a full analytical pipeline that models realistic operational complexity: confidence-dependent routing logic, hallucination probabilities tied to confidence bands, tiered SLA targets by priority, and cost structures that differ by resolution path. The challenge was making the synthetic data behave like real data — with the messy correlations and edge cases you'd actually encounter — so that the analysis would produce genuinely insightful findings rather than trivially clean results. I learned how important it is to build the data generation layer thoughtfully, because every downstream analysis depends on whether the data reflects plausible real-world variance.

---

**Q2: How do you handle messy or missing data? Walk me through your process.**

In this project, the most important missing-data decision was intentional: human_resolution_time_minutes is legitimately null for all non-escalated tickets, and handling that incorrectly would corrupt every metric that involves resolution time. My process starts with documenting the reason for missingness before touching the data — is it missing at random, or is it structurally meaningful? In this case it was structural, so the cleaning script validates that non-escalated tickets have NaN in that column and flags any deviation as an anomaly. For other columns, I ran a full null audit with type coercion and range validation, and built a data quality report that prints the null count per column so any unexpected gaps are immediately visible. The key habit is separating "missing because it doesn't apply" from "missing because something went wrong" — those require entirely different responses.

---

**Q3: How do you translate data findings into recommendations that business stakeholders will actually act on?**

The way I approach this is to anchor every recommendation in a cost or risk that leadership already cares about. In this project, I didn't just report that the hallucination rate was 6% — I connected it to a 0.9-point rating drop and a 10-percentage-point increase in repeat contacts, then explained what that means for support volume and agent load. The recommendation that followed — implementing a pre-send review gate for hallucination-flagged responses — is operationally specific and doesn't require a model replacement, which makes it actionable within the current infrastructure. I've found that recommendations land better when they specify who does what, at what trigger, rather than staying at the level of "we should improve the AI." The more the rec reads like a runbook entry, the more likely it is to move from a slide to a Jira ticket.

---

**Q4: What tradeoffs did you identify in this analysis, and how did you think through them?**

The central tradeoff in this project is between automation and quality. Reducing the escalation rate sounds straightforwardly good from a cost perspective — AI-handled tickets cost roughly $8.50 versus $18–35 for escalated ones — but if you drive automation too aggressively, you push low-confidence tickets through the AI without proper guardrails, which increases hallucination exposure and repeat contacts. I modeled both sides of that tradeoff explicitly: the estimated savings from a 15-point reduction in escalation rate are real, but they're partially offset if hallucination rates rise. The recommendation I landed on is targeted automation — expand AI autonomy specifically in categories where confidence is already high (login, shipping) while holding the line on human oversight for technical support until the model is better calibrated. That's the kind of tradeoff framing I think distinguishes useful analysis from an analysis that just tells you to do the obvious thing.

---

**Q5: What would you add to this project if you had more time or resources?**

Three things, in priority order. First, I'd add time-series analysis to track how KPIs shift week over week — right now the analysis is a 90-day snapshot, but in production you'd want to know whether hallucination rates are trending up after a model update or whether SLA compliance is seasonally affected by ticket volume spikes. Second, I'd build a cohort analysis that tracks individual users across multiple tickets to quantify the long-term retention impact of a hallucination event — not just the immediate rating drop, but whether those customers churn within 30 days. Third, if I had access to actual model internals, I'd try to correlate specific failure types with the classes of prompts or knowledge base gaps that caused them, which would make the knowledge base recommendations in the project much more targeted and prioritized.

---

**Q6: How would you present these findings to a non-technical audience, like a VP of Customer Success?**

I'd lead with the business outcome, not the method. For this project, that means opening with: "Our AI system is handling 60% of tickets at roughly $8.50 each, which is the right direction — but when it fails, the failures are expensive and visible to customers." Then I'd pick two or three findings that map directly to things a VP of Customer Success already worries about: customer ratings, SLA compliance for enterprise accounts, and repeat contacts. I'd use the escalation funnel visual — total tickets in, SLA breaches out — because it tells the story in one image without requiring any statistical background. I'd save the confidence band analysis and category-level KPI tables for the appendix or a follow-up conversation with the ops team. The goal for a leadership audience is to make the problem concrete and the recommended action obvious, not to demonstrate methodological sophistication.
