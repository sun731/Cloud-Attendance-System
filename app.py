from flask import Flask, render_template, request
from models import db, Employee, Admin
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route('/')
def home():
    return render_template("index.html")


from flask import request

@app.route('/employee/login', methods=['GET', 'POST'])
def employee_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        employee = Employee.query.filter_by(email=email).first()

        if employee and employee.password == password:
            return render_template(
                "employee/dashboard.html",
                employee=employee
            )

        return "<h2>Invalid Email or Password</h2>"

    return render_template("employee/login.html")


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.password == password:
            return render_template("admin/dashboard.html")

        return "<h2>Invalid Admin Credentials</h2>"

    return render_template("admin/login.html")

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template("admin/dashboard.html")


@app.route('/admin/add-employee', methods=['GET', 'POST'])
def add_employee():

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


@app.route('/test-db')
def test_db():
    try:
        db.session.execute(db.text("SELECT 1"))
        return "<h2 style='color:green'>✅ Database Connected Successfully!</h2>"
    except Exception as e:
        return f"<h2 style='color:red'>❌ Database Connection Failed</h2><br>{e}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
