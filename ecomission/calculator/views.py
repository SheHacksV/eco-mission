from django.shortcuts import render
from django.contrib import messages
from .forms import RouteForm
from geopy.geocoders import Nominatim
from math import cos, asin, sqrt
import requests
import json

# Create your views here.


def index(request):
    return render(request, 'index.html')


def calculate_distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))


def get_car_details(request):
    if request.method != 'POST':
        route_form = RouteForm()
        return render(request, "car_details.html", {'route_form': route_form})

    route_form = RouteForm(request.POST)

    if not route_form.is_valid():
        route_form = RouteForm()
        return render(request, "car_details.html", {'route_form': route_form})

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
        key = "Bearer " + os.environ.get(API_KEY)

        headers = {'Authorization': key}
        payload = {'type': type, 'distance_unit': distance_unit,
                   'distance_value': distance, 'vehicle_model_id': vehicle_model_id}
        response = requests.get(url, headers=headers, params=payload)
        
        if response.status_code == 200:
            api_response = json.loads(response.text)
            attributes = api_response["data"]["attributes"]
            carbon_kg = attributes["carbon_kg"]
            carbon_mt = attributes["carbon_mt"]
            request.session['carbon_kg'] = carbon_kg
            request.session['social_cost'] = carbon_mt*105
            return redirect('results')

    except:
        messages.add_message(request, messages.ERROR,
                             'Your input was invalid. Please try again.')
        route_form = RouteForm()
        return render(request, "car_details.html", {'route_form': route_form})


def get_results(request):
    return render(request, 'results.html', {'carbon_kg': request.session['carbon_kg'],
                                            'social_cost': request.session['social_cost']})


