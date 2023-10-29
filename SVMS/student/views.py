from .forms import StudentRegistrationForm ,StudentUpdateForm
from django.shortcuts import render, redirect,get_object_or_404
from django.utils import timezone
from django.contrib import messages
from .models import Student 
from driver.models import Driver 
from shared_app.models import Complaint , fee_inc ,delay_req
from django.urls import reverse

def student_login(request):
    if request.method == 'POST':
        # Get the username and password from the request
        username = request.POST['username']
        password = request.POST['password']
        
        # Check if a student with the provided username exists
        try:
            student = Student.objects.get(username=username)
            if (password==student.password):
                if (student.status==False):
                    messages.error(request, 'Your Registration Request is under approval,please wait for Approval..')
                    return redirect('student_login')
                else:
                    messages.success(request, 'Login successful!')
                    return redirect('student_portal', student_id=student.id)
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('/')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html', {'user_role': 'Student'})


def student_signin(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = request.POST.get('confirm_password')
            
            if password == confirm_password:
                form.save()
                messages.success(request, 'Registration successful!')
                return redirect('student_login')
            else:
                messages.error(request, 'Password and Confirm Password do not match.')
        else:
            messages.error(request, 'Registration failed. Please check your input.')
    else:
        form = StudentRegistrationForm()
    enabled_areas, disabled_areas = get_enabled_disabled_areas()
    context = {
        'enabled_areas': enabled_areas,
        'disabled_areas': disabled_areas,
        'form':form,
    }
    return render(request, 'student_signin.html',context)
    
def get_enabled_disabled_areas():
    # List of all possible areas
    all_areas = ["NORTH KARACHI", "NAZIMABAD", "LIAQATABAD", "GULSHAN", "BALDIA TOWN", "SITE AREA"]

    # Get areas already assigned to drivers
    assigned_areas = Driver.objects.values_list('area', flat=True).distinct()

    # Calculate enabled (not assigned) and disabled (assigned) areas
    enabled_areas = [area for area in all_areas if area in assigned_areas]
    disabled_areas = [area for area in all_areas if area not in assigned_areas]

    return enabled_areas, disabled_areas


def student_portal(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    complaints = Complaint.objects.filter(student_id=student_id)

    delay_requests = delay_req.objects.filter(Driver_id=student.driver_id, owner_approval='Approved')
    complaint_del = Complaint.objects.filter(student_id=student_id,owner_approval='Approved')
    fee_increase = fee_inc.objects.filter(Driver_id=student.driver_id, owner_approval='Approved')
    
    # Check and delete fee increase records that are one month old
    current_date = timezone.now().date()
    one_month_ago = current_date - timezone.timedelta(days=30)  # Assuming a month is 30 days
    
    # Delete records older than one month
    complaint_increase_to_delete = complaint_del.filter(day_of_complain__lt=one_month_ago)
    fee_increase_to_delete = fee_increase.filter(day_of_complain__lt=one_month_ago)
    delay_to_delete = delay_requests.filter(day_of_complain__lt=one_month_ago)
    if fee_increase_to_delete.exists():
        messages.success(request, 'Driver Fee Increase Request has been deleted because it was sent over a month ago.')
        fee_increase_to_delete.delete()
    elif complaint_increase_to_delete.exists():
        messages.success(request, 'Driver Fee Increase Request has been deleted because it was sent over a month ago.')
        complaint_increase_to_delete.delete()
    elif delay_to_delete.exists():
        messages.success(request, 'Driver Fee Increase Request has been deleted because it was sent over a month ago.')
        delay_to_delete.delete()
    # Count the number of complaints for the student
    complaint_count = complaints.count()
    fee_inc_count = fee_increase.count()
    delay_count = delay_requests.count()
    all_notifiactions= fee_inc_count+delay_count
    context = {'student': student, 'complaints': complaints, 'complaint_count': complaint_count,'fee_inc_count':fee_inc_count,'delay_count':delay_count,'all_notice':all_notifiactions}
    return render(request, 'student_portal.html',context)

def view_driver(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    driver_id = student.driver_id.id
    driver = get_object_or_404(Driver, id=driver_id)
    print(driver.last_name)
    return render(request, 'view_driver.html', {'student': student, 'driver': driver})


def update_information(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentUpdateForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Information updated successfully.')
            # Redirect to the student portal or any other appropriate page
            return redirect(reverse('student_portal', args=[student.id]))
        else:
            messages.error(request, 'Update info failed. Please check your input.')
    else:
        form = StudentUpdateForm(instance=student)

    return render(request, 'update_info.html', {'student': student, 'form': form})


def complaints_status(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    complaints = Complaint.objects.all()  # Retrieve all complaints
    context = {'student': student,'complaints': complaints,'user_role': 'Student'}
    return render(request, 'std_complain_views.html', context)

def delete_complaint(request, complaint_id):
    complaints = Complaint.objects.all()
    complaint = get_object_or_404(Complaint, id=complaint_id)
    student = get_object_or_404(Student, id=complaint.student_id.id)
    context = {'student': student,'complaints': complaints,'user_role': 'Student'}
    # Check if owner_approval is not 'Approved'
    if complaint.owner_approval != 'Approved':
        complaint.delete()
        messages.success(request, 'Your desired request is deleted successfully.')
        return render(request, 'std_complain_views.html', context)
    else:
        messages.error(request, 'Sorry, you cannot delete an approved request.')
        return render(request, 'std_complain_views.html', context)

def view_driver_requests(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    driver_fee = get_object_or_404(Driver, id=student.driver_id.id)
    fee_increase = fee_inc.objects.filter(Driver_id=student.driver_id, owner_approval='Approved')
    
    context = {'student': student, 'driver': driver_fee, 'fee_inc': fee_increase, 'user_role': 'fee_increase'}
    return render(request, 'student_driver_notifications.html', context)

def view_delay_requests(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    delay_request = delay_req.objects.filter(Driver_id=student.driver_id, owner_approval='Approved')
    context = {'student': student, 'delay_notice':delay_request, 'user_role': 'delay'}
    return render(request, 'student_driver_notifications.html', context)
