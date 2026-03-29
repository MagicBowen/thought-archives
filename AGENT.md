# ThoughtArchives Agent Guide

## Project Intent

This repository contains the `ThoughtArchives / 思想档案` blog built with MkDocs.

The current direction is:

- Replace the third-party Dracula theme with a custom local MkDocs theme.
- Keep the site optimized for long-form software engineering essays rather than generic product docs.
- Preserve clean GitHub Pages deployment with standard MkDocs builds.

## Active Product Decisions

- Brand: bilingual `ThoughtArchives / 思想档案`.
- Visual direction: light-first editorial theme with an optional dark toggle.
- Theme implementation: use MkDocs custom theme development based on the official theme developer guide and `theme.custom_dir`.
- Navigation policy: do not maintain a hand-written `nav` tree in `mkdocs.yml`; navigation must follow the directory structure under `docs` automatically.
- URL policy: keep `use_directory_urls: true`.
- Deployment policy: use the current GitHub Pages artifact workflow in GitHub Actions instead of `mkdocs gh-deploy`.

## Theme Goals

The custom theme should feel like a serious technical archive:

- Reading-first layout for long Chinese and bilingual technical essays.
- Strong typography, restrained color system, and better spacing than stock MkDocs themes.
- Homepage as an editorial landing page, not just a docs index.
- Article pages with clear hierarchy, sticky table of contents, strong code block styling, and better previous/next navigation.
- Responsive behavior must work well on both desktop and mobile.

## Navigation Rules

- The navigation shown by the site must be derived from the physical structure under `docs/`.
- Changing folders or Markdown files under `docs/` should automatically change the navigation without editing `mkdocs.yml`.
- Avoid adding manual `nav:` unless there is a very strong reason and the user explicitly approves that tradeoff.
- Directory names and file names are part of the public URL structure. Rename carefully.

## Content Structure Rules

- Keep Markdown source files under `docs/`.
- Do not edit generated files under `site/`.
- Normalize directory names and paths when needed:
  - no trailing spaces
  - no accidental duplicate naming patterns caused by theme workarounds
  - keep names readable because they become URLs

## Image And Asset Rules

This repository currently has a known MkDocs authoring problem:

- Some images only render correctly because the generated HTML adds an extra output directory layer when `use_directory_urls: true`.
- That behavior makes the Markdown source paths non-standard and confusing.

Required fix direction:

- Authors should write image paths relative to the current Markdown file in the normal Markdown sense.
- The site build must preserve clean page URLs while making those relative image paths resolve correctly in generated HTML.
- The preferred implementation is a local MkDocs hook script using `hooks:` in `mkdocs.yml`, not a third-party dependency unless there is a clear need.

When updating content:

- Prefer standard relative references from the Markdown file to the asset file.
- Fix existing broken or misleading image references as part of migration work.
- Verify both build warnings and rendered HTML paths after any content move.

## Implementation Constraints

- Follow the official MkDocs docs for theme development:
  - https://www.mkdocs.org/dev-guide/themes/
  - https://www.mkdocs.org/user-guide/configuration/
- Prefer extending the built-in `mkdocs` theme with `custom_dir` unless a full local theme is clearly simpler.
- Keep dependencies minimal.
- Avoid adding a heavy frontend toolchain unless the user asks for it.

## Deployment Constraints

- GitHub Actions should:
  - build the MkDocs site
  - upload the built `site/` directory as a Pages artifact
  - deploy through the official Pages actions
- The workflow should publish on push to the main publishing branch.

## Validation Checklist

Before considering work complete:

- `mkdocs build --clean` succeeds.
- Navigation reflects the directory structure under `docs/`.
- Image references resolve correctly in the generated HTML without relying on extra article-name directories.
- The custom theme works for homepage, article pages, code blocks, images, and nested sections.
- GitHub Actions workflow matches the current Pages artifact deployment pattern.

## Notes For Future Agents

- Read representative long-form articles before changing layout. This is a blog with essays, not API docs.
- Keep the design opinionated but restrained.
- If a content-path cleanup changes public URLs, call that out explicitly in the final response.
