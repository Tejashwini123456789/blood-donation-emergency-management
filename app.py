from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
# MySQL configuration
app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB")



mysql = MySQL(app)


# Home page
@app.route("/")
def home():
    return render_template("home.html")


# Registration page
@app.route("/register")
def register_page():
    return render_template("register.html")


# Save donor details
@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]
    blood_group = request.form["blood_group"]
    phone = request.form["phone"]
    city = request.form["city"]

    cursor = mysql.connection.cursor()

    query = """
    INSERT INTO donors (name, age, gender, blood_group, phone, city)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (name, age, gender, blood_group, phone, city)

    cursor.execute(query, values)

    mysql.connection.commit()
    cursor.close()

    return "Donor registered successfully!"


# Search donors
@app.route("/search", methods=["GET", "POST"])
def search():

    donors = []

    if request.method == "POST":

        blood_group = request.form["blood_group"]

        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT * FROM donors WHERE blood_group = %s",
            (blood_group,)
        )

        donors = cursor.fetchall()

        cursor.close()

    return render_template("search.html", donors=donors)


@app.route("/emergency", methods=["GET", "POST"])
def emergency():

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        blood_group = request.form["blood_group"]
        hospital = request.form["hospital"]
        city = request.form["city"]
        phone = request.form["phone"]

        cursor = mysql.connection.cursor()

        query = """
        INSERT INTO emergency_requests
        (patient_name, blood_group, hospital, city, phone)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            patient_name,
            blood_group,
            hospital,
            city,
            phone
        )

        cursor.execute(query, values)

        mysql.connection.commit()
        cursor.close()

        return "Emergency request submitted successfully!"

    return render_template("emergency.html")


@app.route("/donors")
def donors():

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM donors")

    all_donors = cursor.fetchall()

    cursor.close()

    return render_template(
        "donors.html",
        donors=all_donors
    )


@app.route("/dashboard")
def dashboard():

    cursor = mysql.connection.cursor()

    # Total donors
    cursor.execute("SELECT COUNT(*) FROM donors")
    total_donors = cursor.fetchone()[0]

    # Total emergency requests
    cursor.execute("SELECT COUNT(*) FROM emergency_requests")
    total_requests = cursor.fetchone()[0]

    # Total blood groups
    cursor.execute("SELECT COUNT(DISTINCT blood_group) FROM donors")
    total_blood_groups = cursor.fetchone()[0]

    # Total cities
    cursor.execute("SELECT COUNT(DISTINCT city) FROM donors")
    total_cities = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "dashboard.html",
        total_donors=total_donors,
        total_requests=total_requests,
        total_blood_groups=total_blood_groups,
        total_cities=total_cities
    )



@app.route("/delete/<int:donor_id>")
def delete_donor(donor_id):

    cursor = mysql.connection.cursor()

    cursor.execute(
        "DELETE FROM donors WHERE donor_id = %s",
        (donor_id,)
    )

    mysql.connection.commit()
    cursor.close()

    return redirect("/donors")


@app.route("/edit/<int:donor_id>")
def edit_donor(donor_id):

    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT * FROM donors WHERE donor_id = %s",
        (donor_id,)
    )

    donor = cursor.fetchone()

    cursor.close()

    return render_template(
        "edit_donor.html",
        donor=donor
    )


@app.route("/update/<int:donor_id>", methods=["POST"])
def update_donor(donor_id):

    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]
    blood_group = request.form["blood_group"]
    phone = request.form["phone"]
    city = request.form["city"]

    cursor = mysql.connection.cursor()

    cursor.execute(
        """
        UPDATE donors
        SET name=%s,
            age=%s,
            gender=%s,
            blood_group=%s,
            phone=%s,
            city=%s
        WHERE donor_id=%s
        """,
        (name, age, gender, blood_group, phone, city, donor_id)
    )

    mysql.connection.commit()
    cursor.close()

    return redirect("/donors")



@app.route("/requests")
def view_requests():

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM emergency_requests")

    requests = cursor.fetchall()

    cursor.close()

    return render_template(
        "requests.html",
        requests=requests
    )



if __name__ == "__main__":
    app.run(debug=True)