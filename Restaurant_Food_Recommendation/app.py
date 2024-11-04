from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pandas as pd


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
    preferred_cuisine = db.Column(db.String(100))
    preferred_spiciness = db.Column(db.String(50))
    preferred_location = db.Column(db.String(100))
    preferred_cost = db.Column(db.Integer)

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

# @app.route('/preferences', methods=['GET', 'POST'])
# def preferences():
#     if request.method == 'POST':
#         cuisine = request.form.get('cuisine')
#         price_range = request.form.get('price_range')

#         user = User.query.get(session['user_id'])  # Get the logged-in user
#         user.preferences = f"{cuisine}, {price_range}"  # Store user preferences
#         db.session.commit()  # Save changes to the database

#         return redirect(url_for('home'))  # Redirect to home page after saving preferences
    
#     return render_template('preferences.html')

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        cuisine = request.form['cuisine']
        spiciness = request.form['spiciness']
        location = request.form['location']
        cost = int(request.form['cost'])

        user = User.query.get(user_id)
        user.preferred_cuisine = cuisine
        user.preferred_spiciness = spiciness
        user.preferred_location = location
        user.preferred_cost = cost
        db.session.commit()

        return redirect(url_for('recommendations'))

    return render_template('preferences.html')


# Sample restaurant data (ideally from a database or API)
restaurants_data = [
    {'restaurant_name': 'Spicy Delight', 'cuisine': 'Indian', 'spiciness': 'High', 'location': 'Downtown', 'cost': 15*80},
    {'restaurant_name': 'Sweet Haven', 'cuisine': 'Dessert', 'spiciness': 'Low', 'location': 'Suburbs', 'cost': 10*80},
    {'restaurant_name': 'Budget Bites', 'cuisine': 'Fast Food', 'spiciness': 'Medium', 'location': 'Downtown', 'cost': 5*80},
    {'restaurant_name': 'Gourmet Grill', 'cuisine': 'Steakhouse', 'spiciness': 'Medium', 'location': 'Downtown', 'cost': 25*80},
    {'restaurant_name': 'Chennai Spice Hub', 'cuisine': 'South Indian', 'spiciness': 'High', 'location': 'T. Nagar', 'cost': 12 * 80},
    {'restaurant_name': 'The Beach Bistro', 'cuisine': 'Seafood', 'spiciness': 'Medium', 'location': 'Marina Beach', 'cost': 20 * 80},
    {'restaurant_name': 'Cafe Chennai', 'cuisine': 'Cafe', 'spiciness': 'Low', 'location': 'Nungambakkam', 'cost': 8 * 80},
    {'restaurant_name': 'Veggie Delight', 'cuisine': 'Vegetarian', 'spiciness': 'Low', 'location': 'Adyar', 'cost': 10 * 80},
    {'restaurant_name': 'Kebab Kourt', 'cuisine': 'Middle Eastern', 'spiciness': 'High', 'location': 'Anna Nagar', 'cost': 18 * 80},
    {'restaurant_name': 'Sweet Treats', 'cuisine': 'Dessert', 'spiciness': 'Low', 'location': 'Besant Nagar', 'cost': 11 * 80},
    {'restaurant_name': 'Budget Tiffins', 'cuisine': 'South Indian', 'spiciness': 'Medium', 'location': 'Velachery', 'cost': 6 * 80},
    {'restaurant_name': 'Urban Grill', 'cuisine': 'BBQ', 'spiciness': 'Medium', 'location': 'Kodambakkam', 'cost': 22 * 80},
    {'restaurant_name': 'Fusion Fiesta', 'cuisine': 'Fusion', 'spiciness': 'Medium', 'location': 'OMR', 'cost': 17 * 80},
    {'restaurant_name': 'Spicy Express', 'cuisine': 'Chettinad', 'spiciness': 'High', 'location': 'Mylapore', 'cost': 15 * 80},
    {'restaurant_name': 'Tranquil Bites', 'cuisine': 'Continental', 'spiciness': 'Low', 'location': 'Egmore', 'cost': 14 * 80},
    {'restaurant_name': 'Coastal Breeze', 'cuisine': 'Seafood', 'spiciness': 'Medium', 'location': 'ECR', 'cost': 1400},
    {'restaurant_name': 'Heritage Dining', 'cuisine': 'South Indian', 'spiciness': 'High', 'location': 'MRC Nagar', 'cost': 1200},
    {'restaurant_name': 'The Veggie Vault', 'cuisine': 'Vegetarian', 'spiciness': 'Low', 'location': 'Kilpauk', 'cost': 800},
    {'restaurant_name': 'Spice Fiesta', 'cuisine': 'Mexican', 'spiciness': 'High', 'location': 'Thoraipakkam', 'cost': 1300},
    {'restaurant_name': 'Sushi Central', 'cuisine': 'Japanese', 'spiciness': 'Low', 'location': 'Alwarpet', 'cost': 1500},
    {'restaurant_name': 'Arabian Nights', 'cuisine': 'Middle Eastern', 'spiciness': 'Medium', 'location': 'Triplicane', 'cost': 1100},
    {'restaurant_name': 'Curry House', 'cuisine': 'North Indian', 'spiciness': 'High', 'location': 'Guindy', 'cost': 1000},
    {'restaurant_name': 'Pizza Perfection', 'cuisine': 'Italian', 'spiciness': 'Low', 'location': 'Ashok Nagar', 'cost': 900},
    {'restaurant_name': 'Grill Masters', 'cuisine': 'BBQ', 'spiciness': 'Medium', 'location': 'Chromepet', 'cost': 1600},
    {'restaurant_name': 'Chettinad Corner', 'cuisine': 'Chettinad', 'spiciness': 'High', 'location': 'Saidapet', 'cost': 950},
    {'restaurant_name': 'French Flair', 'cuisine': 'French', 'spiciness': 'Low', 'location': 'Nandanam', 'cost': 1800},
    {'restaurant_name': 'Taste of Thailand', 'cuisine': 'Thai', 'spiciness': 'Medium', 'location': 'Velachery', 'cost': 1350},
    {'restaurant_name': 'Mughal Feast', 'cuisine': 'Mughlai', 'spiciness': 'High', 'location': 'Teynampet', 'cost': 1250},
    {'restaurant_name': 'Spicy Dumplings', 'cuisine': 'Chinese', 'spiciness': 'Medium', 'location': 'Thiruvanmiyur', 'cost': 1100},
    {'restaurant_name': 'Healthy Greens', 'cuisine': 'Salads', 'spiciness': 'Low', 'location': 'Perungudi', 'cost': 700},
    {'restaurant_name': 'The Kebab Factory', 'cuisine': 'Kebabs', 'spiciness': 'High', 'location': 'Pallavaram', 'cost': 1050},
    {'restaurant_name': 'Baker\'s Delight', 'cuisine': 'Bakery', 'spiciness': 'Low', 'location': 'Mandaveli', 'cost': 650},
    {'restaurant_name': 'Turkish Treats', 'cuisine': 'Turkish', 'spiciness': 'Medium', 'location': 'Adambakkam', 'cost': 1400},
    {'restaurant_name': 'Flavors of Punjab', 'cuisine': 'Punjabi', 'spiciness': 'High', 'location': 'Kodambakkam', 'cost': 1300},
    {'restaurant_name': 'Vegan Vibes', 'cuisine': 'Vegan', 'spiciness': 'Low', 'location': 'Kotturpuram', 'cost': 900},
]

# Function to get recommendations based on user preferences
def get_recommendations(user_preferences):
    # Convert data to DataFrame
    restaurants_df = pd.DataFrame(restaurants_data)

    # One-hot encode categorical data
    restaurants_encoded = pd.get_dummies(restaurants_df[['cuisine', 'spiciness', 'location']])
    user_pref_encoded = pd.get_dummies(pd.DataFrame([user_preferences]))

    # Align columns between restaurant data and user preferences
    restaurants_encoded, user_pref_encoded = restaurants_encoded.align(user_pref_encoded, fill_value=0, axis=1)

    # Standardize the cost feature
    scaler = StandardScaler()
    restaurants_encoded['cost'] = scaler.fit_transform(restaurants_df[['cost']])
    user_pref_encoded['cost'] = scaler.transform([[user_preferences['cost']]])

    # Compute cosine similarity
    similarities = cosine_similarity(restaurants_encoded, user_pref_encoded)
    restaurants_df['similarity_score'] = similarities.flatten()

    # Return top 3 recommendations
    return restaurants_df.nlargest(3, 'similarity_score').to_dict(orient='records')

@app.route('/recommendations')
def recommendations():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    user_preferences = {
        'cuisine': user.preferred_cuisine,
        'spiciness': user.preferred_spiciness,
        'location': user.preferred_location,
        'cost': user.preferred_cost
    }

    recommended_restaurants = get_recommendations(user_preferences)
    return render_template('home.html', recommendations=recommended_restaurants)


if __name__ == '__main__':
    app.run(debug=True)
