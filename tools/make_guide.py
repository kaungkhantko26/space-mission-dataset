#!/usr/bin/env python3
"""Render USER_GUIDE.md -> docs/guide.html (tiny markdown subset: headings, paragraphs, lists, tables, fenced code, inline code/bold/links)."""
import html, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
src = open(os.path.join(ROOT, "USER_GUIDE.md")).read().split("\n")
slug = lambda t: re.sub(r"[^a-z0-9]+", "-", re.sub(r"^\d+\.\s*", "", t.lower())).strip("-")


def inline(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", t)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)


out, i, title = [], 0, "User guide"
while i < len(src):
    l = src[i]
    if l.startswith("```"):
        j = i + 1; code = []
        while not src[j].startswith("```"): code.append(src[j]); j += 1
        out.append("<pre>" + html.escape("\n".join(code)) + "</pre>"); i = j + 1; continue
    if l.startswith("# "): title = l[2:]; i += 1; continue
    m = re.match(r"(#{2,3}) (.*)", l)
    if m:
        out.append(f'<h{len(m.group(1))} id="{slug(m.group(2))}">{inline(m.group(2))}</h{len(m.group(1))}>'); i += 1; continue
    if l.startswith("|"):
        rows = []
        while i < len(src) and src[i].startswith("|"):
            rows.append([c.strip() for c in src[i].strip().strip("|").split("|")]); i += 1
        h, body = rows[0], [r for r in rows[2:]]
        out.append('<div class="tw"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in h) + "</tr></thead><tbody>" +
                   "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>"); continue
    if re.match(r"^(\*|\d+\.) ", l):
        ordered = l[0].isdigit(); items = []
        while i < len(src) and re.match(r"^(\*|\d+\.) ", src[i]):
            items.append(re.sub(r"^(\*|\d+\.) ", "", src[i])); i += 1
        tag = "ol" if ordered else "ul"
        out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
    if l.strip():
        out.append(f"<p>{inline(l)}</p>")
    i += 1
page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>User Guide - Space Mission Dataset</title><link rel="stylesheet" href="style.css">
<style>main{{max-width:900px;margin:0 auto}}pre{{background:var(--card);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;overflow:auto;font-size:.82rem}}.tw{{overflow-x:auto}}h2{{margin-top:26px}}td code,li code,p code{{white-space:normal;overflow-wrap:anywhere}}</style></head>
<body>
<header><h1>{html.escape(title)}</h1><p class="sub"><a href="index.html">&larr; back to the explorer</a> &middot; <a href="api.html">API reference</a> &middot; <a href="https://github.com/kaungkhantko26/space-mission-dataset">GitHub</a></p></header>
<main>
{chr(10).join(out)}
</main>
<footer><a href="index.html">Explorer</a> &middot; <a href="api.html">API</a></footer>
</body></html>
'''
open(os.path.join(ROOT, "docs", "guide.html"), "w").write(page)
print("docs/guide.html", len(page), "bytes")
