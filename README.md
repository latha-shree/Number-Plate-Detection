🚗 Number Plate Detection & Vehicle Management System

This project is a Flask web application that integrates AI-based number plate detection with a database-driven vehicle management system. It allows users to register vehicles, manage balances, and automatically deduct toll/parking fees when a number plate is detected.

🚀 Features

👤 User Management – User registration, login, and session handling

🚘 Vehicle Registration – Register new vehicles with balance tracking

💰 Balance Management – Add funds and check current balance

📷 Number Plate Detection

Detects vehicle number plates from images/videos using OpenCV + Tesseract

Reads latest detections from CSV (data.csv)

⚡ Automated Fee Deduction

Normal vehicles: ₹100 (₹105 during peak hours)

Green plate vehicles: ₹95 (₹100 during peak hours)

Balance auto-updates in MySQL database

📊 Transaction History (extendable) – Keeps track of deductions

🔐 Secure login with bcrypt password hashing

🛠️ Tech Stack

Backend: Flask (Python)

Database: MySQL (via PyMySQL)

AI/ML: OpenCV, NumPy, Tesseract OCR

Other Libraries: Pandas, Regex, bcrypt, PIL

Frontend: HTML, CSS, Bootstrap (templates)

📂 Project Structure
NumberPlateDetection/
│── app.py                  # Main Flask application
│── main.py / main2.py      # Plate detection scripts (via Streamlit/Python)
│── data.csv                # Stores detected plates
│── templates/              # HTML templates (login, register, balance, dashboard)
│── static/                 # CSS/JS/Images
│── requirements.txt        # Dependencies
│── README.md               # Documentation

⚙️ Installation & Setup

Clone the repository:

git clone https://github.com/your-username/NumberPlateDetection.git
cd NumberPlateDetection


Install dependencies:

pip install -r requirements.txt


Setup MySQL database:

CREATE DATABASE number_plate;
USE number_plate;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    address VARCHAR(255),
    mobile_no VARCHAR(15),
    password VARCHAR(255)
);

CREATE TABLE vehicle_registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    address VARCHAR(255),
    vehicle_number VARCHAR(20) UNIQUE,
    amount FLOAT,
    status VARCHAR(20)
);


Update database credentials in app.py:

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="number_plate"
    )


Run the app:

python app.py


Open in browser:

http://127.0.0.1:5000/

📌 Usage Flow

User registers and logs in

Vehicle registration → add vehicle + initial balance

Detection module (OpenCV + Tesseract) reads plate and stores in data.csv

Flask app checks CSV + DB → finds vehicle and applies balance deduction automatically

Users can check balance anytime from the portal

📊 Future Enhancements

Add live camera feed integration for automatic detection

Deploy on cloud for smart toll/parking automation

Add admin dashboard to view all transactions

Integrate with Razorpay/UPI for online balance top-up

![login](https://github.com/latha-shree/Number-Plate-Detection/blob/main/login.png)
![reg1](https://github.com/latha-shree/Number-Plate-Detection/blob/main/vehicle_reg.png)
![check1](https://github.com/latha-shree/Number-Plate-Detection/blob/main/check_bal1.png)
![img1](https://github.com/latha-shree/Number-Plate-Detection/blob/main/upload_image.png)
![img2](https://github.com/latha-shree/Number-Plate-Detection/blob/main/upload_image1.png)
![img3](https://github.com/latha-shree/Number-Plate-Detection/blob/main/upload_image2.png)
![img3](https://github.com/latha-shree/Number-Plate-Detection/blob/main/upload_image3.png)
![back](https://github.com/latha-shree/Number-Plate-Detection/blob/main/back1.png)
![check1](https://github.com/latha-shree/Number-Plate-Detection/blob/main/check_bal2.png)
![reg2](https://github.com/latha-shree/Number-Plate-Detection/blob/main/vehicle_reg1.png)
![real](https://github.com/latha-shree/Number-Plate-Detection/blob/main/realtime_detect.png)
