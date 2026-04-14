# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

> VibeFinder 1.0

---

## 2. Intended Use

This system suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, energy level, and acoustic preference. It is designed for classroom exploration and prototype experimentation, not for production use.

---

## 3. How It Works (Short Explanation)

Each song in the catalog is compared to a user's taste profile. The recommender awards points for genre and mood matches, then adds a closeness score for energy. Acoustic songs get a small extra boost if the user likes them, or a small penalty if the user prefers non-acoustic tracks. The songs are then ranked by total score and the highest-scoring tracks are returned.

---

## 4. Data

The dataset contains 15 songs in `data/songs.csv`.
It includes genres like pop, lofi, rock, ambient, jazz, synthwave, country, electronic, soul, metal, and acoustic.
The moods include happy, chill, intense, moody, relaxed, focused, romantic, energetic, and mellow.
The catalog mostly reflects a variety of streaming-friendly styles, but it remains small and biased toward familiar mood labels.

---

## 5. Strengths

This recommender works well when the user has a clear preferred genre and mood. The ranking is transparent because each song score is built from simple, easy-to-read rules. It also uses energy as a continuous feature instead of only matching discrete labels.

---

## 6. Limitations and Bias

The system can over-prioritize genre because genre matches are weighted more heavily than mood or acoustic preference. It also treats all users as having the same kind of taste profile, so it cannot represent a listener who likes several different styles equally. Because the catalog is small, some genres are underrepresented and the results may feel repetitive.

---

## 7. Evaluation

I tested the system with multiple user profiles, including a happy pop listener, a chill lofi listener, and an intense rock listener. I verified that the top songs changed according to the preferred energy level and mood. I also reviewed the recommendation explanation text to see why each song was chosen.

---

## 8. Future Work

- Add a second phase that penalizes repeated genre choices to increase diversity.
- Support more user profile dimensions, such as tempo preference or valence.
- Add collaborative filtering signals from other listeners instead of only using content features.

---

## 9. Personal Reflection

Building this recommender showed me how simple math can still produce reasonable music suggestions when the inputs are structured well. I learned that carefully choosing weights is important: too much weight on one feature can make recommendations feel one-dimensional. Using AI tools and code templates helped me move faster, but I still needed to verify the scoring logic and make sure the output matched my intuition.
