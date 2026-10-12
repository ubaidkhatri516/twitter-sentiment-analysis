# Project Report: Real-Time Sentiment Analysis on Twitter (X) Data

## 1. Introduction

Social media platforms contain large volumes of short text expressing opinions, reactions, and experiences. Sentiment analysis uses Natural Language Processing (NLP) to estimate whether a text expresses positive, neutral, or negative sentiment. This project presents an interactive dashboard for exploring the sentiment of public posts matching a selected keyword or hashtag.

## 2. Problem statement

Manually reviewing a large number of social media posts is time-consuming. A simple analytical system is needed to collect eligible posts, preprocess their text, estimate sentiment, and summarize the results through charts and key performance indicators.

## 3. Objectives

1. Retrieve recent public posts matching a keyword or hashtag using the X API.
2. Clean the text by removing URLs and user mentions and normalizing whitespace.
3. Apply VADER sentiment analysis to calculate compound polarity scores.
4. Categorize posts as positive, neutral, or negative.
5. Build a Streamlit dashboard with interactive visualizations and filters.
6. Export analyzed records for further analysis.

## 4. Tools and technologies

| Tool | Role |
|---|---|
| Python | Application logic |
| X API v2 | Recent public-post retrieval |
| Pandas | Data cleaning and transformation |
| VADER | Lexicon/rule-based sentiment analysis |
| Streamlit | Dashboard interface |
| Plotly | Interactive visualizations |
| Pytest | Unit testing |

## 5. Methodology

### Step 1 — Data collection

In live mode, the application sends a request to the X API v2 recent-search endpoint using a keyword or hashtag query. It requests post text, creation time, language, and public metrics. Access depends on the developer account and current API plan. In demo mode, the application uses an included illustrative dataset so the dashboard can be demonstrated without credentials.

### Step 2 — Data cleaning

The text-cleaning function:
- removes HTTP/HTTPS URLs;
- removes `@username` mentions;
- removes the `#` symbol while preserving the hashtag word;
- normalizes repeated whitespace;
- replaces missing text with an empty string;
- removes duplicate text records.

### Step 3 — Sentiment analysis

VADER produces positive, negative, neutral, and compound scores. The compound score is a normalized summary between -1 and +1. The project applies these thresholds:

| Compound score | Label |
|---|---|
| ≥ 0.05 | Positive |
| > -0.05 and < 0.05 | Neutral |
| ≤ -0.05 | Negative |

### Step 4 — Visualization

The dashboard presents:
- total posts analyzed;
- counts and percentages for each sentiment;
- a sentiment-distribution doughnut chart;
- a sentiment-count bar chart;
- sentiment counts over time;
- a searchable table of analyzed posts;
- a CSV download option.

### Step 5 — Evaluation

A basic evaluation includes checking the cleaning output, testing threshold boundaries, verifying that the sentiment labels are generated, and manually reviewing example predictions. A more formal evaluation would require a human-labelled test set and metrics such as accuracy, precision, recall, and F1-score.

## 6. System architecture

```text
X API / Sample CSV
        |
        v
   Data ingestion
        |
        v
 Text cleaning with Pandas
        |
        v
  VADER compound scoring
        |
        v
 Positive / Neutral / Negative
        |
        v
 Streamlit + Plotly dashboard
        |
        v
   CSV export and insights
```

## 7. Expected output

The application provides an interactive dashboard with summary metrics, sentiment charts, a time trend, and a table of classified posts. In demo mode, the values are based on illustrative sample posts. In live mode, the dashboard reflects the posts returned by the API at the time of refresh.

Do not report demo numbers as actual public opinion or as findings from live X data.

## 8. Limitations

1. VADER may misinterpret sarcasm, irony, and context-dependent language.
2. The default live query is limited to English posts.
3. Recent search and request volume depend on X API access and rate limits.
4. The dashboard refreshes on demand; it is not a continuous firehose or streaming system.
5. Automated sentiment labels are estimates and should not be treated as definitive judgements about a person or organization.
6. A small sample dataset is suitable for demonstration, but not for making population-level claims.

## 9. Future enhancements

- Add multilingual sentiment models.
- Add word clouds and keyword frequency analysis.
- Store periodic snapshots to compare sentiment over time.
- Add human-labelled evaluation data and performance metrics.
- Add a scheduled refresh mechanism within API terms and resource limits.
- Add deployment through Streamlit Community Cloud.

## 10. Conclusion

This project demonstrates an end-to-end data analytics workflow: data acquisition, text preprocessing, sentiment scoring, visualization, and export. It combines practical Python skills with NLP and dashboard development. The result is a useful prototype for exploring public social media sentiment while making the limitations of automated classification clear.

## 11. References

1. X Developer Platform, Recent Search Quickstart: https://github.com/xdevplatform/docs/blob/main/x-api/posts/search/quickstart/recent-search.mdx
2. X Developer Platform, Search Posts: https://github.com/xdevplatform/docs/blob/main/x-api/posts/search/introduction.mdx
3. Streamlit Documentation: https://docs.streamlit.io/get-started/installation
4. VADER Sentiment Analysis: https://github.com/cjhutto/vaderSentiment
