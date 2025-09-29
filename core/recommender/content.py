import json
import os
import joblib
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from django.db.models import Count
from core.models import Movie, Rating

ART_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ART_DIR, exist_ok=True)


def _item_bag(movie: Movie) -> str:
    genres = (movie.genres or "").replace("|", " ")
    tags = " ".join(t.tag for t in movie.tags.all())
    overview = movie.overview or ""
    return (genres + " " + tags + " " + overview).lower().strip()


def build_index():
    items = list(Movie.objects.prefetch_related("tags").all())
    ids = [m.movie_id for m in items]
    bags = [_item_bag(m) for m in items]
    vect = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
    X = vect.fit_transform(bags)
    joblib.dump(vect, os.path.join(ART_DIR, "tfidf.pkl"))
    sparse.save_npz(os.path.join(ART_DIR, "matrix.npz"), X)
    with open(os.path.join(ART_DIR, "index.json"), "w") as f:
        json.dump(ids, f)


def mmr_rerank(candidate_idx, X, user_vec, k=20, lambda_=0.7):
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity as cos
    chosen = []
    cand = list(candidate_idx)
    if not cand:
        return []
    user_sims = cos(user_vec, X[cand]).ravel()
    while cand and len(chosen) < k:
        if not chosen:
            j = int(np.argmax(user_sims))
            chosen.append(cand.pop(j))
            user_sims = np.delete(user_sims, j)
            continue
        chosen_mat = X[chosen]
        cand_mat = X[cand]
        div = cos(cand_mat, chosen_mat).max(axis=1)
        scores = lambda_ * user_sims - (1 - lambda_) * div
        j = int(np.argmax(scores))
        chosen.append(cand.pop(j))
        user_sims = np.delete(user_sims, j)
    return chosen


def recommend_for_user(user_id: int, top_k: int = 20, like_threshold: float | None = None, exclude_ids: set[int] | None = None):
    LIKE_THRESHOLD = float(os.getenv("LIKE_THRESHOLD", "3.5"))
    like_threshold = like_threshold or LIKE_THRESHOLD
    exclude_ids = exclude_ids or set()
    liked_qs = Rating.objects.filter(user_id=user_id, rating__gte=like_threshold).values_list("movie__movie_id", flat=True)
    liked = list(liked_qs)
    X = sparse.load_npz(os.path.join(ART_DIR, "matrix.npz"))
    ids = json.load(open(os.path.join(ART_DIR, "index.json")))
    id2row = {mid: i for i, mid in enumerate(ids)}
    if not liked:
        popular = (
            Rating.objects.exclude(movie__movie_id__in=exclude_ids)
            .values("movie__movie_id", "movie__title")
            .annotate(cnt=Count("id"))
            .order_by("-cnt")[: top_k]
        )
        return [{"movieId": r["movie__movie_id"], "title": r["movie__title"], "score": 0.0} for r in popular]
    liked_idx = [id2row[m] for m in liked if m in id2row]
    if not liked_idx:
        return []
    user_vec = X[liked_idx].mean(axis=0)
    user_vec = np.asarray(user_vec)
    if user_vec.ndim == 1:
        user_vec = user_vec.reshape(1, -1)
    user_vec = normalize(user_vec)
    sims = cosine_similarity(user_vec, X).ravel()
    seen = set(liked) | set(exclude_ids)
    candidates = [i for i in np.argsort(-sims) if ids[i] not in seen]
    picked = mmr_rerank(candidates, X, user_vec, k=top_k, lambda_=0.7)
    out = []
    for idx in picked:
        mid = ids[idx]
        m = Movie.objects.get(movie_id=mid)
        out.append({"movieId": mid, "title": m.title, "score": float(sims[idx])})
    return out
