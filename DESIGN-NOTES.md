# Design Notes

This repository deliberately avoids complex JavaScript frameworks, runtime Node dependencies, and external CDNs. It serves as a static HTML proof-of-concept for the Boris compiler.

## Structure
- `site/content/`: Contains the Markdown files that make up the site's pages.
- `site/theme/layouts/`: Contains the raw HTML templates (`home.html`, `main.html`) used by Boris to wrap the Markdown.
- `site/theme/assets/css/`: Contains the single, standalone `field-guide.css` file which provides the styling, dark mode, and responsive layout.

## Remaining Placeholders (TODOs)
Throughout the site (particularly on the `index.md` landing page), there are intentional placeholders labeled `[TODO: ...]`. 

These indicate missing URLs or resources that need to be manually injected before final submission, such as:
- The live deployment URL.
- The URL for the final demo video.
- The specific Release Tag for the Boris v0.7.0 binary.
- The Codex/ChatGPT session ID used during development.

We prefer explicitly marking these as `[TODO]` rather than inventing fake links to preserve the honesty of the project record.
