import grequests
import requests

import re
import random
import json
from collections import Counter

from cuisines import Cuisine


def make_trios(cuisine: Cuisine) -> dict[tuple[int, ...], int]:
    """
    Use build_train_data to create a dictionary of trios for the model.

    @param  cuisine one of the 5 cuisines laid out in Cuisines enum
    @return         a dictionary where the keys are tuples of three ingredient indices and the values are 1 if the trio is correct, -1 otherwise
    """
    correct_ingredients, incorrect_ingredients = build_train_data(cuisine)
    ret = {}
    for _ in [form_triplets(i) for i in correct_ingredients]:
        for triplet in _:
            print(triplet)
            ret[*triplet] = 1
    for _ in [form_triplets(i) for i in incorrect_ingredients]:
        for triplet in _:
            print(triplet)
            ret[*triplet] = -1
    return ret


def form_triplets(ingredients: list[int]) -> list[list[int]]:
    """
    Helper function for make_trios; forms all possible triplets of ingredients from the input list

    @param  ingredients a list of ingredient indices
    @return            a list of lists, where each inner list is a triplet of ingredient indices
    """
    item_pool = []
    for idx, count in enumerate(ingredients):
        item_pool.extend([idx] * count)

    item_counter = Counter(item_pool)
    result = []

    while sum(item_counter.values()) >= 3:
        distinct_items = [item for item in item_counter if item_counter[item] > 0]
        if len(distinct_items) >= 3:
            group = distinct_items[:3]
        else:
            group = []
            for item in item_counter:
                group.extend([item] * min(item_counter[item], 3 - len(group)))
                if len(group) == 3:
                    break

        for item in group:
            item_counter[item] -= 1
            if item_counter[item] == 0:
                del item_counter[item]

        group_counts = [0] * len(ingredients)
        for item in group:
            group_counts[item] += 1

        if all(x <= 1 for x in group_counts):
            result.append(group_counts)

    return result


def build_train_data(cuisine: Cuisine) -> tuple[list[list[int]], list[list[int]]]:
    """
    Use get_cuisine_ingredients to build training data for the model.

    @param  cuisine one of the 5 cuisines laid out in Cuisines enum
    @return         a tuple of two lists: the correct ingredients and the incorrect ingredients
    """
    with open("datasets/ingredients.json") as fp:
        possible_ingredients: list[str] = json.load(fp)
    all_ingredients: list[list[list[str]]] = [get_cuisine_ingredients(i) for i in range(1, 6)]
    for i in range(len(all_ingredients)):
        if i != cuisine - 1:
            all_ingredients[i] = random.sample(all_ingredients[i], len(all_ingredients[i]) // 4)
    for sub_cuisine in all_ingredients:
        for i in range(len(sub_cuisine)):
            sub_cuisine[i] = count(possible_ingredients, sub_cuisine[i])

    correct_ingredients: list[list[int]] = all_ingredients.pop(cuisine - 1)
    incorrect_ingredients: list[list[int]] = sum(all_ingredients, start=[])
    is_in_correct: list[bool] = [True] * len(possible_ingredients)
    for recipe in correct_ingredients:
        for i in range(len(is_in_correct)):
            is_in_correct[i] |= bool(recipe[i])
    for recipe in incorrect_ingredients:
        for i in range(len(possible_ingredients)):
            recipe[i] &= not is_in_correct[i]

    return correct_ingredients, incorrect_ingredients


def count(possible: list[str], raw: list[str]) -> list[int]:
    """
    Count how many times each ingredient from possible appears in raw

    @param  possible a list of all possible ingredients
    @param  raw      a list of ingredients to count
    @return          a list of counts, where the i-th element is the count of the i-th ingredient in possible
    """
    counts = [0] * len(possible)
    for raw_ingredient in raw:
        for j, possible_ingredient in enumerate(possible):
            if raw_ingredient.find(possible_ingredient) != -1:
                counts[j] += 1
    return counts


def get_cuisine_ingredients(cuisine: Cuisine) -> list[list[str]]:
    """
    Fetch all of the ingredients for all of the featured recipes from the allrecipes.com page for the input cuisine

    @param  cuisine one of the 5 cuisines laid out in Cuisines enum
    @return         a list of the ingredients as described above
    """
    CUISINE_LINKS = [
        "https://www.allrecipes.com/recipes/728/world-cuisine/latin-american/mexican/",
        "https://www.allrecipes.com/recipes/723/world-cuisine/european/italian/",
        "https://www.allrecipes.com/recipes/233/world-cuisine/asian/indian/",
        "https://www.allrecipes.com/recipes/235/world-cuisine/middle-eastern/",
        "https://www.allrecipes.com/recipes/695/world-cuisine/asian/chinese/"
    ]
    LIST_ITEM = r"{\n\"@type\": \"ListItem\"\n,\"position\": [0-9]+\n,\"url\": \"https://www.allrecipes.com/recipe/.+/\"\n}"
    LINK = r"https://www.allrecipes.com/recipe/.+/"

    cuisine_link = CUISINE_LINKS[cuisine - 1]
    cuisine_page = requests.get(cuisine_link).text

    items = re.findall(LIST_ITEM, cuisine_page)
    links = re.findall(LINK, "".join(items))
    rs = (grequests.get(link) for link in links)
    recipes = grequests.map(rs, size=10)
    return [get_ingredients_from_recipe(i.text) for i in recipes]


def get_ingredients_from_recipe(recipe: str) -> list[str]:
    """
    Helper function for get_cuisine_ingredients; fetches the ingredients from a recipe page

    @param  recipe  the text of the recipe
    @return         a list of strings representing the ingredients in the recipe
    """
    INGREDIENT_NAME = r"<span data-ingredient-name=\"true\">.+</span>"
    ingredients = re.findall(INGREDIENT_NAME, recipe)
    ingredients = [i[34:-7] for i in ingredients]
    return ingredients

