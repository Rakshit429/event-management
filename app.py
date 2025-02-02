from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import json
import smtplib
import random
import os 
from flask import send_from_directory
from dotenv import load_dotenv
# import pandas as pd
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.feature_extraction.text import CountVectorizer
# import numpy as np

load_dotenv() 
UPLOAD_FOLDER = 'C:/Users/DELL/Documents/kars/static/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///kars.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate=Migrate(app,db)

from flask import session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

def recommend_event(top_n=5):
    """ Recommends events to a user based on interests using TF-IDF and Cosine Similarity. """

    user_entryno=user.interest

    if user.interest == "null":
        return events.query.first(top_n)  # Return empty if no interests are found

    # Convert stored interests from JSON string to list
    user_interests = json.loads(user.interest)

    # Fetch all available events from the database
    all_events = events.query.all()

    if not all_events:
        return []  # Return empty if no events exist

    # Prepare event data
    event_names = [event.name for event in all_events]
    event_tags = [event.tags for event in all_events]  # Tags are used for recommendation

    # Convert user interests and event tags into text format for vectorization
    all_texts = [' '.join(user_interests)] + event_tags

    # Convert text data to TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Compute cosine similarity between user interests (first row) and all event tags
    similarity_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:]).flatten()

    # Get the top N recommended event indices
    top_indices = similarity_scores.argsort()[::-1][:top_n]

    

    # Get event names based on top indices
    recommended_events = [event_names[i] for i in top_indices]

    return recommended_events


def json_to_list(json):
    result=json[1:-1].split(",")
    result[0]=result[0][1:-1]
    for i in range(len(result)-1):
        result[i+1]=result[i+1][2:-1]
    return result

def add_event(entryno,event):
    add_to_students_events=students_events(event=event, entryno=entryno)
    db.session.add(add_to_students_events)
    db.session.commit()



class Registration(db.Model):
    entryno = db.Column(db.String(11), primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(25), nullable=False)
    department=db.Column(db.String(25))
    photo = db.Column(db.String(200))
    interest=db.Column(db.String(300))

class events(db.Model):
    name = db.Column(db.String(40), primary_key=True)
    organiser = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.String(100), nullable=True)
    venue = db.Column(db.String(25), nullable=True)
    starttime = db.Column(db.String(25), nullable=True)
    endtime = db.Column(db.String(25), nullable=True)
    photo = db.Column(db.String(200), nullable=True)
    link = db.Column(db.String(200), nullable=True)
    tags= db.Column(db.String(300), nullable=False)

class students_events(db.Model):
    srno=db.Column(db.Integer, primary_key=True)
    event=db.Column(db.String(40))
    entryno=db.Column(db.String(11))
    feedback=db.Column(db.Integer)

class students_courses(db.Model):
    srno=db.Column(db.Integer, primary_key=True)
    course=db.Column(db.String(12))
    entryno=db.Column(db.String(11))

class course_events(db.Model):
    name = db.Column(db.String(40), primary_key=True)
    course = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    day = db.Column(db.String(100), nullable=True)
    venue = db.Column(db.String(25), nullable=True)
    starttime = db.Column(db.String(25), nullable=True)
    
@app.route('/', methods=['GET', 'POST'])
def kars_registration():
    if request.method=='POST':
        print("post")
        name = request.form['name']
        email = request.form['email']
        entryno=f"20{email[3:5]}{email[:2].upper()}{email[2]}{email[5:9]}"
        password = request.form['password']
        role=request.form.getlist('roles')
        role_json = json.dumps(role)
        if email[9:]=="@iitd.ac.in":
            global registration
            registration = Registration(entryno=entryno ,name=name,email=email,password=password,role=role_json,interest="null",photo="null",department="null")
            global otp
            otp=f"{random.randint(1,9)}{random.randint(1,9)}{random.randint(1,9)}{random.randint(1,9)}{random.randint(1,9)}{random.randint(1,9)}"
            my_email = os.getenv("email")
            receiver_email = email
            subject = "opt for registration in kars website"
            message = otp
            text = f"Subject: {subject}\n\n{message}"
            server = smtplib.SMTP ("smtp.gmail.com", 587)
            server.starttls()
            app_pass=os.getenv("app_pass")
            server.login(my_email, app_pass)
            server.sendmail(my_email, receiver_email, text)
            return redirect("/verify-otp")
        else:
            return "enter valid email"
    return render_template('index.html')


@app.route('/verify-otp', methods=['GET', 'POST'])
def opt_check():
        if request.method=='POST':
            if otp==request.form['digit1']+request.form['digit2']+request.form['digit3']+request.form['digit4']+request.form['digit5']+request.form['digit6']:
                db.session.add(registration)
                db.session.commit()
                return  redirect("/")
            else:
                "try again"
        return render_template('otp.html')


@app.route('/login', methods=['GET', 'POST'])
def kars_login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        Role=request.form['role']
        global user
        user = Registration.query.filter_by(email=email, password=password).first()
        if Role in json_to_list(user.role):
            # Login successful
            return redirect(f'/{Role}')
        else:
            # Invalid credentials
            return "Invalid email or password", 401

@app.route('/student/feedback/<string:event>', methods=['GET', 'POST'])
def event_feedback_fun(event):
    event__name=event
    print(event__name)
    if request.method=='POST':
        print(event__name)
        event___feedback = request.form[f'{event__name}-feedback']
        event__feedback = students_events.query.filter_by(event=event__name,entryno=user.entryno).first()
        event__feedback.feedback = event___feedback
        db.session.add(event__feedback)
        db.session.commit()
    return redirect("/student")
       
@app.route('/student')
def kars_student():
    # Get logged-in student's email from the session
    student_email = user.email
    # Get the student's registered events
    selected_event_names = [event.event for event in students_events.query.filter(students_events.entryno==user.entryno).all()]
    current_time = datetime.now()
    student_events = events.query.filter(events.name.in_(selected_event_names),db.func.datetime(events.date, events.starttime) >= current_time).all()
    from sqlalchemy import func
    feedback_remaining = (students_events.query.filter(students_events.entryno==user.entryno ,students_events.feedback == 0).all())
    for i in feedback_remaining:
        j=events.query.filter(events.name==i.event).first()
        if datetime.strptime(f"{j.date} {j.starttime}", "%Y-%m-%d %H:%M") >= current_time:
            feedback_remaining.remove(i)
    print(feedback_remaining)
    print(student_events)
    # feedback_remaining=students_events.query.filter(feedback==0, db.func.datetime(events.date, events.starttime) <= current_time).all()
    return render_template(
        'student_protal.html',  
        student_events=student_events,
        feedback_remaining=feedback_remaining,
        recommend_events=recommend_event(5)
    )


@app.route('/club')
def kars_club():
    return render_template('club.html')


@app.route('/department')
def kars_department():
    return render_template('department.html')


@app.route('/student/profile', methods=['GET', 'POST'])
def kars_profile():
    if request.method=='POST':
        interests = request.form.getlist('interests')
        if interests:
            interests_json = json.dumps(interests)
            user.interest=interests_json
        photo = request.files['photo']
        if photo:
            filename = secure_filename(photo.filename)  # Sanitize the filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(file_path)
            user.photo=filename
        department = request.form['department']
        if department:
            user.department=department
        db.session.add(user)
        db.session.commit()
    return render_template('profile.html',User=user,interests=json_to_list(user.interest))


@app.route('/student/event')
def kars_event():
    current_time = datetime.now()
    selected_event_names = [event.event for event in students_events.query.all()]
    Events =events.query.filter(events.name.notin_(selected_event_names),db.func.datetime(events.date, events.starttime) >= current_time).all()
    return render_template('event.html',Events=Events)

@app.route('/add_event/<string:name>')
def add_event(name):
    add_to_students_events=students_events(event=name, entryno=user.entryno, feedback=0)
    db.session.add(add_to_students_events)
    db.session.commit()
    return redirect("/student/event")


@app.route('/student/academic_schedule')
def kars_schedule():
    courseList = [selected_course.course for selected_course in students_courses.query.filter(students_courses.entryno==user.entryno).all()]
    return render_template('academic_schedule.html',courseList=courseList)

@app.route('/student/academic_schedule/remove_course/<string:name>')
def remove_event(name):
    course_remove=students_courses.query.filter(students_courses.entryno==user.entryno,students_courses.course==name).first()
    db.session.delete(course_remove)
    db.session.commit()
    return redirect("/student/academic_schedule")


@app.route('/student/academic_schedule/add_course', methods=['GET', 'POST'])
def add_course():
    name = request.form['courseName']
    add_to_students_courses=students_courses(course=name, entryno=user.entryno)
    db.session.add(add_to_students_courses)
    db.session.commit()
    return redirect('/student/academic_schedule')

@app.route('/fest', methods=['GET', 'POST'])
def kars_fest():
    if request.method=='POST':
        print("post2")
        name = request.form['eventName']
        organiser = request.form['organiser']
        description = request.form['description']
        date = request.form['date']
        starttime = request.form['starttime']
        endtime = request.form['endtime']
        venue = request.form['venue']
        link= request.form["link"]
        tags=request.form["tags"]
        photo = request.files["photo"]
        filename = secure_filename(photo.filename)  # Sanitize the filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(file_path)
        event = events(name = name, photo =filename, organiser = organiser, description = description, date = date, venue = venue, starttime= starttime, endtime= endtime ,link=link,tags=tags)
        db.session.add(event)
        db.session.commit()
    return render_template('fest.html')

  
@app.route('/course-coordinator')
def kars_course():
    return render_template('course.html')


if __name__ == "__main__":
    app.run(debug=True)