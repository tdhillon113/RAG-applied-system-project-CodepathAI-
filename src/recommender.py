import csv
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

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


def recommend_songs(user_prefs: Dict[str, Any], songs: List[Dict[str, Any]], k: int = 5) -> List[Tuple[Dict[str, Any], float, str]]:
    scored_songs: List[Tuple[Dict[str, Any], float, str]] = []

    for song in songs:
        score, explanation = score_song(user_prefs, song)
        scored_songs.append((song, score, explanation))

    scored_songs.sort(key=lambda item: item[1], reverse=True)
    return scored_songs[:k]
