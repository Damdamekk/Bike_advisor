import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# Wczytanie danych
csv_path = "dane_treningowe.csv"
df = pd.read_csv(csv_path)

# Zakodowanie zmiennych kategorycznych
encoders = {}
for col in df.columns:
    if df[col].dtype == 'object' and col != "rower":
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

# Zakodowanie etykiety (nazwa roweru)
label_encoder = LabelEncoder()
df["rower"] = label_encoder.fit_transform(df["rower"])
encoders["rower"] = label_encoder

# Podział na cechy i etykietę
X = df.drop("rower", axis=1)
y = df["rower"]

# Podział na zbiory treningowy i testowy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Trening modelu
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Ewaluacja
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Zapis modelu i encoderów
with open("model.pkl", "wb") as f:
    pickle.dump((model, encoders), f)

print("Model zapisany do pliku model.pkl")
