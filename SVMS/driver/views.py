from django.shortcuts import render, redirect,get_object_or_404
from .forms import DriverRegistrationForm , DriverUpdateForm
from django.utils import timezone
from django.contrib import messages
from .models import Driver 
from student.models import Student
from shared_app.models import Complaint,delay_req,fee_inc


def driver_login(request):
    if request.method == 'POST':
        # Get the username and password from the request
        username = request.POST['username']
        password = request.POST['password']
        
        # Check if a student with the provided username exists
        try:
            driver = Driver.objects.get(username=username)            
            if (password==driver.password):
                if (driver.status==False):
                    messages.error(request, 'Your Registration Request is under approval,please wait for Approval..')
                    return redirect('driver_login')
                else:
                    messages.success(request, 'Login successful!')
                    return redirect('driver_portal',driver_id=driver.id)  # Redirect to the home page after successful login
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('/')
        except Driver.DoesNotExist:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'user_role': 'Driver'})

def driver_signin(request):
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = request.POST.get('confirm_password')
            
            if password == confirm_password:
                form.save()
                messages.success(request, 'Registration successful!')
                return redirect('driver_login')
            else:
                messages.error(request, 'Password and Confirm Password do not match.')
        else:
            messages.error(request, 'Registration failed. Please check your input.')
    else:
        form = DriverRegistrationForm()
    enabled_areas, disabled_areas = get_enabled_disabled_areas()
    context = {
        'enabled_areas': enabled_areas,
        'disabled_areas': disabled_areas,
        'form':form,
    }
    return render(request, 'driver_signin.html',context)

def get_enabled_disabled_areas():
    # List of all possible areas
    all_areas = ["NORTH KARACHI", "NAZIMABAD", "LIAQATABAD", "GULSHAN", "BALDIA TOWN", "SITE AREA"]

    # Get areas already assigned to drivers
    assigned_areas = Driver.objects.values_list('area', flat=True).distinct()

    # Calculate enabled (not assigned) and disabled (assigned) areas
    enabled_areas = [area for area in all_areas if area not in assigned_areas]
    disabled_areas = [area for area in all_areas if area in assigned_areas]

    return enabled_areas, disabled_areas


def driver_portal(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    complaints = Complaint.objects.filter(driver_id=driver.id)

    delay_requests = delay_req.objects.filter(Driver_id=driver.id, owner_approval='Approved')
    fee_increase = fee_inc.objects.filter(Driver_id=driver.id, owner_approval='Approved')
    
    # Check and delete records that are one month old
    current_date = timezone.now().date()
    one_month_ago = current_date - timezone.timedelta(days=30)  # Assuming a month is 30 days
    
    # Delete fee increase records older than one month
    fee_increase_to_delete = fee_increase.filter(day_of_complain__lt=one_month_ago)
    if fee_increase_to_delete.exists():
        fee_increase_to_delete.delete()
        messages.success(request, 'Driver Fee Increase Request(s) have been deleted because they were sent over a month ago.')

    # Delete complaint records older than one month
    complaint_increase_to_delete = complaints.filter(day_of_complain__lt=one_month_ago)
    if complaint_increase_to_delete.exists():
        complaint_increase_to_delete.delete()
        messages.success(request, 'Complaint(s) have been deleted because they were sent over a month ago.')

    # Delete delay request records older than one month
    delay_to_delete = delay_requests.filter(day_of_complain__lt=one_month_ago)
    if delay_to_delete.exists():
        delay_to_delete.delete()
        messages.success(request, 'Delay Request(s) have been deleted because they were sent over a month ago.')

    fee_inc_count = fee_increase.count()
    delay_count = delay_requests.count()
    all_notifications = fee_inc_count + delay_count
    # Count the number of complaints for the driver
    complaint_count = complaints.count()
    
    context = {
        'driver': driver,
        'complaint_count': complaint_count,
        'fee_inc_count': fee_inc_count,
        'delay_count': delay_count,
        'all_notifications': all_notifications
    }
    return render(request, 'driver_portal.html', context)


def driver_view_students(request, driver_id):
    # Retrieve the driver object with the specified driver_id
    driver = get_object_or_404(Driver, id=driver_id)

    # Retrieve students associated with the specified driver
    students = Student.objects.filter(driver_id=driver_id, status=True)

    return render(request, 'driver_student_view.html', {'students': students, 'driver': driver})

def update_driver_info(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    
    if request.method == 'POST':
        form = DriverUpdateForm(request.POST, request.FILES, instance=driver)
        if form.is_valid():  # Call is_valid as a function
            form.save()
            messages.success(request, 'Driver information updated successfully.')
        else:
            # Form is not valid, handle errors
            messages.error(request, 'There were errors in the form. Please correct them.')

    else:
        form = DriverUpdateForm(instance=driver)
    return render(request, 'driver_update_info.html', {'driver': driver, 'form': form})

def driver_view_complaints(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    complaints = Complaint.objects.filter(driver_id=driver.id)  # Retrieve all complaints
    context = {'driver': driver,'complaints': complaints,'user_role': 'Driver'}
    return render(request, 'std_complain_views.html', context)

def driver_delete_complaint(request, complaint_id):
    complaints = Complaint.objects.all()
    complaint = get_object_or_404(Complaint, id=complaint_id)
    driver = get_object_or_404(driver, id=complaint.driver_id)
    context = {'driver': driver,'complaints': complaints,'user_role': 'Driver'}
    # Check if owner_approval is not 'Approved'
    if complaint.owner_approval == 'Approved':
        complaint.delete()
        messages.success(request, 'Your desired request is deleted successfully.')
        return render(request, 'std_complain_views.html', context)
    else:
        messages.error(request, 'Sorry, you cannot delete an approved request.')
        return render(request, 'std_complain_views.html', context)
    

def view_driver_requests(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    fee_increase = fee_inc.objects.filter(Driver_id=driver.id, owner_approval='Approved')
    context = {'driver': driver, 'fee_inc': fee_increase, 'user_role': 'fee_increase'}
    return render(request, 'view_driver_requests_status.html', context)

def view_delay_requests(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    delay_request = delay_req.objects.filter(Driver_id=driver.id, owner_approval='Approved')
    context = {'driver': driver, 'delay_notice':delay_request, 'user_role': 'delay'}
    return render(request, 'view_driver_requests_status.html', context)