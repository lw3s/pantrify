from enum import IntEnum
import re

import requests


Cuisine = int
class Cuisines(IntEnum):
    MEXICAN=1
    ITALIAN=2
    GREEK=3
    INDIAN=4
    THAI=5
    CHINESE=6


def get_cuisine_ingredients(cuisine: Cuisine) -> list[str]:
    """
    Fetch all of the ingredients for all of the featured recipes from the allrecipes.com page for the input cuisine

    @param  cuisine one of the 6 cuisines laid out in Cuisines enum
    @return         a list of the ingredients as described above
    """
    CUISINE_LINKS = [
        "https://www.allrecipes.com/recipes/728/world-cuisine/latin-american/mexican/",
        "https://www.allrecipes.com/recipes/723/world-cuisine/european/italian/",
        "https://www.allrecipes.com/recipes/731/world-cuisine/european/greek/",
        "https://www.allrecipes.com/recipes/233/world-cuisine/asian/indian/",
        "https://www.allrecipes.com/recipes/702/world-cuisine/asian/thai/",
        "https://www.allrecipes.com/recipes/695/world-cuisine/asian/chinese/"
    ]
    LIST_ITEM = r"{\n\"@type\": \"ListItem\"\n,\"position\": [0-9]+\n,\"url\": \"https://www.allrecipes.com/recipe/.+/\"\n}"
    LINK = r"https://www.allrecipes.com/recipe/.+/"

    cuisine_link = CUISINE_LINKS[cuisine-1]
    cuisine_page = requests.get(cuisine_link).text

    items = re.findall(LIST_ITEM, cuisine_page)
    links = re.findall(LINK, "".join(items))
    full_bow = [ get_ingredients_from_recipe(i) for i in links ]
    return sum(full_bow, start = [])


def get_ingredients_from_recipe(link: str) -> list[str]:
    """
    Helper function for get_cuisine_ingredients; fetches the ingredients from a recipe page

    @param  link    the link to the recipe
    @return         a list of strings representing the ingredients in the recipe
    """
    INGREDIENT_NAME = r"<span data-ingredient-name=\"true\">.+</span>"
    string_form = requests.get(link).text
    ingredients = re.findall(INGREDIENT_NAME, string_form)
    ingredients = [ i[34:-7] for i in ingredients ]
    return ingredients

