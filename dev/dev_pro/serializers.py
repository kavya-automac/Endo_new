# from django.contrib.gis.serializers.geojson import Serializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Patientreports,Patientsdetails,UserDetails
import random

from rest_framework import serializers
from .models import *

class PatientsdetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patientsdetails
        fields = '__all__'


class newPatientsdetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewPatientsdetails
        fields = '__all__'

class PatientreportsSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient_details_id.patient_name')
    class Meta:
        model = Patientreports
        fields = ['id', 'patient_name', 'report_file', 'date', 'time']



class newPatientreportsSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient_details_id.patient_name')
    class Meta:
        model = NewPatientreports
        fields = ['id', 'patient_name', 'report_file', 'date', 'time']



class Patient_save_report(serializers.ModelSerializer):
    class Meta:
        model = Patientreports
        fields = '__all__'

class newPatient_save_report(serializers.ModelSerializer):
    class Meta:
        model = NewPatientreports
        fields = '__all__'


class ReportSerializers(serializers.ModelSerializer):
    class Meta:
        model = Patientreports
        fields = '__all__'


class PatientDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = Patientsdetails
        fields = ['id','patient_name','age','gender','procedure','mobile','patient_email','referred','updated_at']

class newPatientDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = NewPatientsdetails
        fields = ['id','patient_name','age','gender','procedure','mobile','patient_email','referred','updated_at']

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(error_messages={'blank': 'username_field_cannot_be_blank.'},required=True)

    password = serializers.CharField(error_messages={'blank': ' password_field_cannot_be_blank.'},required=True)



    class Meta:
        model = User
        fields = ['username','password']

# class RegistrationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['firstname','speciality','username','password','mobile','email_id']







class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['mobile_no', 'speciality']  # Fields specific to UserDetails


class RegistrationSerializer(serializers.ModelSerializer):
    speciality = serializers.CharField(write_only=True)
    mobile_no = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'speciality', 'mobile_no']  # Use first_name instead of firstname
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is not returned
        }

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': 'This_username_is_already_taken.'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'This_email_was_already_existed'})
        if UserDetails.objects.filter(mobile_no=data['mobile_no']).exists():
            raise serializers.ValidationError({'mobile_no': 'This_mobile_number_is_already_registered.'})

        return data

    def create(self, validated_data):
        speciality = validated_data.pop('speciality')
        mobile_no = validated_data.pop('mobile_no')

        # Create the User instance
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', '')  # Use first_name here
        )
        user.save()

        # Create the UserDetails instance linked to the User
        details=UserDetails.objects.create(user_id=user, speciality=speciality, mobile_no=mobile_no)
        details.save()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.IntegerField(required=False, read_only=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email_does_not_exist.")
        return value

    def generate_otp(self):
        """Generate a random 6-digit OTP"""
        return random.randint(100000, 999999)


class PasswordUpdateSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({ "confirm_password": "Password_and_Confirm_Password_do_not_match."})


        return attrs


class patient_detailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patientsdetails
        fields = '__all__'