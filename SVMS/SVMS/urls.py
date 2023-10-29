from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from shared_app import views as share
from student import views as stu
from owner import views as owner
from driver import views as driver
from fees import views as fee

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', share.home_page, name='home'),
    path('about_us/', share.about_page, name='about_us'),
    path('contact_us/', share.contact_page, name='contact_us'),
    path('driver_complain/<int:student_id>/', share.driver_complain, name='driver_complain'),
    path('fee_inc_req/<int:driver_id>/', share.fee_increase_request, name='fee_inc_req'),
    path('delay_request/<int:driver_id>/', share.delay_request, name='delay_request'),
    path('logout/', share.logout_view, name='logout'),
    path('student_login/', stu.student_login, name='student_login'),
    path('Student_signin/', stu.student_signin, name='student_signin'),
    path('Student_portal/<int:student_id>/', stu.student_portal, name='student_portal'),
    path('update_information/<int:student_id>/', stu.update_information, name='update_information'),
    path('view_driver/<int:student_id>/', stu.view_driver, name='view_driver'),
    path('complain_status_Stu/<int:student_id>/', stu.complaints_status, name='complain_status_Stu'),
    path('delete_complaint/<int:complaint_id>/', stu.delete_complaint, name='delete_complaint'),
    path('view_driver_requests/<int:student_id>/', stu.view_driver_requests, name='view_driver_requests'),
    path('view_delay_requests/<int:student_id>/', stu.view_delay_requests, name='view_delay_requests'),
    path('Driver_login/', driver.driver_login, name='driver_login'),
    path('Driver_signin/', driver.driver_signin, name='driver_signin'),
    path('Driver_portal/<int:driver_id>/', driver.driver_portal, name='driver_portal'),
    path('Driver_view_students/<int:driver_id>/', driver.driver_view_students, name='driver_view_students'),
    path('update_driver_info/<int:driver_id>/', driver.update_driver_info, name='update_driver_info'),
    path('driver_view_complaint/<int:driver_id>/', driver.driver_view_complaints, name='driver_view_complaint'),
    path('driver_delete_complaint/<int:complaint_id>/', driver.driver_delete_complaint, name='driver_delete_complaint'),
    path('driver_fee_requests_view/<int:driver_id>/', driver.view_driver_requests, name='driver_fee_requests_view'),
    path('driver_delay_requests/<int:driver_id>/', driver.view_delay_requests, name='driver_delay_requests'),
    path('owner_login/', owner.owner_login, name='owner_login'),
    path('owner_portal/',owner.owner_portal,name='owner_portal'),
    path('view_students/', owner.view_students, name='view_students'),
    path('view_drivers/', owner.view_drivers, name='view_drivers'),
    path('approve_students/', owner.approve_students, name='approve_students'),
    path('approve_student/<int:student_id>/', owner.approve_student, name='approve_student'),
    path('reject_student/<int:student_id>/', owner.reject_student, name='reject_student'),
    path('approve_drivers/', owner.approve_drivers, name='approve_drivers'),
    path('approve_driver/<int:driver_id>/', owner.approve_driver, name='approve_driver'),
    path('reject_driver/<int:driver_id>/', owner.reject_driver, name='reject_driver'),
    path('Fee_inc_req/', owner.all_Fee_inc_req, name='Fee_inc_req'),
    path('response_fee_req/<int:fee_id>/', owner.response_fee_req, name='response_fee_req'),
    path('delay_req/', owner.all_delay_req, name='delay_req'),
    path('response_delay_req/<int:delay_id>/', owner.response_delay_req, name='response_delay_req'),
    path('complaints/', owner.all_complaints, name='all_complaints'),
    path('update_complaint/<int:complaint_id>/', owner.update_complaint, name='update_complaint'),
    path('generate_fee/', fee.generate_fee_records, name='generate_fee'),
    path('search_by_student_fee/', fee.search_student_by_fee_id, name='search_by_student_fee'),
    path('update_fee_status/<int:fee_id>/', fee.update_fee_status, name='update_fee_status'),
    path('view_student_fee_history/<int:student_id>/', fee.view_fee_history, name='view_student_fee_history'),
    path('driver_fee_records/<int:driver_id>/', fee.driver_fee_records, name='driver_fee_records'),
    path('driver_fee_records_month/<int:driver_id>/<str:selected_month>/', fee.driver_fee_records, name='driver_fee_records_month'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
