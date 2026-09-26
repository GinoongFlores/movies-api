"""
seed.py — starter data for classroom demos.

Why seed at all?
  - A brand-new movies.db is empty. Empty lists make poor lecture demos.
  - Seeding gives every student the same 14 movies on first run so
    GET /movies always shows something useful.

Why HAND-CRAFTED titles (not copied from TMDB / OMDb / etc.)?
  - Academic honesty and copyright: we do not scrape or paste real catalogs.
  - The brief asks for original sample data students can safely share.
  - Fiction also avoids students confusing "demo data" with a live movie API.
  - When you later teach API consumption, THAT is when you call an external API;
    this project teaches building your OWN API first.

These records go through the Model (create_movie), not raw SQL — same path
as a real POST /movies request. That keeps seed behaviour consistent with the API.
"""

from models import create_movie, get_all_movies, init_db, movie_count

# Original sample movies crafted for ITCC 14 — not from any public movie API.
SEED_MOVIES = [
    {
        "title": "Midnight Lanterns",
        "year": 2019,
        "genre": "Drama",
        "director": "Elena Marquez",
        "rating": 8.2,
    },
    {
        "title": "Circuit Rain",
        "year": 2021,
        "genre": "Sci-Fi",
        "director": "Jonah Reyes",
        "rating": 7.5,
    },
    {
        "title": "Harbor of Quiet Stars",
        "year": 2017,
        "genre": "Romance",
        "director": "Sofia Lim",
        "rating": 8.7,
    },
    {
        "title": "The Last Bamboo Train",
        "year": 2015,
        "genre": "Adventure",
        "director": "Marco Villanueva",
        "rating": 7.9,
    },
    {
        "title": "Pixel Ghosts",
        "year": 2023,
        "genre": "Horror",
        "director": "Aya Tanaka",
        "rating": 6.8,
    },
    {
        "title": "Coffee Before Dawn",
        "year": 2018,
        "genre": "Comedy",
        "director": "Luis Ortega",
        "rating": 7.1,
    },
    {
        "title": "Maps Without Roads",
        "year": 2020,
        "genre": "Documentary",
        "director": "Priya Nandakumar",
        "rating": 9.0,
    },
    {
        "title": "Iron Whispers",
        "year": 2016,
        "genre": "Thriller",
        "director": "Daniel Cho",
        "rating": 8.0,
    },
    {
        "title": "Sunken Cathedral",
        "year": 2022,
        "genre": "Fantasy",
        "director": "Isabelle Moreau",
        "rating": 8.4,
    },
    {
        "title": "Classroom Echoes",
        "year": 2014,
        "genre": "Drama",
        "director": "Kenji Sato",
        "rating": 7.6,
    },
    {
        "title": "Neon Bazaar",
        "year": 2024,
        "genre": "Action",
        "director": "Rafael Santos",
        "rating": 7.3,
    },
    {
        "title": "Letters from the Reef",
        "year": 2013,
        "genre": "Romance",
        "director": "Amelia Cruz",
        "rating": 8.5,
    },
    {
        "title": "Static Horizon",
        "year": 2021,
        "genre": "Sci-Fi",
        "director": "Noah Bergman",
        "rating": 6.9,
    },
    {
        "title": "The Quiet Algorithm",
        "year": 2025,
        "genre": "Mystery",
        "director": "Hannah Yu",
        "rating": 8.1,
    },
]


def seed(force=False):
    """
    Insert seed movies if the table is empty (or always if force=True).

    By default we skip when data already exists — so restarting the server
    does not duplicate the 14 samples. Delete movies.db (or pass force=True)
    if you want a clean demo database again.
    """
    init_db()
    count = movie_count()
    if count > 0 and not force:
        print(f"Database already has {count} movie(s). Skipping seed.")
        print("Pass force=True or delete movies.db to re-seed.")
        return get_all_movies()

    for movie in SEED_MOVIES:
        create_movie(movie)  # same Model path as POST /movies

    movies = get_all_movies()
    print(f"Seeded {len(movies)} movies.")
    return movies


if __name__ == "__main__":
    # Allows: python seed.py  (from the project folder, with venv active)
    seed()
