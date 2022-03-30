from django.shortcuts import render
from DashboardApp.interconnect import send_request_get
from numerize import numerize
import json


def dashboard(request):
    sales_url = "http://userapp.centralindia.cloudapp.azure.com:8081/last_month_sales"
    [_, sales_response] = send_request_get(sales_url)
    sales_data = sales_response.json()
    sales_months = list(sales_data.keys())
    sales_months.reverse()
    sales = [sales_data[i]['total_sales'] for i in sales_months]
    users_url = "http://userapp.centralindia.cloudapp.azure.com:8080/api/usershistory"
    [_, users_response] = send_request_get(users_url)
    users_data = users_response.json()
    user_months = list(users_data["history"].keys())
    user_months.reverse()
    users = [users_data["history"][i] for i in user_months]
    context = {
        'sales_months': sales_months,
        'sales': sales,
        'user_months': user_months,
        'users': users,
        "user_increase_percent": (users[-1]-users[-2])/100,
        "sales_increase": (sales[-1]-sales[-2]),
        "customers": numerize.numerize(users_data["customer"]),
        "staff": numerize.numerize(users_data["staff"]),
        "delivery": numerize.numerize(users_data["delivery"])
        }
    return render(request, 'dashboard.html', context)
