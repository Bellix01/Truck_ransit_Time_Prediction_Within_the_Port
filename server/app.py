from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
from preprocessing import preprocessing
import pyodbc
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# initialize the connection with database
def connection():
    server = 'DESKTOP-9HOJAES'  
    database = 'BD' 
    user = 'sa'
    password = '@sql2001@' #Your login password
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+user+';PWD='+ password
    conn = pyodbc.connect(cstr)
    return conn

# Load the saved model
cwd = os.getcwd()
model_path = os.path.join(cwd, 'best_model.pkl')
print(model_path)
model = joblib.load(model_path)

# Connection with SQL Server database
@app.route("/")
def main():
    customers = []
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("""
                SELECT TOP 100
                    AMP_ID,
                    TYPE_UNITE,
                    SS_TYPE_UNITE,
                    VIDE_PLEIN,
                    NATURE_MARCHANDISE,
                    TERMINAL,
                    POIDS,
                    COULOIR,
                    DATE_ZRE
                FROM dbo.truck_info
                ORDER BY DATE_ZRE DESC
            """)
        for row in cursor.fetchall():
              customers.append({
                    "AMP_ID": row[0],
                    "TYPE_UNITE": row[1],
                    "SS_TYPE_UNITE": row[2],
                    "VIDE_PLEIN": row[3],
                    "NATURE_MARCHANDISE": row[4],
                    "TERMINAL": row[5],
                    "POIDS": row[6],
                    "COULOIR": row[7],
                    "DATE_ZRE": row[8]
                })
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return json.dumps(customers, indent=4)

# get informationform database for the specific AMP ID
@app.route('/get_truck_info', methods=['POST'])
def get_truck_info():
    data = request.json
    amp_id = data.get('AMP_ID')
    print(amp_id)
    if not amp_id:
        return jsonify({"error": "AMP_ID is required"}), 400
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("""
                SELECT
                    TYPE_UNITE,
                    SS_TYPE_UNITE,
                    VIDE_PLEIN,
                    NATURE_MARCHANDISE,
                    TERMINAL,
                    POIDS,
                    COULOIR,
                    DATE_ZRE
                FROM dbo.truck_info
                WHERE AMP_ID =?
         """, (amp_id,))
        truck_row = cursor.fetchone()
        conn.close()

        if truck_row:
            truck_info = {
                "TYPE_UNITE": truck_row[0],
                "SS_TYPE_UNITE": truck_row[1],
                "VIDE_PLEIN": truck_row[2],
                "NATURE_MARCHANDISE": truck_row[3],
                "TERMINAL": truck_row[4],
                "POIDS": truck_row[5],
                "COULOIR": truck_row[6],
                "DATE_ZRE": truck_row[7]
            }
            return jsonify(truck_info)
        else:
            return jsonify({"error": "No data found for the given AMP_ID"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Precidtion API
@app.route('/get_prediction', methods=['POST'])
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
