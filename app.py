from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


@app.route('/')
def home():
    return render_template("login.html")


@app.route('/test-db')
def test_db():
    try:
        db.session.execute(db.text("SELECT 1"))
        return "<h2 style='color:green'>✅ Database Connected Successfully!</h2>"
    except Exception as e:
        return f"<h2 style='color:red'>❌ Database Connection Failed</h2><br>{e}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
