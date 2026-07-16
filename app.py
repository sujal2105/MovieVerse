import html

import streamlit as st

from recommender import movies, recommend
from fetch import fetch_movie_details, API_KEY
st.html("<style>@media(max-width:640px){.stColumns{display:block!important}div.stButton>button{width:100%}}</style>")

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="MovieVerse",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.html("""
<style>
@media (max-width: 640px) {
    div[data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    div.stButton > button {
        width: 100%;
    }
}
</style>
""")
# ---------------------------------------------------------------------------
# Custom styling (style.css)
# ---------------------------------------------------------------------------
def load_css(path: str = "style.css") -> None:
    try:
        with open(path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Couldn't find {path} — the app will use default styling.")


load_css()

PLACEHOLDER_POSTER = "https://placehold.co/500x750/12121f/e5e7eb?text=No+Poster"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_display_info(row) -> dict:
    """Combine live TMDB data with the local dataset as a fallback,
    so the app still works even without an API key or connection."""

    fallback = {
        "poster": PLACEHOLDER_POSTER,
        "rating": row["vote_average"],
        "year": str(row["release_date"])[:4],
        "overview": " ".join(row["overview"]),
        "genres": ", ".join(row["genres"][:3]),
        "runtime": 0,
        "backdrop": None,
    }

    details = fetch_movie_details(int(row["id"]))
    if not details:
        return fallback

    return {
        "poster": details.get("poster") or fallback["poster"],
        "rating": details.get("rating") or fallback["rating"],
        "year": details.get("year") or fallback["year"],
        "overview": details.get("overview") or fallback["overview"],
        "genres": details.get("genres") or fallback["genres"],
        "runtime": details.get("runtime") or fallback["runtime"],
        "backdrop": details.get("backdrop"),
    }


def genre_badges(genres_csv: str, max_genres: int = 3) -> str:
    genre_names = [g.strip() for g in genres_csv.split(",") if g.strip()][:max_genres]
    return "".join(f"<span class='genre'>{html.escape(g)}</span>" for g in genre_names)


def render_card(row) -> None:
    info = get_display_info(row)

    st.markdown(
        f"""
        <div class="movie-card">
            <img src="{info['poster']}" alt="{html.escape(row['title'])} poster" />
            <h4 class="card-title">{html.escape(row['title'])}</h4>
            <div class="card-meta">
                <span class="rating">⭐ {info['rating']}</span>
                <span class="meta-pill">{info['year']}</span>
            </div>
            <div class="card-genres">{genre_badges(info['genres'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Hero section
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🎬 <span class="gradient-text">MovieVerse</span> 🍿</h1>
        <p>Discover your next favorite movie — powered by AI content-based recommendations.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not API_KEY:
    st.warning(
        "No TMDB_API_KEY found in your .env file, so posters and live ratings are "
        "unavailable — showing dataset info instead. Add a key to unlock full details.",
        icon="⚠️",
    )


# ---------------------------------------------------------------------------
# Search + selection
# ---------------------------------------------------------------------------
movie_list = sorted(movies["title"].unique())

search_col, button_col = st.columns([4, 1])

with search_col:
    selected_movie = st.selectbox("Search for a movie", movie_list)

with button_col:
    st.write("")
    st.write("")
    recommend_clicked = st.button("🔍 Recommend", width="stretch")


# ---------------------------------------------------------------------------
# Selected movie spotlight
# ---------------------------------------------------------------------------
if selected_movie:
    selected_row = movies[movies["title"] == selected_movie].iloc[0]
    info = get_display_info(selected_row)

    st.markdown('<div class="section-title">Now Showing</div>', unsafe_allow_html=True)

    backdrop_style = (
        f"background-image:url('{info['backdrop']}'); background-size:cover; "
        f"background-position:center 22%;"
        if info["backdrop"]
        else ""
    )
    runtime_html = (
        f"<span class='meta-pill'>{info['runtime']} min</span>" if info["runtime"] else ""
    )

    st.markdown(
        f"""
        <div class="spotlight" style="{backdrop_style}">
            <img class="spotlight-poster" src="{info['poster']}" alt="{html.escape(selected_row['title'])} poster" />
            <div class="spotlight-info">
                <h2>{html.escape(selected_row['title'])} <span class="meta-pill">({info['year']})</span></h2>
                <span class="rating">⭐ {info['rating']}</span>
                {runtime_html}
                <div style="margin-top:14px;">{genre_badges(info['genres'])}</div>
                <p class="overview">{html.escape(info['overview'])}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------
if recommend_clicked and selected_movie:
    with st.spinner("Finding movies you'll love..."):
        recommendations = recommend(selected_movie)

    st.markdown('<div class="section-title">You Might Also Like</div>', unsafe_allow_html=True)

    cols = st.columns(len(recommendations))

    for col, rec in zip(cols, recommendations):
        with col:
            render_card(rec)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.write("")
st.write("")
st.markdown(
    "<p style='text-align:center; color:#6B7280;'>Made by Sujal with ❤️ using Streamlit & TMDB API</p>",
    unsafe_allow_html=True,
)