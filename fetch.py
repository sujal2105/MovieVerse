import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")


@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):

    try:

        url = f"https://api.themoviedb.org/3/movie/{movie_id}"

        params = {"api_key": API_KEY}

        response = requests.get(url, params=params, timeout=10)

        response.raise_for_status()

        data = response.json()

        return {
            "poster": f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else None,
            "backdrop": f"https://image.tmdb.org/t/p/original{data['backdrop_path']}" if data.get("backdrop_path") else None,
            "rating": round(data.get("vote_average", 0), 1),
            "year": data.get("release_date", "")[:4],
            "overview": data.get("overview", ""),
            "genres": ", ".join(g["name"] for g in data.get("genres", [])),
            "runtime": data.get("runtime", 0),
        }

    except requests.RequestException:
        return None