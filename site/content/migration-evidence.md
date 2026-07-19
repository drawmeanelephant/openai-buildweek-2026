---
id: migration-evidence
title: Migration Evidence, Not Magic
parent: index
status: published
tags: [migration, dogfood, wordpress, starlight]
---

# Migration Evidence, Not Magic

Boris includes developer migration laboratories for auditing and converting
bounded slices of external content. They are not universal one-click importers,
and this distinction matters.

## What has been exercised

| Source shape | What the lab does | Honest boundary |
|---|---|---|
| WordPress WXR | Reads posts, pages, taxonomies, and local media candidates into a deterministic Boris candidate tree | Complex HTML and unavailable media remain review items |
| Astro/Starlight | Audits Markdown/MDX-shaped documentation, normalizes safe static patterns, and records manual-review events | Runtime components and arbitrary JSX are not silently reimplemented |
| Filed.fyi | Performs a read-only preflight on a real, complex archive | Custom frontmatter and interactive MDX require deliberate normalization |

<Aside kind="warning">
The migration labs are a safer way to understand a move. They do not promise
that an arbitrary production site can become Boris without editorial decisions.
</Aside>

## Why this is a product strength

Migration tools usually fail by being either too timid to help or too confident
to be trusted. Boris takes the middle route: preserve what it can, materialize
safe static equivalents where rules exist, and emit a review record for the
rest.
