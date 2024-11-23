from sklearn.linear_model import LinearRegression
import numpy as np

def predict_trend(data):
    df = pd.DataFrame(data)
    X = df['Year'].values.reshape(-1, 1)
    y = df['Reserve Size'].values
    model = LinearRegression()
    model.fit(X, y)
    future_years = np.array([[2025], [2030], [2035]])
    predictions = model.predict(future_years)
    return predictions
