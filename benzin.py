import pandas as pd

df = pd.read_csv("Benzin.csv", sep=";")

# this is for to make date turn to a real date format so that I can have better data learned from the internet
df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True, errors='coerce')
df = df.drop(columns=["TP MOTORİN (TL/LT)", "FUEL OIL (TL/KG)"])

df_filtered = df[(df['DATE'].dt.year >= 2013) & (df['DATE'].dt.year < 2025)]

df_filtered.to_csv("Benzin_2013_sonrasi.csv", index=False)
df = pd.read_csv("Benzin_2013_sonrasi.csv")

df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True, errors='coerce')


df['YIL'] = df['DATE'].dt.year
for col in df.columns:
    if col not in ['DATE', 'YIL']:
        df[col] = df[col].astype(str).str.replace(",", ".").astype(float)


df_yearly_avg = df.groupby("YIL").mean(numeric_only=True).round(2).reset_index()


df_yearly_avg.to_csv("fuel_price_data.csv", index=False)






