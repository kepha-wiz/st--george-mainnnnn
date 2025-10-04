import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.sql import func
import flask
import os

import sys
sys.path.append('../')
#sys.path.append('C:/Users/Admin/amey3/EduPool/flask/')
#from . import db


from flask_login import UserMixin
from sqlalchemy.sql import func

basename = os.getcwd()


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Admin/amey3/EduPool/flask/instance/database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + basename + '/../instance/database.db'
db = SQLAlchemy(app)


 

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique = True) #email for username
    password=db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    DOB =  db.Column(db.String(150))
    user_type = db.Column(db.String(50))
    
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer(), unique = True)
    course_name = db.Column(db.String(150))
    course_limit = db.Column(db.Integer)
    course_desc = db.Column(db.String(1000))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
class Request(db.Model, UserMixin):
    __tablename__ = 'requests'
    id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    
class Enrollment(db.Model, UserMixin):
    __tablename__ = 'enrollments'
    id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class Quiz(db.Model, UserMixin):
    __tablename__ = 'quizzes'
    id=db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(150))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class QuizQuestion(db.Model, UserMixin):
    __tablename__ = 'quizQuestions'
    id=db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(150))
    option1 = db.Column(db.String(150))
    option2 = db.Column(db.String(150))
    option3 = db.Column(db.String(150))
    max_grade = db.Column(db.Integer)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    
class QuizSubmission(db.Model, UserMixin):
    __tablename__ = 'quizSubmissions'
    id=db.Column(db.Integer, primary_key=True)
    selected_option = db.Column(db.String(150))
    given_grade = db.Column(db.Integer)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    quizQuestion_id = db.Column(db.Integer, db.ForeignKey('quizQuestions.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Essay(db.Model, UserMixin):
    __tablename__ = 'essays'
    id=db.Column(db.Integer, primary_key=True)
    essay_name = db.Column(db.String(150))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class EssayQuestion(db.Model, UserMixin):
    __tablename__ = 'essayQuestions'
    id=db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(150))
    file_upload = db.Column(db.LargeBinary)
    question_type = db.Column(db.String(150))
    max_grade = db.Column(db.Integer)
    essay_id = db.Column(db.Integer, db.ForeignKey('essays.id'))

class EssaySubmission(db.Model, UserMixin):
    __tablename__ = 'essaySubmissions'
    id=db.Column(db.Integer, primary_key=True)
    answer_text = db.Column(db.String(150))
    answer_file = db.Column(db.LargeBinary)
    answer_type = db.Column(db.String(150))
    given_grade = db.Column(db.Integer)
    essay_id = db.Column(db.Integer, db.ForeignKey('essays.id'))
    essayQuestion_id = db.Column(db.Integer, db.ForeignKey('essayQuestions.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Discussion(db.Model):
    __tablename__ = 'discussions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    content = db.Column(db.String(1000))
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Reply(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    date_posted = db.Column(db.DateTime(timezone=True), default=func.now())
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()  # Initialize WebDriver

        # Set up Flask application context
        self.app_context = app.app_context()
        self.app_context.push()

        # Create the database tables
        db.create_all()

    def test_valid_username_password(self): # Test scenario: Valid username and password login
        driver = self.driver
        driver.get("http://127.0.0.1:5000")  # Navigate to Login Page URL

        # Enter a valid username and password combination
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys("fgfd@gdg.com")

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("aaaa")

        # Find the login button and click it
        login_button = driver.find_element(By.ID, "submit")
        login_button.click()  # Click the login button

        # Check if the screen changes
        # Replace "expected_url_after_login" with the actual URL after successful login
        self.assertNotEqual(driver.current_url, "http://127.0.0.1:5000", "Screen should change after successful login")

        # Check if the username and password combination exists in the database
        user = User.query.filter_by(username="fgfd@gdg.com", password="aaaa").first()
        self.assertIsNotNone(user, "Username and password combination should exist in the database")

    def test_invalid_username_password(self): # Test scenario: Invalid username and password login
        # Test scenario: Invalid username and password
        
        driver = self.driver
        driver.get("http://127.0.0.1:5000")  # Navigate to Login Page URL

        # Enter invalid username and password
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys("invalid_username@gmail.com")

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("invalid_password")

        # Find and click the login button
        login_button = driver.find_element(By.ID, "submit")
        login_button.click()

        # Check if the screen remains on the login page
        self.assertEqual(driver.current_url, "http://127.0.0.1:5000/login?next=%2F", "Screen should remain on login page")
	  # Check if the username and password combination does not exist in the database
        user = User.query.filter_by(username="invalid_username@gmail.com", password="invalid_password").first()
        self.assertIsNone(user, "Username and password combination should not exist in the database")


    def tearDown(self):
        self.driver.quit()  # Clean up after the test

        # Drop all tables after the test
        #db.drop_all()

        # Pop Flask application context
        self.app_context.pop()

if __name__ == "__main__":
    unittest.main()

