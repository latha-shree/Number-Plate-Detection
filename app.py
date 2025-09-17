from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
import bcrypt
import cv2
import numpy as np
import pytesseract
import base64
import io
from PIL import Image
import subprocess
import pandas as pd
import re
from datetime import datetime
import os
import time

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Connection Function
def get_db_connection():
    return pymysql.connect(host="localhost", user="root", password="1234", database="number_plate")


# Home Route
@app.route('/')
def home():
    if "user" in session:
        return render_template("index.html", user=session["user"])
    return redirect(url_for("login"))

# User Registration Route
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        address = request.form['address']
        mobile_no = request.form['mobile_no']
        password = request.form['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute("INSERT INTO users (username, address, mobile_no, password) VALUES (%s, %s, %s, %s)",
                           (username, address, mobile_no, hashed_password))
            db.commit()
            return redirect(url_for("login"))
        except pymysql.IntegrityError:
            return "User already exists!"
        finally:
            cursor.close()
            db.close()
    
    return render_template("register.html")

# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
            session["user"] = username
            return redirect(url_for("home"))
        return "Invalid username or password!"

    return render_template("login.html")

'''# Vehicle Registration
@app.route('/register', methods=['POST'])
def register_vehicle():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Please log in first"}), 403

    # Ensure request data is JSON
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid request format"}), 400

    # Extract and validate data
    name = data.get("name")
    address = data.get("address")
    vehicle_number = data.get("vehicle_number")
    amount = data.get("amount")

    if not all([name, address, vehicle_number]) or amount != 500:
        return jsonify({"status": "error", "message": "Invalid details or incorrect payment amount"}), 400
    
    if not all([name, address, vehicle_number]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"status": "error", "message": "Payment amount must be greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid payment amount format"}), 400

    # Establish Database Connection
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("INSERT INTO vehicle_registration (name, address, vehicle_number, amount, status) VALUES (%s, %s, %s, %s, %s)",
                       (name, address, vehicle_number, amount, "Paid"))
        db.commit()
        return jsonify({"status": "success", "message": "Vehicle registered successfully!"})
    except pymysql.IntegrityError:
        return jsonify({"status": "error", "message": "Vehicle number already registered"}), 400
    finally:
        cursor.close()
        db.close()

'''
 
@app.route('/register', methods=['POST'])
def register_vehicle():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Please log in first"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid request format"}), 400

    name = data.get("name")
    address = data.get("address")
    vehicle_number = data.get("vehicle_number")
    amount = data.get("amount")

    if not all([name, address, vehicle_number]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        amount = float(amount)
        if amount <= 500:
            return jsonify({"status": "error", "message": "Payment amount must be greater than 500"}), 400
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid payment amount format"}), 400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        # Check if vehicle already exists
        cursor.execute("SELECT amount FROM vehicle_registration WHERE vehicle_number = %s", (vehicle_number,))
        result = cursor.fetchone()

        if result:
            # Vehicle exists: update balance
            current_balance = result[0]
            new_balance = current_balance + amount
            cursor.execute("UPDATE vehicle_registration SET amount = %s WHERE vehicle_number = %s",
                           (new_balance, vehicle_number))
            message = f"Balance updated. New balance: ₹{new_balance}"
        else:
            # New vehicle: insert record
            cursor.execute("INSERT INTO vehicle_registration (name, address, vehicle_number, amount, status) VALUES (%s, %s, %s, %s, %s)",
                           (name, address, vehicle_number, amount, "Paid"))
            message = "Vehicle registered successfully!"

        db.commit()
        return jsonify({"status": "success", "message": message})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        cursor.close()
        db.close()

# Logout
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))




def get_detected_number_plate():
    """ Read and clean the last detected number plate from data.csv """
    try:
        df = pd.read_csv("data.csv", header=None, names=["timestamp", "number_plate"])  # Read with proper column names
        if df.empty:
            print("⚠ data.csv is empty!")
            return None

        # Get the last detected plate and remove unwanted characters
        detected_plate = df.iloc[-1]["number_plate"]
        detected_plate = re.sub(r"[^A-Za-z0-9]", "", detected_plate).upper().strip()  # Remove all special characters
        
        print(f"🔍 Detected Plate (After Formatting): '{detected_plate}'")  # Debugging
        return detected_plate
    except Exception as e:
        print("❌ Error reading data.csv:", e)
    return None




def check_plate_in_database(detected_plate):
    """Check if the detected plate exists in the database and apply correct deductions."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch vehicle details and check if it's a green plate
        query = "SELECT vehicle_number, amount FROM vehicle_registration WHERE vehicle_number = %s"
        cursor.execute(query, (detected_plate,))
        vehicle = cursor.fetchone()

        if vehicle:
            vehicle_number, amount = vehicle

            # Get current time
            current_hour = datetime.now().hour

            # Check if the number plate is green
            is_green_plate = (vehicle_number == "KA02KJ9088")  # Replace with your green plate logic

            if is_green_plate:
                # Special green plate deduction logic
                deduction_amount = 100 if 17 <= current_hour < 19 else 95
            else:
                # Normal deduction logic
                deduction_amount = 105 if 17 <= current_hour < 19 else 100

            new_amount = max(0, amount - deduction_amount)  # Ensuring balance does not go negative

            # Update balance in database
            update_query = "UPDATE vehicle_registration SET amount = %s WHERE vehicle_number = %s"
            cursor.execute(update_query, (new_amount, detected_plate))
            conn.commit()

            print(f"✅ ₹{deduction_amount} Deducted from {detected_plate}. New Balance: ₹{new_amount}")
            return True  # Plate matched and amount updated

        print(f"🚫 Plate {detected_plate} Not Found in Database.")
        return False  # Plate not found

    except Exception as e:
        print("❌ Database error:", e)
        return False
    finally:
        conn.close()


@app.route('/detect', methods=['GET'])
def detect_number_plate():
    try:
        # Step 1: Launch the Streamlit app (test1.py)
        script_path = r"E:\Internship\Number_plate_detection\num\main.py"  # Correct full path
        process = subprocess.Popen(["streamlit", "run", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        csv_file = "data.csv"
        last_mod_time = os.path.getmtime(csv_file) if os.path.exists(csv_file) else 0  # Get initial mod time

        # Step 2: Wait for CSV file to update
        timeout = 180  # 3 minutes timeout
        start_time = time.time()
        detected_plate = None

        print("🚀 Waiting for number plate detection...")

        while time.time() - start_time < timeout:
            time.sleep(5)  # Check every 5 seconds

            # Check if file has been updated
            if os.path.exists(csv_file):
                current_mod_time = os.path.getmtime(csv_file)
                if current_mod_time != last_mod_time:
                    print("📥 Detected file change. Reading updated CSV...")
                    detected_plate = get_detected_number_plate()
                    if detected_plate:
                        break
                    last_mod_time = current_mod_time  # Update last mod time

        # Step 3: Handle timeout or successful detection
        if not detected_plate:
            print("⚠ Timeout reached. No number plate detected.")
            return jsonify({"error": "No plate detected or timeout reached"})

        # Step 4: Check if the detected plate is in the database
        is_registered = check_plate_in_database(detected_plate)

        # Step 5: Kill the Streamlit process after detection
        process.terminate()
        print("🛑 Streamlit process terminated.")

        if is_registered:
            return jsonify({"message": "✅ Matching - ₹100 Deducted", "plate": detected_plate})
        else:
            return jsonify({"message": "🚫 Not Matching", "plate": detected_plate})

    except Exception as e:
        print(f"❌ Error during detection: {e}")
        return jsonify({"error": str(e)})

    

'''@app.route('/check_balance', methods=['GET', 'POST'])
def check_balance():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get("username")
        vehicle_number = data.get("vehicle_number")

        if not username or not vehicle_number:
            return jsonify({"error": "Missing details"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT name, vehicle_number, amount FROM vehicle_registration WHERE vehicle_number = %s"
            cursor.execute(query, (vehicle_number,))
            result = cursor.fetchone()
            
            if result:
                return jsonify({
                    "name": result[0],
                    "vehicle_number": result[1],
                    "balance": result[2]
                })
            else:
                return jsonify({"error": "Vehicle not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    return render_template("balance.html")  # Show the balance check form
'''

@app.route('/check_balance', methods=['GET', 'POST'])
def check_balance():
    if request.method == 'POST':
        data = request.get_json()
        print("Raw data received:", data)

        username = data.get("username")
        vehicle_number = data.get("vehicle_number")

        if not username or not vehicle_number:
            print("Missing username or vehicle number.")
            return jsonify({"error": "Missing details"}), 400

        vehicle_number = vehicle_number.strip().upper()
        print("Normalized vehicle number:", vehicle_number)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT name, vehicle_number, amount FROM vehicle_registration WHERE vehicle_number = %s"
            cursor.execute(query, (vehicle_number,))
            result = cursor.fetchone()

            print("Query executed for:", vehicle_number)
            print("Database returned:", result)
            
            if result:
                print(f"Amount fetched for vehicle: {vehicle_number}")
                return jsonify({
                    "name": result[0],
                    "vehicle_number": result[1],
                    "balance": result[2]
                })
            else:
                print(f"Vehicle not found: {vehicle_number}")
                return jsonify({"error": "Vehicle not found"}), 404
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    return render_template("balance.html")
'''
@app.route('/check_balance', methods=['GET', 'POST'])
def check_balance():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get("username")
        vehicle_number = data.get("vehicle_number")

        if not username or not vehicle_number:
            return jsonify({"error": "Missing details"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT name, vehicle_number, amount FROM vehicle_registration WHERE vehicle_number = %s"
            cursor.execute(query, (vehicle_number,))
            result = cursor.fetchone()
            
            if result:
                return jsonify({
                    "name": result[0],
                    "vehicle_number": result[1],
                    "balance": result[2]
                })
            else:
                return jsonify({"error": "Vehicle not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    # You can return a template if you're using a form in the frontend
    return render_template("balance.html")  # or just return status if using API only


'''


@app.route('/detect_vehicle', methods=['POST'])
def detect_vehicle():
    try:
        script_path = r"E:\Internship\Number_plate_detection\car1\car1\main2.py"  # Use the correct full path

        # Run the script in a separate process
        process = subprocess.Popen(["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Capture output
        stdout, stderr = process.communicate()

        # Print logs for debugging
        print("STDOUT:", stdout.decode('utf-8'))
        print("STDERR:", stderr.decode('utf-8'))

        return jsonify({
            "status": "success" if not stderr else "error",
            "output": stdout.decode('utf-8'),
            "error": stderr.decode('utf-8')
        })

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({"status": "error", "message": str(e)})




if __name__ == '__main__':
    app.run(debug=True)
