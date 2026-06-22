# MedAlgo Hub

An open **registry + knowledge** platform where researchers publish algorithms,
others read about them, and results are reproduced. We host metadata and
**pointers** — never the code, weights, or data, and never patient images.

**Stack:** Django + HTMX + Tailwind. One repo, one process, one deploy.
Server-rendered, no SPA, no separate API. SQLite in dev, Postgres in prod.

## What this is (and isn't)

- ✅ A catalogue of algorithms with versions, a compatibility matrix, declared
  capabilities, dependencies, and a "read about it" page.
- ✅ Pointers to where code/data actually live (Git repo, Hugging Face dataset).
- ❌ **Not** a compute platform. We do not run uploaded code server-side.
  "Testing" means reproducible recipes you run on your own machine. This is a
  deliberate cost/security decision — see *Roadmap*.

## Quickstart (dev)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed                 # 11 categories + 6 sample algorithms
python manage.py createsuperuser      # for /admin
python manage.py runserver
```

Open http://127.0.0.1:8000 — Home, Explore (live HTMX search), algorithm detail.
Manage content at http://127.0.0.1:8000/admin.

## Project layout

```
config/        Django project (settings, urls, wsgi)
algorithms/    core app: models, views, admin, templates, seed command
templates/     base.html + algorithms/ (server-rendered + HTMX partials)
static/        committed CSS/JS for prod
Dockerfile     single-image deploy
```

## Data model (`algorithms/models.py`)

- **Category** — the 11 plugin kinds (engine, metric, exporter, …).
- **Algorithm** — name, category, field, owner, license *(required)*, blurb,
  markdown description, **pointers** (repo/dataset/docs URLs), declared
  **capabilities** (gpu/network/filesystem/data-access), hooks, deps, signals.
- **Version** — immutable release pinned to a `commit_sha`, with a per-core-line
  **compatibility matrix** (`{"1.2":"ok","1.3":"warn",...}`) and changelog notes.

## Production notes

- **Config is env-driven** (`.env.example`). Set `DEBUG=False`, a real
  `SECRET_KEY`, `ALLOWED_HOSTS`, and `DATABASE_URL=postgres://…`.
- **Static/CSS without Node.** Dev uses the Tailwind Play CDN for zero setup.
  For prod, drop the CDN `<script>` tags in `base.html` and build CSS with the
  **Tailwind standalone CLI** (a single binary, no Node):
  ```bash
  ./tailwindcss -i static/src.css -o static/app.css --minify
  ```
  then `collectstatic`. This removes all external scripts (no CDN-compromise
  surface) and is served hashed by WhiteNoise.
- **Deploy:** `docker build -t medalgo-hub . && docker run -p 8000:8000 medalgo-hub`
  (Railway / Fly / Render / a cheap VPS all work — it's one container).

## Roadmap

1. **Auth & uploads** — `django-allauth` (GitHub/ORCID), a publish form, per-user
   ownership, and **per-artifact license capture** before any external upload.
2. **Search** — swap the dev `icontains` for Postgres full-text (`SearchVector`)
   + optional `pgvector` "find similar".
3. **Knowledge layer** — markdown docs/lessons per algorithm (the "Academy").
4. **Reproducibility** — manifest validation (links resolve, schema parses);
   render a `docker run` recipe + reported metrics.
5. **(Maybe, later) execution** — only a cheap, sandboxed, capability-gated tier
   (`gpu:false, network:false, masks-only`); GPU work stays bring-your-own-compute.

## License

TBD — **must** be settled before the first external upload, alongside upload
terms and the per-artifact license field (we redistribute others' work).
