import os, requests
import streamlit as st

BASE_URL = os.getenv("RECS_BASE_URL", "http://127.0.0.1:8000")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

st.set_page_config(page_title="🎬 Movie Recs", layout="wide")
st.title("🎬 Movie Recommender — Clickable UI")

with st.sidebar:
    st.header("Settings")
    base = st.text_input("API base URL", value=BASE_URL)
    user_id = st.number_input("User ID", min_value=1, value=1)
    k = st.slider("How many recommendations?", 5, 40, 10)
    if st.button("🔧 Rebuild Index (admin)"):
        r = requests.post(f"{base}/api/admin/rebuild_index/", headers={"X-Admin-Token": ADMIN_TOKEN})
        st.success("Index rebuild triggered" if r.ok else f"Failed: {r.status_code} {r.text}")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔎 Search movies")
    q = st.text_input("Title contains")
    if st.button("Search") and q.strip():
        resp = requests.get(f"{base}/api/movies/search/", params={"q": q})
        if resp.ok:
            movies = resp.json()
            if not movies:
                st.info("No results.")
            for m in movies:
                with st.container(border=True):
                    st.markdown(f"**{m['title']}**  ")
                    st.caption(m.get("genres") or "")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("👍 Like (5★)", key=f"like_{m['id']}"):
                            payload = {"user_id": user_id, "movie": m["id"], "rating": 5}
                            r = requests.post(f"{base}/api/ratings/", json=payload)
                            st.toast("Saved 👍" if r.ok else f"Error: {r.text}")
                    with c2:
                        if st.button("👌 Meh (3★)", key=f"meh_{m['id']}"):
                            payload = {"user_id": user_id, "movie": m["id"], "rating": 3}
                            r = requests.post(f"{base}/api/ratings/", json=payload)
                            st.toast("Saved 👌" if r.ok else f"Error: {r.text}")
                    with c3:
                        if st.button("👎 Dislike (1★)", key=f"dis_{m['id']}"):
                            payload = {"user_id": user_id, "movie": m["id"], "rating": 1}
                            r = requests.post(f"{base}/api/ratings/", json=payload)
                            st.toast("Saved 👎" if r.ok else f"Error: {r.text}")
        else:
            st.error(f"Search failed: {resp.status_code}")

with col2:
    st.subheader("✨ Recommendations")
    if st.button("Get Recommendations"):
        r = requests.get(f"{base}/api/recommendations/", params={"user_id": user_id, "k": k})
        if r.ok:
            data = r.json()
            if not data:
                st.info("No recs yet — try liking a few movies.")
            else:
                for rec in data:
                    with st.container(border=True):
                        st.markdown(f"**{rec['title']}**  ")
                        st.caption(f"score: {rec.get('score', 0):.3f}")
        else:
            st.error(f"Failed: {r.status_code} {r.text}")