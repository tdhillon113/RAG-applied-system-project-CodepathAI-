import csv
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.genre_context_rag import GenreArtistRetriever

logger = logging.getLogger(__name__)

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> Tuple[float, str]:
        score = 0.0
        reasons: List[str] = []

        if song.genre.lower() == user.favorite_genre.lower():
            score += 2.0
            reasons.append("genre match (+2.0)")

        if song.mood.lower() == user.favorite_mood.lower():
            score += 1.0
            reasons.append("mood match (+1.0)")

        energy_gap = abs(user.target_energy - song.energy)
        energy_points = max(0.0, 2.0 * (1.0 - energy_gap))
        score += energy_points
        reasons.append(f"energy closeness (+{energy_points:.2f})")

        if user.likes_acoustic:
            if song.acousticness >= 0.7:
                score += 0.5
                reasons.append("acoustic preference match (+0.5)")
            else:
                reasons.append("acoustic preference not matched (+0.0)")
        else:
            if song.acousticness >= 0.7:
                score -= 0.3
                reasons.append("acoustic song not preferred (-0.3)")

        return score, "; ".join(reasons)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored_songs: List[Tuple[Song, float, str]] = [
            (song, *self._score_song(user, song)) for song in self.songs
        ]
        scored_songs.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _, _ in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, explanation = self._score_song(user, song)
        return explanation


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def load_songs(csv_path: str) -> List[Dict[str, Any]]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs: List[Dict[str, Any]] = []

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            songs.append(
                {
                    "id": _to_int(row.get("id", "0")),
                    "title": row.get("title", ""),
                    "artist": row.get("artist", ""),
                    "genre": row.get("genre", ""),
                    "mood": row.get("mood", ""),
                    "energy": _to_float(row.get("energy", "0.0")),
                    "tempo_bpm": _to_float(row.get("tempo_bpm", "0.0")),
                    "valence": _to_float(row.get("valence", "0.0")),
                    "danceability": _to_float(row.get("danceability", "0.0")),
                    "acousticness": _to_float(row.get("acousticness", "0.0")),
                }
            )
    return songs


def score_song(user_prefs: Dict[str, Any], song: Dict[str, Any]) -> Tuple[float, str]:
    score = 0.0
    reasons: List[str] = []

    if song.get("genre", "").lower() == str(user_prefs.get("genre", "")).lower():
        score += 2.0
        reasons.append("genre match (+2.0)")

    if song.get("mood", "").lower() == str(user_prefs.get("mood", "")).lower():
        score += 1.0
        reasons.append("mood match (+1.0)")

    energy_gap = abs(float(user_prefs.get("energy", 0.5)) - float(song.get("energy", 0.0)))
    energy_points = max(0.0, 2.0 * (1.0 - energy_gap))
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    if user_prefs.get("likes_acoustic", False):
        if float(song.get("acousticness", 0.0)) >= 0.7:
            score += 0.5
            reasons.append("acoustic preference match (+0.5)")
        else:
            reasons.append("acoustic preference not matched (+0.0)")
    else:
        if float(song.get("acousticness", 0.0)) >= 0.7:
            score -= 0.3
            reasons.append("acoustic song not preferred (-0.3)")

    return score, "; ".join(reasons)


def score_song_with_rag(
    user_prefs: Dict[str, Any],
    song: Dict[str, Any],
    retriever: GenreArtistRetriever,
) -> Tuple[float, str]:
    """
    Score a song using both traditional metrics and RAG-enhanced genre/artist context.

    This function augments the baseline score with context retrieved from the genre/artist
    knowledge base, enabling intelligent cross-genre recommendations.

    Args:
        user_prefs: User preferences dictionary with keys: genre, mood, energy, likes_acoustic.
        song: Song dictionary with music attributes.
        retriever: GenreArtistRetriever instance for context lookup.

    Returns:
        Tuple of (score, explanation_text).
    """
    score = 0.0
    reasons: List[str] = []

    user_genre = str(user_prefs.get("genre", ""))
    song_genre = song.get("genre", "")

    # Base genre scoring
    if song_genre.lower() == user_genre.lower():
        score += 2.0
        reasons.append("genre match (+2.0)")
    else:
        # RAG ENHANCEMENT: Check for genre relationships
        synergy_bonus = retriever.get_synergy_bonus(
            user_genre, song_genre, user_prefs.get("favorite_artist")
        )
        if synergy_bonus > 0:
            score += synergy_bonus
            reasons.append(f"genre affinity via RAG (+{synergy_bonus:.2f})")
            logger.debug(
                f"RAG bonus applied for song {song.get('title')}: {synergy_bonus:.2f}"
            )

    # Mood scoring
    if song.get("mood", "").lower() == str(user_prefs.get("mood", "")).lower():
        score += 1.0
        reasons.append("mood match (+1.0)")

    # Energy scoring
    energy_gap = abs(float(user_prefs.get("energy", 0.5)) - float(song.get("energy", 0.0)))
    energy_points = max(0.0, 2.0 * (1.0 - energy_gap))
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    # Acoustic preference
    if user_prefs.get("likes_acoustic", False):
        if float(song.get("acousticness", 0.0)) >= 0.7:
            score += 0.5
            reasons.append("acoustic preference match (+0.5)")
        else:
            reasons.append("acoustic preference not matched (+0.0)")
    else:
        if float(song.get("acousticness", 0.0)) >= 0.7:
            score -= 0.3
            reasons.append("acoustic song not preferred (-0.3)")

    return score, "; ".join(reasons)


def recommend_songs(user_prefs: Dict[str, Any], songs: List[Dict[str, Any]], k: int = 5) -> List[Tuple[Dict[str, Any], float, str]]:
    scored_songs: List[Tuple[Dict[str, Any], float, str]] = []

    for song in songs:
        score, explanation = score_song(user_prefs, song)
        scored_songs.append((song, score, explanation))

    scored_songs.sort(key=lambda item: item[1], reverse=True)
    return scored_songs[:k]


def recommend_songs_with_rag(
    user_prefs: Dict[str, Any],
    songs: List[Dict[str, Any]],
    k: int = 5,
    retriever: Optional[GenreArtistRetriever] = None,
) -> List[Tuple[Dict[str, Any], float, str]]:
    """
    Recommend songs using RAG-enhanced genre and artist context.

    This is the main recommendation function that uses RAG to provide context-aware results.
    It retrieves genre and artist relationships to make smarter cross-genre recommendations.

    Args:
        user_prefs: User preferences dictionary.
        songs: List of song dictionaries to score.
        k: Number of top recommendations to return.
        retriever: GenreArtistRetriever instance. If None, creates a new one.

    Returns:
        List of (song, score, explanation) tuples sorted by score descending.
    """
    if retriever is None:
        retriever = GenreArtistRetriever()
        logger.info("Created new GenreArtistRetriever for recommendation")

    scored_songs: List[Tuple[Dict[str, Any], float, str]] = []

    for song in songs:
        score, explanation = score_song_with_rag(user_prefs, song, retriever)
        scored_songs.append((song, score, explanation))

    scored_songs.sort(key=lambda item: item[1], reverse=True)
    logger.info(f"Recommended {min(len(scored_songs[:k]), k)} songs for user")
    return scored_songs[:k]
