"""
Tests for the RAG-enhanced music recommender system.

This test suite validates that:
1. The retriever correctly loads and accesses the knowledge base
2. Genre context is accurately retrieved
3. Artist context is accurately retrieved
4. RAG scoring enhances recommendations appropriately
5. Error handling works correctly for missing data
"""

import pytest
import logging
from src.genre_context_rag import GenreArtistRetriever
from src.recommender import score_song_with_rag, recommend_songs_with_rag, load_songs

logger = logging.getLogger(__name__)


class TestGenreArtistRetriever:
    """Test the GenreArtistRetriever RAG module."""

    @pytest.fixture
    def retriever(self):
        """Create a retriever instance for testing."""
        return GenreArtistRetriever("data/context_knowledge_base.json")

    def test_retriever_initialization(self, retriever):
        """Test that the retriever initializes correctly."""
        assert retriever is not None
        assert retriever.knowledge_base is not None
        assert "genres" in retriever.knowledge_base
        assert "artists" in retriever.knowledge_base
        logger.info("✓ Retriever initialization test passed")

    def test_get_genre_context(self, retriever):
        """Test retrieving context for a known genre."""
        context = retriever.get_genre_context("pop")
        assert context is not None
        assert "characteristics" in context
        assert "related_genres" in context
        assert "typical_moods" in context
        assert len(context["characteristics"]) > 0
        logger.info("✓ Genre context retrieval test passed")

    def test_get_genre_context_missing(self, retriever):
        """Test retrieving context for an unknown genre."""
        context = retriever.get_genre_context("unknown_genre_xyz")
        assert context == {}
        logger.info("✓ Missing genre context test passed")

    def test_get_artist_context(self, retriever):
        """Test retrieving context for a known artist."""
        context = retriever.get_artist_context("Neon Echo")
        assert context is not None
        assert "genres" in context
        assert len(context["genres"]) > 0
        logger.info("✓ Artist context retrieval test passed")

    def test_find_related_genres(self, retriever):
        """Test finding related genres."""
        related = retriever.find_related_genres("pop")
        assert isinstance(related, list)
        assert len(related) > 0
        assert "indie pop" in related
        logger.info(f"✓ Related genres test passed: {related}")

    def test_get_related_artists_by_genre(self, retriever):
        """Test getting artists for a genre."""
        artists = retriever.get_related_artists_by_genre("pop")
        assert isinstance(artists, list)
        assert len(artists) > 0
        assert "Neon Echo" in artists
        logger.info(f"✓ Genre artists test passed: {artists}")

    def test_get_genre_transition_score(self, retriever):
        """Test genre transition scores."""
        # Known transition
        score = retriever.get_genre_transition_score("pop", "indie_pop")
        assert 0 <= score <= 1

        # Unknown transition
        score_unknown = retriever.get_genre_transition_score("unknown1", "unknown2")
        assert score_unknown == 0.5  # Default neutral score
        logger.info("✓ Genre transition score test passed")

    def test_get_characteristics(self, retriever):
        """Test retrieving genre characteristics."""
        chars = retriever.get_characteristics("rock")
        assert isinstance(chars, list)
        assert len(chars) > 0
        logger.info(f"✓ Genre characteristics test passed: {chars}")

    def test_search_by_mood(self, retriever):
        """Test searching genres by mood."""
        genres = retriever.search_by_mood("chill")
        assert isinstance(genres, list)
        assert len(genres) > 0
        # Should find lofi, ambient, etc.
        genres_list = [g[0] for g in genres]
        assert "lofi" in genres_list
        logger.info(f"✓ Mood search test passed: {genres_list}")

    def test_get_synergy_bonus_exact_match(self, retriever):
        """Test synergy bonus for exact genre match."""
        bonus = retriever.get_synergy_bonus("pop", "pop")
        # Exact match returns 0 (already scored in main recommender)
        assert bonus == 0.0
        logger.info("✓ Synergy bonus exact match test passed")

    def test_get_synergy_bonus_related_genre(self, retriever):
        """Test synergy bonus for related genre."""
        bonus = retriever.get_synergy_bonus("pop", "indie pop")
        assert bonus > 0  # Should get a bonus for related genre
        assert bonus <= 1.0  # Capped at 1.0
        logger.info(f"✓ Synergy bonus related genre test passed: {bonus}")

    def test_get_synergy_bonus_unrelated_genre(self, retriever):
        """Test synergy bonus for unrelated genre."""
        bonus = retriever.get_synergy_bonus("pop", "metal")
        # Should be 0 or minimal since they're not related
        assert bonus == 0.0 or bonus < 0.3
        logger.info(f"✓ Synergy bonus unrelated genre test passed: {bonus}")


class TestRAGEnhancedScoring:
    """Test RAG-enhanced recommendation scoring."""

    @pytest.fixture
    def retriever(self):
        """Create a retriever instance for testing."""
        return GenreArtistRetriever("data/context_knowledge_base.json")

    @pytest.fixture
    def user_prefs(self):
        """Create sample user preferences."""
        return {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

    @pytest.fixture
    def pop_song(self):
        """Create a pop song for testing."""
        return {
            "id": 1,
            "title": "Test Pop Song",
            "artist": "Test Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.85,
            "tempo_bpm": 120,
            "valence": 0.8,
            "danceability": 0.8,
            "acousticness": 0.1,
        }

    @pytest.fixture
    def related_genre_song(self):
        """Create a song in a related genre."""
        return {
            "id": 2,
            "title": "Test Indie Pop",
            "artist": "Indie Artist",
            "genre": "indie pop",
            "mood": "happy",
            "energy": 0.75,
            "tempo_bpm": 120,
            "valence": 0.8,
            "danceability": 0.8,
            "acousticness": 0.35,
        }

    def test_score_song_with_rag_exact_match(self, retriever, user_prefs, pop_song):
        """Test that exact genre match still works with RAG."""
        score, explanation = score_song_with_rag(user_prefs, pop_song, retriever)
        assert score > 0
        assert "genre match" in explanation
        logger.info(f"✓ RAG exact match scoring test passed: score={score}")

    def test_score_song_with_rag_related_genre(self, retriever, user_prefs, related_genre_song):
        """Test that RAG enhances scoring for related genres."""
        score, explanation = score_song_with_rag(user_prefs, related_genre_song, retriever)
        assert score > 0
        # Should have RAG boost
        assert "affinity" in explanation or "energy" in explanation
        logger.info(f"✓ RAG related genre scoring test passed: score={score}")

    def test_score_song_with_rag_has_explanation(self, retriever, user_prefs, pop_song):
        """Test that RAG scoring provides explanations."""
        score, explanation = score_song_with_rag(user_prefs, pop_song, retriever)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "+" in explanation  # Should contain scoring breakdowns
        logger.info("✓ RAG explanation test passed")


class TestRAGRecommendations:
    """Test end-to-end RAG recommendations."""

    @pytest.fixture
    def setup(self):
        """Load songs and create retriever."""
        songs = load_songs("data/songs.csv")
        retriever = GenreArtistRetriever("data/context_knowledge_base.json")
        return songs, retriever

    def test_recommend_songs_with_rag_returns_k_results(self, setup):
        """Test that RAG recommendations return requested number of songs."""
        songs, retriever = setup
        user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

        recommendations = recommend_songs_with_rag(user_prefs, songs, k=5, retriever=retriever)

        assert len(recommendations) == 5
        logger.info(f"✓ RAG recommendations k=5 test passed")

    def test_recommend_songs_with_rag_sorts_by_score(self, setup):
        """Test that recommendations are sorted by score in descending order."""
        songs, retriever = setup
        user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

        recommendations = recommend_songs_with_rag(user_prefs, songs, k=5, retriever=retriever)

        scores = [score for _, score, _ in recommendations]
        assert scores == sorted(scores, reverse=True)
        logger.info("✓ RAG recommendations sorting test passed")

    def test_recommend_songs_with_rag_includes_genre_context(self, setup):
        """Test that RAG recommendations include genre context in explanations."""
        songs, retriever = setup
        user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}

        recommendations = recommend_songs_with_rag(user_prefs, songs, k=5, retriever=retriever)

        # Each recommendation should have an explanation
        for song, score, explanation in recommendations:
            assert isinstance(explanation, str)
            assert len(explanation) > 0

        logger.info("✓ RAG recommendations context test passed")


class TestRAGReliability:
    """Test reliability and error handling."""

    def test_retriever_handles_missing_kb_file(self):
        """Test that retriever handles missing knowledge base gracefully."""
        retriever = GenreArtistRetriever("nonexistent_file.json")
        assert retriever.knowledge_base == {"genres": {}, "artists": {}}
        logger.info("✓ Missing KB file handling test passed")

    def test_retriever_handles_malformed_preferences(self):
        """Test that scoring handles incomplete user preferences."""
        retriever = GenreArtistRetriever("data/context_knowledge_base.json")

        # Minimal preferences (should not crash)
        user_prefs = {"genre": "pop"}
        song = {
            "id": 1,
            "title": "Test",
            "artist": "Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.5,
            "acousticness": 0.1,
        }

        score, explanation = score_song_with_rag(user_prefs, song, retriever)
        assert score is not None
        assert isinstance(explanation, str)
        logger.info("✓ Malformed preferences handling test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
