from flask import Blueprint, render_template, request, session, redirect, url_for
from models import db, Employee, Admin

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.password == password:
            session["admin"] = admin.username
            return redirect(url_for("admin.admin_dashboard"))

        return "<h2>Invalid Admin Credentials</h2>"

    return render_template("admin/login.html")


@admin_bp.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    return render_template("admin/dashboard.html")


@admin_bp.route("/admin/add-employee", methods=["GET", "POST"])
def add_employee():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":

        employee = Employee(
            name=request.form["name"],
            email=request.form["email"],
            password=request.form["password"],
            department=request.form["department"],
            designation=request.form["designation"],
            phone=request.form["phone"],
            status=request.form["status"]
        )

        db.session.add(employee)
        db.session.commit()

        return "<h2>Employee Added Successfully!</h2><br><a href='/admin/dashboard'>Back to Dashboard</a>"

    return render_template("admin/add_employee.html")

@admin_bp.route("/admin/view-employees")
def view_employees():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    employees = Employee.query.all()

    return render_template(
        "admin/view_employees.html",
        employees=employees
    )


@admin_bp.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(url_for("admin.admin_login"))
