import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuration for photo uploads
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the data - assuming a CSV structure for the guide
DATA_FILE = 'universal_food_data.csv'

def get_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=['id', 'name', 'park', 'meal_type', 'price', 'rating', 'image_path'])

@app.route('/')
def index():
    df = get_data()
    
    # Get filter parameters
    search_query = request.args.get('search', '').lower()
    park_filter = request.args.get('park', '')
    meal_filter = request.args.get('meal_type', '')

    # Apply Filters
    if search_query:
        df = df[df['name'].str.lower().str.contains(search_query)]
    if park_filter:
        df = df[df['park'] == park_filter]
    if meal_filter:
        df = df[df['meal_type'] == meal_filter]

    # Automatic price sorting (Low to High)
    df = df.sort_values(by='price')

    items = df.to_dict('records')
    return render_template('index.html', items=items)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    name = request.form.get('item_name')
    rating = request.form.get('rating')
    file = request.files.get('photo')
    
    # Handle photo upload
    image_path = ""
    if file:
        filename = f"{name.replace(' ', '_')}_{file.filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = f"uploads/{filename}"

    # Email-based feedback logic (simulated via log/flash)
    # In a production environment, use Flask-Mail here
    print(f"Feedback Received: {name} - Rating: {rating} - Image: {image_path}")
    
    flash('Thank you for your rating and photo!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)