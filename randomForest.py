
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
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

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Train RandomForest model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
predictions = model.predict(X_test)
print("Mean Squared Error:", mean_squared_error(y_test, predictions))
print("R² Score:", r2_score(y_test, predictions))

# Feature importances
importances = model.feature_importances_
print("\nFeature Importances:")
for feature, importance in zip(features.columns, importances):
    print(f"{feature}: {importance:.4f}")

# Plot actual vs predicted
plt.figure(figsize=(8, 6))
plt.scatter(y_test, predictions)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.xlabel("Actual Passenger Count")
plt.ylabel("Predicted Passenger Count")
plt.title("Random Forest: Actual vs Predicted Passenger Count")
plt.grid(True)
plt.tight_layout()
plt.show()

# Future Prediction Example 
future_data = pd.DataFrame({
    'AvgFare': [5.25],
    'KURŞUNSUZ BENZİN (TL/LT)': [42.5],
    'MOTORİN (TL/LT)': [41.0],
    'Istanbul_Population': [16700000]
})
future_prediction = model.predict(future_data)
print(f"\n Forecast: Estimated Passenger Count for 2025: {int(future_prediction[0])}")
