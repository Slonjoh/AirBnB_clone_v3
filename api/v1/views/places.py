#!/usr/bin/python3
"""
Defines the RESTful API actions for Places objects
"""

from api.v1.views import app_views
from flask import jsonify, abort, request, make_response, Flask
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.amenity import Amenity
from models.state import State


@app_views.route('/cities/<city_id>/places',
                 methods=['GET'], strict_slashes=False)
def get_places(city_id):
    """Retrieves the list of all Place objects of a City"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>',
                 methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/cities/<city_id>/places',
                 methods=['POST'], strict_slashes=False)
def create_place(city_id):
    """Creates a Place"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    data = request.get_json()
    if data is None:
        abort(400, 'Not a JSON')
    if 'user_id' not in data:
        abort(400, 'Missing user_id')
    if 'name' not in data:
        abort(400, 'Missing name')
    user_id = data['user_id']
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    data['city_id'] = city_id
    place = Place(**data)
    place.save()
    return make_response(jsonify(place.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    data = request.get_json()
    if data is None:
        abort(400, 'Not a JSON')
    for key, value in data.items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    place.save()
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route('/places_search', methods=['POST'])
def places_search():
    """Search for places based on the request body JSON"""
    try:
        search_params = request.get_json()
    except Exception as e:
        return jsonify({"error": "Not a JSON"}), 400

    if not search_params or all(len(v) == 0 for v in search_params.values()):
        places = storage.all(Place).values()
    else:
        states = search_params.get('states', [])
        cities = search_params.get('cities', [])
        amenities = search_params.get('amenities', [])

        if states:
            state_places = [city.places for state_id in states
                            for state in storage.all(State).values()
                            if state.id == state_id
                            for city in state.cities]
        else:
            state_places = []

        if cities:
            city_places = [storage.get(City, city_id).places
                           for city_id in cities]
        else:
            city_places = []

        places = set([place for place_list in state_places + city_places
                      for place in place_list])

        if amenities:
            amenity_set = set(amenities)
            places = [place for place in places
                      if all(amenity_id in
                             (amenity.id for amenity in place.amenities)
                             for amenity_id in amenity_set)]

    return jsonify([place.to_dict() for place in places])
