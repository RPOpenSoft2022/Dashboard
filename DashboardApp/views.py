from django.forms import ValidationError
from django.shortcuts import render
from Dashboard.settings import DELIVERY_MICROSERVICE_URL, ORDERS_MICROSERVICE_URL, STORES_MICROSERVICE_URL, USERS_MICROSERVICE_URL
from .interconnect import send_request_get


def dashboard(request):
    url = ORDERS_MICROSERVICE_URL + '/last_month_sales/'
    succ, resp = send_request_get(url)

    if not succ:
        raise ValidationError("/orders/last_month_sales : Could not connect to orders microservices")

    resp = resp.json()
    print(resp)
    context = {
        'last_month_sales': resp
    }


    return render(request, 'dashboard.html')
