import pandas as pd


def analyze_scores(scores):
    df = pd.DataFrame({"Score": scores})

    result = {
        "count": len(df),
        "average": df["Score"].mean(),
        "highest": df["Score"].max(),
        "lowest": df["Score"].min()
    }

    return result