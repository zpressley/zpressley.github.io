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
    title: "Fantasy Baseball Platform",
    year: "2026",
    kind: "Build",
    blurb:
      "A Postgres-backed fantasy baseball application that folds a prospect database, a trade evaluator, and a draft tool into one system wired to live MLB data.",
    tags: ["Postgres", "Python", "Data Modeling", "APIs"],
    href: "projects/fantasy-baseball.html",
  },
  {
    title: "Placeholder — RevOps Case Study",
    year: "2026",
    kind: "Case study",
    blurb:
      "Replace this entry in assets/js/projects.js. A good case study names the problem, the constraint you were working under, what you built, and what changed as a result.",
    tags: ["RevOps", "Salesforce", "Process"],
    href: "projects/_template.html",
    draft: true,
  },
  {
    title: "Placeholder — Analysis or Tool",
    year: "2025",
    kind: "Analysis",
    blurb:
      "Copy projects/_template.html to a new file, write it up, then point a new entry here at it.",
    tags: ["SQL", "Reporting"],
    href: "projects/_template.html",
    draft: true,
  },
];
