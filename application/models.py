from .database import db

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    type = db.Column(db.String(), default="student")
    is_active = db.Column(db.Boolean(), default=True)
    company_details = db.relationship("Company", backref="user_account", uselist=False)
    student_details = db.relationship("Student", backref="user_account", uselist=False)

class Company(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    company_name = db.Column(db.String(), nullable=False)
    industry = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    hr_contact = db.Column(db.String(), nullable=False)
    website = db.Column(db.String(), nullable=True)
    description = db.Column(db.String(), nullable=True)
    approval_status = db.Column(db.String(), default="pending")
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    drives = db.relationship("PlacementDrive", backref="company_details")

class Student(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.String(), nullable=False)
    roll_number = db.Column(db.String(), unique=True, nullable=False)
    branch = db.Column(db.String(), nullable=False)
    cgpa = db.Column(db.Float(), nullable=False)
    graduation_year = db.Column(db.Integer(), nullable=False)
    phone = db.Column(db.String(), nullable=False)
    skills = db.Column(db.String(), nullable=True)
    resume_link = db.Column(db.String(), nullable=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    applications = db.relationship("Application", backref="student_details")

class PlacementDrive(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    job_title = db.Column(db.String(), nullable=False)
    job_description = db.Column(db.String(), nullable=False)
    eligibility_criteria = db.Column(db.String(), nullable=False)
    required_skills = db.Column(db.String(), nullable=True)
    experience = db.Column(db.String(), nullable=True)
    required_cgpa = db.Column(db.Float(), nullable=False)
    eligible_branches = db.Column(db.String(), nullable=False)
    ctc = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    drive_date = db.Column(db.String(), nullable=False)
    application_deadline = db.Column(db.String(), nullable=False)
    max_positions = db.Column(db.Integer(), nullable=False)
    approval_status = db.Column(db.String(), default="pending")
    drive_status = db.Column(db.String(), default="upcoming")
    company_id = db.Column(db.Integer(), db.ForeignKey("company.id"), nullable=False)
    applications = db.relationship("Application", backref="drive_details")

class Application(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    application_date = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), default="applied")
    student_id = db.Column(db.Integer(), db.ForeignKey("student.id"), nullable=False)
    drive_id = db.Column(db.Integer(), db.ForeignKey("placement_drive.id"), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    message = db.Column(db.String(), nullable=False)
    notification_type = db.Column(db.String(), nullable=False)  # shortlisted, selected, rejected
    is_read = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.String(), nullable=False)
    student_id = db.Column(db.Integer(), db.ForeignKey("student.id"), nullable=False)
    application_id = db.Column(db.Integer(), db.ForeignKey("application.id"), nullable=False)
    student = db.relationship("Student", backref="notifications")
    application = db.relationship("Application", backref="notifications")
