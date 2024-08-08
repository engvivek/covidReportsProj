from django.contrib import admin
from django.urls import path

from covidReportsApp.views import AssignCountryToUser, CovidUserRegisteration, GetCovidReportAllCountry, GetCovidReportByCountryCd, GetCovidReportByCountryName, TokenValidateApi, UserLogin, GenerateReportSendEmail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('covidReportsApp/TokenValidateApi/', TokenValidateApi.as_view()),
    path('covidReportsApp/CovidUserRegisteration/', CovidUserRegisteration.as_view()),
    path('covidReportsApp/UserLogin/', UserLogin.as_view()),
    path('covidReportsApp/AssignCountryToUser/', AssignCountryToUser.as_view()),
    path('covidReportsApp/GetCovidReportByCountryCd/', GetCovidReportByCountryCd.as_view()),
    path('covidReportsApp/GetCovidReportByCountryName/', GetCovidReportByCountryName.as_view()),
    path('covidReportsApp/GetCovidReportAllCountry/', GetCovidReportAllCountry.as_view()),
    path('covidReportsApp/GenerateReportSendEmail/', GenerateReportSendEmail.as_view()),
]
