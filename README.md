# Portfolio

A lightweight static portfolio site. No framework, no build step, no dependencies —
plain HTML, one stylesheet, and about 100 lines of JavaScript. Open `index.html` in a
browser and it works.

**Live:** https://zpressley.github.io/

## Adding a project

1. Copy `projects/_template.html` to `projects/your-slug.html` and write it up.
2. Add an entry to the top of the array in `assets/js/projects.js`:

```js
{
  title: "Project name",
  year: "2026",
  kind: "Case study",              // Case study | Build | Analysis | Tool
  blurb: "One or two sentences.",
  tags: ["RevOps", "SQL"],         // these also become the filter chips
  href: "projects/your-slug.html", // or an external URL + external: true
}
```

3. Commit and push. GitHub Pages redeploys in about a minute.

That's the whole workflow — the filter chips, the project count, and the grid all
build themselves from that array.

## Layout

```
index.html              home — hero, work grid, about, contact
projects/
  _template.html        copy this for each new case study
  fantasy-baseball.html
assets/
  css/style.css         all styling; colors are CSS variables at the top
  js/projects.js        project data — the only file you need to edit regularly
  js/main.js            grid rendering, filters, theme toggle
  img/                  screenshots
.nojekyll               tells GitHub Pages to serve the files as-is
```

## Changing the look

Every color lives in the `:root` block at the top of `assets/css/style.css`.
`--accent` is the teal; change that one value and the whole site follows.
The light theme overrides sit right below it.

## Local preview

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```
