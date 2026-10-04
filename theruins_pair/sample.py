import pandas as pd

data = {
    "Name": ["Best", "Beam", "Poom"],
    "Score": [80, 70, 90]
}

df = pd.DataFrame(data)

print(df)

average_score = df["Score"].mean()
highest_score = df["Score"].max()

print("Average score:", average_score)
print("Highest score:", highest_score)