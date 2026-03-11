from flask import Flask, render_template, redirect, request
from flask import current_app as app
from .models import *
from datetime import datetime

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/logout")
def logout():
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        this_user = User.query.filter_by(username=username).first()
        if this_user:
            if this_user.password == pwd:
                if not this_user.is_active:
                    return render_template("blacklisted.html")
                if this_user.type == "admin":
                    return redirect("/admin")
                elif this_user.type == "company":
                    company = Company.query.filter_by(user_id=this_user.id).first()
                    if company.approval_status == "approved":
                        return redirect(f"/company/{this_user.id}")
                    else:
                        return render_template("pending_approval.html")
                else:
                    return redirect(f"/student/{this_user.id}")
            else:
                return render_template("incorrect_p.html")
        else:
            return render_template("not_exist.html")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_type = request.form.get("user_type")
        return redirect(f"/register/{user_type}")
    
    return render_template("register.html")

@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        pwd = request.form.get("pwd")
        full_name = request.form.get("full_name")
        roll_number = request.form.get("roll_number")
        branch = request.form.get("branch")
        cgpa = request.form.get("cgpa")
        graduation_year = request.form.get("graduation_year")
        phone = request.form.get("phone")
        skills = request.form.get("skills")
        resume_link = request.form.get("resume_link")
        
        user_name = User.query.filter_by(username=username).first()
        user_email = User.query.filter_by(email=email).first()
        roll_check = Student.query.filter_by(roll_number=roll_number).first()
        
        if user_name or user_email or roll_check:
            return render_template("already.html")
        else:
            new_user = User(username=username, email=email, password=pwd, type="student")
            db.session.add(new_user)
            db.session.commit()
            
            new_student = Student(
                full_name=full_name,
                roll_number=roll_number,
                branch=branch,
                cgpa=float(cgpa),
                graduation_year=int(graduation_year),
                phone=phone,
                skills=skills,
                resume_link=resume_link,
                user_id=new_user.id
            )
            db.session.add(new_student)
            db.session.commit()
            return redirect("/login")
        
    return render_template("register_student.html")

@app.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        pwd = request.form.get("pwd")
        company_name = request.form.get("company_name")
        industry = request.form.get("industry")
        location = request.form.get("location")
        hr_contact = request.form.get("hr_contact")
        website = request.form.get("website")
        description = request.form.get("description")
        
        user_name = User.query.filter_by(username=username).first()
        user_email = User.query.filter_by(email=email).first()
        
        if user_name or user_email:
            return render_template("already.html")
        else:
            new_user = User(username=username, email=email, password=pwd, type="company")
            db.session.add(new_user)
            db.session.commit()
            
            new_company = Company(
                company_name=company_name,
                industry=industry,
                location=location,
                hr_contact=hr_contact,
                website=website,
                description=description,
                user_id=new_user.id
            )
            db.session.add(new_company)
            db.session.commit()
            return redirect("/login")
        
    return render_template("register_company.html")

@app.route("/admin")
def admin_dash():
    this_user = User.query.filter_by(type="admin").first()
    pending_companies = Company.query.filter_by(approval_status="pending").all()
    all_companies = Company.query.all()
    pending_drives = PlacementDrive.query.filter_by(approval_status="pending").all()
    all_drives = PlacementDrive.query.all()
    all_students = Student.query.all()
    all_applications = Application.query.all()
    
    # Historical placement data
    closed_drives = PlacementDrive.query.filter_by(drive_status="closed").all()
    selected_applications = Application.query.filter_by(status="selected").all()
    placed_student_ids = set([app.student_id for app in selected_applications])
    
    return render_template("admin_dash.html", 
                         this_user=this_user,
                         pending_companies=pending_companies,
                         all_companies=all_companies,
                         pending_drives=pending_drives,
                         all_drives=all_drives,
                         all_students=all_students,
                         all_applications=all_applications,
                         closed_drives=closed_drives,
                         selected_applications=selected_applications,
                         placed_count=len(placed_student_ids))

@app.route("/admin/approve_company/<int:company_id>")
def approve_company(company_id):
    company = Company.query.get(company_id)
    company.approval_status = "approved"
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/reject_company/<int:company_id>")
def reject_company(company_id):
    company = Company.query.get(company_id)
    company.approval_status = "rejected"
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/approve_drive/<int:drive_id>")
def approve_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    drive.approval_status = "approved"
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/reject_drive/<int:drive_id>")
def reject_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    drive.approval_status = "rejected"
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/delete_student/<int:student_id>")
def delete_student(student_id):
    student = Student.query.get(student_id)
    user = User.query.get(student.user_id)
    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/delete_company/<int:company_id>")
def delete_company(company_id):
    company = Company.query.get(company_id)
    user = User.query.get(company.user_id)
    db.session.delete(company)
    db.session.delete(user)
    db.session.commit()
    return redirect("/admin")

@app.route("/view_company/<int:company_id>")
def view_company_profile(company_id):
    company = Company.query.get(company_id)
    drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    return render_template("view_company_profile.html", company=company, drives=drives)

@app.route("/admin/search")
def admin_search():
    search_query = request.args.get("search")
    search_type = request.args.get("search_type")
    results = []
    
    if search_type == "student":
        results = Student.query.filter(
            (Student.full_name.like(f"%{search_query}%")) | 
            (Student.roll_number.like(f"%{search_query}%")) |
            (Student.phone.like(f"%{search_query}%"))
        ).all()
    elif search_type == "company":
        results = Company.query.filter(
            (Company.company_name.like(f"%{search_query}%")) |
            (Company.industry.like(f"%{search_query}%"))
        ).all()
    
    return render_template("search_results.html", results=results, search_type=search_type)

@app.route("/admin/blacklist_student/<int:student_id>")
def blacklist_student(student_id):
    student = Student.query.get(student_id)
    user = User.query.get(student.user_id)
    user.is_active = False
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/activate_student/<int:student_id>")
def activate_student(student_id):
    student = Student.query.get(student_id)
    user = User.query.get(student.user_id)
    user.is_active = True
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/blacklist_company/<int:company_id>")
def blacklist_company(company_id):
    company = Company.query.get(company_id)
    user = User.query.get(company.user_id)
    user.is_active = False
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/activate_company/<int:company_id>")
def activate_company(company_id):
    company = Company.query.get(company_id)
    user = User.query.get(company.user_id)
    user.is_active = True
    db.session.commit()
    return redirect("/admin")

@app.route("/company/<int:user_id>")
def company_dash(user_id):
    this_user = User.query.get(user_id)
    company = Company.query.filter_by(user_id=user_id).first()
    upcoming_drives = PlacementDrive.query.filter_by(
        company_id=company.id,
        drive_status="upcoming",
        approval_status="approved"
    ).all()
    closed_drives = PlacementDrive.query.filter_by(
        company_id=company.id,
        drive_status="closed"
    ).all()
    pending_drives = PlacementDrive.query.filter_by(
        company_id=company.id,
        approval_status="pending"
    ).all()
    rejected_drives = PlacementDrive.query.filter_by(
        company_id=company.id,
        approval_status="rejected"
    ).all()
    
    return render_template("company_dash.html",
                         this_user=this_user,
                         company=company,
                         upcoming_drives=upcoming_drives,
                         closed_drives=closed_drives,
                         pending_drives=pending_drives,
                         rejected_drives=rejected_drives)

@app.route("/company/create_drive/<int:user_id>", methods=["GET", "POST"])
def create_drive(user_id):
    company = Company.query.filter_by(user_id=user_id).first()
    
    # Only approved companies can create drives
    if company.approval_status != "approved":
        return render_template("pending_approval.html")
    
    if request.method == "POST":
        job_title = request.form.get("job_title")
        job_description = request.form.get("job_description")
        eligibility_criteria = request.form.get("eligibility_criteria")
        required_skills = request.form.get("required_skills")
        experience = request.form.get("experience")
        required_cgpa = request.form.get("required_cgpa")
        eligible_branches = request.form.get("eligible_branches")
        ctc = request.form.get("ctc")
        location = request.form.get("location")
        drive_date = request.form.get("drive_date")
        application_deadline = request.form.get("application_deadline")
        max_positions = request.form.get("max_positions")
        
        new_drive = PlacementDrive(
            job_title=job_title,
            job_description=job_description,
            eligibility_criteria=eligibility_criteria,
            required_skills=required_skills,
            experience=experience,
            required_cgpa=float(required_cgpa),
            eligible_branches=eligible_branches,
            ctc=ctc,
            location=location,
            drive_date=drive_date,
            application_deadline=application_deadline,
            max_positions=int(max_positions),
            company_id=company.id
        )
        db.session.add(new_drive)
        db.session.commit()
        return redirect(f"/company/{user_id}")
    
    return render_template("create_drive.html", user_id=user_id)

@app.route("/company/view_applications/<int:drive_id>")
def view_applications(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template("view_applications.html", drive=drive, applications=applications)

@app.route("/company/update_application/<int:app_id>", methods=["GET", "POST"])
def update_application(app_id):
    application = Application.query.get(app_id)
    drive = application.drive_details
    source = request.args.get("source", "")
    
    # Count current selected students for this drive
    selected_count = Application.query.filter_by(
        drive_id=drive.id,
        status="selected"
    ).count()
    positions_remaining = drive.max_positions - selected_count
    
    if request.method == "POST":
        new_status = request.form.get("status")
        old_status = application.status
        source = request.form.get("source", "")
        
        # Check if trying to select and positions are full
        if new_status == "selected" and old_status != "selected":
            if selected_count >= drive.max_positions:
                return render_template("update_application.html", 
                                     application=application, 
                                     positions_remaining=0,
                                     source=source,
                                     error=f"Cannot select more candidates. All {drive.max_positions} positions are filled.")
        
        application.status = new_status
        db.session.commit()
        
        # Create notification if status changed
        if new_status != old_status and new_status in ["shortlisted", "interview", "selected", "rejected"]:
            status_messages = {
                "shortlisted": f"Congratulations! You have been shortlisted for {application.drive_details.job_title} at {application.drive_details.company_details.company_name}",
                "interview": f"You have been scheduled for an interview for {application.drive_details.job_title} at {application.drive_details.company_details.company_name}",
                "selected": f"Congratulations! You have been PLACED for {application.drive_details.job_title} at {application.drive_details.company_details.company_name}!",
                "rejected": f"We regret to inform you that your application for {application.drive_details.job_title} at {application.drive_details.company_details.company_name} was not successful."
            }
            notification = Notification(
                message=status_messages[new_status],
                notification_type=new_status,
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
                student_id=application.student_id,
                application_id=application.id
            )
            db.session.add(notification)
            db.session.commit()
        
        # Redirect based on source
        if source in ["shortlisted", "interview"]:
            return redirect(f"/company/view_shortlisted/{application.drive_id}")
        else:
            return redirect(f"/company/view_applications/{application.drive_id}")
    
    return render_template("update_application.html", application=application, positions_remaining=positions_remaining, source=source)

@app.route("/company/close_drive/<int:drive_id>")
def close_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    drive.drive_status = "closed"
    db.session.commit()
    company = Company.query.get(drive.company_id)
    return redirect(f"/company/{company.user_id}")

@app.route("/company/edit_profile/<int:user_id>", methods=["GET", "POST"])
def edit_company_profile(user_id):
    company = Company.query.filter_by(user_id=user_id).first()
    if request.method == "POST":
        company.company_name = request.form.get("company_name")
        company.industry = request.form.get("industry")
        company.location = request.form.get("location")
        company.hr_contact = request.form.get("hr_contact")
        company.website = request.form.get("website")
        company.description = request.form.get("description")
        db.session.commit()
        return redirect(f"/company/{user_id}")
    return render_template("edit_company_profile.html", company=company, user_id=user_id)

@app.route("/company/edit_drive/<int:drive_id>", methods=["GET", "POST"])
def edit_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    company = Company.query.get(drive.company_id)
    if request.method == "POST":
        drive.job_title = request.form.get("job_title")
        drive.job_description = request.form.get("job_description")
        drive.eligibility_criteria = request.form.get("eligibility_criteria")
        drive.required_skills = request.form.get("required_skills")
        drive.experience = request.form.get("experience")
        drive.required_cgpa = float(request.form.get("required_cgpa"))
        drive.eligible_branches = request.form.get("eligible_branches")
        drive.ctc = request.form.get("ctc")
        drive.location = request.form.get("location")
        drive.drive_date = request.form.get("drive_date")
        drive.application_deadline = request.form.get("application_deadline")
        drive.max_positions = int(request.form.get("max_positions"))
        # If drive was rejected, resubmit for approval
        if drive.approval_status == "rejected":
            drive.approval_status = "pending"
        db.session.commit()
        return redirect(f"/company/{company.user_id}")
    return render_template("edit_drive.html", drive=drive, user_id=company.user_id)

@app.route("/company/reopen_drive/<int:drive_id>")
def reopen_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    drive.drive_status = "upcoming"
    db.session.commit()
    company = Company.query.get(drive.company_id)
    return redirect(f"/company/{company.user_id}")

@app.route("/company/view_shortlisted/<int:drive_id>")
def view_shortlisted(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    shortlisted_apps = Application.query.filter_by(drive_id=drive_id, status="shortlisted").all()
    interview_apps = Application.query.filter_by(drive_id=drive_id, status="interview").all()
    selected_apps = Application.query.filter_by(drive_id=drive_id, status="selected").all()
    return render_template("view_shortlisted.html", drive=drive, shortlisted_apps=shortlisted_apps, interview_apps=interview_apps, selected_apps=selected_apps)

@app.route("/company/delete_drive/<int:drive_id>")
def delete_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    company = Company.query.get(drive.company_id)
    user_id = company.user_id
    # Delete associated applications first
    Application.query.filter_by(drive_id=drive_id).delete()
    db.session.delete(drive)
    db.session.commit()
    return redirect(f"/company/{user_id}")

@app.route("/student/<int:user_id>")
def student_dash(user_id):
    this_user = User.query.get(user_id)
    student = Student.query.filter_by(user_id=user_id).first()
    
    approved_drives = PlacementDrive.query.filter_by(
        approval_status="approved",
        drive_status="upcoming"
    ).all()
    
    # Build drive info with eligibility status
    all_drives_info = []
    eligible_drives = []
    for drive in approved_drives:
        branches = [b.strip() for b in drive.eligible_branches.split(",")]
        already_applied = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        
        # Determine eligibility
        is_branch_eligible = student.branch in branches
        is_cgpa_eligible = student.cgpa >= drive.required_cgpa
        is_eligible = is_branch_eligible and is_cgpa_eligible and not already_applied
        
        # Build reason if not eligible
        reason = ""
        if already_applied:
            reason = "Already Applied"
        elif not is_branch_eligible and not is_cgpa_eligible:
            reason = f"Branch ({student.branch}) & CGPA ({student.cgpa}) not eligible"
        elif not is_branch_eligible:
            reason = f"Branch ({student.branch}) not in {drive.eligible_branches}"
        elif not is_cgpa_eligible:
            reason = f"CGPA ({student.cgpa}) below required ({drive.required_cgpa})"
        
        drive_info = {
            'drive': drive,
            'is_eligible': is_eligible,
            'already_applied': already_applied is not None,
            'reason': reason
        }
        all_drives_info.append(drive_info)
        
        if is_eligible:
            eligible_drives.append(drive)
    
    # Current applications (upcoming drives)
    all_applications = Application.query.filter_by(student_id=student.id).all()
    my_applications = [app for app in all_applications if app.drive_details.drive_status == "upcoming"]
    
    # Placement history (closed drives)
    placement_history = [app for app in all_applications if app.drive_details.drive_status == "closed"]
    
    # Get notifications
    notifications = Notification.query.filter_by(student_id=student.id).order_by(Notification.id.desc()).limit(10).all()
    unread_count = Notification.query.filter_by(student_id=student.id, is_read=False).count()
    
    return render_template("student_dash.html",
                         this_user=this_user,
                         student=student,
                         eligible_drives=eligible_drives,
                         all_drives_info=all_drives_info,
                         my_applications=my_applications,
                         placement_history=placement_history,
                         notifications=notifications,
                         unread_count=unread_count)

@app.route("/student/apply/<int:student_id>/<int:drive_id>")
def apply_drive(student_id, drive_id):
    student = Student.query.get(student_id)
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    existing_application = Application.query.filter_by(
        student_id=student_id,
        drive_id=drive_id
    ).first()
    
    if not existing_application:
        new_application = Application(
            application_date=current_date,
            student_id=student_id,
            drive_id=drive_id
        )
        db.session.add(new_application)
        db.session.commit()
    
    return redirect(f"/student/{student.user_id}")

@app.route("/student/update_profile/<int:user_id>", methods=["GET", "POST"])
def update_profile(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if request.method == "POST":
        student.full_name = request.form.get("full_name")
        student.phone = request.form.get("phone")
        student.cgpa = float(request.form.get("cgpa"))
        student.skills = request.form.get("skills")
        student.resume_link = request.form.get("resume_link")
        db.session.commit()
        return redirect(f"/student/{user_id}")
    
    return render_template("update_profile.html", student=student, user_id=user_id)

@app.route("/student/view_drive/<int:drive_id>")
def view_drive(drive_id):
    drive = PlacementDrive.query.get(drive_id)
    return render_template("view_drive.html", drive=drive)

@app.route("/student/search/<int:user_id>")
def student_search(user_id):
    this_user = User.query.get(user_id)
    student = Student.query.filter_by(user_id=user_id).first()
    search_query = request.args.get("search", "")
    
    # Get all approved upcoming drives
    approved_drives = PlacementDrive.query.filter_by(
        approval_status="approved",
        drive_status="upcoming"
    ).all()
    
    # Filter by search query (company, position, or skills)
    results = []
    for drive in approved_drives:
        # Check eligibility
        branches = [b.strip() for b in drive.eligible_branches.split(",")]
        if student.branch not in branches or student.cgpa < drive.required_cgpa:
            continue
        
        # Check if already applied
        already_applied = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        if already_applied:
            continue
        
        # Search matching
        if search_query:
            search_lower = search_query.lower()
            if (search_lower in drive.job_title.lower() or
                search_lower in drive.company_details.company_name.lower() or
                (drive.required_skills and search_lower in drive.required_skills.lower())):
                results.append(drive)
        else:
            results.append(drive)
    
    return render_template("student_search_results.html", 
                         this_user=this_user,
                         student=student,
                         results=results, 
                         search_query=search_query)

@app.route("/student/mark_notification_read/<int:notification_id>/<int:user_id>")
def mark_notification_read(notification_id, user_id):
    notification = Notification.query.get(notification_id)
    if notification:
        notification.is_read = True
        db.session.commit()
    return redirect(f"/student/{user_id}")

@app.route("/student/mark_all_read/<int:user_id>")
def mark_all_notifications_read(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    Notification.query.filter_by(student_id=student.id, is_read=False).update({Notification.is_read: True})
    db.session.commit()
    return redirect(f"/student/{user_id}")

@app.route("/view_student/<int:student_id>")
def view_student_profile(student_id):
    student = Student.query.get(student_id)
    applications = Application.query.filter_by(student_id=student_id).all()
    return render_template("view_student_profile.html", student=student, applications=applications)
