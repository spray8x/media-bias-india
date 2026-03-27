import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_sentiment(df):
    analyzer = SentimentIntensityAnalyzer()

    def score(row):
        # combine title and description for richer context
        text = row["title"]
        if row["description"] and len(str(row["description"])) > 0:
            text = text + ". " + str(row["description"])
        return analyzer.polarity_scores(text)

    print("Running VADER sentiment analysis...")

    scores = df.apply(score, axis=1)

    df["sentiment_positive"] = scores.apply(lambda x: x["pos"])
    df["sentiment_negative"] = scores.apply(lambda x: x["neg"])
    df["sentiment_neutral"]  = scores.apply(lambda x: x["neu"])
    df["sentiment_compound"] = scores.apply(lambda x: x["compound"])

    # human readable label based on compound score
    def label(compound):
        if compound >= 0.05:
            return "Positive"
        elif compound <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    df["sentiment_label"] = df["sentiment_compound"].apply(label)

    print(f"Done. Sentiment breakdown:")
    print(df["sentiment_label"].value_counts().to_string())
    print(f"\nAverage compound score by lean:")
    print(df.groupby("lean")["sentiment_compound"].mean().round(3).to_string())

    return df


if __name__ == "__main__":
    df = pd.read_csv("data/articles.csv")
    df = analyze_sentiment(df)
    df.to_csv("data/articles.csv", index=False)
    print("\nSaved back to data/articles.csv")
