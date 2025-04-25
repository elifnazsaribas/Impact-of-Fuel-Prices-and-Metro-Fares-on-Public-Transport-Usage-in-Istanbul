import pandas as pd


df = pd.read_csv("Istanbulkart_fare.csv", sep=';', decimal=',')

df = df.drop(columns=["Number"]).iloc[:-1]

df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
df["Year"] = df["Date"].dt.year

avg_per_year = df.groupby("Year").mean(numeric_only=True)

all_years = pd.Series(range(df["Year"].min(), df["Year"].max() + 1))
filled_avg = avg_per_year.reindex(all_years, method="ffill")

filled_avg = filled_avg.round(2)
filled_avg.index.name = "Year"
filled_avg = filled_avg.reset_index()

filled_avg.to_csv("Istanbulkart_Fare_Avg.csv", index=False)
