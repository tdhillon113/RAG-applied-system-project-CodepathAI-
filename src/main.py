"""
Command line runner for the Music Recommender Simulation with RAG.

This demonstrates music recommendations enhanced with Retrieval-Augmented Generation
to provide context-aware genre and artist insights.
"""

import logging

from src.recommender import load_songs, recommend_songs_with_rag
from src.genre_context_rag import GenreArtistRetriever

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the music recommender with RAG enhancement."""
    logger.info("Starting Music Recommender with RAG")

    # Load songs
    songs = load_songs("data/songs.csv")
    logger.info(f"Loaded {len(songs)} songs")

    # Initialize RAG retriever
    retriever = GenreArtistRetriever("data/context_knowledge_base.json")

    # Example user profile
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    logger.info(f"User preferences: {user_prefs}")

    # Get recommendations with RAG
    recommendations = recommend_songs_with_rag(user_prefs, songs, k=5, retriever=retriever)

    print("\n" + "=" * 70)
    print("🎵 MUSIC RECOMMENDER WITH GENRE/ARTIST CONTEXT (RAG)")
    print("=" * 70)
    print(f"\nUser Preferences: Genre={user_prefs['genre']}, Mood={user_prefs['mood']}, Energy={user_prefs['energy']}")
    print("\n" + "-" * 70)
    print("Top 5 Recommendations (with RAG Context):")
    print("-" * 70 + "\n")

    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"{i}. {song['title']} - {song['artist']}")
        print(f"   Genre: {song['genre']} | Score: {score:.2f}")
        print(f"   Because: {explanation}")

        # Retrieve and display genre context
        genre_context = retriever.get_genre_context(song["genre"])
        if genre_context:
            characteristics = genre_context.get("characteristics", [])
            if characteristics:
                print(f"   Genre characteristics: {', '.join(characteristics)}")

        print()

    print("=" * 70)
    print("✨ Recommendations powered by Retrieval-Augmented Generation (RAG)")
    print("=" * 70)


if __name__ == "__main__":
    main()

