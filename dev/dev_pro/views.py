import json
import os
import time
from asyncio import current_task

import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView

from .models import *
from .serializers import *

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.core.mail import send_mail
from rest_framework import response, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
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




@api_view(['POST'])
def add_patient(request):
    # current_user = request.user
    # if request.user.is_authenticated:
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
    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['DELETE'])
def delete_patients(request):
    # if request.user.is_authenticated:
    ids_to_delete = request.data.get('ids', [])  # Expects a list of ids to delete
    if not ids_to_delete:
        return JsonResponse({"status": "No_IDs_provided"}, status=status.HTTP_400_BAD_REQUEST)
    patients = Patientsdetails.objects.filter(id__in=ids_to_delete)

    if patients.exists():
        patients.delete()
        return JsonResponse({"status": "Patients_deleted_successfully"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"status": "No_patients_found_with_the_provided_IDs"}, status=status.HTTP_404_NOT_FOUND)
    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
# def patient_report_file(request,patient_id):
def patient_report_file(request):

    # if request.user.is_authenticated:
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



    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)


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


@api_view(['POST'])
def patient_save_report(request):
    # if request.user.is_authenticated:
    if request.method != 'POST':
        return JsonResponse({"status": "Method not allowed"}, status=405)

    # Extract required fields from the request
    patient_details_id = request.data.get('patient_details_id')
    pdf_file_path1 = request.data.get('pdf_file_path')
    current_date = request.data.get('date')
    current_time = request.data.get('time')

    # Debug print statements
    print('Received pdf_file_path:', pdf_file_path1)
    print('Received date:', current_date)
    print('Received time:', current_time)

    # Validate required fields
    if not all([patient_details_id, pdf_file_path1, current_date, current_time]):
        return JsonResponse(
            {"status": "patient_details_id, pdf_file_path, date, and time are required."},
            status=400
        )

    # Local file path
    # file_path = os.path.join(r'C:/Users/DeLL/Downloads/', str(pdf_file_path1))
    file_path = os.path.join(r'/home/pi/Downloads/', str(pdf_file_path1))
    print('Full local file path:', file_path)
    print('Full local file path:', type(file_path))

    # Check if the file exists locally
    # if not os.path.exists(file_path):
    #     return JsonResponse({"status": "The provided file path does not exist."}, status=400)

    # Upload file to S3 bucket
    # s3_object_key = f"patients_{patient_details_id}_{pdf_file_path1}"
    # print("S3 object key:", s3_object_key)


    # add later try and except




    # try:
    #     time.sleep(2)
    #     file_url = upload_file(file_path, "samplebucketautomac2", object_name=str(pdf_file_path1), region=None)
    #     print('File upload URL:', file_url)
    # except Exception as e:
    #     print("s3 bucket exception",e)



    # Determine the database to use
    database = DatabaseRouter.db_for_write()
    print("Database in use:", database)

    # Database write operation
    try:
        if database == 'default':
            try:
                report = Patientreports.objects.create(
                    patient_details_id_id=patient_details_id,
                    #add later
                    # report_file='https://samplebucketautomac2.s3.ap-south-1.amazonaws.com/'+str(file_url),
                    report_file=file_path,
                    date=current_date,
                    time=current_time
                )
                report.save()
            except Exception as e:
                print("default db error ------> ", e)
            # Assuming patient_details_id is a valid ID
            # try:
            #     patient_details_instance = Patientsdetails.objects.get(id=patient_details_id)
            # except Patientsdetails.DoesNotExist:
            #     return JsonResponse({"status": "Patient not found."}, status=404)
            #
            # # Now create the report, passing the patient instance
            # try:
            #     report = Patientreports.objects.create(
            #         patient_details_id=patient_details_instance,  # Pass the instance, not just the ID
            #         report_file='https://samplebucketautomac2.s3.ap-south-1.amazonaws.com/' + str(file_url),
            #         date=current_date,
            #         time=current_time
            #     )
            #     report.save()
            # except Exception as e:
            #     print("Error saving report:", e)
            #     return JsonResponse({"status": f"Error saving report: {str(e)}"}, status=500)


        elif database == 'fallback':
            print("Using fallback database")
            print("patient_details_id",patient_details_id)
            try:
                report = NewPatientreports.objects.create(
                    patient_details_id=patient_details_id,
                    report_file=file_path,
                    date=current_date,
                    time=current_time
                )
                report.save()
            except Exception as e:
                print("/////////////////////////////////",e)
            print("report fLLBck",report)
        else:
            return JsonResponse({"status": "Database router error."}, status=500)



        return JsonResponse({
            'status': 'report_created_successfully',
            'file_url': 'file_url'
        }, status=201)

    except Exception as e:
        print('execption111111111111111   ',e)
        return JsonResponse({"status": f"Database write error: {str(e)}"}, status=500)


    # else:
    #     return JsonResponse({"status": "unauthorized_user"}, status=status.HTTP_401_UNAUTHORIZED)





@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')

            print("Username:",username)
            print("Password:",password)

            user = authenticate(username=username,password=password)

            if user is not None:
                login(request, user)
                # user_id = User.objects.get(username=request.user)
                return Response({"status": "user_validated"}, status=status.HTTP_200_OK)
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
def send_email(request):
    email = request.data.get('email')
    name = request.data.get('name')
    report_id = request.data.get('report_id')


    s3_link_query=Patientreports.objects.get(id=report_id)
    print("s3_link_query",s3_link_query)
    print("s3_link_query",s3_link_query.report_file)



    # s3_pdf_url = request.data.get('s3_pdf_url')  # Expecting the S3 URL in the request
    # s3_pdf_url = "https://samplebucketautomac2.s3.ap-south-1.amazonaws.com/Venu_2024-12-2407_23_50.pdf"  # Expecting the S3 URL in the request
    s3_pdf_url = str(s3_link_query.report_file) # Expecting the S3 URL in the request

    # if not email :
    #     return Response({"status": "Email and S3 PDF URL are required."}, status=400)


    try:
        response = requests.get(s3_pdf_url)
        response.raise_for_status()
        pdf_content = response.content
        pdf_filename = s3_pdf_url.split('/')[-1]
    except requests.exceptions.RequestException as e:
        return Response({"status": f"Failed to download PDF: {e}"}, status=500)

        # Create email
    # name="neeraj"
    email_subject = 'Endoscopy Report'
    email_body = f"""
    <p>Dear {name},</p>
    <p>We are sending you your endoscopy report as part of your recent medical examination. Please review the attached document at your earliest convenience.</p>
    <p>Should you have any concerns, you may contact us at [+918726165268].</p>
    <p>Thank you,</p>
    <p>[Hospital Name]</p>
    """

    email_message = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[email],
    )
    email_message.content_subtype = 'html'  # Send as HTML
    email_message.attach(pdf_filename, pdf_content, 'application/pdf')

    # Send email
    try:
        email_message.send()
    except Exception as e:
        return Response({"status": f"Failed to send email: {e}"}, status=500)



    return Response({'status': 'PDF sent successfully'}, status=200)










