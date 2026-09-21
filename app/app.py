from flask import Flask, jsonify
import os
import mysql.connector

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "1.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "DEV")

DB_HOST = os.getenv("DB_HOST", "customer-db-dev")
DB_USER = os.getenv("DB_USER", "customer")
DB_PASSWORD = os.getenv("DB_PASSWORD", "customer123")
DB_NAME = os.getenv("DB_NAME", "customerdb")


@app.route("/")
def home():
    return jsonify({
        "application": "Customer Application",
        "version": VERSION,
        "environment": ENVIRONMENT
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "version": VERSION,
        "environment": ENVIRONMENT
    })


@app.route("/db-test")
def db_test():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            "database": "CONNECTED",
            "result": result[0],
            "host": DB_HOST
        })

    except Exception as e:
        return jsonify({
            "database": "NOT CONNECTED",
            "error": str(e)
        }), 500


@app.route("/version")
def version():
    return jsonify({
        "version": VERSION
    })


@app.route("/environment")
def environment():
    return jsonify({
        "environment": ENVIRONMENT
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)