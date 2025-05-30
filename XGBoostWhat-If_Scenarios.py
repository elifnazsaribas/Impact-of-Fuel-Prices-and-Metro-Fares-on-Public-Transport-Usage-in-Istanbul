
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
import matplotlib.pyplot as plt

# File paths
fare_path = "csv/Istanbulkart_fare.csv"
fuel_path = "csv/fuel_price_data.csv"
passenger_path = "csv/passenger_data.csv"
car_sales_path = "csv/car_sales_data.csv"
population_path = "csv/Cleaned_Istanbul_Population_Data.csv"

# Read data
df_fare = pd.read_csv(fare_path, delimiter=';', encoding='utf-8')
df_fuel = pd.read_csv(fuel_path)
df_passenger = pd.read_csv(passenger_path, sep=';')
df_car_sales = pd.read_csv(car_sales_path)
df_population = pd.read_csv(population_path)

# Clean fare data
df_fare['Date'] = pd.to_datetime(df_fare['Date'], dayfirst=True, errors='coerce')
df_fare['Year'] = df_fare['Date'].dt.year
fare_columns = ['Full Istanbulkart', 'Student Istanbulkart', 'Discounted Istanbulkart']
for col in fare_columns:
    df_fare[col] = df_fare[col].astype(str).str.replace(',', '.')
    df_fare[col] = pd.to_numeric(df_fare[col], errors='coerce')
df_fare['AvgFare'] = df_fare[fare_columns].mean(axis=1)
df_fare_avg = df_fare.groupby('Year')['AvgFare'].mean().reset_index()

# Clean and align other datasets
df_passenger['passenger'] = df_passenger['passenger'].str.replace('.', '', regex=False).astype(int)
df_fuel['Year'] = df_fuel['YIL'].astype(int)
df_fuel = df_fuel.drop(columns=['YIL'])
df_car_sales['Year'] = df_car_sales['Year'].astype(int)
df_passenger['Year'] = df_passenger['Year'].astype(int)
df_population.columns = ['Year', 'Istanbul_Population']
df_population['Year'] = df_population['Year'].astype(int)

# Merge all datasets
df_merged = df_fare_avg.merge(df_fuel, on="Year") \
                       .merge(df_passenger, on="Year") \
                       .merge(df_car_sales, on="Year") \
                       .merge(df_population, on="Year")

# Features and target
features = df_merged[['AvgFare', 'KURŞUNSUZ BENZİN (TL/LT)', 'MOTORİN (TL/LT)', 'Istanbul_Population']]
target = df_merged['passenger']

# Train full model on all data
model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
model.fit(features, target)

# Predict full series for plotting
df_merged['PredictedPassenger'] = model.predict(features)

# Plot actual vs predicted (over years)
plt.figure(figsize=(10, 6))
plt.plot(df_merged['Year'], df_merged['passenger'], label="Actual", marker='o')
plt.plot(df_merged['Year'], df_merged['PredictedPassenger'], label="Predicted", marker='x')
plt.xlabel("Year")
plt.ylabel("Passenger Count")
plt.title("Actual vs Predicted Passenger Count (XGBoost)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# What-if Scenarios
print("\n WHAT-IF SCENARIOS:")

scenarios = [
    {"name": "High Fare (6.0)", "AvgFare": 6.0, "Benzin": 42.5, "Motorin": 41.0, "Population": 16700000},
    {"name": "Low Fuel Prices", "AvgFare": 5.25, "Benzin": 30.0, "Motorin": 29.0, "Population": 16700000},
    {"name": "High Population (17M)", "AvgFare": 5.25, "Benzin": 42.5, "Motorin": 41.0, "Population": 17000000},
]

for s in scenarios:
    input_data = pd.DataFrame({
        'AvgFare': [s["AvgFare"]],
        'KURŞUNSUZ BENZİN (TL/LT)': [s["Benzin"]],
        'MOTORİN (TL/LT)': [s["Motorin"]],
        'Istanbul_Population': [s["Population"]]
    })
    prediction = model.predict(input_data)[0]
    print(f"{s['name']}: Estimated Passenger Count = {int(prediction)}")
