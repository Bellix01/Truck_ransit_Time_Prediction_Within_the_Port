from flask import Flask, jsonify
import pyodbc
from flask_cors import CORS
import json
app = Flask(__name__)
CORS(app)  # Allow only the React app origin


def connection():
    server = 'DESKTOP-9HOJAES'  
    database = 'Northwind' 
    user = 'sa'
    password = '@sql2001@' #Your login password
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+user+';PWD='+ password
    conn = pyodbc.connect(cstr)
    return conn
@app.route("/")
def main():
    customers = []
    try:
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CustomerID, CompanyName, ContactName, ContactTitle, Address, City, PostalCode, Country, Phone FROM dbo.Customers")
        for row in cursor.fetchall():
            customers.append({
                "CustomerID": row[0],
                "CompanyName": row[1],
                "ContactName": row[2],
                "ContactTitle": row[3],
                "Address": row[4],
                "City": row[5],
                "PostalCode": row[6],
                "Country": row[7],
                "Phone": row[8]
            })
        conn.close()
        # print(json.dumps(customers, indent=4))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return json.dumps(customers, indent=4)

if(__name__ == "__main__"):
    app.run()