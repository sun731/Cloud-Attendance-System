from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    return f"""
    <h2>Login Successful</h2>

    Email : {email}<br>

    Password : {password}
    """


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
