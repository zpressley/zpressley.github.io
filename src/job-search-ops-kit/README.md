# Go-To-Job-Market Kit

The genericized version of the Go-To-Job-Market System described in the
[case study](https://zpressley.github.io/projects/job-search-ops.html): a Notion
workspace, a verified accomplishment bank, and three scheduled Claude skills that handle
the repetitive parts of a job search.

Everything personal has been stripped out. The bootstrap prompt interviews you about your
own background and builds your own version.

## Start here

`bootstrap-prompt.md` is the whole setup. Paste it into a Claude session with Notion
connected and work through the phases. It walks through connecting tools, interviewing you
about your background, building a verified Background Bank, standing up the four-database
architecture, and installing the skills.

## What's in the box

| File | What it does |
| --- | --- |
| `bootstrap-prompt.md` | The setup script. Phases 0 through 7, start to finish |
| `job-application-tailor-template.skill` | Reads a job description, writes a tailored resume, cover letter, and spoken intro, pulling only from verified background |
| `meeting-investigator-template.skill` | Pre-call company research, honest green/red flag read, and public professional profiles of who you're meeting |
| `linkedin-alert-parser-template.skill` | Parses LinkedIn job-alert emails and dedupes against what you already track |
| `daily-digest-automation.md` | The weekday morning status email, generalized |
| `ai-writing-tells.md` | A checklist for catching AI-sounding writing before it reaches a recruiter |
| `resume-style-by-industry.md` | Where the default tech resume format is the wrong call, and what academia, government, legal, and creative fields expect instead |
| `email-style-guide.md` | Voice rules for anything the system sends on your behalf |
| `notion-gotchas.md` | Notion API problems I hit and how I got around them |

## The one rule worth keeping

The Background Bank is a verification layer, not a content store. Every claim in it traces
to a real source document. Conflicting numbers get flagged rather than quietly resolved.
Anything unconfirmed stays out until you sign off on it. The tailoring skill pulls only
from that page, and flags gaps instead of inventing something to fill them.

Skip that part and you have a very fast way to put things on a resume that fall apart
under a follow-up question.

## Installing the skills

The `.skill` files are zip archives containing a `SKILL.md`. Install them in Cowork or
Claude Code the same way as any other skill. Each one is a template. Read it before you run
it, because the phrasing assumes the Notion structure the bootstrap prompt builds.
