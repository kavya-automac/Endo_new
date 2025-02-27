"""
URL configuration for dev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('dev_pro.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
    path('register', TemplateView.as_view(template_name='index.html')),
    path('forgot', TemplateView.as_view(template_name='index.html')),
    path('otpnumber', TemplateView.as_view(template_name='index.html')),
    path('otpemail', TemplateView.as_view(template_name='index.html')),
    path('settingpwd', TemplateView.as_view(template_name='index.html')),
    path('account', TemplateView.as_view(template_name='index.html')),
    path('patientinfo', TemplateView.as_view(template_name='index.html')),
    path('headersetting', TemplateView.as_view(template_name='index.html')),
    path('hospital', TemplateView.as_view(template_name='index.html')),
    path('allpatients', TemplateView.as_view(template_name='index.html')),
    # path('cameronwillamson', TemplateView.as_view(template_name='index.html')),
    path('cameronwillamson/<str:patient_name>/', TemplateView.as_view(template_name='index.html')),
    path('videocapturing', TemplateView.as_view(template_name='index.html')),
    path('selectpicture', TemplateView.as_view(template_name='index.html')),
    path('exportreport', TemplateView.as_view(template_name='index.html')),
    path('edituser', TemplateView.as_view(template_name='index.html')),
    path('wifi', TemplateView.as_view(template_name='index.html')),
    path('editpatient', TemplateView.as_view(template_name='index.html')),
    path('login', TemplateView.as_view(template_name='index.html')),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
