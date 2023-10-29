from django.conf import settings
from datetime import datetime
from django.utils.timezone import make_aware
from .models import Student, Fee, Driver
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from django.core.files.storage import FileSystemStorage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.core.mail import EmailMessage
from django.db.models.functions import TruncMonth
from django.db.models import DateField
from django.db.models import Count
import os

def generate_fee_records(request):
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Get all students
    students = Student.objects.filter(status=True)

    # Get today's date
    today = datetime.now().date()

    # Iterate through students
    for student in students:
        # Calculate the total fee for the current month
        total_fee = student.driver_id.fee_amount

        # Check if the student already has unpaid fee records for previous months
        unpaid_fee_records = Fee.objects.filter(
            student_id=student,
            status='Unpaid',
            month_of_fee__lt=datetime(current_year, current_month, 1)
        )
        

        # Add the unpaid fees for previous months to the total fee
        for fee_record in unpaid_fee_records:
            total_fee += fee_record.fee_amount + 500  # Add 500 for each unpaid month
        
        # Check if the student already has a fee record for the current month and year
        existing_fee_records = Fee.objects.filter(
            student_id=student,
            month_of_fee__month=current_month,
            month_of_fee__year=current_year
        )

        if not existing_fee_records:
            # Create a new fee record for the current month and year
            driver=get_object_or_404(Driver,id=student.driver_id.id)
            new_fee_record = Fee.objects.create(
                student_id=student,
                driver_id=student.driver_id,
                fee_amount=total_fee+driver.fee_amount,  # Use the calculated total fee
                month_of_fee=datetime(current_year, current_month, 1),
                date_of_fee_issue=datetime.now(),
                status='Pending',
                due_date_of_fee=datetime(current_year, current_month, 15)  # Adjust the due date as needed
            )
            generate_pdf_voucher(new_fee_record.id)
            send_fee_email(new_fee_record.id)

    # Update the status of fee records with due dates in the past to 'Unpaid'
    updated_fee_records = Fee.objects.filter(due_date_of_fee__lt=today, status='Pending')
    for fee_record in updated_fee_records:
        send_late_fee_email(fee_record.id)
    updated_fee_records.update(status='Unpaid')

    fee = Fee.objects.all()
    context = {'fees': fee}

    # Return a response with a success message
    return render(request, 'generate_fee_records.html', context)

def search_student_by_fee_id(request):
    # Get the fee_id from the GET request
    fee_id = request.GET.get('feeid')

    # Perform the search using the fee_id
    if fee_id:
        fees = Fee.objects.filter(id=fee_id)
    else:
        fees = Fee.objects.all()

    # Render the search results in a template
    return render(request, 'generate_fee_records.html', {'fees': fees})

def view_fee_history(request,student_id):
    students=get_object_or_404(Student,id=student_id)
    fee_history = Fee.objects.filter(student_id=students.id).order_by('-month_of_fee')

    # Calculate total fees paid and total fees balance
    total_fees_paid = sum([fee.fee_amount for fee in fee_history if fee.status == 'Paid'])
    total_fees_balance = sum([fee.fee_amount for fee in fee_history if fee.status == 'Pending'])

    context = {
        'student':students,
        'fees': fee_history,
        'total_fees_paid': total_fees_paid,
        'total_fees_balance': total_fees_balance,
    }
    return render(request, 'student_fee_view.html', context)

def driver_fee_records(request, driver_id, selected_month=None):
    driver = get_object_or_404(Driver, id=driver_id)
    fee_history = Fee.objects.filter(driver_id=driver.id).order_by('-month_of_fee')

    # Calculate total fees paid and total fees balance
    total_fees_paid = sum([fee.fee_amount for fee in fee_history if fee.status == 'Paid'])
    total_fees_balance = sum([fee.fee_amount for fee in fee_history if fee.status == 'Pending'])

    # Calculate total owner's fee cuts
    total_owner_fee_cuts = sum([fee.Owner_fee for fee in fee_history])
    total_driver_fee = total_fees_paid - total_owner_fee_cuts

    # Extract distinct months from the fee history using TruncMonth
    available_months = (
        Fee.objects
        .filter(driver_id=driver.id)
        .annotate(month=TruncMonth('month_of_fee', output_field=DateField()))
        .values('month')
        .annotate(count=Count('month'))
        .order_by('-month')
    )

    # Convert the selected_month string into a date object
    selected_date = None
    if selected_month:
        try:
            selected_date = datetime.strptime(selected_month, '%Y-%m-%d').date()
        except ValueError:
            print('erwr')

    # Filter fee records for the selected month if a valid date is provided
    if selected_date:
        fee_history = fee_history.filter(month_of_fee__month=selected_date.month, month_of_fee__year=selected_date.year)
        total_fees_paid = sum([fee.fee_amount for fee in fee_history if fee.status == 'Paid'])
        total_fees_balance = sum([fee.fee_amount for fee in fee_history if fee.status == 'Pending'])
        total_owner_fee_cuts = sum([fee.Owner_fee for fee in fee_history])
        total_driver_fee = total_fees_paid - total_owner_fee_cuts
    print("Selected Date:", selected_date)

    context = {
        'driver': driver,
        'fees': fee_history,
        'total_fees_paid': total_fees_paid,
        'total_fees_balance': total_fees_balance,
        'total_owner_fee_cuts': total_owner_fee_cuts,
        'available_months': available_months,
        'total_driver_fee': total_driver_fee,
        'selected_month': selected_month,  # Pass the selected month to the template
    }

    return render(request, 'Driver_fee_view.html', context)

def send_late_fee_email(fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    student = get_object_or_404(Student, id=fee.student_id.id)
    driver = get_object_or_404(Driver, id=fee.driver_id.id)

    subject = f'Fee Voucher for {fee.month_of_fee} for {student.first_name}'
    message = f"Dear {student.father_name},\n\n" \
                f"I hope this email finds you in good health and high spirits. This email is to inform you that the fee voucher for your child, {student.first_name}, for the month of {fee.month_of_fee}, has been generated and is attached to this email.\n\n" \
                "Please find the attached voucher for your reference. The voucher contains all the necessary details regarding the fee amount, due date, and driver details.\n\n" \
                "We have noticed that the fee for the previous month remains unpaid. To ensure the continued provision of our van service, we kindly request you to settle the outstanding fee at your earliest convenience.\n\n" \
                "If you have any queries or concerns, please feel free to contact us. We would be happy to assist you.\n\n" \
                "Thank you for your cooperation and support.\n\n" \
                "Best regards,\n\n" \
                "Van Owner"

    from_email = 'uitvanowner@gmail.com'  # Replace with your email
    recipient_list = [student.email]

    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.send()
        print('Email sent successfully')
    except FileNotFoundError:
        print(f'PDF file not found for fee ID: {fee_id}')

def update_fee_status(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)

    # Check if the request method is POST
    if request.method == 'POST':
        # Update the fee status to 'Paid'
        fee.status = 'Paid'
        fee.date_of_submission=datetime.now().date()
        fee.Owner_fee= (fee.fee_amount * 0.20)
        fee.save()

        # Update the status to 'Paid' for all other unpaid fees of the same student
        student = get_object_or_404(Student, id=fee.student_id.id)
        unpaid_fees = Fee.objects.filter(student_id=student, status='Unpaid')
        for unpaid_fee in unpaid_fees:
            unpaid_fee.status = 'Paid'
            unpaid_fee.date_of_submission=datetime.now().date()
            unpaid_fee.save()
        # Redirect back to the fee records page
        return redirect('generate_fee')

    return render(request, 'update_fee_status.html', {'fees': fee})

def generate_pdf_voucher(fee_id):
    # Fetch the fee record
    fee = get_object_or_404(Fee, id=fee_id)
    student = get_object_or_404(Student, id=fee.student_id.id)
    driver = get_object_or_404(Driver, id=fee.driver_id.id)

    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{fee_id}.pdf"'

    # Create a PDF document
    pdf_file = canvas.Canvas(response, pagesize=(5.5*inch, 8.5*inch))

    # Set font size and style for title
    pdf_file.setFont("Helvetica-Bold", 25)
    pdf_file.drawCentredString(2.75*inch, 8*inch, "Van Fee Voucher")

    # Set font size and style for table headers
    pdf_file.setFont("Helvetica-Bold", 20)

    # Define table headers
    table_headers = ["Field", "Value"]

    # Draw table headers
    x, y = 0.5 * inch, 6.8 * inch
    col_width = 3 * inch
    for header in table_headers:
        pdf_file.drawString(x, y, header)
        x += col_width

    # Set font size and style for table data
    pdf_file.setFont("Helvetica", 13)

    # Define table data
    table_data = [
        ["Fee ID", fee.id],
        ["Student ID", fee.student_id.id],
        ["Student Name", f"{student.first_name} {student.last_name}"],
        ["Father Name", student.father_name],
        ["Driver ID", fee.driver_id.id],
        ["Driver Name", f"{driver.first_name} {driver.last_name}"],
        ["Date of Fee Issue", fee.date_of_fee_issue],  # You should update this field name
        ["", "------------------"],  # Add comma to separate items
        ["Due Date", fee.due_date_of_fee],  # You should update this field name
        ["", "------------------"],  # Add comma to separate items
        ["Fee Amount", fee.fee_amount],
        ["", "------------------"],  # Add comma to separate items
    ]

    # Draw table data
    x, y = 0.6 * inch, 6 * inch
    for data_row in table_data:
        pdf_file.drawString(x, y, data_row[0])
        pdf_file.drawString(x + col_width, y, str(data_row[1]))
        y -= 0.45 * inch

    # Draw stamp section
    pdf_file.rect(3.5 * inch, 0.5 * inch, 1.5 * inch, 0.3 * inch)
    pdf_file.line(3.5 * inch, 0.8 * inch, 5 * inch, 0.8 * inch)
    pdf_file.line(3.5 * inch, 0.8 * inch, 3.5 * inch, 0.5 * inch)
    pdf_file.line(5 * inch, 0.8 * inch, 5 * inch, 0.5 * inch)
    pdf_file.line(3.5 * inch, 0.5 * inch, 5 * inch, 0.5 * inch)
    pdf_file.drawCentredString(4.25 * inch, 0.65 * inch, "stamp here")

    pdf_file.save()
    fs = FileSystemStorage(location='media/vouchers')
    with fs.open(f'{fee_id}.pdf', 'wb') as pdf_file:
        pdf_file.write(response.content)
    return response
def send_fee_email(fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    student = get_object_or_404(Student, id=fee.student_id.id)
    driver = get_object_or_404(Driver, id=fee.driver_id.id)

    subject = f'Fee Voucher for {fee.month_of_fee} for {student.first_name}'
    message = f"Dear {student.father_name},\n\n" \
              f"I hope this email finds you in good health and high spirits. This email is to inform you that the fee voucher for your child, {student.first_name}, for the month of {fee.month_of_fee}, has been generated and is attached to this email.\n\n" \
              "Please find the attached voucher for your reference. The voucher contains all the necessary details regarding the fee amount, due date, and driver details.\n\n" \
              "If you have any queries or concerns, please feel free to contact us. We would be happy to assist you.\n\n" \
              "Thank you for your cooperation and support.\n\n" \
              "Best regards,\n\n" \
              "Van Owner"

    from_email = 'uitvanowner@gmail.com'  # Replace with your email
    recipient_list = [student.email]

    try:
        fs = FileSystemStorage(location='media/vouchers')
        with fs.open(f'{fee_id}.pdf', 'rb') as pdf_file:
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.attach(f'{fee_id}.pdf', pdf_file.read(), 'application/pdf')
            email.send()
            print('Email sent successfully')
    except FileNotFoundError:
        print(f'PDF file not found for fee ID: {fee_id}')