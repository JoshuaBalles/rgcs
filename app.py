from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Temporary login bypass
@app.route('/login', methods=['POST'])
def login_bypass():
    # Here you can later add your authentication logic
    return redirect(url_for('dashboard'))

# Forgot Password route
@app.route('/forgotpassword')
def forgot_password():
    return render_template('forgotpassword.html')

# Add a route for handling the form submission if necessary
@app.route('/resetpassword', methods=['POST'])
def reset_password():
    # Here you can add logic to handle password reset
    # For example, you might send an email to the user with a reset link
    return redirect(url_for('login'))  # Redirect to login page after initiating password reset

if __name__ == '__main__':
    app.run(debug=True)
