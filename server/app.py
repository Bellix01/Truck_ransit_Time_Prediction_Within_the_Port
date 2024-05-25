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
    logging.debug(f"Fetched weather data sample: {weather_data}")
    conn.close()

    # Convert weather data to DataFrame and lowercase column names
    # Make sure weather_rows is a list of tuples with the correct length
    weather_data = pd.DataFrame(weather_data, index=[0])
    logging.debug(f"Fetched weather data sample: {weather_data.columns}")
    # weather_data.columns = weather_data.columns.str.lower()

    # Convert datetime to datetime object
    weather_data['datetime'] = weather_data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    weather_data['datetime']  = pd.to_datetime(weather_data['datetime'])
    logging.debug(f"Fetched weather data type: {type(weather_data['datetime'])}")
    logging.debug(f"Fetched data type: {type(df['date_zre'])}")
    # Merge truck data with weather data based on date_zre and datetime (tolerance of 30 minutes)
    merged_data = pd.merge_asof(df.sort_values('date_zre'), 
                             weather_data.sort_values('datetime'),                              
                            left_on='date_zre',                                                        
                            right_on='datetime', 
                            direction='nearest', 
                            tolerance=pd.Timedelta('30 minutes'))

    # Drop rows where merge_asof could not find a match within the tolerance
    merged_data.dropna(inplace=True)

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

    # Make predictions using the model
    predictions = model.predict(processed_data)
    
    # Return the predictions as JSON
    return jsonify(predictions.tolist())

if __name__ == '__main__':
    app.run(debug=True)
