from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
from preprocessing import preprocessing
import pyodbc
import json
from flask_cors import CORS
import logging
logging.basicConfig(level=logging.DEBUG)
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
    trucks = []
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
              trucks.append({
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
    return json.dumps(trucks, indent=4)

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


@app.route('/get_prediction', methods=['POST'])
def get_prediction():
    data = request.get_json()
    df = pd.DataFrame(data, index=[0])
    df.columns = df.columns.str.lower()

    # Convert DATE_ZRE to datetime
    df['date_zre'] = pd.to_datetime(df['date_zre'], format='%d/%m/%y %H:%M:%S,%f')

    start_date = (df['date_zre'] - pd.Timedelta(minutes=30)).min().strftime('%Y-%m-%d %H:%M:%S.%f')
    end_date = (df['date_zre'] + pd.Timedelta(minutes=30)).max().strftime('%Y-%m-%d %H:%M:%S.%f')
    # Fetch weather data from the database
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT *
    FROM dbo.historic_weather_data
    WHERE datetime >= ? AND datetime <= ?
""", (start_date, end_date,))
    weather_rows = cursor.fetchone()
    weather_data = {
                "datetime": weather_rows[0],
                "temp": weather_rows[1],
                "precip": weather_rows[2],
                "windspeed": weather_rows[3],
                "winddir": weather_rows[4],
                "windgust": weather_rows[5],
                "dew": weather_rows[6],
                "visibility": weather_rows[7]
            }
    conn.close()

    weather_data = pd.DataFrame(weather_data, index=[0])

    weather_data['datetime'] = weather_data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    weather_data['datetime']  = pd.to_datetime(weather_data['datetime'])
    # logging.debug(f"Fetched weather data type: {type(weather_data['datetime'])}")
    merged_data = pd.merge_asof(df.sort_values('date_zre'), 
                             weather_data.sort_values('datetime'),                              
                            left_on='date_zre',                                                        
                            right_on='datetime', 
                            direction='nearest', 
                            tolerance=pd.Timedelta('30 minutes'))

    merged_data = merged_data.drop('datetime', axis =1)

    if merged_data.empty:
        return jsonify({"error": "No matching weather data found within 30 minutes tolerance"}), 400

    # Preprocess the merged DataFrame
    processed_data = preprocessing(merged_data)

    # Ensure that the processed DataFrame has all the expected columns
    expected_columns = model.regressor_.named_steps['columntransformer'].get_feature_names_out()
    missing_cols = set(expected_columns) - set(processed_data.columns)
    for col in missing_cols:
        processed_data[col] = 0
    processed_data = processed_data[expected_columns]

    predictions = model.predict(processed_data)
    
    return jsonify(predictions.tolist())

@app.route('/predictions', methods=['POST'])
def store_predictions():
    data = request.json
    amp_id = data.get('amp_id')
    prediction_value = data.get('prediction_value')
    if not amp_id:
        return jsonify({"error": "AMP_ID is required"}), 400
    if not prediction_value:
        return jsonify({"error": "Prediction value is required"}), 400
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dbo.predictions (amp_id, prediction_value)
            VALUES (?, ?)
        """, (amp_id, prediction_value[0]))
        conn.commit()
        conn.close()
        # logging.debug(f"prediction_value: {prediction_value}")
        return jsonify({"message": "Prediction value stored successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/display_predictions', methods=['GET'])
def fetch_predictions():
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT amp_id, prediction_value
            FROM dbo.predictions
        """)
        predictions = []
        for row in cursor.fetchall():
            predictions.append({
                "amp_id": row[0],
                "prediction_value": row[1]
            })
        conn.close()
        return jsonify(predictions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/check_amp_id_exists',methods=['POST'])
def check_amp_id_exists():
    data = request.get_json()
    amp_id = data.get('amp_id')

    if not amp_id:
        return jsonify({"error": "No AMP ID provided"}), 400

    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(1) FROM dbo.predictions WHERE amp_id = ?", (amp_id,))
        exists = cursor.fetchone()[0] > 0
        conn.close()
        return jsonify({"exists": exists}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
