import requests

from config import API_OPEN_WEATHER_KEY, OPEN_WEATHER_BASE_URL, OPEN_WEATHER_API_KEY_START


def get_current_city_weather(city):
    city_url = f'&q={city}'
    url = OPEN_WEATHER_BASE_URL + OPEN_WEATHER_API_KEY_START + API_OPEN_WEATHER_KEY + city_url
    request_result = requests.get(url)
    return request_result.json().get('main').get('temp')


def get_calorie_goal(weight, height, age):
    return 10 * weight + 6.25 * height - 5 * age


def get_water_goal(weight, activity, city):
    weather = get_current_city_weather(city)
    if weather > 25:
        weather_coef = int(weather - 25) * 100
    else:
        weather_coef = 0

    return weight * 30 + activity // 30 * 500 + weather_coef


def get_food_info(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:  # Проверяем, есть ли найденные продукты
            first_product = products[0]
            return float(first_product.get('nutriments', {}).get('energy-kcal_100g', 0))
        return 100
    print(f"Ошибка: {response.status_code}")
    return None


def calculate_burned_calories(activity_type, weight, duration):
    calories_coefs_values = {
        "бег": 10.0,
        "плавание": 8.0,
        "велосипед": 7.5,
        "ходьба": 3.5,
        "йога": 2.5,
        "силовая": 5.0,
        "танцы": 4.5
    }

    water_coefs_values = {
        "бег": 10.0,
        "плавание": 7.0,
        "велосипед": 9.0,
        "ходьба": 4.0,
        "йога": 2.0,
        "силовая": 6.0,
        "танцы": 5.0
    }

    calories_coef = calories_coefs_values.get(activity_type.lower(), 5.0)
    water_coef = water_coefs_values.get(activity_type.lower(), 5.0)

    burned_calories = calories_coef * 3.5 * (weight / 200) * duration
    required_water = water_coef * duration

    return int(burned_calories), int(required_water)


def get_sport_recommendations(excess_calories, weight, available_time, city):

    weather = get_current_city_weather(city)
    if weather < 15:
        activities = ["плавание", "йога", "силовая", "танцы"]
    else:
        activities = ["бег", "велосипед", "ходьба"]

    recommendations = []

    for activity in activities:
        burned_calories, extra_water = calculate_burned_calories(activity, weight, available_time)

        if burned_calories > 0:
            needed_time = int((excess_calories * available_time) / burned_calories)
        else:
            needed_time = 0

        recommendations.append({
            "activity": activity,
            "calories_may_burn": burned_calories,
            "water_needed": extra_water,
            "time_to_goal": needed_time
        })

    recommendations.sort(key=lambda x: x['calories_may_burn'], reverse=True)

    return recommendations
