from flask import Flask, render_template
from config import Config
from models import db
from routes.admin import admin_bp
from routes.employee import employee_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Register Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(employee_bp)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/test-db')
def test_db():
    try:
        db.session.execute(db.text("SELECT 1"))
        return "<h2 style='color:green'>✅ Database Connected Successfully!</h2>"
    except Exception as e:
        return f"<h2 style='color:red'>❌ Database Connection Failed</h2><br>{e}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
