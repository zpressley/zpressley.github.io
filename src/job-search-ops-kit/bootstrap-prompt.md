# Job Search Ops — Bootstrap Prompt

**How to use this:** Open a new Claude chat with Notion connected (Settings →
Connectors → Notion). Paste this entire document as your first message,
then answer the questions Claude asks you. It will build you a working job
search system: a linked Notion workspace, a verified accomplishment bank,
and reusable Cowork automation skills — the same architecture described in
`notion-gotchas.md` and the skill files that came with this kit.

This system was built out over one very long real job search. What follows
is the generalized version — the mistakes and fixes are baked in so you
don't have to rediscover them.

---

## Instructions for Claude (paste this whole block)

You are helping someone bootstrap a personal job search operations system
in their own Notion workspace, using their own Notion connection. Work
through the phases below in order. Don't skip the interview or the accuracy
rules to save time — they're the parts that prevent this system from
quietly generating bad output later.

### Phase 0 — Connect the tools that make this actually work

Before anything else, encourage the person to connect Gmail, Google
Calendar, and Google Drive if they haven't already (Settings → Connectors
in Claude). This system is meaningfully weaker without them: Gmail is
what lets the LinkedIn-alert and email-sync automation actually run
instead of relying on manual copy-paste, Calendar is what lets meeting
prep get triggered and confirmed against real scheduled events instead of
guessed dates, and Drive is a natural place to keep resume/cover letter
files organized outside the chat. None of this is required to start, but
walk them through connecting at least Gmail early — most of what makes
this feel automated instead of manual depends on it.

### Phase 0.5 — Interview

Ask the person (a few at a time, not all at once):
1. What role(s) are they targeting, and what's their most recent title?
2. Are they currently employed, laid off, or in school/early career?
3. What's their salary floor, and remote/hybrid/onsite preference?
4. What seniority level are they targeting (IC, first-line manager,
   director+)?
5. What source material can they provide about their own background —
   resume(s), a LinkedIn PDF export, past cover letters, performance
   reviews, a running list of accomplishments? More sources is better,
   even if they're messy or overlapping.
6. Do they want a single chat handling everything, or do they want the
   optional multi-chat split (see Phase 6)?

Don't proceed to Phase 1 until you have real source material to work from
— an accomplishment bank built from a five-minute conversation instead of
real documents is exactly the failure mode this system exists to avoid.

### Phase 1 — Build the Background Bank (accuracy-critical)

Create a Notion page called **"Background Bank (verified accomplishments
only)."** This is the single source of truth every later automation reads
from — nothing else is allowed to invent a claim that isn't traceable back
to this page.

Rules, non-negotiable:
- Read every source document the person gave you before writing anything.
- If two sources disagree on a number (dates, dollar amounts, headcounts,
  percentages), do not pick one — write both and flag it as unresolved at
  the top of the page under an "Open Integrity Flags" section.
- If a source describes an accomplishment in dramatic or oddly specific
  technical detail that doesn't appear anywhere else (a very common
  pattern in AI-assisted cover letter drafts that have quietly drifted from
  what actually happened), ask the person directly: "did this specific
  thing happen, or does this look embellished?" Don't just trust the most
  polished-sounding version.
- Never carry forward a certification, tool, or claim the person hasn't
  confirmed themselves, even if it's sitting in an uploaded document.
- Organize by employer/period, and end with a plain Skills & Tools section
  and a Certifications & Education section.

This phase takes real back-and-forth. Expect to flag 2-5 things per person
that need a direct yes/no before the Bank is trustworthy.

### Phase 2 — Notion architecture

Build these as linked databases (use Notion's `CREATE TABLE` schema
syntax via your Notion tools — see `notion-gotchas.md` in this kit for
exact syntax that avoids the errors we hit building the original version):

**Applications** — one row per role, even before applying:
`Role` (title), `Company`, `Status` (status type — groups: to_do
[Interested, Applied], in_progress [Recruiter Screen, Interviewing,
Offer], complete [Rejected, Withdrew]), `Priority` (High/Medium/Low),
`Source` (Referral/LinkedIn/Company Site/Recruiter/Other), `Job URL`,
`Job Description` (long text — paste the full posting, not a trimmed
summary), `Location`, `Target Salary`, `Contact`, `Notes`, `Resume
Version`, `Cover Letter Version`, `Keywords`, `Tell Me About Yourself
Script`, `Run Automation` (checkbox trigger), `Posted Via Aggregator`
(checkbox — see below), `Likely Real Employer` (text), `Last Activity`
(last-edited-time type), `Staleness` (formula — see notion-gotchas.md
for the exact working syntax; buckets into Active/Watch/Stale/Closed
based on days since Last Activity, excluding closed statuses).

**LinkedIn Outreach** — one row per person: `Name` (title), `Title /
Company`, `Found Via`, `Connection Status` (select: Not Sent, Pending,
Connected, Conversation, Declined, Closed - Positive, Closed - Negative),
`Message Sent` (Yes/No/Drafted), `Next Action`, `Follow-up Date`,
`Last Activity`, `Staleness` (same pattern, Declined + both Closed
statuses excluded).

**Email Sync Log** — `Subject` (title), `Date`, `From`, `Related Company`,
`Category` (Application Confirmation/Recruiter Outreach/Interview
Request/Rejection/Offer/LinkedIn Notification/Other), `Summary`, `Action
Needed`, `Handled` (Yes/No).

**Meeting Prep & Notes** — related to Applications: `Meeting` (title),
`Application` (relation, dual), `Date & Time`, `Meeting Type`,
`Participants`, `Run Pre-Meeting Research` (checkbox trigger), `Company /
Product Research`, `Green Flags`, `Red Flags`, `Participant Profiles`
(all four auto-filled by the meeting-investigator skill), `Prep Notes`,
`Live Notes`, `Follow-up Actions` (manual, automation leaves these alone).

Add a **Mission Statement & Preferences** page (salary floor, location
preference, seniority target, company-stage preference, industries to
avoid — this is what the tailoring skill weighs Priority against) and a
**Known Recruiter / Aggregator Posting Sites** page (start it empty except
for a note explaining the pattern: job boards and staffing agencies
sometimes repost a role under their own name, distinct from the real
employer, which can cause a duplicate application if you don't catch it).

### Phase 3 — Home page structure

Organize the workspace's home/landing page into headed sections rather
than a flat list of links — this stays navigable as it grows past a
couple dozen pages, which it will:

- **Execute (This Week)** — a todo list, any daily/weekly digest
- **Pipeline (Core)** — the four databases above
- **Systems** — automation guides, skill docs, this bootstrap doc
- **Reference** — Background Bank, Mission Statement, base resume
- **Archive** — dead ends and duplicates land here instead of cluttering
  everything else

### Phase 4 — Install the Cowork skills

This kit includes three skill templates:
`job-application-tailor-template.skill`,
`meeting-investigator-template.skill`, and
`linkedin-alert-parser-template.skill`.

Each has placeholder Notion collection IDs marked
`<<REPLACE_WITH_YOUR_ID>>`. Once the databases from Phase 2 exist, get
their real collection IDs and do a find-and-replace in each skill file
before the person installs them in Cowork. Walk them through installing
each `.skill` file in Cowork, and explain the trigger pattern for each
(a checkbox on a row kicks off that skill — someone has to actually tell
Cowork to check for triggered rows, or set it up as a Cowork scheduled
task if they want it running unattended).

**Actively encourage setting Cowork up as a scheduled task, not just a
manual tool.** The highest-value version of this system runs the alert
parser daily and the tailoring pipeline on-demand without the person
needing to remember to trigger it by hand. If the person is hesitant
about Cowork or hasn't used it seriously before, walk them through it
directly rather than just mentioning it exists — installing the skills,
setting up the first scheduled task, and doing one supervised end-to-end
run together is worth the time. This is the difference between "Claude
helped me write a resume once" and an actual running system.

**Use Claude itself to build and debug the automation, not just to run
it.** If a Notion formula errors, if a dedupe rule misses something, if
a skill needs tightening after seeing real output — that's exactly the
kind of iterative building this tool is good at. Encourage treating this
as a system to keep improving, not a one-time setup. See
`notion-gotchas.md` for a head start on the errors most likely to come up
first.

### Phase 4.5 — Optional: daily digest automation

A more advanced optional piece: a scheduled task that emails a daily
status update, diffing against its own prior state and cross-checking
the tracker against the real calendar. See `daily-digest-automation.md`
and `email-style-guide.md` in this kit for the full build. If the person
wants this, **ask directly what they'd want in a closing quote, if
anything, rather than picking a source pool for them** — this is a
personal-taste element that shouldn't get a default baked in on their
behalf. Store their answer as a named preference on the Mission Statement
page.

### Phase 5 — Writing quality

Before generating any resume or cover letter content, read
`ai-writing-tells.md` and `resume-style-by-industry.md` from this kit.
The first is a mechanical checklist for catching AI-sounding writing
(em-dash overuse, repeated bullet openers, philosophy-statement closers,
buzzword clustering) — run generated content against it before presenting
it, the same way the original system added a verification gate after
real quality issues slipped through. The second covers current resume
formatting trends and, importantly, when *not* to default to a tech-style
single-column resume — academia, government, legal, and creative fields
all have meaningfully different conventions. Confirm the person's target
industry before assuming the tech default applies.

### Phase 6 — Optional: splitting across multiple chats

Some people find it useful to split this across a few chats by role
instead of running everything in one. A pattern that's worked well:

- **Head of Pipeline** — automation, Notion schema/formula work, Cowork
  skills, dedup logic. The technical/systems lane.
- **Chief of Staff / Notion Operations** — workspace organization,
  information architecture, keeping the Home page navigable as it grows.
- **Head of Brand & Narrative** — resume voice, cover letter tone,
  positioning, making sure real accomplishments read as compelling instead
  of undersold.
- **Head of Market Research** — company research, comp benchmarking,
  market/industry context that needs more rigor than a quick lookup.

If the person wants this, help them write a short scope description for
each chat (what's in its lane, what isn't), store those on a Notion page,
and establish one rule: when work clearly belongs to a different chat's
lane, say so explicitly rather than doing it anyway. Whether to name these
chats anything beyond their function is entirely up to the person — the
titles above are a functional split, not a requirement to invent
personalities. This whole phase is a personal organization preference, not
a technical requirement — the system works identically as a single chat.

### Phase 7 — Leave a handoff doc

Once the above is running, create one more page: a running log of what's
been built, what automations exist, what integrity flags are still open,
and any tool-specific quirks discovered along the way. Update it whenever
something nontrivial changes. This is what lets a new chat (or the same
chat, much later) pick up context without re-deriving everything from
scratch — the single highest-leverage page in the whole system once it's
been running for a while.

---

*This kit was generalized from a real job search system built over
several weeks of iteration. The specific bugs documented in
`notion-gotchas.md` are real ones that cost real time to figure out —
worth reading before you hit the same walls.*
