from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)

app.secret_key = '2c14dce27b6d4e5fa5e45ae7fb15c4af'  # Replace with a strong secret key


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False) 
    password = db.Column(db.String(150), nullable=False)
    preferences = db.Column(db.String(500))

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user = User.query.get(session['user_id'])  # Get user from the session
    recommendations = get_recommendations(user.preferences)  # Get recommendations based on user preferences
    
    return render_template('home.html', recommendations=recommendations)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('preferences'))
        return 'Invalid credentials'
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            return 'Passwords do not match'

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(username=username, email=email, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))  # Redirect to login after signup

    return render_template('signup.html')

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST':
        cuisine = request.form.get('cuisine')
        price_range = request.form.get('price_range')

        user = User.query.get(session['user_id'])  # Get the logged-in user
        user.preferences = f"{cuisine}, {price_range}"  # Store user preferences
        db.session.commit()  # Save changes to the database

        return redirect(url_for('home'))  # Redirect to home page after saving preferences
    
    return render_template('preferences.html')


def get_recommendations(preferences):
    # Sample static data for demonstration; replace this with your ML logic
    all_restaurants = [
        {"name": "The Italian Place", "cuisine": "Italian", "price": "$$"},
        {"name": "Sushi World", "cuisine": "Japanese", "price": "$$$"},
        {"name": "Spicy Delights", "cuisine": "Indian", "price": "$"},
        {"name": "Taco Haven", "cuisine": "Mexican", "price": "$"},
        {"name": "Curry Palace", "cuisine": "Indian", "price": "$$"},
        {"name": "Noodle House", "cuisine": "Chinese", "price": "$$"},
    ]
    
    # Example: filter restaurants based on user preferences (this is simplistic)
    cuisine_preference = preferences.split(",")[0].strip() if preferences else None
    recommended = [
        restaurant for restaurant in all_restaurants
        if restaurant['cuisine'].lower() == cuisine_preference.lower() or cuisine_preference is None
    ]
    
    return recommended


if __name__ == '__main__':
    app.run(debug=True)
