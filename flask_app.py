from flask_bootstrap import Bootstrap
import datetime
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
import smtplib
from email.message import EmailMessage
import requests
import random
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from ignore_file import PETFINDER_API, SECRET, ORG_ID, APP_SECRET, EMAIL, EMAIL_PASSWORD, PAYPAL_SECRET, PAYPAL_CLIENT

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


# Function to make the API call and return data
def get_animals():
    # Set up the API endpoint and headers
    AUTH_URL = 'https://api.petfinder.com/v2/oauth2/token'
    API_URL = 'https://api.petfinder.com/v2'

    # Obtain access token
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': PETFINDER_API,
        'client_secret': SECRET
    }
    auth_response = requests.post(AUTH_URL, data=auth_data, timeout=60)
    auth_data = auth_response.json()
    access_token = auth_data['access_token']

    # Make a GET request to the API using the access token
    headers = {'Authorization': f'Bearer {access_token}'}
    params1 = {'organization': ORG_ID, 'limit': 40, 'page': 1}
    response1 = requests.get(f'{API_URL}/animals', headers=headers, params=params1, timeout=60)
    data = response1.json()

    # Process data and return desired results
    animals = []
    for animal in data['animals']:
        name = animal['name']
        description = animal['description']
        # Replace special characters in the description
        description = description.replace("&#039;", "'")
        image_url = animal['primary_photo_cropped']['full'] + '?width=450'
        link = animal['url']

        if animal['type'] == 'Dog':
            animals.append(
                {'name': name, 'description': description, 'image_url': image_url, 'link': link, 'animal_type': 'Dog'})
        elif animal['type'] == 'Cat':
            animals.append(
                {'name': name, 'description': description, 'image_url': image_url, 'link': link, 'animal_type': 'Cat'})
        else:
            animals.append({'name': name, 'description': description, 'image_url': image_url, 'link': link,
                            'animal_type': 'Exotic'})
    return animals

def get_featured_animals():
    # Set up the API endpoint and headers
    AUTH_URL = 'https://api.petfinder.com/v2/oauth2/token'
    API_URL = 'https://api.petfinder.com/v2'

    # Obtain access token
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': PETFINDER_API,
        'client_secret': SECRET
    }
    auth_response = requests.post(AUTH_URL, data=auth_data, timeout=60)
    auth_data = auth_response.json()
    access_token = auth_data['access_token']

    # Make a GET request to the API using the access token
    headers = {'Authorization': f'Bearer {access_token}'}
    params1 = {'organization': ORG_ID, 'limit': 40, 'page': 1}
    response1 = requests.get(f'{API_URL}/animals', headers=headers, params=params1, timeout=60)
    data = response1.json()

    # Process data and return desired results
    dogs = []
    cats = []
    exotics = []
    for animal in data['animals']:
        name = animal['name']
        description = animal['description']
        # Replace special characters in the description
        description = description.replace("&#039;", "'")
        image_url = animal['primary_photo_cropped']['full'] + '?width=450'
        link = animal['url']

        if animal['type'] == 'Dog':
            dogs.append(
                {'name': name, 'description': description, 'image_url': image_url, 'link': link, 'animal_type': 'Dog'})
        elif animal['type'] == 'Cat':
            cats.append(
                {'name': name, 'description': description, 'image_url': image_url, 'link': link, 'animal_type': 'Cat'})
        else:
            exotics.append({'name': name, 'description': description, 'image_url': image_url, 'link': link,
                            'animal_type': animal['type']})

    featured_dog = random.choice(dogs)
    featured_cat = random.choice(cats)

    # Check if the exotics list is empty, if so, choose either a dog or cat randomly
    if not exotics:
        featured_exotic = random.choice(dogs + cats)
    else:
        featured_exotic = random.choice(exotics)

    return [featured_dog, featured_cat, featured_exotic]


class ContactForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=500)], render_kw={"rows": 5})


year = int(datetime.datetime.now().year)

App = Flask(__name__)
App.config['SECRET_KEY'] = f'{APP_SECRET}'
Bootstrap(App)


@App.route("/", methods=['GET', 'POST'])
def home():
    featured_animals = get_featured_animals()
    form = ContactForm()
    if form.validate_on_submit():
        # Send email
        msg = EmailMessage()
        msg['Subject'] = 'Foxy Family Rescue: New Contact Form Submission'
        msg['From'] = str(form.email.data)
        msg['To'] = 'foxyfamilyrescue@gmail.com'
        msg.set_content(
            f"Name: {form.first_name.data.title()} {form.last_name.data.title()}\nPhone: {form.phone_number.data}\nEmail: {form.email.data}\nMessage: {form.message.data}")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(f'{EMAIL}', f'{EMAIL_PASSWORD}')
            smtp.send_message(msg)
        return '<div class="text-center"><h1>Thank you for reaching out to Foxy Family Rescue! We will get back to you soon!</h1><button class="btn btn-primary mt-3" style="text-align: center;" onclick="window.location.href=\'/\'">Return Home</button></div>'

    return render_template("home.html", year=year,
                           featured_dog=featured_animals[0],
                           featured_cat=featured_animals[1],
                           featured_exotic=featured_animals[2], form=form)


@App.route("/Dogs")
def dogs_page():
    dogs = [animal for animal in get_animals() if animal['animal_type'] == 'Dog']
    return render_template("dogs.html", year=year, pets=dogs)


@App.route("/paypaltest")
def paypal_page():
    client_id = f'{PAYPAL_CLIENT}'
    secret_key = f'{PAYPAL_SECRET}'

    # Request for the access token
    auth_response = requests.post('https://api.sandbox.paypal.com/v1/oauth2/token',
                                  headers={
                                      'Accept': 'application/json',
                                      'Accept-Language': 'en_US',
                                  },
                                  data={
                                      'grant_type': 'client_credentials'
                                  },
                                  auth=(client_id, secret_key), timeout=60)

    # Get the access token from the response
    access_token = auth_response.json()['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'PayPal-Request-Id': 'PRODUCT-18062019-001',
        'Prefer': 'return=representation',
    }

    # Create product
    product_data = {
        "name": "Video Streaming Service Subscription",
        "description": "Video streaming service subscription plan",
        "type": "SERVICE",
        "category": "SOFTWARE",
        "image_url": "https://example.com/streaming.jpg",
        "home_url": "https://example.com/home"
    }
    product_response = requests.post('https://api.sandbox.paypal.com/v1/catalogs/products', headers=headers, json=product_data, timeout=60)
    product_id = product_response.json()['id']

    # Create plan
    plan_data = {
        "product_id": product_id,
        "name": "Video Streaming Service Plan",
        "description": "Video streaming service basic subscription plan",
        "status": "ACTIVE",
        "billing_cycles": [
            {
                "frequency": {"interval_unit": "MONTH", "interval_count": 1},
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": 12,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": "10",
                        "currency_code": "USD"
                    }
                }
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "setup_fee": {
                "value": "10",
                "currency_code": "USD"
            },
            "setup_fee_failure_action": "CONTINUE",
            "payment_failure_threshold": 3
        },
        "taxes": {
            "percentage": "10",
            "inclusive": False
        }
    }
    plan_response = requests.post('https://api.sandbox.paypal.com/v1/billing/plans', headers=headers, json=plan_data, timeout=60)
    print(f"plan response: {plan_response.status_code}")
    plan_id = plan_response.json()['id']
    print(plan_response.json())
    # Pass client_id and plan_id to the template
    return render_template("testPaypal.html", clientID=client_id, planID=plan_id)

@App.route("/Cats")
def cats_page():
    cats = [animal for animal in get_animals() if animal['animal_type'] == 'Cat']
    return render_template("cats.html", year=year, pets=cats)


@App.route("/Exotics")
def exotics_page():
    exotics = [animal for animal in get_animals() if animal['animal_type'] != 'Dog' and animal['animal_type'] != 'Cat']
    return render_template("Exotics.html", year=year, pets=exotics)

if __name__ == '__main__':
    App.run(debug=True)
