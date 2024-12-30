from django.urls import path
from . import views
from .views import *

urlpatterns = [
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
    # path('patient_report_file/<int:patient_id>', patient_report_file,name='patient_report_file'),
    path('patient_save_report/', patient_save_report,name='patient_save_report'),
    path('worker/', WorkersListAPIView.as_view(),name='WorkersListAPIView'),
    path('send-email/', send_email, name='send-email'),

]
