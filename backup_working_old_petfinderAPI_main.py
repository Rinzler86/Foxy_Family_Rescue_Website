from flask_bootstrap import Bootstrap
import datetime
from flask import Flask, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_sslify import SSLify
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
import smtplib
from email.message import EmailMessage
import requests
from ignore_file import PETFINDER_API, SECRET, APP_SECRET, EMAIL, EMAIL_PASSWORD
import secrets


ORG_ID = 'tn998'
AUTH_URL = 'https://api.petfinder.com/v2/oauth2/token'
API_URL = 'https://api.petfinder.com/v2'

# Obtain access token
auth_data = {
    'grant_type': 'client_credentials',
    'client_id': PETFINDER_API,
    'client_secret': SECRET
}
auth_response = requests.post(AUTH_URL, data=auth_data)
auth_data = auth_response.json()
access_token = auth_data['access_token']

# Make a GET request to the API using the access token
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get(f'{API_URL}/animals?organization=TN998', headers=headers)
data = response.json()

class Animal:
    def __init__(self, name, description, image_url, link):
        self.name = name
        self.description = description
        self.image_url = image_url
        self.link = link

class Dog(Animal):
    pass

class Cat(Animal):
    pass

class Exotic(Animal):
    pass

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
        dogs.append(Dog(name, description, image_url, link))
    elif animal['type'] == 'Cat':
        cats.append(Cat(name, description, image_url, link))
    else:
        exotics.append(Exotic(name, description, image_url, link))

class FeaturedPets:
    def __init__(self, animal_type):
        self.animal_type = animal_type
        self.featured_pet = None
        self.all_pets = self.get_all_pets()

    def get_all_pets(self):
        if self.animal_type == 'Dog':
            return dogs
        elif self.animal_type == 'Cat':
            return cats
        else:
            return exotics

    def get_featured_pet(self):
        if self.featured_pet:
            return self.featured_pet

        random_pet = secrets.SystemRandom().choice(self.all_pets)
        self.featured_pet = random_pet
        return self.featured_pet

class DogFeaturedPets(FeaturedPets):
    def __init__(self):
        super().__init__('Dog')

class CatFeaturedPets(FeaturedPets):
    def __init__(self):
        super().__init__('Cat')

class ExoticFeaturedPets(FeaturedPets):
    def __init__(self):
        super().__init__('Exotic')

dog_featured_pets = DogFeaturedPets()
cat_featured_pets = CatFeaturedPets()
exotic_featured_pets = ExoticFeaturedPets()



class ContactForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=500)], render_kw={"rows": 5})


year = int(datetime.datetime.now().year)

App = Flask(__name__)
sslify = SSLify(App)
App.config['SECRET_KEY'] = f'{APP_SECRET}'
Bootstrap(App)


@App.route("/", methods=['GET', 'POST'])
def home():
    print(dog_featured_pets.all_pets)
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
                           featured_dog=dog_featured_pets.get_featured_pet(),
                           featured_cat=cat_featured_pets.get_featured_pet(),
                           featured_exotic=exotic_featured_pets.get_featured_pet(), form=form)


@App.route("/Dogs")
def dogs_page():
    print(dogs)
    return render_template("dogs.html", year=year, pets=dogs)


@App.route("/Cats")
def cats_page():
    return render_template("cats.html", year=year, pets=cats)


@App.route("/Exotics")
def exotics_page():
    return render_template("Exotics.html", year=year, pets=exotics)

if __name__ == '__main__':
    App.run()
