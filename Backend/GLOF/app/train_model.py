import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Load synthetic data
df = pd.read_csv('data/synthetic_data.csv')

# Split features and target
X = df.drop(columns=['GLOF_Occurred','Month','Day'])
y = df['GLOF_Occurred']

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost model
model = xgb.XGBClassifier()
model.fit(X_train, y_train)

# Predict and evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")

# Save the model
joblib.dump(model, 'data/glof_prediction_model.pkl')
print("Model saved as data/glof_prediction_model.pkl")
