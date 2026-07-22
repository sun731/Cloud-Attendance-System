from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class Admin(db.Model):
    __tablename__ = "admins"

    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)


class Employee(db.Model):
    __tablename__ = "employees"

    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500))
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)


class Attendance(db.Model):
    __tablename__ = "attendance"

    attendance_id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.employee_id"),
        nullable=False
    )

    attendance_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    check_in = db.Column(db.Time)

    check_out = db.Column(db.Time)

    attendance_status = db.Column(
        db.String(20),
        default="Present"
    )

    employee = db.relationship(
        "Employee",
        backref="attendance_records"
    )
