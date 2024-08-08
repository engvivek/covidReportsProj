import csv
from io import StringIO
from django.core.mail import send_mail, EmailMessage
import json
from time import sleep
import jwt
import requests
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from datetime import timedelta, datetime, timezone
from covidReportsApp.models import *
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.template.loader import render_to_string

User = get_user_model()


key = "covidreports"

headers = {
            "x-rapidapi-key": "f9fd8444a3mshe0f6de28b038155p15bf50jsn519f54f7f1e0",
	        "x-rapidapi-host": "covid-19-data.p.rapidapi.com"
          }

class CovidUserRegisteration(View):
    def post(self, request):
        get_payload = json.loads(request.body.decode('utf-8'))
        name = get_payload.get('Name')
        uname = get_payload.get('UserName')
        passw = get_payload.get('Password')
        mobile = get_payload.get('Mobile')
        email = get_payload.get('Email_Id')

        check_user = UserRegistration.objects.filter(username=uname)

        if check_user.exists():
            return HttpResponse(json.dumps({"status": "Username already exist. Please choose another username!"}, 
                                           ), content_type="application/json", status=400)
        else:
            user_insert = UserRegistration.objects.create(name=name,
                                                          username=uname,
                                                          mobile=mobile,
                                                          email=email)
            user_insert.set_password(passw)
            user_insert.save()

            return HttpResponse(json.dumps({"status": "User "+uname+" registered successfully!"}), content_type="application/json")

class UserLogin(View):
    def post(self, request):
        get_payload = json.loads(request.body.decode('utf-8'))
        usernm = get_payload.get('username')
        passw = get_payload.get('password')

        check_user = UserRegistration.objects.filter(username=usernm)

        if check_user.exists():
            login(request, check_user.first())

            get_date_time = datetime.now(tz=timezone.utc)+timedelta(seconds=3600)
            token_inp = {"userName":usernm, "exp": get_date_time}

            token = jwt.encode(token_inp, key, algorithm="HS256")
            return HttpResponse(json.dumps({"token": token, "loginStatus": "Logged In"}), content_type="application/json")
        
        else:
            return HttpResponse(json.dumps({"status": "Username/Password is incorrect. Please try again!"}), 
                                content_type="application/json", status=401)
            
        
class AssignCountryToUser(View):
    def post(self, request):
        #get_token = request.headers['Authorization'].split(' ')
        #obj = TokenValidateApi()
        #ret = obj.tokenValidator(get_token)

        #if ret['status'] == "Successfull":

        get_payload = json.loads(request.body.decode('utf-8'))

        if request.user.is_authenticated:
            uname = get_payload.get('username')
            country_list = get_payload.get('assigned_country')

            check_user = CovidReportByUser.objects.filter(username=uname).values()

            if len(check_user) != 0:
                check_user.update(countries_handled_by_user=country_list)

                return HttpResponse(json.dumps({"status": "Record for user "+uname+" is updated successfully!"}), 
                                    content_type="application/json")
            else:
                assign_to_user = CovidReportByUser.objects.create(username=uname,
                                                                  countries_handled_by_user=country_list)
                assign_to_user.save()

                return HttpResponse(json.dumps({"status": "Record Inserted for user "+uname+" successfully!"}), 
                                    content_type="application/json")
        else:
            return HttpResponse(json.dumps({"error": "User logged in session timed out!"}), content_type="application/json", status=401)

class TokenValidateApi(View):
    def tokenValidator(self, inp_token):
        try:
            validate = jwt.decode(inp_token[1], key, algorithms="HS256")
            return({"status": "Successfull", "token_payload": validate})
        except jwt.exceptions.ExpiredSignatureError:
            return ({"status": "Token Expired"})
        except jwt.exceptions.InvalidSignatureError:
            return ({"status": "Invalid Token"})
        

class GetCovidReportByCountryCd(View):
    def get(self, request):
        if request.user.is_authenticated:
            get_payload = json.loads(request.body.decode('utf-8'))
            country_cd = get_payload.get('country')

            api_link = "https://covid-19-data.p.rapidapi.com/country/code?format=json&code="+country_cd
            api_req = requests.get(api_link, headers=headers)
            api_data = api_req.json()

            if api_req.status_code == 200:
                return HttpResponse(json.dumps({"data":api_data}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({"error": "Error connecting to URL"}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"error": "User logged in session timed out!"}), content_type="application/json", status=401)
        
class GetCovidReportByCountryName(View):
    def get(self, request):
            get_last_key = ""
            if isinstance(request, HttpRequest):
                if request.user.is_authenticated:
                    request_dict = {
                                    'method': request.method,
                                    'headers': dict(request.headers),  # Convert headers to a dictionary
                                    'GET': request.GET.dict(),          # Query parameters
                                    'POST': request.POST.dict(),        # Form data
                                    'COOKIES': request.COOKIES,          # Cookies
                                    'body': request.body.decode('utf-8')  # Body of the request (assuming UTF-8 encoding)
                                    }
                    last_key = ' '.join(list(request_dict.keys())).split(' ')
                    get_last_key = last_key[-1]
                else:
                    return HttpResponse(json.dumps({"error": "User logged in session timed out!"}), content_type="application/json", status=401)
            else:
                last_key = ' '.join(list(request.keys()))
                get_last_key = last_key

            if get_last_key != "reports":
                get_payload = json.loads(request.body.decode('utf-8'))
                country_name = get_payload.get('country')
            else:
                country_name = request['reports']['country']

            pos = 0
            country_covid_data = []
            if isinstance(country_name, list) and get_last_key == "reports":
                for cntry_nm in country_name:
                    temp_data = []
                    api_link = "https://covid-19-data.p.rapidapi.com/country?name="+cntry_nm+"&format=json"
                    api_req = requests.get(api_link, headers=headers)
                    api_data = api_req.json()
                    sleep(1)
                    
                    temp_data.append(api_data[0]['country'])
                    temp_data.append(api_data[0]['confirmed'])
                    temp_data.append(api_data[0]['recovered'])
                    temp_data.append(api_data[0]['critical'])
                    temp_data.append(api_data[0]['deaths'])
                    temp_data.append(api_data[0]['lastChange'])
                    temp_data.append(api_data[0]['lastUpdate'])
                    
                    country_covid_data.insert(pos, temp_data)
                    pos = pos + 1
            else:
                api_link = "https://covid-19-data.p.rapidapi.com/country?name="+country_name+"&format=json"
                api_req = requests.get(api_link, headers=headers)
                api_data = api_req.json()

            if get_last_key != "reports":
                if api_req.status_code == 200:
                    return HttpResponse(json.dumps({"data":api_data}), content_type="application/json")
                else:
                    return HttpResponse(json.dumps({"error": "Error connecting to URL"}), content_type="application/json")
            else:
                if api_req.status_code == 200:
                    return country_covid_data
                else:
                    return ({"error": "Error connecting to URL"})

class GetCovidReportAllCountry(View):
    def get(self, request):
        if request.user.is_authenticated:
            api_link = "https://covid-19-data.p.rapidapi.com/country/all?format=json"
            api_req = requests.get(api_link, headers=headers)
            api_data = api_req.json()

            if api_req.status_code == 200:
                return HttpResponse(json.dumps({"data":api_data}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({"error": "Error connecting to URL"}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"error": "User logged in session timed out!"}), content_type="application/json", status=401)

class GenerateReportSendEmail(View):
    def post(self, request):
        if request.user.is_authenticated:
            get_payload = json.loads(request.body.decode('utf-8'))

            userid = get_payload.get('userId', 'None')
            bycountry = get_payload.get('byCountry', 'None')
            report_type = get_payload.get('reportType')

            call_report_by = ""

            if userid != "None":
                call_report_by = "BYUSERID"
            elif bycountry != "None":
                call_report_by = "BYCOUNTRY"

            obj = GenerateReportByType()
            report = obj.html_or_csv_report(request, call_report_by, report_type)

            sub = "Covid Report"
            frm_email = settings.EMAIL_HOST_USER

            if report_type == "HTML":
                send_mail(sub,
                          '',
                          frm_email,
                          ["vivekkumar16011993@gmail.com"],
                          fail_silently=False,
                          html_message=report
                         )
            
                return HttpResponse(json.dumps({"status": "Email sent Successfully with HTML!"}), content_type="application/json")
            else:
                email = EmailMessage(subject=sub,
                                     body='Hi,\n\nPlease find the attached CSV file.\n\nThanks and Regards\nVivek Kumar',
                                     from_email=frm_email,
                                     to=['vivekkumar16011993@gmail.com'],
                                    )
                email.attach('report.csv', report, 'text/csv')
                email.send()

                return HttpResponse(json.dumps({"status": "Email sent Successfully with CSV attachemnt!"}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"error": "User logged in session timed out!"}), content_type="application/json", status=401)
    
class GenerateReportByType(View):
    def html_or_csv_report(self, request_inp, input, report_format):
        get_payload = json.loads(request_inp.body.decode('utf-8'))
        usernm = get_payload.get('userId')

        country_list = []

        if input == "BYUSERID":
            if request_inp.user.is_authenticated:
                get_details = CovidReportByUser.objects.filter(username=usernm).values()
                if len(get_details) != 0:
                    if len(get_details[0].get('countries_handled_by_user')) != 0:
                        country_list = get_details[0].get('countries_handled_by_user').split(',')
                        inp = {"reports":{"country": country_list}}
                        obj = GetCovidReportByCountryName()
                        country_covid_data = obj.get(inp)

                        if report_format == "HTML":
                            ret_html_report = GenerateHtmlReport(country_covid_data)
                            return ret_html_report
                        elif report_format == "CSV":
                            ret_csv_report = GenerateCsvReport(country_covid_data)
                            return ret_csv_report
            else:
                return HttpResponse(json.dumps({"error": "User logged in session timed out!"}), content_type="application/json")

def GenerateHtmlReport(country_covid_data):
    data = {
        'headers': ['Country Name', 'Confirmed Cases', 'Recovered Cases', 
                    'Critical', 'Total Deaths', 'Last Change in Data', 'Last Update'],
        'rows': [],
    }

    for l in country_covid_data:
        data['rows'].append(l)
    
    html_content = render_to_string('email_template.html', {'data': data})
    return html_content

def GenerateCsvReport(country_covid_data):
    output = StringIO()                    # Create a string buffer to hold CSV data
    writer = csv.writer(output)
    data = []

    writer.writerow(['Country Name', 'Confirmed Cases', 'Recovered Cases', 
                    'Critical', 'Total Deaths', 'Last Change in Data', 'Last Update'])      # Write the header row
    
    for l in country_covid_data:
        data.append(l)
    
    writer.writerows(data)                 # Write data rows

    # Get the CSV string
    csv_data = output.getvalue()
    output.close()
    return csv_data