
# MovieRec

A minimal movie recommendation backend built with **Python/Django** and the public **MovieLens (ml-latest-small)** dataset. The project is structured for iterative experiments (algorithms, evaluation, and API) and ships with Docker support for quick local runs.

> Status: work-in-progress. Contributions and issues are welcome.

---

## Features

- **Django project** (`backend/`) with a reusable app in `core/`
- **MovieLens `ml-latest-small/`** dataset included for quick bootstrapping
- Pluggable recommendation logic (start simple: popularity & user-based CF; iterate to model-based)
- REST-style endpoints for fetching movies and (optionally) posting ratings
- **Dockerfile** + **docker-compose** for one-command startup

> Tip: If you only need to experiment in a notebook, you can load the CSVs from `ml-latest-small/` directly and skip Django.

---

## Project layout

```
movierec/
├─ backend/              # Django project (settings, urls, wsgi/asgi)
├─ core/                 # App: models, data loading, simple recommenders, views
├─ ml-latest-small/      # MovieLens dataset (CSV files)
├─ Dockerfile
├─ docker-compose.yaml
├─ manage.py
└─ requirements.txt
```

> The exact modules may evolve; check `core/` for the latest algorithm and API code.

---

## Quickstart (local)

### 1) Clone & create a virtual env

```bash
git clone https://github.com/kanyebek/movierec.git
cd movierec

# Python 3.11+ is recommended
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```


### 2) Initialize the DB

```bash
python manage.py migrate
```

### 3) (Optional) Load MovieLens data into the DB

If a management command exists (e.g., `load_movielens`), run:

```bash
python manage.py load_movielens --path ./ml-latest-small
```

If not, check `core/` for a data-loading script and run it as documented there.

### 4) Run the dev server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## Quickstart (Docker)

```bash
# From the repository root:
docker compose up --build
# Then visit http://localhost:8000/
```

To stop:

```bash
docker compose down
```

---

## API (typical shape)

> Exact routes may differ; open `backend/urls.py` and `core/views.py` to confirm.

- `GET /api/movies` — list or search movies
- `GET /api/movies/{id}` — movie details
- `GET /api/recommend?user_id={id}` — top-N recommendations for a user
- `POST /api/ratings` — submit a rating payload like `{ user_id, movie_id, rating }`

If DRF or another framework is used, the browsable API may be available at `/api/`.

---

## Recommendation approaches

Start simple and iterate:

1. **Baseline / Popularity**: top-rated or most-rated movies (global prior)
2. **User-based CF**: cosine/pearson similarity on user–item matrix
3. **Item-based CF**: neighbors computed on item vectors
4. **Matrix factorization** (e.g., SVD/ALS) once ratings are persisted
5. **Hybrid**: fallback to popularity for cold-start users/items

> Persist user ratings (via `/api/ratings`) to continuously improve personalized recommendations.

---

## Development workflow

- Code style: black + isort
- Lint: `ruff`

Example:

```bash
pip install -U black isort ruff pytest
black . && isort . && ruff check .
pytest -q
```

---

## Common issues & tips

- **Dataset path**: if a loader expects a path, pass `--path ./ml-latest-small` or set `MOVIELENS_DIR` env var.
- **Migrations**: if models change, run `python manage.py makemigrations && python manage.py migrate`.
- **CORS**: if you add a separate UI, enable CORS for your frontend origin.
- **Docker file changes**: rebuild with `docker compose up --build`.

---

## Roadmap

- [ ] Confirm and document the exact API routes
- [ ] Add rating persistence & simple CF baseline
- [ ] Add evaluation scripts (precision@k, recall@k, MAP, NDCG)
- [ ] Add Swagger/OpenAPI docs
- [ ] Ship a lightweight UI (React/Streamlit) for demo

---

