import requests

BASE_URL = 'https://api.nationalize.io/'


def get_nationality(name):
    response = requests.get(
        BASE_URL,
        params={'name': name},
    )
    json_response = response.json()
    probablities = json_response.get('country')

    if probablities:
        max_probability_country = max(
            probablities, key=lambda country: country['probability']
        )
        return max_probability_country.get('country_id')
    else:
        return None
