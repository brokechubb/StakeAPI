# StakeAPI Documentation

This directory contains the full StakeAPI documentation site, built with Jekyll and the [just-the-docs](https://just-the-docs.github.io/just-the-docs/) theme.

## Viewing the Docs

The documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch.

**Live site:** [https://brokechubb.github.io/StakeAPI/](https://brokechubb.github.io/StakeAPI/)

## Building Locally

```bash
cd docs
bundle install
bundle exec jekyll serve
```

Then open `http://localhost:4000/StakeAPI/` in your browser.

## Structure

- `getting-started/` — Installation, authentication, quick start
- `guides/` — In-depth guides for all features
- `api-reference/` — Complete API documentation
- `resources/` — Examples, FAQ, troubleshooting, changelog
- `_config.yml` — Jekyll site configuration
- `sitemap.xml` — Sitemap for search engines
