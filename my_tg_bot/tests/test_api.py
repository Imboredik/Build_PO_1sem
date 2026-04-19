import pytest
from unittest.mock import patch, Mock
from my_tg_bot.bot.api import get_random_cocktail


@pytest.fixture
def mock_response():
    mock_data = {
        "drinks": [
            {
                "strDrink": "Test Cocktail",
                "strInstructions": "Mix ingredients.",
                "strIngredient1": "Ingredient1",
                "strMeasure1": "1 oz",
                "strIngredient2": "Ingredient2",
                "strMeasure2": "2 oz",
                "strIngredient3": None,
                "strDrinkThumb": "https://example.com/image.jpg"
            }
        ]
    }
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_data
    return mock_resp


def test_get_random_cocktail_success(mock_response):
    with patch('requests.get', return_value=mock_response) as mock_get:
        name, instructions, ingredients, photo_url = get_random_cocktail()

        assert name == "Test Cocktail"
        assert instructions == "Mix ingredients."
        assert ingredients == ["1 oz Ingredient1", "2 oz Ingredient2"]
        assert photo_url == "https://example.com/image.jpg"
        mock_get.assert_called_once_with("https://www.thecocktaildb.com/api/json/v1/1/random.php")


def test_get_random_cocktail_failure():
    mock_resp = Mock()
    mock_resp.status_code = 500

    with patch('requests.get', return_value=mock_resp):
        name, instructions, ingredients, photo_url = get_random_cocktail()

        assert name is None
        assert instructions is None
        assert ingredients is None
        assert photo_url is None