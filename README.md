# thought-archives

ThoughtArchives / 思想档案 is a MkDocs-based technical blog with a custom local theme.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

## Notes

- Navigation follows the directory structure under `docs/`.
- The homepage renders a newest-first archive list across all posts.
- Archive ordering uses each Markdown file's last modified time.
- Relative media references in Markdown are rewritten during build so authors can write paths relative to the current Markdown file.

## Deployment

GitHub Pages deployment is handled by `.github/workflows/ci.yml` using the Pages artifact workflow.
