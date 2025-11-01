from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('api/get-csrf-token/', views.some_safe_api_view, name='get_csrf_token'),
    path('login/', login_view, name='login_view'),
    path('register/', register_view, name='register_view'),
    path('forgot/', email_verification, name='email_verification'),
    path('verify/', validate_otp, name='validate_otp'),
    path('update/', update_password, name='update_password'),
    path('all/', patient_list, name='patient_list'),
    path('logout/', logout_view, name='logout_view'),
    path('add-patient/', add_patient, name='add_patient'),  # Update to match with hyphen
    path('delete_patients/multiple-delete/', delete_patients, name='delete_patients'),
    path('patient_report_file/', patient_report_file,name='patient_report_file'),
    path('delete_reports/multiple-delete/', delete_patient_records,name='delete_patient_records'),
    # path('patient_report_file/<int:patient_id>', patient_report_file,name='patient_report_file'),
    path('patient_save_report/', patient_save_report,name='patient_save_report'),
    path('update_record/<str:patient_id>/', update_record,name='save_record'),
    path('save_record/', save_record,name='save_record'),
    path('view_record/', view_record, name='view_record'),
    path('send-email/', send_email, name='send-email'),
    path('video_feed/', video_feed, name='video_feed'),
    path('user_details_update/', user_details_update, name='user_details_update'),
    path('patient_details_update/', patient_details_update, name='patient_details_update'),
    # path('user_details_update/', user_details_update, name='user_details_update'),
    # path('patient_details_update/', patient_details_update, name='patient_details_update'),
    path('internet_test/', internet_test, name='internet_test'),
    path('wifi_test_rpi/', wifi_test_rpi, name='wifi_test_rpi'),

]
