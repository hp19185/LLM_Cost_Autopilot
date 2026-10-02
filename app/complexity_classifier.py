from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

from app.feature_extractor import extract_features


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "data" / "complexity_dataset.csv"

MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "complexity_classifier.pkl"


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

def load_dataset():

    df = pd.read_csv(DATASET_PATH)

    features = []

    for prompt in df["prompt"]:

        features.append(
            extract_features(prompt)
        )

    X = pd.DataFrame(features)

    y = df["tier"]

    return X, y


# --------------------------------------------------
# Train classifier
# --------------------------------------------------

def train_classifier():

    print("\n----- LOADING DATASET -----")

    X, y = load_dataset()

    print("Total samples:", len(X))
    print("Features:", list(X.columns))

    print("\nClass distribution:")
    print(y.value_counts().sort_index())


    # --------------------------------------------------
    # Train/Test split
    # --------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )


    print("\nTraining samples:", len(X_train))
    print("Testing samples:", len(X_test))


    # --------------------------------------------------
    # Random Forest
    # --------------------------------------------------

    classifier = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=6
    )


    print("\n----- TRAINING CLASSIFIER -----")

    classifier.fit(
        X_train,
        y_train
    )


    # --------------------------------------------------
    # Evaluation
    # --------------------------------------------------

    predictions = classifier.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )


    print("\n----- CLASSIFIER RESULTS -----")

    print(
        f"Accuracy: {accuracy * 100:.2f}%"
    )


    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )


    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )


    # --------------------------------------------------
    # Feature importance
    # --------------------------------------------------

    print("\n----- FEATURE IMPORTANCE -----")

    importance = pd.Series(
        classifier.feature_importances_,
        index=X.columns
    ).sort_values(
        ascending=False
    )


    for feature, value in importance.items():

        print(
            f"{feature}: {value:.4f}"
        )


    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    MODEL_DIR.mkdir(
        exist_ok=True
    )

    joblib.dump(
        classifier,
        MODEL_PATH
    )


    print("\n----- MODEL SAVED -----")

    print(
        f"Model: {MODEL_PATH}"
    )


    return classifier


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    train_classifier()