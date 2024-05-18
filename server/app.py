# from flask import Flask

# app = Flask(__name__)

# @app.route("/members")
# def members():
#     return{"members":["Member1","Memebr2","Member3"]}

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# Load the trained model
model = joblib.load('best_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    df = pd.DataFrame(data)
    
    predictions = model.predict(df)
    
    # Return the predictions as JSON
    return jsonify(predictions.tolist())

if __name__ == '__main__':
    app.run(debug=True)
