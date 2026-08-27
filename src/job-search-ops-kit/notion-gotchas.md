# Notion API Gotchas, Learned the Hard Way

Real errors hit while building this system, and what actually fixed them.
If you're building something similar via Claude's Notion tools, this will
save you the same round-trips.

## Formula properties

**Problem:** `ADD COLUMN "Staleness" FORMULA(if(...))` fails with
`Unexpected character: =` or similar cryptic errors that look like an
operator problem.

**Fix:** The formula expression must be a single-quoted string literal in
the DDL, not bare syntax:

```
ADD COLUMN "Staleness" FORMULA('if(prop("Status") == "Rejected", "CLOSED", "ACTIVE")')
```

Standard operators (`==`, `>=`, `and`/`or`) work fine *inside* the quoted
string. Don't waste time on function-call workarounds like `equal()` or
`greaterThanOrEqualTo()`. That's solving the wrong problem.

**Also:** avoid raw emoji characters inside formula string literals. They
can silently corrupt into garbled text on write. Plain ASCII labels are
safer for anything a formula generates. Use Notion's native color-coded
Select/Status properties if you want color, not emoji-in-text.

## Adding options to an existing Select/Status column

`ADD COLUMN` only works for genuinely new columns. To add options to one
that already exists:

```
ALTER COLUMN "Connection Status" SET SELECT('Option A':gray, 'Option B':green, ...)
```

List *all* existing options plus the new ones, with their original colors
This replaces the full option set, it doesn't append.

## Cross-database SQL queries

`notion-query-data-sources` can run aggregate queries (COUNT, GROUP BY)
against a single database fine. Subqueries spanning multiple data sources
in one query currently require a Notion Business plan, which is a real
plan gate, not a tool bug, and shows up as an upsell error.

## Formula/rollup fields aren't queryable

Formula and rollup properties (anything computed, like a Staleness or
Days-in-Pipeline field) show up in a `notAvailableInQuerySql` list and
can't be filtered/selected via the SQL query tool, only read via direct
page fetch. Even then, a page fetch returns an opaque `formulaResult://`
pointer, not the resolved value. There's currently no reliable way to
programmatically read what a formula actually evaluates to. You have to
trust the formula logic and spot-check in the Notion UI.

## Case-sensitivity trap in SQL queries

A query like `SELECT "company" FROM ...` may silently match a differently-
cased property (`"Company"`) due to case-insensitive column resolution in
the query layer, which can make a genuinely empty duplicate property look
"100% filled" in an aggregate query. If two similarly-named properties
exist, verify with a direct page fetch, not a SQL aggregate, before
concluding either one is in use.

## Duplicate properties appear on their own sometimes

If a property's type gets changed through the Notion UI (e.g., converting
a Select to a Status type, or fixing a field's casing), Notion can
sometimes create a fresh duplicate property instead of modifying the
original in place, leaving an orphaned duplicate with generic default
values. Periodically check the schema for near-duplicate names before
assuming everything is one clean copy.

## No delete/trash tool

There's no direct "delete this page" tool available through these Notion
integrations. `notion-move-pages` (relocate) exists; permanent deletion
requires the person doing it manually in the Notion UI. One practical
workaround: move anything you'd otherwise delete to an "Archive" section
so it's out of the way even if it isn't truly gone.

**Careful with full-page content rewrites:** repositioning an existing
child page's reference during a full-content replace can occasionally get
treated as a removal by Notion's content-diffing, actually trashing the
page rather than just moving it. Prefer small, targeted search-and-replace
edits over full-page rewrites when reorganizing a page that has many
existing child pages.

## Intermittent "No approval received" errors

Some write operations return this on the first attempt and succeed
identically on retry, with no discernible pattern to when it happens.
Just retry once before assuming something is actually broken.

## Dedup logic: don't trust a unique ID alone

If you're deduping records sourced from an external feed (job board
listings, RSS, etc.), matching on a unique ID from that feed isn't
sufficient, because the same underlying listing can get issued multiple
different tracking IDs (reposts, syndication, multiple entry points).
Dedupe primarily on the semantic content (e.g., Company + Role title,
normalized) and treat ID matching as a secondary signal, not the primary
one.
