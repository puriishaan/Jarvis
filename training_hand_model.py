import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Folder containing  CSV files
DATA_DIR = "hand_data"

# Load all CSVs
all_data = []
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".csv"):
        filepath = os.path.join(DATA_DIR, filename)
        df = pd.read_csv(filepath, header=None)
        all_data.append(df)

# Combine all gesture data into one DataFrame
data = pd.concat(all_data, ignore_index=True)

# Split features and labels
X = data.iloc[:, :-1].values  # First 63 columns: landmarks
y = data.iloc[:, -1].values   # Last column: label

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred, target_names=le.classes_))

# Save model and label encoder
joblib.dump(clf, "hand_gesture_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("Model and encoder saved.")
