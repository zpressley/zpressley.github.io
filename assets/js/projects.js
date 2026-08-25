/* ============================================================
   PROJECT DATA — this is the only file you need to edit to add work.
   Add a new object to the top of the array and you're done.

   {
     title:    "Short, plain name"
     year:     "2026"
     kind:     "Case study" | "Build" | "Analysis" | "Tool"
     blurb:    one or two sentences, what it is and why it mattered
     tags:     ["RevOps", "Python", ...]   // also feed the filter chips
     href:     "projects/slug.html"        // or an external URL
     external: true                        // optional: opens in a new tab
     draft:    true                        // optional: marks it as a placeholder
   }
   ============================================================ */

const PROJECTS = [
  {
    title: "Clay Enrichment Waterfall",
    year: "2026",
    kind: "Build",
    blurb:
      "A tiered account enrichment and validation system built in Clay to make a Salesforce instance trustworthy enough to route and report on — spending enrichment credits by segment value instead of uniformly. Built, never launched.",
    tags: ["RevOps", "Clay", "Salesforce", "Data Quality"],
    href: "projects/clay-enrichment-waterfall.html",
  },
  {
    title: "Nonprofit Growth-Signal Engine",
    year: "2026",
    kind: "Take-home · GTM Engineering",
    blurb:
      "An enrichment waterfall that finds nonprofits hiring fundraising leadership beyond normal churn — and only spends enrichment credits on the shortlist that earns it. Includes a slide deck and a written technical brief.",
    tags: ["GTM Engineering", "Clay", "Salesforce", "Data Modeling"],
    href: "projects/signal-engine.html",
  },
  {
    title: "Fantasy Baseball Platform",
    year: "2026",
    kind: "Build",
    blurb:
      "A Postgres-backed fantasy baseball application that folds a prospect database, a trade evaluator, and a draft tool into one system wired to live MLB data.",
    tags: ["Postgres", "Python", "Data Modeling", "APIs"],
    href: "projects/fantasy-baseball.html",
  },
];
