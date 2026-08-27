# Daily Job-Search Digest Automation

An optional fourth automation: a scheduled task that runs weekday
mornings, diffs the tracker against its own prior snapshot, cross-checks
it against the real calendar, and sends a status email. This is the most
complex piece in the kit because it's the only one that actively compares
"what we think is true" against "what's actually true" and catches the
gap, rather than just processing new input.

## What it does

Two things from one run:
1. **Updates an internal Notion digest page in place** (plain markdown).
   This page is the automation's own memory of what it already reported,
   which is what makes real day-over-day diffing possible instead of
   just dumping current state every time.
2. **Sends a styled HTML email** summarizing pipeline status, meetings,
   what's genuinely new, a short action list, and progress since the
   last run.

It's worth building because it catches things neither the tracker nor the
calendar surfaces on its own: a meeting-prep note says one time, the
actual calendar invite (updated later) says another, and now there's a
double-booking nobody noticed yet. Diffing live calendar state against
what the database assumes is where the real value is.

## Prerequisites

- Notion connector, with access to the Applications and LinkedIn Outreach
  databases plus a plain internal digest page (not a database row).
- Calendar connector.
- Email-sending connector.
- A `Status` field on Applications that's a real funnel (Interested →
  Applied → named interview stages → a terminal state), not a single
  generic "Interviewing" bucket, and a `Last Activity` (last-edited-time)
  field on both databases.

## Closed-item suppression

Once something moves into a closed/terminal state, stop actively
featuring it once it's been closed more than 2-3 days. Exceptions: an
open offer is never suppressed, a closed item still relevant to something
active gets a brief mention for context, and a closed item can appear
once as genuinely new news right when it happens, then drops off.

## The run, step by step

1. Fetch the internal digest page first, before touching anything else.
   Read its content and its own "last updated" date; that's the prior
   snapshot and the day-gap reference.
2. Query both databases for full current state.
3. Apply the suppression rule when deciding what makes each section.
4. Query the calendar for the next ~7 days and past 2-3 days,
   cross-referencing attendees/titles/companies against the tracker.
5. **Cross-check calendar reality against what the tracker assumes.**
   This is where the highest-value catches happen. Trust the calendar
   event's actual timestamp over a database note or a prep page written
   before a reschedule.
6. Overwrite the internal digest page (don't duplicate it) with fresh
   state plus an updated "last updated" date. If anything time-sensitive
   turned up, write it back onto the relevant tracker row too (a note
   plus a follow-up flag) so the source of truth stays accurate, not
   just the digest.
7. Send the email.
8. Only fire a push notification if something genuinely needs attention
   before the recipient opens the email. A routine "nothing changed" run
   should stay silent, which is what makes a notification meaningful
   when it does happen.

## Quote sources: ask, don't assume

The version this was generalized from closes each email with a short
quote, and the specific source pool was a personal choice tied to the
original person's own taste. **Don't carry a specific pool over into a
new deployment.** Ask the person directly what they'd actually want, if
anything: a specific author or tradition, a general theme (perseverance,
craftsmanship, patience), a mix that rotates, or no quote at all. Store
whatever they choose on the Mission Statement page as a named preference,
and have the digest prompt reference that instead of a hardcoded list.
If they don't want a quote, skip the section entirely rather than
defaulting to something generic.

## Scheduling

Use the platform's real scheduled-task/trigger tool, a proper
cron-backed scheduled task, not an in-process or local cron. Anything
scheduled outside the platform's own trigger system gets lost the moment
the session ends and will silently stop running. Write the trigger's
prompt as a fully standalone instruction: each firing starts a fresh
session with no memory of prior runs, so the prompt needs the real data
source IDs, the digest page URL, and the template inline or via a
referenced skill, not "do what we did last time."

## Gotchas

- **Calendar event timestamp vs. timezone label mismatches.** Some
  calendar events carry an explicit UTC offset on the timestamp itself
  alongside a timezone label that doesn't match it. The offset embedded
  in the timestamp is authoritative for the actual instant; trust that
  over a mismatched timezone label. This is exactly how a real
  double-booking got caught in the original build: two events had
  identical actual start instants despite different timezone labels.
- **Formula fields aren't SQL-queryable** (see `notion-gotchas.md`).
  Don't spend a query attempt on a staleness-style formula column in SQL
  mode; derive it from a real date field instead.
- **Large query results can exceed a tool's inline token limit** and get
  dumped to a scratch file. Re-running with a tighter column list or a
  `WHERE` clause is usually faster than reading the dumped file.
- **Diff against the digest page's own "last updated" date, not a
  hardcoded day count.** This is what makes a Monday run correctly roll
  up the whole weekend instead of just assuming "yesterday."

See `email-style-guide.md` in this kit for the actual visual template and
writing rules this automation's output should follow.
