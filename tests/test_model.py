import joblib
from sklearn.metrics import accuracy_score

def test_model_accuracy():
    model = joblib.load("model/titanic_model.pkl")
    X_test = [[3, 1, 25, 8.5], [1, 0, 40, 100]]
    y_test = [1, 0]
    preds = model.predict(X_test)
    assert accuracy_score(y_test, preds) > 0.7
