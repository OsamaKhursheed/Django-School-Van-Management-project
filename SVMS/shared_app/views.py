from django.shortcuts import render,redirect ,get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from .models import Student ,Driver,Complaint,fee_inc
from shared_app.form import ComplaintForm ,FeeIncreaseRequestForm,delayRequestForm
from django.contrib.auth import logout

# Create your views here.

def home_page(request):
    return render(request,'home.html')

def about_page(request):
    return render(request,'about_us.html')

def contact_page(request):
    return render(request,'contact_us.html')

def login_page(request):
    return render(request,'login.html')


def driver_complain(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if student.driver_id:
        driver = get_object_or_404(Driver, id=student.driver_id.id)

        if request.method == 'POST':
            form = ComplaintForm(request.POST)

            if form.is_valid():
                # Create a new complaint instance for each submission
                complaint = form.save(commit=False)
                complaint.student_id = student
                complaint.driver_id = driver.id
                complaint.day_of_complain = timezone.now().date()
                complaint.save()
                # Redirect or render a success page, or add a success message
                return redirect('driver_complain', student.id)
                messages.error(request, 'Complain Register sucessfull.')
        else:
            form = ComplaintForm()
            messages.error(request, 'Complain Register sucessfull.')

        context = {
            'student': student,
            'driver': driver,
            'complaint_form': form,
        }

        return render(request, 'report_driver.html', context)
    
def fee_increase_request(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    
    if request.method == 'POST':
        form = FeeIncreaseRequestForm(request.POST)
        if form.is_valid():
            fee_increase_request = form.save(commit=False)
            fee_increase_request.Driver_id = driver  # Set the driver association
            fee_increase_request.day_of_complain = timezone.now().date()
            fee_increase_request.save()
            messages.success(request, 'Request Register sucessfull.')
            return redirect('fee_inc_req',driver.id)  # Replace 'success_page' with your desired URL
    else:
        form = FeeIncreaseRequestForm()
    
    context = {'form': form, 'user_role': 'fee_increase', 'driver': driver}
    return render(request, 'driver_requests.html', context)


def delay_request(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    
    if request.method == 'POST':
        form = delayRequestForm(request.POST)
        if form.is_valid():
            delay_request_instance = form.save(commit=False)
            delay_request_instance.Driver_id = driver  # Set the driver association
            delay_request_instance.day_of_complain = timezone.now().date()
            delay_request_instance.save()
            messages.success(request, 'Request registered successfully.')
            return redirect('driver_portal', driver_id=driver.id)  # Correct the URL name and argument
    else:
        form = delayRequestForm()
    
    context = {'form': form, 'user_role': 'delay', 'driver': driver}
    return render(request, 'driver_requests.html', context)

def logout_view(request):
    # Perform logout actions (e.g., clear sessions or cookies)
    logout(request)
    # Redirect to the login page or any other desired URL
    return redirect('home')  # Replace 'login' with the actual URL name for your login view
