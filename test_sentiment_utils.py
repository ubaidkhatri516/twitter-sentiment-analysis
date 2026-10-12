import pandas as pd
import pytest

from sentiment_utils import analyze_dataframe, classify_compound, clean_text


def test_clean_text_removes_url_and_mention():
    cleaned = clean_text("Great work @someone! https://example.com #Python")
    assert "@someone" not in cleaned
    assert "https://" not in cleaned
    assert "Python" in cleaned


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.05, "Positive"),
        (0.7, "Positive"),
        (0.049, "Neutral"),
        (0.0, "Neutral"),
        (-0.049, "Neutral"),
        (-0.05, "Negative"),
        (-0.8, "Negative"),
    ],
)
def test_classify_compound_thresholds(score, expected):
    assert classify_compound(score) == expected


def test_analyze_dataframe_adds_sentiment_columns():
    source = pd.DataFrame(
        {
            "id": ["1", "2", "3"],
            "text": [
                "I absolutely love this, it's wonderful!",
                "The item arrived today.",
                "This is terrible and disappointing.",
            ],
        }
    )
    result = analyze_dataframe(source)
    assert {"clean_text", "compound", "sentiment"}.issubset(result.columns)
    assert len(result) == 3
    assert set(result["sentiment"]).issubset({"Positive", "Neutral", "Negative"})


def test_analyze_dataframe_deduplicates_text():
    source = pd.DataFrame({"text": ["Nice product", "Nice product"]})
    result = analyze_dataframe(source)
    assert len(result) == 1
