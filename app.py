from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


# MySQL Database Connection
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return connection


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Patient Registration
@app.route("/register-patient", methods=["GET", "POST"])
def register_patient():

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO patients
            (name, age, gender, phone, email, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (name, age, gender, phone, email, address)

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        # Go back to Dashboard
        return redirect(url_for("home"))

    return render_template("register_patient.html")


# Add Doctor
@app.route("/add-doctor", methods=["GET", "POST"])
def add_doctor():

    if request.method == "POST":

        name = request.form["name"]
        specialization = request.form["specialization"]
        phone = request.form["phone"]
        email = request.form["email"]
        available_days = request.form["available_days"]
        available_time = request.form["available_time"]

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO doctors
            (name, specialization, phone, email, available_days, available_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            name,
            specialization,
            phone,
            email,
            available_days,
            available_time
        )

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        # Go back to Dashboard
        return redirect(url_for("home"))

    return render_template("add_doctor.html")


# View Doctors
@app.route("/doctors")
def doctors():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM doctors ORDER BY doctor_id"

    cursor.execute(query)
    doctors_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "doctors.html",
        doctors=doctors_list
    )


# Doctor Search
@app.route("/search-doctor", methods=["GET", "POST"])
def search_doctor():

    doctors_list = []

    if request.method == "POST":

        search = request.form["search"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM doctors
            WHERE name LIKE %s
            OR specialization LIKE %s
        """

        search_value = "%" + search + "%"

        cursor.execute(
            query,
            (search_value, search_value)
        )

        doctors_list = cursor.fetchall()

        cursor.close()
        connection.close()

    return render_template(
        "search_doctor.html",
        doctors=doctors_list
    )


# Book Appointment
@app.route("/book-appointment", methods=["GET", "POST"])
def book_appointment():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get all patients
    cursor.execute(
        "SELECT * FROM patients ORDER BY name"
    )
    patients = cursor.fetchall()

    # Get all doctors
    cursor.execute(
        "SELECT * FROM doctors ORDER BY name"
    )
    doctors = cursor.fetchall()

    if request.method == "POST":

        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        reason = request.form["reason"]

        query = """
            INSERT INTO appointments
            (patient_id, doctor_id, appointment_date, appointment_time, reason)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            patient_id,
            doctor_id,
            appointment_date,
            appointment_time,
            reason
        )

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        # Go back to Dashboard
        return redirect(url_for("home"))

    cursor.close()
    connection.close()

    return render_template(
        "book_appointment.html",
        patients=patients,
        doctors=doctors
    )


# View Appointments
@app.route("/appointments")
def appointments():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            a.appointment_id,
            p.name AS patient_name,
            d.name AS doctor_name,
            d.specialization,
            a.appointment_date,
            a.appointment_time,
            a.status,
            a.reason
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date, a.appointment_time
    """

    cursor.execute(query)
    appointments_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "appointments.html",
        appointments=appointments_list
    )


# Cancel Appointment
@app.route(
    "/cancel-appointment/<int:appointment_id>",
    methods=["POST"]
)
def cancel_appointment(appointment_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE appointments
        SET status = 'Cancelled'
        WHERE appointment_id = %s
    """

    cursor.execute(
        query,
        (appointment_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    # Go back to Dashboard
    return redirect(url_for("home"))


# Appointment History
@app.route("/appointment-history")
def appointment_history():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            a.appointment_id,
            p.name AS patient_name,
            d.name AS doctor_name,
            d.specialization,
            a.appointment_date,
            a.appointment_time,
            a.reason,
            a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date DESC,
                 a.appointment_time DESC
    """

    cursor.execute(query)
    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "appointment_history.html",
        history=history
    )


# Run Application
if __name__ == "__main__":
    app.run(debug=True)