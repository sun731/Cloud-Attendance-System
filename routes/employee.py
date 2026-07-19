from flask import Blueprint, render_template, request, session, redirect, url_for
from models import Employee, Attendance, db
from datetime import date, datetime

employee_bp = Blueprint("employee", __name__)


@employee_bp.route("/employee/login", methods=["GET", "POST"])
def employee_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        employee = Employee.query.filter_by(email=email).first()

        if employee and employee.password == password:

            session["employee_id"] = employee.employee_id
            session["employee_name"] = employee.name

            return redirect(url_for("employee.employee_dashboard"))

        return "<h2>Invalid Email or Password</h2>"

    return render_template("employee/login.html")


@employee_bp.route("/employee/dashboard")
def employee_dashboard():

    if "employee_id" not in session:
        return redirect(url_for("employee.employee_login"))

    employee = Employee.query.get(session["employee_id"])

    return render_template(
        "employee/dashboard.html",
        employee=employee
    )

@employee_bp.route("/employee/check-in")
def check_in():

    if "employee_id" not in session:
        return redirect(url_for("employee.employee_login"))

    employee_id = session["employee_id"]

    today = date.today()

    existing = Attendance.query.filter_by(
        employee_id=employee_id,
        attendance_date=today
    ).first()

    if existing:
        return """
        <h2>You have already checked in today.</h2>
        <br>
        <a href="/employee/dashboard">Back to Dashboard</a>
        """

    attendance = Attendance(
        employee_id=employee_id,
        attendance_date=today,
        check_in=datetime.now().time(),
        attendance_status="Present"
    )

    db.session.add(attendance)
    db.session.commit()

    return """
    <h2>Check In Successful!</h2>
    <br>
    <a href="/employee/dashboard">Back to Dashboard</a>
    """


@employee_bp.route("/employee/logout")
def employee_logout():

    session.pop("employee_id", None)
    session.pop("employee_name", None)

    return redirect(url_for("employee.employee_login"))

