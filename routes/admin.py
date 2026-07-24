from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, Admin, Employee, Attendance
from datetime import date
import csv
from io import StringIO
from flask import Response
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
import uuid
from botocore.exceptions import ClientError
BUCKET_NAME = "attendance-system-images-abhinand"

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if "admin" in session:
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()


        if admin and check_password_hash(admin.password, password):
            session["admin"] = admin.username
            flash("Welcome Administrator!", "success")
            return redirect(url_for("admin.admin_dashboard"))

        flash("Invalid Admin Credentials!", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/admin/dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    from datetime import date
    from sqlalchemy import extract

    today = date.today()

    total_employees = Employee.query.count()

    checked_in_today = Attendance.query.filter_by(
        attendance_date=today
    ).count()

    checked_out_today = Attendance.query.filter(
        Attendance.attendance_date == today,
        Attendance.check_out != None
    ).count()

    absent_today = max(0, total_employees - checked_in_today)

    if total_employees > 0:
        attendance_percentage = round(
            (checked_in_today / total_employees) * 100,
            2
        )
    else:
        attendance_percentage = 0

    monthly_records = Attendance.query.filter(
        extract("month", Attendance.attendance_date) == today.month,
        extract("year", Attendance.attendance_date) == today.year
    ).count()

    return render_template(
        "admin/dashboard.html",
        total_employees=total_employees,
        checked_in_today=checked_in_today,
        checked_out_today=checked_out_today,
        absent_today=absent_today,
        attendance_percentage=attendance_percentage,
        monthly_records=monthly_records
    )


@admin_bp.route("/admin/add-employee", methods=["GET", "POST"])
def add_employee():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        existing_employee = Employee.query.filter_by(
            email=email
        ).first()

        if existing_employee:
            flash("An employee with this email already exists.", "danger")
            return redirect(url_for("admin.add_employee"))

        image_url = None

        photo = request.files.get("photo")

        if photo and photo.filename:

            allowed_extensions = {"png", "jpg", "jpeg"}

            extension = photo.filename.rsplit(".", 1)[1].lower()

            if extension not in allowed_extensions:
                flash("Only JPG, JPEG and PNG files are allowed.", "danger")
                return redirect(url_for("admin.add_employee"))

            try:

                filename = f"{uuid.uuid4()}.{extension}"

                s3 = boto3.client("s3")

                s3.upload_fileobj(
                    photo,
                    BUCKET_NAME,
                    filename,
                    ExtraArgs={
                        "ContentType": photo.content_type
                    }
                )

                image_url = (
                    f"https://{BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{filename}"
                )

            except ClientError as e:

                flash(f"S3 Upload Failed: {e}", "danger")
                return redirect(url_for("admin.add_employee"))

        employee = Employee(
            name=request.form["name"],
            email=email,
            password=generate_password_hash(request.form["password"]),
            image_url=image_url,
            department=request.form["department"],
            designation=request.form["designation"],
            phone=request.form["phone"],
            status=request.form["status"]
        )

        try:

            db.session.add(employee)
            db.session.commit()

            flash("Employee added successfully!", "success")

            return redirect(url_for("admin.view_employees"))

        except Exception:

            db.session.rollback()

            flash("An employee with this email already exists.", "danger")

            return redirect(url_for("admin.add_employee"))

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


@admin_bp.route("/admin/edit-employee/<int:employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):

    if "admin" not in session:
        return redirect(url_for("home"))

    employee = Employee.query.get_or_404(employee_id)

    if request.method == "POST":

        employee.name = request.form["name"]
        employee.email = request.form["email"]
        employee.password = generate_password_hash(request.form["password"])
        employee.department = request.form["department"]
        employee.designation = request.form["designation"]
        employee.phone = request.form["phone"]
        employee.status = request.form["status"]

        db.session.commit()

        flash("Employee updated successfully!", "success")
        return redirect(url_for("admin.view_employees"))

    return render_template(
        "admin/edit_employee.html",
        employee=employee
    )


@admin_bp.route("/admin/delete-employee/<int:employee_id>")
def delete_employee(employee_id):

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    employee = Employee.query.get_or_404(employee_id)

    # Delete all attendance records first
    Attendance.query.filter_by(
        employee_id=employee.employee_id
    ).delete()

    # Delete employee
    db.session.delete(employee)

    db.session.commit()

    flash("Employee deleted successfully!", "success")

    return redirect(url_for("admin.view_employees"))


@admin_bp.route("/admin/attendance")
def view_attendance():

    if "admin" not in session:
        return redirect(url_for("home"))

    search = request.args.get("search", "")
    attendance_date = request.args.get("attendance_date", "")
    status = request.args.get("status", "")

    query = (
        db.session.query(Attendance, Employee)
        .join(Employee, Attendance.employee_id == Employee.employee_id)
    )

    if search:
        query = query.filter(Employee.name.ilike(f"%{search}%"))

    if attendance_date:
        query = query.filter(
            Attendance.attendance_date == attendance_date
        )

    if status:
        query = query.filter(
            Attendance.attendance_status == status
        )

    records = query.order_by(
        Attendance.attendance_date.desc(),
        Employee.name
    ).all()

    return render_template(
        "admin/attendance.html",
        records=records,
        search=search,
        attendance_date=attendance_date,
        status=status
    )

@admin_bp.route("/admin/export-attendance")
def export_attendance():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    search = request.args.get("search", "")
    attendance_date = request.args.get("attendance_date", "")
    status = request.args.get("status", "")

    query = (
        db.session.query(Attendance, Employee)
        .join(Employee, Attendance.employee_id == Employee.employee_id)
    )

    if search:
        query = query.filter(Employee.name.ilike(f"%{search}%"))

    if attendance_date:
        query = query.filter(
            Attendance.attendance_date == attendance_date
        )

    if status:
        query = query.filter(
            Attendance.attendance_status == status
        )

    records = query.order_by(
        Attendance.attendance_date.desc(),
        Employee.name
    ).all()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Employee",
        "Department",
        "Date",
        "Check In",
        "Check Out",
        "Status"
    ])

    for attendance, employee in records:

        writer.writerow([
            employee.name,
            employee.department,
            attendance.attendance_date,
            attendance.check_in,
            attendance.check_out,
            attendance.attendance_status
        ])

    csv_data = output.getvalue()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=attendance_report.csv"
        }
    )


@admin_bp.route("/admin/export-monthly-report")
def export_monthly_report():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    from sqlalchemy import extract
    import calendar

    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    if not month or not year:
        flash("Please select a month and year.", "danger")
        return redirect(url_for("admin.monthly_report"))

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Employee ID",
        "Employee Name",
        "Department",
        "Present Days",
        "Attendance Percentage"
    ])

    working_days = calendar.monthrange(year, month)[1]

    employees = Employee.query.order_by(Employee.name).all()

    for employee in employees:

        present_days = Attendance.query.filter(
            Attendance.employee_id == employee.employee_id,
            extract("month", Attendance.attendance_date) == month,
            extract("year", Attendance.attendance_date) == year
        ).count()

        percentage = round(
            (present_days / working_days) * 100,
            2
        ) if working_days else 0

        writer.writerow([
            employee.employee_id,
            employee.name,
            employee.department,
            present_days,
            f"{percentage}%"
        ])

    # Upload CSV to Amazon S3
    try:

        s3 = boto3.client("s3")

        filename = f"attendance-reports/attendance_{month}_{year}.csv"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=output.getvalue(),
            ContentType="text/csv"
        )

        print("Monthly report uploaded to S3.")

    except ClientError as e:

        print(f"S3 Upload Failed: {e}")

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=attendance_{month}_{year}.csv"
        }
    )  


@admin_bp.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))


@admin_bp.route("/admin/monthly-report", methods=["GET"])
def monthly_report():

    if "admin" not in session:
        return redirect(url_for("admin.admin_login"))

    from sqlalchemy import extract
    import calendar

    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    report = []

    total_employees = Employee.query.count()

    total_records = 0
    working_days = 0
    average_attendance = 0
    best_employee = None
    best_percentage = 0

    if month and year:

        working_days = calendar.monthrange(year, month)[1]

        employees = Employee.query.order_by(Employee.name).all()

        total_percentage = 0

        for employee in employees:

            present_days = Attendance.query.filter(
                Attendance.employee_id == employee.employee_id,
                extract("month", Attendance.attendance_date) == month,
                extract("year", Attendance.attendance_date) == year
            ).count()

            percentage = round(
                (present_days / working_days) * 100,
                2
            ) if working_days else 0

            if percentage >= 90:
                status = "Excellent"

            elif percentage >= 75:
                status = "Good"

            elif percentage >= 60:
                status = "Average"

            else:
                status = "Poor"

            report.append({

                "employee": employee,

                "present_days": present_days,

                "percentage": percentage,

                "status": status

            })

            total_records += present_days
            total_percentage += percentage

            if percentage > best_percentage:

                best_percentage = percentage
                best_employee = employee.name

        if total_employees > 0:

            average_attendance = round(
                total_percentage / total_employees,
                2
            )

    return render_template(

        "admin/monthly_report.html",

        report=report,

        month=month,

        year=year,

        total_employees=total_employees,

        total_records=total_records,

        working_days=working_days,

        average_attendance=average_attendance,

        best_employee=best_employee,

        best_percentage=best_percentage

    )
