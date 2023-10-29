import sys
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect,get_object_or_404
from student.models import Student
from django.contrib import messages
from driver.models import Driver
from shared_app.models import Complaint,fee_inc,delay_req
from fees.models import Fee

def owner_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            print('Login successful', file=sys.stdout)
            
            # Store user information in the session
            request.session['user_id'] = user.id
            request.session['user_role'] = 'Owner'
            
            return redirect('owner_portal')
        else:
            print('Login failed', file=sys.stdout)
    
    return render(request, 'login.html', {'user_role': 'Owner'})

def owner_portal(request):
    # Retrieve user information from the session
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')

    if user_id is None or user_role != 'Owner':
        # If user is not authenticated, redirect to login page or handle accordingly
        return redirect('owner_login')
    student = Student.objects.filter(status=False)
    student_count = student.count()
    
    driver = Driver.objects.filter(status=False)
    driver_count = driver.count()

    all_count=student_count + driver_count

    complaints = Complaint.objects.filter(owner_approval='Pending')
    complaint_count = complaints.count()

    Fee_inc_req = fee_inc.objects.filter(owner_approval='Pending')
    Fee_inc_req_count = Fee_inc_req.count()
    
    delay_req1 = delay_req.objects.filter(owner_approval='Pending')
    delay_req_count = delay_req1.count()
    
    fees = Fee.objects.all()

    # Calculate the total owner's fee by summing the Owner_fee field
    total_owner_fee = sum(fee.Owner_fee for fee in fees)

    all_req= complaint_count + Fee_inc_req_count + delay_req_count
    context = {'student_count': student_count,'complaint_count':complaint_count,'driver_count': driver_count,'all_count': all_count,'Fee_inc_req_count':Fee_inc_req_count,'delay_req_count':delay_req_count,'all_req':all_req,'total_owner_fee':total_owner_fee}
    return render(request, 'owner_portal.html', context)


def view_students(request):
    # Retrieve students with status=False from the database
    students = Student.objects.all()
    # Pass the filtered students to a template for rendering
    return render(request, 'view_students.html', {'students': students, 'user_role': 'Student'})

def view_drivers(request):
    # Retrieve students with status=False from the database
    drivers = Driver.objects.all()
    # Pass the filtered students to a template for rendering
    return render(request, 'view_students.html', {'drivers': drivers, 'user_role': 'Driver'})

def approve_students(request):
    # Retrieve students with status=False from the database
    students = Student.objects.filter(status=False)
    context={'students': students,'user_role':'Student'}
    # Pass the filtered students to a template for rendering
    return render(request, 'approve_students.html', context)

def approve_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        get_driver_id=get_driver(student.area)
        if get_driver_id is not None:
            student.driver_id = get_driver_id
            student.status = True
            student.save()
            send_response_to_student_email(student.id,'approve')
            messages.success(request, 'Student approved successfully!')
        else:
            send_response_to_student_email(student.id,'reject')
            student.delete()
            messages.error(request, 'Van is Full Of Capacity')
            messages.success(request, 'Student rejected and record deleted successfully!')
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
    return redirect('view_students')  # Redirect to the view_students page

def get_driver(student_area):
    try:
        driver = Driver.objects.get(area=student_area)
        total_students = Student.objects.filter(driver_id=driver.id).count()
        if driver.van_capacity == total_students:
            # There is enough capacity in the van
            return None
    except Driver.DoesNotExist:
        return driver

# Function to reject a student
def reject_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        send_response_to_student_email(student.id,'reject')
        student.delete()  # Delete the student record
        messages.success(request, 'Student rejected and record deleted successfully!')
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
    return redirect('view_students')  # Redirect to the view_students page

def approve_drivers(request):
    # Retrieve students with status=False from the database
    drivers = Driver.objects.filter(status=False)
    context={'drivers': drivers,'user_role': 'Driver'}
    # Pass the filtered students to a template for rendering
    return render(request, 'approve_students.html', context)

def approve_driver(request, driver_id):
    try:
        driver = Driver.objects.get(id=driver_id)
        driver.status = True  # Set the status to True (approved)
        driver.save()
        send_response_to_driver_email(driver.id,'accept')
        messages.success(request, 'Driver approved successfully!')
    except Driver.DoesNotExist:
        messages.error(request, 'driver not found.')
    return redirect('view_drivers')  # Redirect to the view_students page

# Function to reject a student
def reject_driver(request, driver_id):
    try:
        driver = Driver.objects.get(id=driver_id)
        driver.delete()
        send_response_to_driver_email(driver.id,'reject')
        messages.success(request, 'Driver request rejected and record deleted successfully!')
    except Driver.DoesNotExist:
        messages.error(request, 'Driver not found.')
    return redirect('view_drivers')  # Redirect to the view_students page

def all_complaints(request):
    complaints = Complaint.objects.filter(owner_approval="Pending")  # Retrieve all complaints
    context = {'complaints': complaints,'user_role':'complain'}
    return render(request, 'view_complain.html', context)

def update_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    action = request.GET.get('action')
    print(action)
    if request.method == 'POST':
        driver_comment = request.POST.get('driver_comment')
        if driver_comment:
            complaint.owner_comments = driver_comment
            if action == 'accept':
                complaint.owner_approval = 'Approved'
                complain_email_student(complaint.id,'approve')
                complaint.save()
                send_complain_acknowledge_email_to_driver(complaint.id)
                messages.success(request, 'Comment submitted successfully.')
            elif action == 'reject':
                complaint.owner_approval = 'Rejected'
                complaint.save()
                complain_email_student(complaint.id,'reject')
                messages.success(request, 'Comment submitted successfully.')
        else:
            messages.error(request, 'Please enter a comment.')
    messages.error(request, 'Request entertained successfully.')
    return redirect('all_complaints')

def all_Fee_inc_req(request):
    fee_req = fee_inc.objects.filter(owner_approval="Pending")  # Retrieve all complaints
    context = {'fee_increase': fee_req,'user_role':'fee_increase'}
    return render(request, 'view_complain.html', context)

def response_fee_req(request, fee_id):
    fee_request = get_object_or_404(fee_inc, id=fee_id)
    driver = get_object_or_404(Driver, id=fee_request.Driver_id.id)
    action = request.GET.get('action')
    if request.method == 'POST':
        owner_comment = request.POST.get('owner_comment')
        modified_amount = request.POST.get('modified_amount')
        if owner_comment:
            fee_request.owner_comments = owner_comment
            if action == 'accept':
                fee_request.amount = modified_amount
                fee_request.owner_approval = 'Approved'
                driver.fee_amount=driver.fee_amount+int(modified_amount)
                driver.save()
                fee_request.save()
                messages.success(request, 'Request handled successfully.')
                send_fee_request_approval_email_to_driver(fee_request.id,'accept')
                send_fee_request_approval_email_to_students(fee_request.id)
            elif action == 'reject':
                fee_request.owner_approval = 'Rejected'
                fee_request.save()
                messages.success(request, 'Request handled successfully.')
                send_fee_request_approval_email_to_driver(fee_request.id,'reject')
        else:
            messages.error(request, 'Please enter a comment.')
    messages.error(request, 'Request entertained successfully.')
    return redirect('Fee_inc_req')

def all_delay_req(request):
    delay_requ = delay_req.objects.filter(owner_approval="Pending")  # Retrieve all complaints
    context = {'delays': delay_requ,'user_role':'delay'}
    return render(request, 'view_complain.html', context)

def response_delay_req(request, delay_id):
    delay_request = get_object_or_404(delay_req, id=delay_id)
    action = request.GET.get('action')
    if request.method == 'POST':
        owner_comment = request.POST.get('owner_comment')
        if owner_comment:
            delay_request.owner_comments = owner_comment
            if action == 'accept':
                delay_request.owner_approval = 'Approved'
                delay_request.save()
                messages.success(request, 'Comment submitted successfully.')
                send_delay_request_email_to_driver(delay_request.id,'accept')
            elif action == 'reject':
                delay_request.owner_approval = 'Rejected'
                delay_request.save()
                messages.success(request, 'Comment submitted successfully.')
                send_delay_request_email_to_driver(delay_request.id,'reject')
                send_delay_request_email_to_student(delay_request.id)
            delay_request.save()
            messages.success(request, 'Comment submitted successfully.')
        else:
            messages.error(request, 'Please enter a comment.')
    messages.error(request, 'Request entertained successfully.')
    return redirect('delay_req')


def send_response_to_student_email(student_id,status):
    student = get_object_or_404(Student, id=student_id)
    if status=='approve':
        subject = f'Registration Request Accepted - School Van Management System'
    elif status=='reject':
        subject = f'Registration Request Rejected - School Van Management System'
    if status=='approve' :
        message = f"Dear {student.first_name},\n\n" \
                f"We hope this email finds you well. We are pleased to inform you that your registration request for the School Van Management System has been successfully accepted. Additionally, we have assigned a dedicated driver for your convenience.\n\n" \
                f"Here are the details you need to access your portal:\n\n" \
                f"Username: {student.username}\n" \
                f"Password: {student.password}\n\n" \
                f"With these credentials, you can now log in to your portal and manage your school van transportation details. Here are a few things you can do through your portal:\n\n" \
                f"- Update Information: Make changes to your transportation information such as your pick-up/drop-off location or contact details. Please note that any changes should be made well in advance.\n" \
                f"- Receive Alerts: Stay informed about any important updates or announcements related to school transportation.\n\n" \
                f"We are committed to providing a safe and efficient transportation service for our students, and we believe that this system will help streamline the process and enhance your overall experience.\n\n" \
                f"If you encounter any issues or have questions about using the portal, please do not hesitate to contact our transportation department at [Transportation Department Contact Information].\n\n" \
                f"We look forward to ensuring a smooth and comfortable transportation experience for you throughout the school year. Thank you for choosing our school's van service.\n\n" \
                f"Best regards,\n\n" \
                f"Osama Khursheed\n" \
                f"Van Owner"
    elif status=='reject':
        message=f"Dear {student.first_name},\n\n" \
              f"I hope this message finds you well. We regret to inform you that your registration request for the School Van Management System has not been approved at this time. After careful consideration, we are unable to accommodate your request for the following reason:\n\n" \
              f"We cannot process your request now; please try again later.\n\n" \
              f"We understand that reliable transportation is crucial for students, and we sincerely apologize for any inconvenience this may cause. Please note that our decision is based on factors beyond our control, and we have made every effort to prioritize the safety and efficiency of our transportation service.\n\n" \
              f"If you have any questions or require further clarification regarding this decision, please do not hesitate to reach out to our transportation department at [Transportation Department Contact Information]. They will be happy to assist you and provide any necessary information.\n\n" \
              f"We appreciate your understanding in this matter and hope that alternative transportation arrangements can be made to ensure your convenience and safety during the upcoming school year.\n\n" \
              f"Thank you for considering our school's van service, and we wish you a successful and enjoyable academic year.\n\n" \
              f"Best regards,\n\n" \
              f"Osama Khursheed\n" \
              f"Van Owner"
    from_email = 'uitvanowner@gmail.com'
    recipient_list = [student.email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.send()
        print('Email sent successfully')
    except Exception as e:
        print(f'Email sending failed: {str(e)}')


def send_response_to_driver_email(driver_id,status):
    driver = get_object_or_404(Driver, id=driver_id)
    if status=='approve':
        subject = f'Registration Request Accepted - School Van Management System'
    elif status=='reject':
        subject = f'Registration Request Rejected - School Van Management System'
    if status=='approve' :
        message = f"Dear {driver.first_name},\n\n" \
                f"We hope this email finds you well. We are pleased to inform you that your registration request for the School Van Management System has been successfully accepted. Additionally, we have assigned a dedicated driver for your convenience.\n\n" \
                f"Here are the details you need to access your portal:\n\n" \
                f"Username: {driver.username}\n" \
                f"Password: {driver.password}\n\n" \
                f"With these credentials, you can now log in to your portal and manage your school van transportation details. Here are a few things you can do through your portal:\n\n" \
                f"- Update Information: Make changes to your transportation information such as your pick-up/drop-off location or contact details. Please note that any changes should be made well in advance.\n" \
                f"- Receive Alerts: Stay informed about any important updates or announcements related to school transportation.\n\n" \
                f"We are committed to providing a safe and efficient transportation service for our students, and we believe that this system will help streamline the process and enhance your overall experience.\n\n" \
                f"If you encounter any issues or have questions about using the portal, please do not hesitate to contact our transportation department at [Transportation Department Contact Information].\n\n" \
                f"We look forward to ensuring a smooth and comfortable transportation experience for you throughout the school year. Thank you for choosing our school's van service.\n\n" \
                f"Best regards,\n\n" \
                f"Osama Khursheed\n" \
                f"Van Owner"
    elif status=='reject':
        message=f"Dear {driver.first_name},\n\n" \
              f"I hope this message finds you well. We regret to inform you that your registration request for the School Van Management System has not been approved at this time. After careful consideration, we are unable to accommodate your request for the following reason:\n\n" \
              f"We cannot process your request now; please try again later.\n\n" \
              f"We understand that reliable transportation is crucial for students, and we sincerely apologize for any inconvenience this may cause. Please note that our decision is based on factors beyond our control, and we have made every effort to prioritize the safety and efficiency of our transportation service.\n\n" \
              f"If you have any questions or require further clarification regarding this decision, please do not hesitate to reach out to our transportation department at [Transportation Department Contact Information]. They will be happy to assist you and provide any necessary information.\n\n" \
              f"We appreciate your understanding in this matter and hope that alternative transportation arrangements can be made to ensure your convenience and safety during the upcoming school year.\n\n" \
              f"Thank you for considering our school's van service, and we wish you a successful and enjoyable academic year.\n\n" \
              f"Best regards,\n\n" \
              f"Osama Khursheed\n" \
              f"Van Owner"
    from_email = 'uitvanowner@gmail.com'
    recipient_list = [driver.email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.send()
        print('Email sent successfully')
    except Exception as e:
        print(f'Email sending failed: {str(e)}')

def complain_email_student(complain_id, status):
    complaint = get_object_or_404(Complaint, id=complain_id)
    student = get_object_or_404(Student, id=complaint.student_id.id)

    if status == 'approve':
        subject = 'Acknowledgment of Your Complaint Regarding Your Van Driver'
        message = f"Dear {student.first_name},\n\n" \
                  f"I hope this message finds you well. We wanted to acknowledge the complaint you recently submitted regarding your school van driver's behavior and actions. Your feedback is important to us, as it helps us maintain a safe and respectful environment for all students utilizing our transportation services.\n\n" \
                  f"We take such complaints seriously and have initiated an investigation into the matter to ensure a thorough understanding of the situation. Please rest assured that we are committed to addressing and resolving the issues you've raised promptly.\n\n" \
                  f"Our top priority is the safety and well-being of our students, and we will take appropriate action based on the findings of our investigation. We understand that a positive and comfortable transportation experience is essential for your academic journey, and we will do our utmost to ensure that this is achieved.\n\n" \
                  f"Van Owner Comments: {complaint.owner_comments}\n\n" \
                  f"If you have any further information or details you would like to share about the incident or any additional concerns, please do not hesitate to contact us. Your input is invaluable in helping us improve our transportation services.\n\n" \
                  f"We appreciate your patience and understanding as we work to resolve this matter. We are dedicated to providing the best possible service to our students and will keep you updated on the progress of the investigation.\n\n" \
                  f"Thank you for bringing this issue to our attention. We are committed to ensuring a safe and pleasant transportation experience for all our students.\n\n" \
                  f"Best regards,\n\n" \
                  f"Osama Khursheed\n" \
                  f"Van Owner"
    elif status == 'reject':
        subject = 'Complaint Request Rejected - School Van System'
        message = f"Dear {student.first_name},\n\n" \
                  f"I hope this message finds you well. We wanted to follow up regarding your recent complaint about your school van driver. After a thorough investigation and careful consideration of the matter, we regret to inform you that we are unable to proceed with your request at this time.\n\n" \
                  f"Our investigation did not reveal any substantial evidence to support the allegations made in your complaint. We understand that it can be frustrating when issues arise during your transportation, but it is essential for us to make fair and informed decisions based on the available information.\n\n" \
                  f"Owner Comments: {complaint.owner_comments}\n\n" \
                  f"Please know that we take all complaints seriously and investigate them thoroughly to ensure the safety and well-being of our students. While we were unable to substantiate your specific concerns in this instance, please do not hesitate to reach out if you encounter any further issues or have additional feedback in the future.\n\n" \
                  f"We appreciate your understanding and cooperation in this matter. Your feedback is valuable as we strive to provide the best possible transportation services for our students.\n\n" \
                  f"Thank you for your continued support, and we hope you have a successful and enjoyable academic year.\n\n" \
                  f"Best regards,\n\n" \
                  f"Osama Khursheed\n" \
                  f"Van Owner"

    from_email = 'uitvanowner@gmail.com'
    recipient_list = [student.email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.send()
        print('Email sent successfully')
    except Exception as e:
        print(f'Email sending failed: {str(e)}')

def send_complain_acknowledge_email_to_driver(complain_id):
    complaint = get_object_or_404(Complaint, id=complain_id)
    driver = get_object_or_404(Driver, id=complaint.driver_id.id)

    subject = 'Acknowledgment of Complaint Regarding Your Van'
    message = f"Dear {driver.first_name},\n\n" \
              f"I hope this message finds you well. We wanted to acknowledge the complaint submitted regarding your school van. Your passengers' feedback is essential to us, as it helps us maintain a safe and respectful environment for all students utilizing our transportation services.\n\n" \
              f"We take such complaints seriously and have initiated an investigation into the matter to ensure a thorough understanding of the situation. Please rest assured that we are committed to addressing and resolving the issues raised promptly.\n\n" \
              f"Complaint Content: {complaint.complain_content}\n\n" \
              f"Van Owner Comments: {complaint.owner_comments}\n\n" \
              f"If you have any further information or details you would like to share about the incident or any additional concerns, please do not hesitate to contact us. Your input is invaluable in helping us improve our transportation services.\n\n" \
              f"We appreciate your patience and understanding as we work to resolve this matter. We are dedicated to providing the best possible service to our students and will keep you updated on the progress of the investigation.\n\n" \
              f"Thank you for your continued support, and we hope you have a successful and enjoyable experience as a school van driver.\n\n" \
              f"Best regards,\n\n" \
              f"Osama Khursheed\n" \
              f"Van Owner"

    from_email = 'uitvanowner@gmail.com'
    recipient_list = [driver.email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.send()
        print('Email sent successfully to driver')
    except Exception as e:
        print(f'Email sending failed to driver: {str(e)}')

def send_fee_request_approval_email_to_students(fee_id):
    fee_request = get_object_or_404(fee_inc, id=fee_id)
    students = Student.objects.filter(driver_id=fee_request.Driver_id.id)
    for student in students:
        subject = 'Fee Increase Notice - School Van System'
        message = f"Dear {student.first_name},\n\n" \
                f"We hope this email finds you well. We are writing to inform you that your fee increase request for the school van transportation service has been approved. Starting from next month, your monthly fee amount will be increased to ${fee_request.amount}.\n\n" \
                f"Please ensure that the updated fee amount is paid accordingly. If you have any questions or concerns regarding this fee increase or any other matters related to the school van service, please feel free to contact us.\n\n" \
                f"Request Reason: {fee_request.reason}\n\n" \
                f"Owner Comments: {fee_request.owner_comments}\n\n" \
                f"Thank you for choosing our school's van service, and we appreciate your continued support.\n\n" \
                f"Best regards,\n\n" \
                f"Van Owner"

        from_email = 'uitvanowner@gmail.com'
        recipient_list = [student.email]
        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.send()
            print('Fee increase email sent to student successfully')
        except Exception as e:
            print(f'Email sending failed to student: {str(e)}')


def send_fee_request_approval_email_to_driver(fee_id,status):
    fee_request = get_object_or_404(fee_inc, id=fee_id)
    driver = get_object_or_404(Driver, id=fee_request.Driver_id.id)
    if status=='accept':
        subject = 'Fee Increase Request Approval - School Van System'
        message = f"Dear {driver.first_name},\n\n" \
                f"We are pleased to inform you that your request for a fee increase has been approved. Starting from next month, your monthly fee amount will be increased to ${fee_request.amount}.\n\n" \
                f"Owner Comments: {fee_request.owner_comments}\n\n" \
                f"Thank you for your dedication and hard work as a school van driver. We believe that this fee increase reflects your commitment and contribution to our transportation service.\n\n" \
                f"Please be aware of the updated fee amount, and we appreciate your continued support.\n\n" \
                f"Best regards,\n\n" \
                f"Van Owner"
    elif status=='reject':
        subject = 'Fee Increase Request Rejected - School Van System'
        message = f"Dear {driver.first_name},\n\n" \
                f"We regret to inform you that your request for a fee increase has been rejected. After careful consideration, we are unable to accommodate your request at this time.\n\n" \
                f"We appreciate your dedication as a school van driver, and we understand that this decision may be disappointing. Please note that our decision is based on factors beyond our control, and we have made every effort to prioritize the overall service quality and affordability for our students.\n\n" \
                f"Your current fee amount will remain unchanged, and we hope you will continue to provide excellent transportation services to our students.\n\n" \
                f"Owner Comments: {fee_request.owner_comments}\n\n" \
                f"If you have any questions or require further clarification regarding this decision, please do not hesitate to reach out to our transportation department at [Transportation Department Contact Information]. They will be happy to assist you and provide any necessary information.\n\n" \
                f"We appreciate your understanding and cooperation in this matter.\n\n" \
                f"Thank you for your continued support, and we hope you have a successful and enjoyable experience as a school van driver.\n\n" \
                f"Best regards,\n\n" \
                f"Van Owner"
    from_email = 'uitvanowner@gmail.com'
    recipient_list = [driver.email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.send()
        print('Request approval email sent to driver successfully')
    except Exception as e:
        print(f'Email sending failed to driver: {str(e)}')

def send_delay_request_email_to_driver(delay_id,status):
    delay_request = get_object_or_404(delay_req, id=delay_id)
    driver = get_object_or_404(Driver, id=delay_request.Driver_id.id)
    if status=='accept':
        subject = 'Delay Request Approval - School Van System'
        message = f"Dear {driver.first_name},\n\n" \
                f"We would like to inform you that your request for a delay in your school van route has been approved. Starting from the next school day, the adjusted schedule will be implemented to accommodate the delay.\n\n" \
                f"Reason for Delay: {delay_request.reason}\n\n" \
                f"Owner Comments: {delay_request.owner_comments}\n\n" \
                f"We appreciate your understanding and cooperation in this matter. The safety and convenience of our students are of utmost importance to us, and we believe that this adjustment will contribute to a smoother transportation experience.\n\n" \
                f"If you have any further questions or concerns regarding this schedule adjustment or any other matters related to your route, please feel free to contact us.\n\n" \
                f"Thank you for your dedication to providing a reliable and safe transportation service for our students.\n\n" \
                f"Best regards,\n\n" \
                f"Van Owner"

    elif status=='reject':
        subject = 'Delay Request Rejected - School Van System'
        message = f"Dear {driver.first_name},\n\n" \
                f"We regret to inform you that your request for a fee increase has been rejected. After careful consideration, we are unable to accommodate your request at this time.\n\n" \
                f"We appreciate your dedication as a school van driver, and we understand that this decision may be disappointing. Please note that our decision is based on factors beyond our control, and we have made every effort to prioritize the overall service quality and affordability for our students.\n\n" \
                f"Your current fee amount will remain unchanged, and we hope you will continue to provide excellent transportation services to our students.\n\n" \
                f"Owner Comments: {delay_request.owner_comments}\n\n" \
                f"If you have any questions or require further clarification regarding this decision, please do not hesitate to reach out to our transportation department at [Transportation Department Contact Information]. They will be happy to assist you and provide any necessary information.\n\n" \
                f"We appreciate your understanding and cooperation in this matter.\n\n" \
                f"Thank you for your continued support, and we hope you have a successful and enjoyable experience as a school van driver.\n\n" \
                f"Best regards,\n\n" \
                f"Van Owner"
    from_email = 'uitvanowner@gmail.com'
    recipient_list = [driver.email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.send()
        print('Request approval email sent to driver successfully')
    except Exception as e:
        print(f'Email sending failed to driver: {str(e)}')



def send_delay_request_email_to_student(delay_id):
    delay_request = get_object_or_404(delay_req, id=delay_id)
    students = Student.objects.filter(driver_id=delay_request.Driver_id)
    for student in students:
        subject = 'Fee Increase Notice - School Van System'
        message = f"Dear {student.first_name},\n\n" \
                f"We hope this email finds you well. We wanted to inform you that there will be a slight delay in your school van route starting from the next school day. This adjustment has been made to ensure the safety and convenience of all students on board.\n\n" \
                f"Reason for Delay: {delay_request.reason}\n\n" \
                f"Date for Delay: {delay_request.date}\n\n" \
                f"Time Of Arrival: {delay_request.time}\n\n" \
                f"We understand the importance of punctuality and are committed to minimizing any inconvenience caused by this delay. Please make the necessary adjustments to your schedule accordingly to accommodate the updated pick-up and drop-off times.\n\n" \
                f"If you have any questions or concerns about this schedule adjustment or need further information, please feel free to contact us. Your feedback is valuable as we strive to provide the best possible transportation services.\n\n" \
                f"Thank you for choosing our school's van service, and we appreciate your understanding and cooperation during this adjustment.\n\n" \
                f"Best regards,\n\n" \
                f"Van Owner"

        from_email = 'uitvanowner@gmail.com'
        recipient_list = [student.email]
        try:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.send()
            print('Fee increase email sent to student successfully')
        except Exception as e:
            print(f'Email sending failed to student: {str(e)}')