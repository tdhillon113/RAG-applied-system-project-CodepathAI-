"""
Retrieval-Augmented Generation (RAG) module for artist and genre context.

This module retrieves context from a knowledge base about genres and artists
to enhance music recommendations with semantic understanding.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class GenreArtistRetriever:
    """
    Retrieves genre and artist context from a knowledge base.

    This retriever looks up information about genres, artists, and their relationships
    to provide enriched context for music recommendations.
    """

    def __init__(self, kb_path: str = "data/context_knowledge_base.json"):
        """
        Initialize the retriever with a knowledge base.

        Args:
            kb_path: Path to the JSON knowledge base file.
        """
        self.kb_path = kb_path
        self.knowledge_base: Dict[str, Any] = {}
        self._load_knowledge_base()
        logger.info(f"GenreArtistRetriever initialized with KB from {kb_path}")

    def _load_knowledge_base(self) -> None:
        """Load the knowledge base from JSON file."""
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
            logger.debug(
                f"Knowledge base loaded: {len(self.knowledge_base.get('genres', {}))} genres, "
                f"{len(self.knowledge_base.get('artists', {}))} artists"
            )
        except FileNotFoundError:
            logger.error(f"Knowledge base file not found at {self.kb_path}")
            self.knowledge_base = {"genres": {}, "artists": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse knowledge base JSON: {e}")
            self.knowledge_base = {"genres": {}, "artists": {}}

    def get_genre_context(self, genre: str) -> Dict[str, Any]:
        """
        Retrieve context for a specific genre.

        Args:
            genre: The genre name to look up.

        Returns:
            Dictionary containing genre context, or empty dict if not found.
        """
        genres = self.knowledge_base.get("genres", {})
        context = genres.get(genre.lower(), {})
        if context:
            logger.debug(f"Retrieved context for genre: {genre}")
        else:
            logger.debug(f"No context found for genre: {genre}")
        return context

    def get_artist_context(self, artist: str) -> Dict[str, Any]:
        """
        Retrieve context for a specific artist.

        Args:
            artist: The artist name to look up.

        Returns:
            Dictionary containing artist context, or empty dict if not found.
        """
        artists = self.knowledge_base.get("artists", {})
        context = artists.get(artist, {})
        if context:
            logger.debug(f"Retrieved context for artist: {artist}")
        else:
            logger.debug(f"No context found for artist: {artist}")
        return context

    def find_related_genres(self, current_genre: str) -> List[str]:
        """
        Find genres related to the current genre.

        Args:
            current_genre: The genre to find relations for.

        Returns:
            List of related genres, or empty list if not found.
        """
        context = self.get_genre_context(current_genre)
        related = context.get("related_genres", [])
        logger.debug(f"Found {len(related)} related genres for {current_genre}: {related}")
        return related

    def get_related_artists_by_genre(self, genre: str) -> List[str]:
        """
        Get notable artists for a given genre.

        Args:
            genre: The genre to get artists for.

        Returns:
            List of notable artist names.
        """
        context = self.get_genre_context(genre)
        artists = context.get("notable_artists", [])
        logger.debug(f"Found {len(artists)} notable artists for genre {genre}")
        return artists

    def get_genre_transition_score(self, from_genre: str, to_genre: str) -> float:
        """
        Get a score representing how smoothly one can transition from one genre to another.

        This is useful for building coherent playlists or understanding genre affinity.

        Args:
            from_genre: Starting genre.
            to_genre: Target genre.

        Returns:
            Score between 0 and 1, or 0.5 (default neutral) if not explicitly defined.
        """
        transitions = self.knowledge_base.get("genre_transitions", {})
        key = f"{from_genre.lower()}_to_{to_genre.lower()}"
        score = transitions.get(key, 0.5)  # Default to neutral
        logger.debug(
            f"Genre transition score from {from_genre} to {to_genre}: {score}"
        )
        return score

    def get_characteristics(self, genre: str) -> List[str]:
        """
        Get the key characteristics of a genre.

        Args:
            genre: The genre name.

        Returns:
            List of characteristic descriptions.
        """
        context = self.get_genre_context(genre)
        characteristics = context.get("characteristics", [])
        return characteristics

    def search_by_mood(self, target_mood: str) -> List[Tuple[str, List[str]]]:
        """
        Find genres that typically match a given mood.

        Args:
            target_mood: The target mood (e.g., 'happy', 'chill').

        Returns:
            List of (genre, moods) tuples that match the target mood.
        """
        matching_genres: List[Tuple[str, List[str]]] = []
        genres = self.knowledge_base.get("genres", {})

        for genre, context in genres.items():
            typical_moods = context.get("typical_moods", [])
            if target_mood.lower() in [m.lower() for m in typical_moods]:
                matching_genres.append((genre, typical_moods))

        logger.debug(f"Found {len(matching_genres)} genres matching mood '{target_mood}'")
        return matching_genres

    def get_synergy_bonus(
        self, user_genre: str, song_genre: str, user_artist: Optional[str] = None
    ) -> float:
        """
        Calculate a synergy bonus between user preference and song based on genre/artist affinity.

        This is the core RAG enhancement: it uses retrieval to boost scoring.

        Args:
            user_genre: User's preferred genre.
            song_genre: The song's genre.
            user_artist: (Optional) User's favorite artist.

        Returns:
            Bonus score (0.0 to 1.0) based on context retrieval.
        """
        bonus = 0.0

        # Exact match
        if user_genre.lower() == song_genre.lower():
            return 0.0  # Already scored in main recommender

        # Check if song_genre is related to user's preferred genre
        related = self.find_related_genres(user_genre)
        if song_genre.lower() in [r.lower() for r in related]:
            bonus += 0.5
            logger.debug(
                f"Synergy bonus: {song_genre} is related to user's {user_genre} (+0.5)"
            )

        # Check for artist affinity (if user has favorite artist)
        if user_artist:
            user_artist_context = self.get_artist_context(user_artist)
            user_genres = user_artist_context.get("genres", [])

            if song_genre.lower() in [g.lower() for g in user_genres]:
                bonus += 0.3
                logger.debug(
                    f"Artist affinity bonus: {song_genre} matches user's artist {user_artist} (+0.3)"
                )

        # Check genre transition smoothness
        transition_score = self.get_genre_transition_score(user_genre, song_genre)
        if transition_score > 0.7:
            bonus += 0.2
            logger.debug(
                f"Smooth transition bonus: {user_genre} → {song_genre} is smooth (+0.2)"
            )

        logger.debug(f"Total synergy bonus for {song_genre} vs {user_genre}: {bonus}")
        return min(bonus, 1.0)  # Cap at 1.0
