from flask import Flask
import os
from db import db
from db.models import *

app = Flask(__name__)
# Ensure instance folder exists and use proper path
os.makedirs(app.instance_path, exist_ok=True)
db_path = os.path.join(app.instance_path, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Create sample testimonials
    testimonial1 = Testimonial(
        client_name='Sarah Johnson',
        client_title='Marketing Executive',
        testimonial_text='The holistic approach here has completely transformed my life. I came in feeling stressed and overwhelmed, but now I feel balanced and at peace.',
        rating=5,
        is_approved=True,
        is_featured=True
    )
    
    testimonial2 = Testimonial(
        client_name='Michael Chen', 
        client_title='Software Engineer',
        testimonial_text='I\'ve tried many different therapies over the years, but nothing compares to the integrated healing approach here.',
        rating=5,
        is_approved=True,
        is_featured=False
    )
    
    testimonial3 = Testimonial(
        client_name='Emily Rodriguez',
        client_title='Teacher', 
        testimonial_text='After struggling with anxiety for years, I finally found relief through the personalized treatment plan they created for me.',
        rating=5,
        is_approved=True,
        is_featured=True
    )
    
    testimonial4 = Testimonial(
        client_name='Jessica Williams',
        client_title='Yoga Instructor',
        testimonial_text='As someone who works in the wellness industry, I can truly appreciate the quality of care here.',
        rating=4,
        is_approved=False,
        is_featured=False
    )
    
    db.session.add_all([testimonial1, testimonial2, testimonial3, testimonial4])
    db.session.commit()
    print('Sample testimonials created successfully!')
