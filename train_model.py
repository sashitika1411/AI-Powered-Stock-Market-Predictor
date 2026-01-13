import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

# Load data
data = pd.read_csv("data/stock_data.csv")

# Feature (day index) and target (price)
X = data.index.values.reshape(-1, 1)
y = data["Close"].values

# Train model
model = LinearRegression()
model.fit(X, y)

# Create model folder if not exists
os.makedirs("model", exist_ok=True)

# Save trained model
joblib.dump(model, "model/stock_model.pkl")

print("✅ Model trained and saved successfully")
