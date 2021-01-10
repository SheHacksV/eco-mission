from django.shortcuts import render
from django.contrib import messages
from .forms import RouteForm
from geopy.geocoders import Nominatim
from math import cos, asin, sqrt
import requests
import json
import os

# Create your views here.


def index(request):
    return render(request, 'calculator/index.html')


def calculate_distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))


def get_car_details(request):
    if request.method != 'POST':
        route_form = RouteForm()
        return render(request, "calculator/car_details.html", {'route_form': route_form})

    route_form = RouteForm(request.POST)

    if not route_form.is_valid():
        route_form = RouteForm()
        return render(request, "calculator/car_details.html", {'route_form': route_form})

    departure_postcode = route_form.cleaned_data.get('departure_postcode')
    destination_postcode = route_form.cleaned_data.get('destination_postcode')

    geo_locator = Nominatim(user_agent="ecomission")

    try:
        departure_location = geo_locator.geocode(departure_postcode)
        destination_location = geo_locator.geocode(destination_postcode)

        distance = calculate_distance(departure_location.latitude, departure_location.longitude,
                                      destination_location.latitude, destination_location.longitude)
        distance_unit = "km"
        type = "vehicle"
        vehicle_model_id = "17b83590-9500-4460-92cd-f8ffdcc20102"

        url = "https://www.carboninterface.com/api/v1/estimates"
        #key = "Bearer " + os.environ.get(CARBON_API_KEY)
        key = "Bearer " + "4egbuH6TWH33h2As62X9Lw"

        headers = {'Authorization': key, 'Content-Type': 'application/json'}
        payload = {'type': type, 'distance_unit': distance_unit,
                   'distance_value': int(distance), 'vehicle_model_id': vehicle_model_id}
        response = requests.get(url, headers=headers, params=payload)
        print(response.status_code)

        if response.status_code == 200:
            api_response = json.loads(response.text)
            print(response.text)
            attributes = api_response["data"]["attributes"]
            carbon_lb = attributes["carbon_lb"]
            carbon_mt = attributes["carbon_mt"]
            request.session['distance'] = distance
            request.session['carbon_lb'] = carbon_lb
            request.session['social_cost'] = carbon_mt*105
            return redirect('get_results')


    except:
        messages.add_message(request, messages.ERROR,
                             'Your input was invalid. Please try again.')
        route_form = RouteForm()
        return render(request, "calculator/car_details.html", {'route_form': route_form})


def get_results(request):
    #return render(request, 'calculator/results.html', {'distance': request.session['distance'],
    #                                                   'carbon_lb': request.session['carbon_lb'],
    #                                                   'social_cost': request.session['social_cost']})
    return render(request, 'calculator/results.html')

def about(request):
    return render(request, 'calculator/about.html')


