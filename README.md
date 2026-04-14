# 🎵 Music Recommender Simulation

## Project Summary

This project builds a small music recommendation simulator that compares songs from a CSV catalog against a user's taste profile. The system uses genre, mood, energy, and acoustic character to score each song and then ranks the best matches.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

---

## How The System Works

This recommender reads song data from `data/songs.csv` and compares each song to a user's preferences.

- Song features used by the system:
  - `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`
- User profile data:
  - preferred `genre`, preferred `mood`, target `energy`, and whether the user likes acoustic songs
- Scoring rule:
  - +2.0 points if the song genre matches the user's favorite genre
  - +1.0 point if the song mood matches the user's favorite mood
  - Up to +2.0 points for how close the song's energy is to the user's target energy
  - +0.5 points for acoustic songs if the user prefers acoustic tracks, or -0.3 if the user does not prefer acoustic songs
- Ranking rule:
  - Every song is scored, then the top songs are sorted by score from highest to lowest

This means the system first judges each song individually, then creates a ranked output list of the best recommendations.

Algorithm Recipe:

- Score genre matches more heavily than mood matches.
- Use a distance-based energy score so songs closer to the target energy earn more points.
- Keep acoustic preference as a tiebreaker, not a dominant factor.

Potential bias:

- The system may still favor songs that match the dominant genre in the catalog.
- Songs with a strong energy fit can climb the ranking even if their mood is less ideal.

---

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate       # Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

When I changed the genre weight from 2.0 to 0.5, the recommendations shifted to prioritize mood matches over genre. For a user preferring pop and happy mood, "Rooftop Lights" (indie pop, happy) scored higher than "Gym Hero" (pop, intense), showing that mood became more influential.

When I added a valence bonus (+0.5) for songs with high valence (>0.7) when the user prefers happy mood, songs like "Sunrise City" and "Rooftop Lights" gained extra points, reinforcing happy recommendations.

For users who like acoustic music, the system gives a small bonus to highly acoustic songs, but since the catalog has few pop/acoustic combinations, the top recommendations remained similar unless acoustic preference was the only matching factor.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

- The system is limited to a small dataset of 15 songs, which may not represent diverse musical tastes.
- It ignores lyrics, language, artist popularity, and cultural context, focusing only on numerical features.
- The scoring heavily favors genre matches, potentially biasing towards popular genres in the catalog like pop and lofi.
- Acoustic preference is a minor factor, which might not adequately capture user preferences for instrumental vs. produced music.
- The energy scoring uses a simple distance metric, which may not account for user tolerance to energy variations.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

This project demonstrated how recommendation systems transform user preferences and item features into numerical scores to rank options. By assigning weights to different attributes like genre, mood, and energy, the system creates a simple prediction model that prioritizes matches based on predefined rules. I learned that even basic scoring functions can produce reasonable results, but they require careful tuning to balance different factors and avoid overemphasizing certain features.

Bias and unfairness can emerge from the data itself or the scoring logic. For instance, if the song catalog predominantly features certain genres or artists, the system will inherently favor those, potentially excluding underrepresented music styles. Additionally, the binary matching for genre and mood assumes users have strict preferences, which may not reflect real-world flexibility, leading to unfair exclusion of borderline matches. In a real product, this could perpetuate cultural biases if the training data lacks diversity.


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

This system recommends songs by scoring them based on user preferences for genre, mood, energy, and acoustic style. It is designed for educational purposes to demonstrate basic recommendation algorithms, not for commercial use.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

The system looks at each song's genre, mood, energy level, and how acoustic it is. It compares these to what the user likes: their favorite genre, preferred mood, target energy, and whether they enjoy acoustic music. For each song, it adds points for matches—2 points for genre, 1 for mood, up to 2 for energy closeness, and a small bonus or penalty for acoustic preference. The songs are then ranked by total score.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

The dataset contains 15 songs in CSV format. No songs were added or removed from the original file. Genres include pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, electronic, soul, metal, and acoustic. Moods range from happy and chill to intense and romantic. The data appears to reflect a mix of modern electronic and chill music tastes, with a bias towards instrumental and low-energy tracks.

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

The system works well for users with clear preferences, such as those who like high-energy pop music, where it accurately ranks matching songs at the top. Its simplicity makes the scoring transparent and easy to understand, allowing users to see why certain songs were recommended. It performs reliably for straightforward profiles without conflicting preferences.

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

The system struggles with nuanced preferences, ignoring features like tempo, danceability, or lyrics that might matter to some users. It assumes all users prioritize genre equally, which may not hold for those who care more about mood. The catalog's overrepresentation of pop and lofi genres creates bias, favoring those over less common ones like metal or country. In a real product, this could unfairly exclude users with minority tastes or perpetuate algorithmic bias by amplifying popular but not necessarily diverse content.

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations

I evaluated the system by running it with different user profiles, such as pop/happy/high-energy users and those preferring acoustic music. I compared the top recommendations to my expectations based on the scoring rules and noted how changes to weights affected rankings. The unit tests ensured the core logic worked correctly, and manual inspection of scores confirmed the algorithm's behavior.
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

If I had more time, I would add support for more features like tempo ranges, danceability, and valence in scoring. I could also implement user feedback loops to adjust weights dynamically and balance diversity by avoiding over-recommending similar songs.

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

Building this system surprised me with how small changes in weights could drastically shift recommendations, highlighting the importance of tuning in real systems. It made me appreciate the complexity of real recommenders like Spotify, which use vast data and machine learning. Human judgment still matters in interpreting cultural context and subjective appeal that algorithms can't capture.

