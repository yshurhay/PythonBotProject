from geopy.geocoders import Nominatim


def get_address(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((latitude, longitude))
    return location.address
