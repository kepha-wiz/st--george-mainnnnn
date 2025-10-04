import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os

basename = os.getcwd()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + basename + '/../instance/database.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Admin/amey3/EduPool/flask/instance/database.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)  # Email for username
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    DOB =  db.Column(db.String(150))
    user_type = db.Column(db.String(50))

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer(), unique=True)
    course_name = db.Column(db.String(150))
    course_limit = db.Column(db.Integer)
    course_desc = db.Column(db.String(1000))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(150))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class QuizQuestion(db.Model):
    __tablename__ = 'quizQuestions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(150))
    option1 = db.Column(db.String(150))
    option2 = db.Column(db.String(150))
    option3 = db.Column(db.String(150))
    max_grade = db.Column(db.Integer)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    
class QuizSubmission(db.Model):
    __tablename__ = 'quizSubmissions'
    id = db.Column(db.Integer, primary_key=True)
    selected_option = db.Column(db.String(150))
    given_grade = db.Column(db.Integer)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    quizQuestion_id = db.Column(db.Integer, db.ForeignKey('quizQuestions.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Essay(db.Model):
    __tablename__ = 'essays'
    id = db.Column(db.Integer, primary_key=True)
    essay_name = db.Column(db.String(150))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class EssayQuestion(db.Model):
    __tablename__ = 'essayQuestions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(150))
    file_upload = db.Column(db.LargeBinary)
    question_type = db.Column(db.String(150))
    max_grade = db.Column(db.Integer)
    essay_id = db.Column(db.Integer, db.ForeignKey('essays.id'))

class EssaySubmission(db.Model):
    __tablename__ = 'essaySubmissions'
    id = db.Column(db.Integer, primary_key=True)
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
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def test_submit_assignment_essay(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")  # Navigate to Login Page URL

        # Query the database to retrieve a random user of type "Student"
        random_user = User.query.filter_by(user_type='student').order_by(func.random()).first()

        # Fill in the login fields with the username and password of the random user
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(random_user.username)

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(random_user.password)

        # Find the login button and click it
        login_button = driver.find_element(By.ID, "submit")
        login_button.click()  # Click the login button

        # Check if the screen changes after successful login
        self.assertNotEqual(driver.current_url, "http://127.0.0.1:5000", "Screen should change after successful login")
        
        

        # Click on the first course button under enrolled courses
        course_button = driver.find_element(By.ID, "course")
        course_button.click()

        
        # Click on the first link button under essays
        essay_link_button = driver.find_element(By.ID, "essay_link")
        essay_link_button.click()
        
        # Find the radio button for "Text Response" by its ID
        text_response_radio = driver.find_element(By.ID, "text_response")
        text_response_radio.click()  # Select "Text Response"
        
        # Find the text box for the response by its ID and enter a sample response
        text_response_input = driver.find_element(By.ID, "text_response_input")
        text_response_input.send_keys("Sample response")  # Enter the response
        
        # Click on the submit assignments button
        submit_button = driver.find_element(By.ID, "submit_quiz_button")
        submit_button.click()

        # Check the database to verify quiz submission
        #session = self.Session()

        #quiz_submission_count = EssaySubmission.query(essaySubmissions).filter_by(student_id=random_user.id).count()
        #session.close()

        #self.assertEqual(quiz_submission_count, len(quiz_questions), "Quiz submission count should match the number of questions")

        submitted_assignment = EssaySubmission.query.filter_by(answer_text="Sample response").first()
        self.assertIsNotNone(submitted_assignment, "Assignment should be posted under essays section")



  

    def tearDown(self):
        self.driver.quit()
        self.app_context.pop()

if __name__ == "__main__":
    unittest.main()