from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
from flask_sqlalchemy import SQLAlchemy
from preprocessing import preprocessing
from sqlalchemy.sql import text

db = SQLAlchemy()
# create the app
app = Flask(__name__)
# change string to the name of your database; add path if necessary
db_name = 'BD3.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)


# Get the current working directory
cwd = os.getcwd()
model_path = os.path.join(cwd, 'best_model.pkl')
print(model_path)
model = joblib.load(model_path)

@app.route('/')
def testdb():
    try:
        db.session.query(text('1')).from_statement(text('SELECT 1')).all()
        return '<h1>It works.</h1>'
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    df = pd.DataFrame(data, index=[0])
    # Preprocess the DataFrame
    df = preprocessing(df)
    
    # Ensure that the processed DataFrame has all the expected columns
    expected_columns = model.regressor_.named_steps['columntransformer'].get_feature_names_out()
    missing_cols = set(expected_columns) - set(df.columns)
    for col in missing_cols:
        df[col] = 0
    df = df[expected_columns]

    predictions = model.predict(df)
    
    # Return the predictions as JSON
    return jsonify(predictions.tolist())

if __name__ == '__main__':
    app.run(debug=True)
