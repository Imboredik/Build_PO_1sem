import requests

def get_random_cocktail():
    url = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()["drinks"][0]

        name = data['strDrink']
        instructions = data['strInstructions']
        ingredients = []

        for i in range(1, 16):
            ing = data.get(f"strIngredient{i}")
            measure = data.get(f"strMeasure{i}")
            if ing:
                ingredients.append(f"{measure or ''} {ing}".strip())
        photo_url = data["strDrinkThumb"]
        return name, instructions, ingredients, photo_url
    else:
        return None, None, None, None