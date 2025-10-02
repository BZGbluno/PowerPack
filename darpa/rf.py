from datasets import load_dataset
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_squared_error
import numpy as np

dataset = load_dataset("adult-census")  # HF version of UCI Adult
df = dataset["train"].to_pandas()


df['income'] = df['income'].apply(lambda x: 1 if x == '>50K' else 0)

X = df.drop(columns=['income'])
y = df['income']

categorical_cols = X.select_dtypes(include=['string']).columns
numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns

encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
X_encoded = encoder.fit_transform(X[categorical_cols])

X_processed = np.hstack([X[numeric_cols].values, X_encoded])

X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y.values, test_size=0.2, random_state=42
)

rf = RandomForestRegressor(
    n_estimators=100,    # number of trees
    max_depth=None,      # max depth of trees
    n_jobs=-1,           # use all cores
    random_state=42
)

rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse:.4f}")

# tweak RF hyperparameters for power experiments
# n_estimators (number of trees), max_depth (tree depth), min_samples_split, max_features
