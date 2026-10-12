# Social Pulse — Real-Time Sentiment Analysis on X (Twitter)

A beginner-friendly Data Analytics project that collects public posts from X (formerly Twitter), cleans the text, classifies sentiment with VADER NLP, and visualizes results in an interactive Streamlit dashboard.

## Features

- **Demo mode:** runs without API credentials using the included sample dataset.
- **Live X API mode:** searches recent public posts using a keyword or hashtag.
- **NLP preprocessing:** removes URLs and user mentions, normalizes whitespace, and preserves readable text.
- **VADER sentiment scoring:** compound scores from -1 to +1, classified as Positive, Neutral, or Negative.
- **Interactive dashboard:** KPI metrics, sentiment pie/bar charts, time trend, text filters, and downloadable CSV.
- **CSV export:** download the filtered, analyzed posts.
- **API key safety:** token is read from Streamlit secrets or the `X_BEARER_TOKEN` environment variable.

> **Important:** Demo data is synthetic/illustrative. It must not be described as live public opinion. Live mode requires an X developer app, a valid Bearer Token, and endpoint access. X API plans, rate limits, and terms can change. The recent-search endpoint generally covers the previous seven days; this dashboard fetches data when you click refresh, rather than maintaining a continuous streaming connection.

## Project structure

```text
twitter_sentiment_analysis_project/
├── app.py
├── sentiment_utils.py
├── requirements.txt
├── README.md
├── PROJECT_REPORT.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
├── data/
│   └── sample_posts.csv
└── tests/
    └── test_sentiment_utils.py
```

## 1. Requirements

- Python 3.10–3.14
- Internet connection for package installation and live X API requests
- Optional: X Developer Portal account and API Bearer Token for live mode

## 2. Install and run on Windows

Open Command Prompt or PowerShell in this project folder:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

If the `streamlit` command is not recognized, use:

```bash
python -m streamlit run app.py
```

The dashboard should open in your browser. Choose **Demo dataset** to explore immediately.

## 3. Enable live X API search

1. Create or open an app in the [X Developer Portal](https://developer.x.com/en/portal/dashboard).
2. Find the app's Bearer Token under keys and tokens.
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
4. Replace the placeholder with your token:

```toml
X_BEARER_TOKEN = "your_real_bearer_token"
```

5. Ensure `.streamlit/secrets.toml` remains untracked by Git. The `.gitignore` in this project excludes it.
6. Restart Streamlit, choose **Live X API**, enter a keyword or hashtag, and click **Load / refresh data**.

Alternatively, set an environment variable named `X_BEARER_TOKEN` before launching the app. Never commit your real token to GitHub. If a token is accidentally exposed, revoke or rotate it immediately.

## 4. Analyze your own CSV

The included dashboard uses the sample dataset in demo mode. To analyze your own CSV, make sure it contains a column named `text`. You can also call `analyze_uploaded_csv()` from `sentiment_utils.py` in your own workflow. For example:

```python
import pandas as pd
from sentiment_utils import analyze_dataframe

posts = pd.read_csv("my_posts.csv")  # must include a 'text' column
results = analyze_dataframe(posts)
results.to_csv("analyzed_posts.csv", index=False)
```

## 5. Run tests

```bash
pytest -q
```

## 6. Push to GitHub

1. Extract the ZIP.
2. Create a new empty repository on GitHub.
3. Open a terminal in the extracted project folder.
4. Run:

```bash
git init
git add .
git commit -m "Add social media sentiment analysis dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own repository URL. Do not upload `.venv`, `.env`, or `.streamlit/secrets.toml`.

## 7. Deploy the dashboard

For Streamlit Community Cloud, push the project to GitHub, create a new app, select `app.py`, and add `X_BEARER_TOKEN` in the deployment's Secrets settings if you want live mode. Demo mode works without a token.

## Sentiment interpretation

The VADER compound score is interpreted using common thresholds:

- **Positive:** compound score ≥ 0.05
- **Neutral:** compound score > -0.05 and < 0.05
- **Negative:** compound score ≤ -0.05

These are heuristic labels, not ground truth. Sarcasm, irony, context, slang, and languages other than English can reduce accuracy.

## Data and privacy notes

- Only retrieve data permitted by your X API access and the applicable platform terms.
- Avoid collecting or publishing unnecessary personal data.
- This project stores no API token in the source files.
- Sample posts are provided for demonstration and do not represent real users or current public sentiment.

## References

- [X API recent search quickstart](https://github.com/xdevplatform/docs/blob/main/x-api/posts/search/quickstart/recent-search.mdx)
- [X API search posts overview](https://github.com/xdevplatform/docs/blob/main/x-api/posts/search/introduction.mdx)
- [Streamlit installation guide](https://docs.streamlit.io/get-started/installation)
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)
