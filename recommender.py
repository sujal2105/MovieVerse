import pickle


# Load processed files
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))


def recommend(movie):

    # Find movie index
    movie_index = movies[movies["title"] == movie].index[0]

    # Get similarity scores
    distances = similarity[movie_index]

    # Sort movies by similarity
    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []

    for i in movie_list:
        recommendations.append(
            movies.iloc[i[0]]
        )

    return recommendations


# Test
if __name__ == "__main__":

    movies_found = recommend("Avatar")

    for movie in movies_found:
        print(movie["title"])