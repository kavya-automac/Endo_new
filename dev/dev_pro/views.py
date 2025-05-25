import datetime
import socket

import requests

from . import wifi_code
from .models import *
from .serializers import *

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.core.mail import send_mail
from rest_framework import response, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import cv2
from django.http import StreamingHttpResponse
from .models import *
import random
from dev.database_router import DatabaseRouter
from .serializers import LoginSerializer, ReportSerializers,PatientDetailSerializers,RegistrationSerializer,UserDetailsSerializer,EmailVerificationSerializer,PasswordUpdateSerializer
# from .utils import upload_file
import boto3
from botocore.exceptions import NoCredentialsError
from django.core.mail import EmailMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import shutil
import time
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Patientreports, NewPatientreports
# from .utils import DatabaseRouter, upload_file  # Assuming these utilities are defined
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import User, UserDetails  # Replace with your actual model imports


@api_view(['POST'])
def add_patient(request):
    try:
        current_user = request.user
        if current_user.is_authenticated:
            print("request", current_user.is_authenticated)

            if request.method == 'POST':

                if DatabaseRouter.db_for_write() == 'default':
                    print("if")
                    db = DatabaseRouter.db_for_write(Patientsdetails)  # Pass the model
                    patient_email = Patientsdetails.objects.using(db).filter(patient_email=request.data.get('patient_email'))
                    if patient_email.exists():
                        return JsonResponse({"status": "patient_already_exists"})
                    serializer = PatientsdetailsSerializer(data=request.data)

                elif DatabaseRouter.db_for_write() == 'fallback':
                    print('else')
                    db = DatabaseRouter.db_for_write(NewPatientsdetails)  # Pass the model
                    patient_email = NewPatientsdetails.objects.using(db).filter(patient_email=request.data.get('patient_email'))
                    if patient_email.exists():
                        return JsonResponse({"status": "patient_already_exists"})
                    serializer = newPatientsdetailsSerializer(data=request.data)
                else:
                    pass
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({"status": "patient_added_successfully"})

                else:
                    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"status": "login_required"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})



@api_view(['DELETE'])
def delete_patients(request):
    try:
        current_user = request.user
        if current_user.is_authenticated:
            print("request", current_user.is_authenticated)
            ids_to_delete = request.data.get('ids', [])  # Expects a list of ids to delete
            if not ids_to_delete:
                return JsonResponse({"status": "No_IDs_provided"}, status=status.HTTP_400_BAD_REQUEST)
            patients = Patientsdetails.objects.filter(id__in=ids_to_delete)

            if patients.exists():
                patients.delete()
                return JsonResponse({"status": "Patients_deleted_successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return JsonResponse({"status": "No_patients_found_with_the_provided_IDs"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({"status": "login_required"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


@api_view(['GET'])
# def patient_report_file(request,patient_id):
def patient_report_file(request):
    try:
        current_user = request.user
        if current_user.is_authenticated:
            print("request", current_user.is_authenticated)

            params_id=request.query_params.get("patient_id")

            if DatabaseRouter.db_for_read() == 'default':
                print("if")
                db = DatabaseRouter.db_for_read(Patientreports)  # Pass the model
                reports = Patientreports.objects.filter(patient_details_id_id=params_id)
                # print('reports',reports[0].report_file)
                print('reports',reports)
                result=[]
                for i in reports:
                    print("i",i)
                    result.append({"id":i.id,"patient_name":i.patient_details_id.patient_name,
                                   "report_file":str(i.report_file),"date":i.date,"time":i.time
                                        })

                # serializer = PatientreportsSerializer(reports, many=True)

                resultant=result
                # print("resultant",resultant)

            elif DatabaseRouter.db_for_read() =='fallback':
                print('else')
                db = DatabaseRouter.db_for_read(NewPatientreports)  # Pass the model
                reports = Patientreports.objects.filter(patient_details_id_id=params_id)
                serializer = PatientreportsSerializer(reports, many=True)
                newreports = NewPatientreports.objects.filter(patient_details_id_id=params_id)
                newserializer = newPatientreportsSerializer(newreports, many=True)
                resultant = serializer.data + newserializer.data


            else:
                pass

            if resultant:

                return JsonResponse(
                    {"patient_reports":resultant},
                    status=status.HTTP_200_OK  # Correct usage of status code
                )
            else:
                return JsonResponse(
                    {"status": "No_reports_found_for_this_patient."},
                    # {"file_not_found": "No_reports_found_for_this_patient."},
                    status=status.HTTP_404_NOT_FOUND  # Correct usage of status code
                )

        else:
            return JsonResponse({"status": "login_required"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


# @api_view(['POST'])
# def patient_save_report(request):
#     # if request.user.is_authenticated:
#     if request.method != 'POST':
#         return JsonResponse({"status": "Method not allowed"}, status=405)
#
#     # Extract required fields from the request
#     patient_details_id = request.data.get('patient_details_id')
#     pdf_file_path1 = request.data.get('pdf_file_path')
#     current_date = request.data.get('date')
#     current_time = request.data.get('time')
#
#     # Debug print statements
#     print('Received pdf_file_path:', pdf_file_path1)
#     print('Received date:', current_date)
#     print('Received time:', current_time)
#
#     # Validate required fields
#     if not all([patient_details_id, pdf_file_path1, current_date, current_time]):
#         return JsonResponse(
#             {"status": "patient_details_id, pdf_file_path, date, and time are required."},
#             status=400
#         )
#
#     # Local file path
#     file_path = os.path.join(r'C:/Users/DeLL/Downloads/', str(pdf_file_path1))
#     print('Full local file path:', file_path)
#
#     # Check if the file exists locally
#     # if not os.path.exists(file_path):
#     #     return JsonResponse({"status": "The provided file path does not exist."}, status=400)
#
#
#     # Handle S3 upload errors
#     # if "Error" in file_url:
#     #     return JsonResponse({"status": file_url}, status=500)
#
#     # Determine the database to use
#     database = DatabaseRouter.db_for_write()
#     print("Database in use:", database)
#
#     # Database write operation
#     try:
#         if database == 'default':
#             report = Patientreports.objects.create(
#                 patient_details_id_id=patient_details_id,
#                 report_file=str(file_path),
#                 date=current_date,
#                 time=current_time
#             )
#         elif database == 'fallback':
#             print("Using fallback database")
#             report = NewPatientreports.objects.create(
#                 patient_details_id_id=patient_details_id,
#                 report_file=str(file_path),
#                 date=current_date,
#                 time=current_time
#             )
#         else:
#             return JsonResponse({"status": "Database router error."}, status=500)
#
#         report.save()
#
#         return JsonResponse({
#             'status': 'report_created_successfully',
#             'file_url': str(file_path)
#         }, status=201)
#
#     except Exception as e:
#         return JsonResponse({"status": f"Database write error: {str(e)}"}, status=500)
#
#
#     # else:
#    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)


# @api_view(['POST'])
# def patient_save_report(request):
#     # if request.user.is_authenticated:
#     if request.method != 'POST':
#         return JsonResponse({"status": "Method not allowed"}, status=405)
#
#     # Extract required fields from the request
#     patient_details_id = request.data.get('patient_details_id')
#     pdf_file_path1 = request.data.get('pdf_file_path')
#     current_date = request.data.get('date')
#     current_time = request.data.get('time')
#
#     # Debug print statements
#     print('Received pdf_file_path:', pdf_file_path1)
#     print('Received date:', current_date)
#     print('Received time:', current_time)
#
#     # Validate required fields
#     if not all([patient_details_id, pdf_file_path1, current_date, current_time]):
#         return JsonResponse(
#             {"status": "patient_details_id, pdf_file_path, date, and time are required."},
#             status=400
#         )
#
#     # Local file path
#     # file_path = os.path.join(r'C:/Users/DeLL/Downloads/', str(pdf_file_path1))
#     file_path = os.path.join(r'/home/pi/Downloads/', str(pdf_file_path1))
#     print('Full local file path:', file_path)
#     print('Full local file path:', type(file_path))
#
#     # Check if the file exists locally
#     # if not os.path.exists(file_path):
#     #     return JsonResponse({"status": "The provided file path does not exist."}, status=400)
#
#     # Upload file to S3 bucket
#     # s3_object_key = f"patients_{patient_details_id}_{pdf_file_path1}"
#     # print("S3 object key:", s3_object_key)
#
#
#     # add later try and except
#
#
#
#
#     # try:
#     #     time.sleep(2)
#     #     file_url = upload_file(file_path, "samplebucketautomac2", object_name=str(pdf_file_path1), region=None)
#     #     print('File upload URL:', file_url)
#     # except Exception as e:
#     #     print("s3 bucket exception",e)
#
#
#
#     # Determine the database to use
#     database = DatabaseRouter.db_for_write()
#     print("Database in use:", database)
#
#     # Database write operation
#     try:
#         if database == 'default':
#             try:
#                 report = Patientreports.objects.create(
#                     patient_details_id_id=patient_details_id,
#                     #add later
#                     # report_file='https://samplebucketautomac2.s3.ap-south-1.amazonaws.com/'+str(file_url),
#                     report_file=file_path,
#                     date=current_date,
#                     time=current_time
#                 )
#                 report.save()
#             except Exception as e:
#                 print("default db error ------> ", e)
#             # Assuming patient_details_id is a valid ID
#             # try:
#             #     patient_details_instance = Patientsdetails.objects.get(id=patient_details_id)
#             # except Patientsdetails.DoesNotExist:
#             #     return JsonResponse({"status": "Patient not found."}, status=404)
#             #
#             # # Now create the report, passing the patient instance
#             # try:
#             #     report = Patientreports.objects.create(
#             #         patient_details_id=patient_details_instance,  # Pass the instance, not just the ID
#             #         report_file='https://samplebucketautomac2.s3.ap-south-1.amazonaws.com/' + str(file_url),
#             #         date=current_date,
#             #         time=current_time
#             #     )
#             #     report.save()
#             # except Exception as e:
#             #     print("Error saving report:", e)
#             #     return JsonResponse({"status": f"Error saving report: {str(e)}"}, status=500)
#
#
#         elif database == 'fallback':
#             print("Using fallback database")
#             print("patient_details_id",patient_details_id)
#             try:
#                 report = NewPatientreports.objects.create(
#                     patient_details_id=patient_details_id,
#                     report_file=file_path,
#                     date=current_date,
#                     time=current_time
#                 )
#                 report.save()
#             except Exception as e:
#                 print("/////////////////////////////////",e)
#             print("report fLLBck",report)
#         else:
#             return JsonResponse({"status": "Database router error."}, status=500)
#
#
#
#         return JsonResponse({
#             'status': 'report_created_successfully',
#             'file_url': 'file_url'
#         }, status=201)
#
#     except Exception as e:
#         print('execption111111111111111   ',e)
#         return JsonResponse({"status": f"Database write error: {str(e)}"}, status=500)
#
#
#     # else:
#     #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)



#
# @api_view(['POST'])
# def patient_save_report(request):
#     if request.method != 'POST':
#         return JsonResponse({"status": "Method not allowed"}, status=405)
#
#     # Extract required fields from the request
#     patient_details_id = request.data.get('patient_details_id')
#     pdf_file_path1 = request.data.get('pdf_file_path')
#     current_date = request.data.get('date')
#     current_time = request.data.get('time')
#
#     print('Received pdf_file_path:', pdf_file_path1)
#     print('Received date:', current_date)
#     print('Received time:', current_time)
#
#     # Validate required fields
#     if not all([patient_details_id, pdf_file_path1, current_date, current_time]):
#         return JsonResponse(
#             {"status": "patient_details_id, pdf_file_path, date, and time are required."},
#             status=400
#         )
#
#     # Local file paths
#     # source_path = os.path.join(r'C:/Users/DeLL/Downloads/', str(pdf_file_path1))
#     source_path = os.path.join(r'/home/pi/Downloads/', str(pdf_file_path1))
#     destination_path = os.path.join(settings.MEDIA_ROOT, 'reports', str(pdf_file_path1))
#
#     # Check if the file exists locally
#     if not os.path.exists(source_path):
#         return JsonResponse({"status": "The provided file path does not exist."}, status=400)
#
#     # Move the file to the media directory
#     os.makedirs(os.path.dirname(destination_path), exist_ok=True)
#     shutil.copy(source_path, destination_path)
#     print('File moved to:', destination_path)
#
#     # Get the file URL
#     relative_path = f"/reports/{pdf_file_path1}"
#     file_url = f"{request.scheme}://{request.get_host()}{relative_path}"
#
#     print("Generated file URL:", file_url)
#
#     # Determine the database to use
#     database = DatabaseRouter.db_for_write()
#     print("Database in use:", database)
#
#     try:
#         if database == 'default':
#             report = Patientreports.objects.create(
#                 patient_details_id_id=patient_details_id,
#                 report_file=relative_path,  # Save relative path
#                 date=current_date,
#                 time=current_time
#             )
#             report.save()
#         elif database == 'fallback':
#             report = NewPatientreports.objects.create(
#                 patient_details_id=patient_details_id,
#                 report_file=relative_path,  # Save relative path
#                 date=current_date,
#                 time=current_time
#             )
#             report.save()
#         else:
#             return JsonResponse({"status": "Database router error."}, status=500)
#
#         return JsonResponse({
#             'status': 'report_created_successfully',
#             'file_url': file_url
#         }, status=201)
#
#     except Exception as e:
#         print("Exception occurred while saving to database:", e)
#         return JsonResponse({"status": f"Database write error: {str(e)}"}, status=500)


#######################################  below one working ######################## without video save



# @api_view(['POST'])
# def patient_save_report(request):
#     if request.method != 'POST':
#         return JsonResponse({"status": "Method not allowed"}, status=405)
#
#     # Extract required fields from the request
#     patient_details_id = request.data.get('patient_details_id')
#     pdf_file_path1 = request.data.get('pdf_file_path')
#     current_date = request.data.get('date')
#     current_time = request.data.get('time')
#
#     print('Received pdf_file_path:', pdf_file_path1)
#     print('Received date:', current_date)
#     print('Received time:', current_time)
#
#     # Validate required fields
#     if not all([patient_details_id, pdf_file_path1, current_date, current_time]):
#         return JsonResponse(
#             {"status": "patient_details_id, pdf_file_path, date, and time are required."},
#             status=400
#         )
#
#     # Local file paths
#     # source_path = os.path.join(r'C:/Users/DeLL/Downloads/', str(pdf_file_path1))
#     source_path = os.path.join(r'/home/pi/Downloads/', str(pdf_file_path1))
#
#     destination_path = os.path.join(settings.MEDIA_ROOT, 'reports', str(pdf_file_path1))
#     print("destination_path",destination_path)
#     print('source_path',source_path)
#     time.sleep(2)
#
#     # Check if the file exists locally
#     if not os.path.exists(source_path):
#         print("not exists")
#         return JsonResponse({"status": "The provided file path does not exist."}, status=400)
#
#     # Move the file to the media directory
#     os.makedirs(os.path.dirname(destination_path), exist_ok=True)
#     shutil.copy(source_path, destination_path)
#     print('File moved to:', destination_path)
#
#     # Get the file URL
#     relative_path = f"/reports/{pdf_file_path1}"
#     file_url = f"{request.scheme}://{request.get_host()}{relative_path}"
#
#     print("Generated file URL:", file_url)
#
#     # Determine the database to use
#     database = DatabaseRouter.db_for_write()
#     print("Database in use:", database)
#
#     try:
#         if database == 'default':
#             report = Patientreports.objects.create(
#                 patient_details_id_id=patient_details_id,
#                 report_file=relative_path,  # Save relative path
#                 date=current_date,
#                 time=current_time
#             )
#             report.save()
#         elif database == 'fallback':
#             report = NewPatientreports.objects.create(
#                 patient_details_id=patient_details_id,
#                 report_file=relative_path,  # Save relative path
#                 date=current_date,
#                 time=current_time
#             )
#             report.save()
#         else:
#             return JsonResponse({"status": "Database router error."}, status=500)
#
#         return JsonResponse({
#             'status': 'report_created_successfully',
#             'file_url': file_url,
#             "report_id": report.id
#
#         }, status=201)
#
#     except Exception as e:
#         print("Exception occurred while saving to database:", e)
#         return JsonResponse({"status": f"Database write error: {str(e)}"}, status=500)

@api_view(['POST'])
def patient_save_report(request):
    try:
        current_user = request.user
        if current_user.is_authenticated:
            print("request", current_user.is_authenticated)
            if request.method != 'POST':
                return JsonResponse({"status": "Method not allowed"}, status=405)

            # Extract required fields from the request
            patient_details_id = request.data.get('patient_details_id')
            pdf_file_path1 = request.data.get('pdf_file_path')
            current_date = request.data.get('date')
            current_time = request.data.get('time')
            list_of_video_report = request.data.get('list_of_video_report', [])  # Get the list of videos

            print('Received pdf_file_path:', pdf_file_path1)
            print('Received date:', current_date)
            print('Received time:', current_time)
            print('Received list_of_video_report:', list_of_video_report)

            # Validate required fields
            if not all([patient_details_id, pdf_file_path1, current_date, current_time]):
                return JsonResponse(
                    {"status": "patient_details_id, pdf_file_path, date, and time are required."},
                    status=400
                )

            # Local file paths
            # source_path = os.path.join(r'C:/Users/DeLL/Downloads/', str(pdf_file_path1))
            source_path = os.path.join(r'/home/pi/Downloads/', str(pdf_file_path1))
            destination_path = os.path.join(settings.MEDIA_ROOT, 'reports', str(pdf_file_path1))
            print('destination_path:', destination_path)
            print('source_path:', source_path)
            time.sleep(2)

            # Check if the file exists locally
            if not os.path.exists(source_path):
                return JsonResponse({"status": "The provided file path does not exist."}, status=400)

            # Move the file to the media directory
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.copy(source_path, destination_path)
            print('File moved to:', destination_path)

            # Get the file URL
            relative_path = f"/reports/{pdf_file_path1}"
            print('relative_path:', relative_path)
            file_url = f"{request.scheme}://{request.get_host()}{relative_path}"

            print("Generated file URL:", file_url)

            # Determine the database to use
            database = DatabaseRouter.db_for_write()
            print("Database in use:", database)

            try:
                # Create the report entry in the appropriate database
                if database == 'default':
                    report = Patientreports.objects.create(
                        patient_details_id_id=patient_details_id,
                        report_file=relative_path,  # Save relative path
                        date=current_date,
                        time=current_time
                    )
                elif database == 'fallback':
                    report = NewPatientreports.objects.create(
                        patient_details_id=patient_details_id,
                        report_file=relative_path,  # Save relative path
                        date=current_date,
                        time=current_time
                    )
                else:
                    return JsonResponse({"status": "Database router error at report save ."}, status=500)

                # Save the report and get its ID
                # Save the report and get its ID
                report.save()
                report_id = report.id
                if database == 'default':

                    # Save each video file individually
                    if list_of_video_report:
                        for video_file in list_of_video_report:
                            save_video=video_store.objects.create(report_data_id=report, video_file=video_file)
                            save_video.save()
                elif database == 'fallback':
                    if list_of_video_report:
                        for video_file in list_of_video_report:
                            save_video1 = New_video_store.objects.create(report_data_id=report, video_file=video_file)
                            save_video1.save()
                else:
                    return JsonResponse({"status": "Database router error at video save ."}, status=500)

                # Process and save the list of videos
                # if list_of_video_report:
                #     video_entries = [
                #         video_store(report_data_id=report, video_file=video_file)
                #         for video_file in list_of_video_report
                #     ]
                #     video_store.objects.bulk_create(video_entries)

                return JsonResponse({
                    'status': 'report_created_successfully',
                    'file_url': file_url,
                    'report_id': report_id
                }, status=201)

            except Exception as e:
                print("Exception occurred while saving to database:", e)
                return JsonResponse({"status": f"Database write error: {str(e)}"}, status=500)

        else:
            return JsonResponse({"status": "login_required"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})














@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username_email = serializer.validated_data.get('username')

            is_email = False
            try:
                validate_email(username_email)
                is_email = True
            except ValidationError:
                pass

            if is_email:
                try:
                    found_user = User.objects.get(email=username_email)
                    username = found_user.username
                except User.DoesNotExist:
                    username = None
            else:
                username = username_email
            password = serializer.validated_data.get('password')

            print("Username:",username)
            print("Password:",password)

            user = authenticate(username=username,password=password)

            if user is not None:
                login(request, user)
                user_data = User.objects.get(id=user.id)
                print('user_data', user_data)
                userdetails = UserDetails.objects.get(user_id=user.id)
                print('userdetails', userdetails)

                result = {
                    "user_id": user.id,
                    "username": user_data.username,
                    "email": user_data.email,
                    "mobile_no": userdetails.mobile_no,
                    "Speciality": userdetails.speciality,
                    "first_name": user_data.first_name
                }
                # print('result', result)

                return Response({"status": "user_validated", "user_id": user.id, "user_details_data": result},
                                status=status.HTTP_200_OK)
            else:
                return Response({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'status': 'Invalid_Credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @csrf_exempt
def register_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save()
            serializer.save(using='default')
            # serializer.save(using='fallback')
            return Response({"status": "User_created_successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def email_verification(request):
    # if request.user.is_authenticated:
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = random.randint(100000, 999999)

            try:
                user = User.objects.get(email=email)
                user_details, created = UserDetails.objects.get_or_create(user_id=user)
                user_details.otp = otp
                user_details.save()

                send_mail(
                    subject="Your OTP for Email Verification",
                    message=f"Your OTP is: {otp}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                return Response({"message": "OTP_sent_successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User_with_this_email_does_not_exist."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def validate_otp(request):
    # if request.user.is_authenticated:
        otp = request.data.get('otp')

        if not otp:
            return Response({"error": "OTP_is_required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_details = UserDetails.objects.get(otp=otp)

            if user_details:
                return Response({"message": "OTP_verified_successfully."}, status=status.HTTP_200_OK)

        except UserDetails.DoesNotExist:
            return Response({"error": "Invalid_OTP."}, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def update_password(request):
    # if request.user.is_authenticated:
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not email or not password or not confirm_password:
            return Response({"error": "Email, password, and confirm_password are_required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            serializer = PasswordUpdateSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(password)
                user.save()
                return Response({"message": "Password_updated_successfully."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": "User_with_this_email_does_not_exist."}, status=status.HTTP_404_NOT_FOUND)
    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def patient_list(request):
    # if request.user.is_authenticated:
        if DatabaseRouter.db_for_write() == 'default':
            print("if")
            db = DatabaseRouter.db_for_read(Patientsdetails)  # Pass the model
            patients = Patientsdetails.objects.using(db).all()
            serializer = PatientDetailSerializers(patients, many=True)
            result=serializer.data
        elif DatabaseRouter.db_for_write() == 'fallback':
            print("elif")
            newdb = DatabaseRouter.db_for_read(NewPatientsdetails)  # Pass the model
            newpatients = NewPatientsdetails.objects.using(newdb).all()
            newserializer = newPatientDetailSerializers(newpatients, many=True)
            db = DatabaseRouter.db_for_read(Patientsdetails)  # Pass the model
            patients = Patientsdetails.objects.using(db).all()
            serializer = PatientDetailSerializers(patients, many=True)
            print('serializer.data',serializer.data)
            print('newserializer.data',newserializer.data)

            result = serializer.data + newserializer.data
            print('result...........fallback',result)


        else:
            pass



        return Response(result)
    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)
@api_view(['POST'])
def logout_view(request):
        logout(request)
        return Response({"message": "Successfully_logged_out."}, status=status.HTTP_200_OK)




class WorkersListAPIView(APIView):

    def get(self, request, *args, **kwargs):
        print("getttt WorkersListAPIView")
        # try:
        print('db', DatabaseRouter.db_for_read())
        if DatabaseRouter.db_for_read() == 'default':
            print("if")
            db = DatabaseRouter.db_for_read(Patientsdetails)  # Pass the model
        elif DatabaseRouter.db_for_read() == 'fallback':
            print('else')
            db = DatabaseRouter.db_for_read(Patientsdetails)
        # db = DatabaseRouter.db_for_read()[0](DatabaseRouter.db_for_read()[1])  # Pass the model


        data = Patientsdetails.objects.using(db).all()
        serializer = patient_detailsSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # except Exception as e:
        #     print("eeeee",e)




# class SendPDFEmailAPIView(APIView):
#     def post(self, request):
#         # Parse data from the request
#         recipient_email = request.data.get('email')
#         pdf_url = "https://samplebucketautomac2.s3.ap-south-1.amazonaws.com/Venu_2024-12-2407_23_50.pdf"
#
#         if not recipient_email:
#             return Response({"error": "Recipient email is required."}, status=status.HTTP_400_BAD_REQUEST)
#
#         # Download the file from S3 URL
#         try:
#             response = requests.get(pdf_url)
#             response.raise_for_status()
#             pdf_content = response.content
#         except Exception as e:
#             return Response({"error": f"Failed to fetch the PDF file. Error: {str(e)}"},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         # Send email with attachment
#         try:
#             email = EmailMessage(
#                 subject="Your PDF File",
#                 body="Please find the attached PDF file.",
#                 to=[recipient_email],
#             )
#             email.attach("Venu_2024-12-2407_23_50.pdf", pdf_content, "application/pdf")
#             email.send()
#         except Exception as e:
#             return Response({"error": f"Failed to send email. Error: {str(e)}"},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         return Response({"message": "Email sent successfully!"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def email_verification(request):
    # if request.user.is_authenticated:
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = random.randint(100000, 999999)

            try:
                user = User.objects.get(email=email)
                user_details, created = UserDetails.objects.get_or_create(user_id=user)
                user_details.otp = otp
                user_details.save()

                send_mail(
                    subject="Your OTP for Email Verification",
                    message=f"Your OTP is: {otp}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                return Response({"message": "OTP_sent_successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User_with_this_email_does_not_exist."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def validate_otp(request):
    # if request.user.is_authenticated:
        otp = request.data.get('otp')

        if not otp:
            return Response({"error": "OTP_is_required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_details = UserDetails.objects.get(otp=otp)

            if user_details:
                return Response({"message": "OTP_verified_successfully."}, status=status.HTTP_200_OK)

        except UserDetails.DoesNotExist:
            return Response({"error": "Invalid_OTP."}, status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def update_password(request):
    # if request.user.is_authenticated:
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not email or not password or not confirm_password:
            return Response({"error": "Email, password, and confirm_password are_required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            serializer = PasswordUpdateSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(password)
                user.save()
                return Response({"message": "Password_updated_successfully."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": "User_with_this_email_does_not_exist."}, status=status.HTTP_404_NOT_FOUND)
    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def patient_list(request):
    try:
        current_user = request.user
        if current_user.is_authenticated:
            print("request", current_user.is_authenticated)
            if DatabaseRouter.db_for_write() == 'default':
                print("if")
                db = DatabaseRouter.db_for_read(Patientsdetails)  # Pass the model
                patients = Patientsdetails.objects.using(db).all()
                serializer = PatientDetailSerializers(patients, many=True)
                result=serializer.data
            elif DatabaseRouter.db_for_write() == 'fallback':
                print("elif")
                newdb = DatabaseRouter.db_for_read(NewPatientsdetails)  # Pass the model
                newpatients = NewPatientsdetails.objects.using(newdb).all()
                newserializer = newPatientDetailSerializers(newpatients, many=True)
                db = DatabaseRouter.db_for_read(Patientsdetails)  # Pass the model
                patients = Patientsdetails.objects.using(db).all()
                serializer = PatientDetailSerializers(patients, many=True)
                print('serializer.data',serializer.data)
                print('newserializer.data',newserializer.data)

                result = serializer.data + newserializer.data
                print('result...........fallback',result)


            else:
                pass


            return Response(result)
        else:
            return JsonResponse({"status": "login_required"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


#
# @api_view(['POST'])
# def logout_view(request):
#         logout(request)
#         return Response({"message": "Successfully_logged_out."}, status=status.HTTP_200_OK)




@api_view(['POST'])
def send_email(request):
    try:
        current_user = request.user
        if current_user.is_authenticated:
            print("request", current_user.is_authenticated)
            # Extract data from request
            email = request.data.get('email')
            name = request.data.get('name')
            report_id = request.data.get('report_id')

            if not all([email, name, report_id]):
                return Response({"status": "Email, name, and report_id are required."}, status=400)

            # Fetch report from database
            try:
                report = Patientreports.objects.get(id=report_id)
            except Patientreports.DoesNotExist:
                return Response({"status": "Report not found."}, status=404)

            # Construct full PDF URL
            base_url = "http://127.0.0.1:8000/media"
            pdf_url = f"{base_url}{report.report_file}"
            pdf_filename = pdf_url.split('/')[-1]

            try:
                # Fetch PDF content
                response = requests.get(pdf_url)
                response.raise_for_status()
                pdf_content = response.content
            except requests.exceptions.RequestException as e:
                return Response({"status": f"Failed to download PDF: {e}"}, status=500)

            # Email content
            email_subject = "Endoscopy Report"
            email_body = f"""
            <p>Dear {name},</p>
            <p>Please find your endoscopy report attached.</p>
            <p>If you have any questions, feel free to contact us at [+918726165268].</p>
            <p>Thank you,</p>
            <p>[Hospital Name]</p>
            """

            # Send email
            email_message = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            email_message.content_subtype = "html"  # HTML email
            email_message.attach(pdf_filename, pdf_content, "application/pdf")

            try:
                email_message.send()
            except Exception as e:
                return Response({"status": f"Failed to send email: {e}"}, status=500)

            return Response({"status": "PDF sent successfully"}, status=200)

        else:
            return JsonResponse({"status": "login_required"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})



@api_view(['PUT'])
def user_details_update(request):
    try:
        current_user = request.user
        if current_user.is_authenticated:
            print("request", current_user.is_authenticated)
            # Extract data from request
            user_id = request.data.get('user_id')
            username = request.data.get('username')
            email = request.data.get('email')
            mobile = request.data.get('mobile_no')
            speciality = request.data.get('Speciality')
            firstname = request.data.get('first_name')

            # Validate required fields
            if not all([user_id, username, email, mobile, speciality]):
                return Response(
                    {"status": "Error", "message": "user_id, username, email, mobile, and speciality are required."},
                    status=400
                )

            try:
                # Fetch and update user details
                user = User.objects.get(id=user_id)
                user.username = username
                user.email = email
                user.first_name = firstname
                user.save()

                # Update or create related user details
                user_details, created = UserDetails.objects.update_or_create(
                    user_id=user,  # Assuming user_id is a ForeignKey to User
                    defaults={"mobile_no": mobile, "speciality": speciality}
                )

                return JsonResponse({"status": "success", "message": "User details updated successfully.",
                                     "edited_data": {"user_id": user_id, "username": username, "email": email,
                                                     "mobile_no": mobile,
                                                     "Speciality": speciality, "first_name": firstname}
                                     })

            except ObjectDoesNotExist:
                return Response({"status": "Error", "message": "User not found."}, status=404)
            except Exception as e:
                return Response({"status": "Error", "message": str(e)}, status=500)
        else:
            return JsonResponse({"status": "login_required"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})




@api_view(['PUT'])
def patient_details_update(request):
    try:
        current_user = request.user
        if current_user.is_authenticated:
            print("request", current_user.is_authenticated)
            # Extract data from request
            patient_id = request.data.get('patient_id')
            patient_name = request.data.get('patient_name')
            age = request.data.get('age')
            gender = request.data.get('gender')
            procedure = request.data.get('procedure')
            mobile = request.data.get('mobile')
            patient_email = request.data.get('patient_email')
            referred = request.data.get('referred')
            updated_at = request.data.get('updated_at')

            # Validate required fields
            if not patient_id:
                return Response(
                    {"status": "Error", "message": "'patient_id' is required to update patient details."},
                    status=400
                )

            try:
                # Fetch the patient record
                patient_data = Patientsdetails.objects.get(id=patient_id)

                # Update fields if they are provided
                if patient_name:
                    patient_data.patient_name = patient_name
                if age:
                    patient_data.age = age
                if gender:
                    patient_data.gender = gender
                if procedure:
                    patient_data.procedure = procedure
                if mobile:
                    patient_data.mobile = mobile
                if patient_email:
                    patient_data.patient_email = patient_email
                if referred:
                    patient_data.referred = referred
                else:
                    pass

                patient_data.updated_at = datetime.datetime.now()

                # Save the updated patient data
                patient_data.save()

                return JsonResponse({"status": "success", "message": "Patient details updated successfully."})

            except ObjectDoesNotExist:
                return Response(
                    {"status": "Error", "message": "Patient not found with the given 'patient_id'."},
                    status=404
                )

            except Exception as e:
                return Response(
                    {"status": "Error", "message": f"An error occurred: {str(e)}"},
                    status=500
                )
        else:
            return JsonResponse({"status": "login_required"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})



@api_view(['GET'])
def internet_test(request):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return JsonResponse({"message": "connected"})
    except Exception as e:
        return JsonResponse({"message": "disconnected","status": str(e)})


@api_view(['POST'])
def wifi_test_rpi(request):
    sid_data = request.data.get('sid')
    password_data = request.data.get('password')
    try:
        wifi_con_status = wifi_code.connect_to_wifi(sid_data, password_data)
        if wifi_con_status:
            return JsonResponse({"message": "connected"})
        else:
            return JsonResponse({"message": "failed to connect"}, status=500)
    except Exception as e:
        return JsonResponse({"message": "error", "details": str(e)}, status=500)


def generate_frames():
    # Open the camera
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        raise RuntimeError("Error: Camera not accessible.")

    while True:
        success, frame = capture.read()
        if not success:
            break

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame as part of the HTTP response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




@api_view(['GET'])

def video_feed(request):
    # Use StreamingHttpResponse to stream the video feed
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')





