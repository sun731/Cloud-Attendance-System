from flask import Flask, render_template, request
from config import Config
from models import db, Employee
from routes.admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Register Admin Blueprint
app.register_blueprint(admin_bp)


@app.route('/')
def home():
    return render_template("index.html")


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


@app.route('/test-db')
def test_db():
    try:
        db.session.execute(db.text("SELECT 1"))
        return "<h2 style='color:green'>✅ Database Connected Successfully!</h2>"
    except Exception as e:
        return f"<h2 style='color:red'>❌ Database Connection Failed</h2><br>{e}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
