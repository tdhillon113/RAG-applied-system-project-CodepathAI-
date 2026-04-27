"""
Streamlit UI for Music Recommender with Genre/Artist Context RAG.

Run with: streamlit run src/app.py
"""

import streamlit as st
import logging
from src.recommender import load_songs, recommend_songs_with_rag
from src.genre_context_rag import GenreArtistRetriever

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="🎵 Music Recommender with RAG",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🎵 Music Recommender with Genre/Artist Context")
st.markdown("*Powered by Retrieval-Augmented Generation (RAG)*")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Settings")

    st.markdown("---")
    st.subheader("Your Music Preferences")

    # Load data
    @st.cache_resource
    def load_data():
        songs = load_songs("data/songs.csv")
        retriever = GenreArtistRetriever("data/context_knowledge_base.json")
        return songs, retriever

    songs, retriever = load_data()

    # Get unique genres and moods from data
    genres = sorted(set(song["genre"] for song in songs))
    moods = sorted(set(song["mood"] for song in songs))

    # User preference inputs
    selected_genre = st.selectbox(
        "Favorite Genre",
        genres,
        help="Pick your favorite music genre"
    )

    selected_mood = st.selectbox(
        "Preferred Mood",
        moods,
        help="How do you want to feel?"
    )

    energy_level = st.slider(
        "Energy Level",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="0 = Chill, 1 = High Energy"
    )

    likes_acoustic = st.checkbox(
        "I like acoustic music",
        value=False,
        help="Prefer acoustic/organic instruments"
    )

    st.markdown("---")

    # Number of recommendations
    num_recommendations = st.slider(
        "Number of Recommendations",
        min_value=1,
        max_value=10,
        value=5
    )

    st.markdown("---")
    st.info(
        "💡 **How RAG Works**: The system retrieves genre relationships "
        "from our knowledge base to make smart cross-genre recommendations. "
        "For example, a pop fan might get indie pop suggestions!"
    )

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Your Preferences")

    # Display user preferences as cards
    pref_col1, pref_col2, pref_col3, pref_col4 = st.columns(4)

    with pref_col1:
        st.metric("Genre", selected_genre.upper())

    with pref_col2:
        st.metric("Mood", selected_mood.upper())

    with pref_col3:
        st.metric("Energy", f"{energy_level:.1f}")

    with pref_col4:
        st.metric("Acoustic", "Yes ✓" if likes_acoustic else "No ✗")

with col2:
    if st.button("🎵 Get Recommendations", use_container_width=True, type="primary"):
        st.session_state.show_recommendations = True

# Show recommendations if button was clicked
if st.session_state.get("show_recommendations", False):
    st.divider()

    # Prepare user preferences
    user_prefs = {
        "genre": selected_genre,
        "mood": selected_mood,
        "energy": energy_level,
        "likes_acoustic": likes_acoustic,
    }

    # Get recommendations with RAG
    with st.spinner("🔍 Finding perfect recommendations with RAG..."):
        recommendations = recommend_songs_with_rag(
            user_prefs, songs, k=num_recommendations, retriever=retriever
        )

    st.subheader(f"🎶 Top {len(recommendations)} Recommendations")

    # Display each recommendation
    for idx, (song, score, explanation) in enumerate(recommendations, 1):
        with st.container(border=True):
            # Header with song title and artist
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {idx}. {song['title']}")
                st.markdown(f"**Artist:** {song['artist']}")

            with col2:
                # Score display
                st.metric("Score", f"{score:.2f}/5.0")

            # Song details in expandable section
            song_col1, song_col2, song_col3, song_col4 = st.columns(4)

            with song_col1:
                st.caption(f"🎸 Genre: {song['genre']}")

            with song_col2:
                st.caption(f"😊 Mood: {song['mood']}")

            with song_col3:
                st.caption(f"⚡ Energy: {song['energy']:.2f}")

            with song_col4:
                st.caption(f"🎼 Tempo: {song['tempo_bpm']:.0f} BPM")

            # Explanation (why this song was recommended)
            st.markdown("**Why this recommendation:**")

            # Highlight RAG enhancements in the explanation
            if "RAG" in explanation or "affinity" in explanation:
                st.success(f"✨ {explanation}")
            else:
                st.info(f"📍 {explanation}")

            # Genre context from knowledge base
            genre_context = retriever.get_genre_context(song["genre"])
            if genre_context:
                with st.expander("📚 Genre Context"):
                    st.markdown(f"**Description:** {genre_context.get('description', 'N/A')}")

                    characteristics = genre_context.get("characteristics", [])
                    if characteristics:
                        chars_str = ", ".join(characteristics)
                        st.markdown(f"**Characteristics:** {chars_str}")

                    related = genre_context.get("related_genres", [])
                    if related:
                        related_str = ", ".join(related)
                        st.markdown(f"**Related Genres:** {related_str}")

                    moods = genre_context.get("typical_moods", [])
                    if moods:
                        moods_str = ", ".join(moods)
                        st.markdown(f"**Typical Moods:** {moods_str}")

            st.divider()

    # Summary statistics
    st.subheader("📈 Recommendation Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        avg_score = sum(score for _, score, _ in recommendations) / len(recommendations)
        st.metric("Average Score", f"{avg_score:.2f}")

    with summary_col2:
        rag_enhanced = sum(1 for _, _, exp in recommendations if "RAG" in exp or "affinity" in exp)
        st.metric("RAG-Enhanced", f"{rag_enhanced}/{len(recommendations)}")

    with summary_col3:
        genres_in_recs = len(set(song["genre"] for song, _, _ in recommendations))
        st.metric("Unique Genres", genres_in_recs)

    # Knowledge base exploration
    with st.expander("🔍 Explore Knowledge Base"):
        st.subheader("Genre Relationships")

        explore_genre = st.selectbox(
            "Select a genre to explore",
            genres,
            key="explore_genre"
        )

        kb_col1, kb_col2 = st.columns(2)

        with kb_col1:
            st.markdown("**Related Genres:**")
            related = retriever.find_related_genres(explore_genre)
            if related:
                for rel_genre in related:
                    st.write(f"• {rel_genre}")
            else:
                st.write("No related genres found")

        with kb_col2:
            st.markdown("**Notable Artists:**")
            artists = retriever.get_related_artists_by_genre(explore_genre)
            if artists:
                for artist in artists:
                    st.write(f"• {artist}")
            else:
                st.write("No artists found")

# Footer
st.divider()
st.markdown("""
---
### About This Project

This music recommender uses **Retrieval-Augmented Generation (RAG)** to enhance recommendations.

**How it works:**
1. You provide your music preferences (genre, mood, energy, acoustic preference)
2. The system retrieves relevant context from a knowledge base about genres and artists
3. It combines traditional scoring with RAG-enhanced synergy bonuses
4. You get recommendations that consider both exact matches AND genre relationships

**RAG Benefits:**
- 🎯 Understands that indie pop is adjacent to pop
- 🎯 Recognizes genre transitions and collaborations
- 🎯 Makes recommendations feel natural, not just algorithmic

**What's Being Retrieved:**
- Genre characteristics and descriptions
- Related genres and common transitions
- Artist influences and collaboration styles
- Typical moods and energy levels per genre

*Built with Python, Streamlit, and RAG principles*
""")
