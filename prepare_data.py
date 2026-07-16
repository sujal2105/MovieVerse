import pandas as pd
import ast
import pickle


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading dataset...")

# Load dataset
movies = pd.read_csv("movies.csv")

# Keep required columns
movies = movies[
    [
        "id",
        "title",
        "genres",
        "keywords",
        "overview",
        "vote_average",
        "release_date"
    ]
]

# Remove missing values
movies.dropna(inplace=True)
def convert(text):
    result = []

    for item in ast.literal_eval(text):
        result.append(item["name"])

    return result
movies["genres"] = movies["genres"].apply(convert)
movies["keywords"] = movies["keywords"].apply(convert)


movies["overview"] = movies["overview"].apply(lambda x: x.split())

movies["tags"] = (
    movies["genres"]
    + movies["keywords"]
    + movies["overview"]
)

movies["tags"] = movies["tags"].apply(lambda x: " ".join(x))

movies["tags"] = movies["tags"].apply(lambda x: x.lower())


print("\nCreating vectors...")

cv = CountVectorizer(
    max_features=5000,
    stop_words="english"
)

vectors = cv.fit_transform(movies["tags"]).toarray()

print("Calculating similarity...")

similarity = cosine_similarity(vectors)

print("Similarity Shape:", similarity.shape)

print("Saving processed data...")

pickle.dump(
    movies,
    open("movies.pkl", "wb")
)

pickle.dump(
    similarity,
    open("similarity.pkl", "wb")
)

print("Done!")