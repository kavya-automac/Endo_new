from django.contrib import admin
from .models import (Patientreports,Patientsdetails,UserDetails,video_store)

class PatientsdetailsPro(admin.ModelAdmin):
    list_display = ('id','patient_name','age','gender','procedure','mobile','patient_email','referred')


class PatientreportPro(admin.ModelAdmin):
    list_display = ('id', 'report_file', 'date', 'time', 'get_patient_name')

    # Display patient name instead of patient_details_id in the admin
    def get_patient_name(self, obj):
        return obj.patient_details_id.patient_name
    get_patient_name.short_description = 'Patient Name'

# Customizing UserDetails admin
class UserDetailsPro(admin.ModelAdmin):
    list_display = ('get_username', 'mobile_no', 'speciality', 'otp')

    # Display the username of the linked User
    def get_username(self, obj):
        return obj.user_id.username
    get_username.short_description = 'Username'








@admin.register(video_store)
class video_store_Admin(admin.ModelAdmin):
    list_display = ['id','video_file']


# Register your models here.
admin.site.register(Patientsdetails,PatientsdetailsPro)
admin.site.register(Patientreports,PatientreportPro)
admin.site.register(UserDetails,UserDetailsPro)


