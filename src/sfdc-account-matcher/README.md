# SFDC Account & Contact Matcher

Source for the matching tool described in the
[case study](https://zpressley.github.io/projects/sfdc-account-matcher.html).
A browser sample of the string-matching half runs
[here](https://zpressley.github.io/demo/account-matcher.html).

Built where no Salesforce API access was available, so nothing here is a live lookup —
it all runs in batch against periodically exported account and contact CSVs. That
constraint drove the architecture rather than the other way around.

## What's in here

| File | What it is |
| --- | --- |
| `account_matcher.py` | The main Streamlit app. Two tabs — account matching and contact matching — with three selectable account algorithms |
| `email_name_matcher.py` | A standalone contact matcher, specialized for email + name inputs with configurable name strategies |
| `fuzzy_match_accounts.py` | The simple version that came first: a script, top 3 by `token_sort_ratio`, CSV in, CSV out |
| `setup_enhanced_matcher.sh` | Environment setup — venv, dependencies, launch scripts, sample CSV templates |
| `USER_GUIDE.md` | Written for teammates, not engineers |
| `requirements.txt` | Pinned dependencies |

## How account matching works

Names are normalized first — `clean_company_name()` strips fourteen legal-suffix patterns
by regex (inc, corp, llc, ltd, gmbh, plc, bv, srl, pte and the rest), drops punctuation,
and collapses whitespace. `Acme, Inc.` and `Acme Inc` should never have been different
strings.

Then one of three algorithms, chosen in the UI:

**Semantic (BERT)** — `all-MiniLM-L6-v2` via `sentence-transformers`. Embeddings for the
whole Salesforce account list are computed once and cached; incoming names are encoded per
run and scored by cosine similarity against the full matrix at once. This is the engine
that can resolve a subsidiary to its parent, which string comparison structurally cannot.

**Fuzzy String** — `rapidfuzz`'s `token_set_ratio` through `process.extract`, batched.
Fast, cheap, and reliable on the textual variants: abbreviations, suffixes, formatting.

**Hybrid** — semantic runs first, then the names it *didn't* match fall through to fuzzy.
Not both engines on everything: the expensive one goes first and the cheap one sweeps up
behind it. This is the mode worth using.

## How contact matching works

Contacts have a real identifier, so they get a priority cascade instead of a scorer:

1. **Exact email match** → 100%. Email is an identifier; it leads.
2. **Exact name match** → 100%.
3. **Word-indexed fuzzy match.** Rather than scoring against every contact, an inverted
   index of name words (3+ characters) narrows to a candidate set first, capped at 100,
   and fuzzy matching runs only on that. This is what makes it fast on large exports.

`email_name_matcher.py` handles the same problem differently — it validates the name
*against* an email match rather than short-circuiting on it, so a matching email whose
name disagrees becomes a flag instead of a trusted match.

Every result carries the method that produced it — `Email Exact`, `Smart Fuzzy (91%)`,
`Semantic Match` — so a reviewer sees *why* something matched, not just how well.

## Confidence bands

| Band | Score | Handling |
| --- | --- | --- |
| High | 90%+ | Trusted directly |
| Medium | 75–89% | Spot check |
| Review | Below 75% | Flagged for a human |

Output includes `CASE SAFE ID` columns, formatted for Salesforce campaign member uploads.

## Running it

```bash
pip install -r requirements.txt
streamlit run account_matcher.py
```

First run downloads the `all-MiniLM-L6-v2` model (~90MB).

`setup_enhanced_matcher.sh` automates the whole environment, but hardcodes a path to the
machine it was written on — edit that before running it elsewhere.

Both tools expect CSV exports: an incoming list, and a Salesforce reference export. No
customer data is included in this repository.

## Changes since it ran

The code here is what was actually built and used, with one fix applied after the fact:

**`Input_Index` collision in Hybrid mode.** Hybrid runs the semantic pass over the full
input, then hands the *unmatched* names to the fuzzy pass. The fuzzy pass numbered its
results by position in that filtered list, so after the two halves were concatenated the
`Input_Index` column contained duplicates pointing at the wrong rows — a six-row input
could come back as `[0, 3, 0, 1, 2, 3]`.

`Input_Name` was always correct, and the exported CSV keys off the name, so no output was
ever wrong because of this. Both matching functions now take an optional `input_indices`
map and Hybrid passes the original row numbers through; the same input now yields
`[0, 3, 1, 2, 4, 5]`. Behaviour is unchanged when the parameter is omitted.

This bug was in the original. It's noted rather than quietly fixed, because the version
that ran in production is the honest thing to describe.

## Stack

Python · pandas · numpy · rapidfuzz · sentence-transformers · torch · scikit-learn · Streamlit · chardet
