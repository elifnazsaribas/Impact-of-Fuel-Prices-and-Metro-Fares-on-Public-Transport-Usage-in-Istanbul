import pandas as pd

df = pd.read_csv("Otomobil_Sales.csv", sep=";")

df = df.drop(columns=[
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

df.to_csv("car_sales_data.csv", index=False)
