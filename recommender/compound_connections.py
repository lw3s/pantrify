import pandas as pd


taste_trios_df = pd.read_csv("datasets/taste_trios.csv")
highly_trios_df = taste_trios_df[taste_trios_df["Classification Output"] == "Highly Compatible"].drop(columns=["Classification Output"])
moderately_trios_df = taste_trios_df[taste_trios_df["Classification Output"] == "Moderately Compatible"].drop(columns=["Classification Output"])
compatible_trio_df = taste_trios_df[taste_trios_df["Classification Output"] == "Compatible"].drop(columns=["Classification Output"])


def get_all_compatible_ingredients(ingredient: str, compatibility: str) -> set[str]:
    """
    Get all ingredients that are compatible of the given compatibility level with the input ingredient

    @param  ingredient      one of the ingredients in the dataset
    @param  compatibility   "highly" or "moderately" or "compatible"
    @return                 a set of strings representing the ingredients that are compatible with the input ngredient of the given compatibility level
    """
    if compatibility not in ["highly", "moderately", "compatible"]:
        raise ValueError(f'Invalid compatibility: {compatibility}. Must be one of ["highly", "moderately", "compatible"]')
    correct_df = eval(compatibility + "trios_df")
    matchesWithIngredient = correct_df[(correct_df == ingredient).any(axis=1)]

    ingredients_set = set()
    for _, row in matchesWithIngredient.iterrows():
        ingredients_set.update(row)
    ingredients_set.remove(ingredient)
    return ingredients_set


def check_for_connections(ingredient1: str, ingredient2: str, compatibilityLevel: str):
    """
    Check if there is a connection between two ingredients of the given compatibility level by checking if there is a 3rd ingredient that is compatible with both ingredient1 and ingredient2

    @param  ingredient1         one of the ingredients in the dataset
    @param  ingredient2         another one of the ingredients in the dataset
    @param  compatibilityLevel  "highly" or "moderately" or "compatible"
    @return                     Set of ingredients that are compatible with both ingredient1 and ingredient2
    """
    # Assuming it is NOT in the same taste trio, we will check if there is a connection between the two ingredients
    # Goal is to find a 3rd ingredient that is compatible with both ingredient1 and ingredient2, even though ingredient1 and ingredient2 are not in the same taste trio
    # Get all rows where ingredient1 appears in any column
    ingredients1_set = get_all_compatible_ingredients(ingredient1, compatibilityLevel)
    ingredients2_set = get_all_compatible_ingredients(ingredient2, compatibilityLevel)

    # Find overlapping ingredients
    matchesWithBothIngredients = list(ingredients1_set.intersection(ingredients2_set))

    return matchesWithBothIngredients


def bfs_connections_search(ingredient1: str, ingredient2: str, compatibilityLevel: str):
    """
    Perform a BFS search to find all possible connections between two ingredients of the given compatibility level

    @param  ingredient1         one of the ingredients in the dataset
    @param  ingredient2         another one of the ingredients in the dataset
    @param  compatibilityLevel  "highly" or "moderately" or "compatible"
    @return                     Set of all intermediate ingredients found in paths between ingredient1 and ingredient2
    """

    MAX_DEPTH = 4  # Maximum number of "hops" to search through before giving up
    visited_paths = set()
    queue = [(ingredient1, [ingredient1])]  # Queue contains tuples of (current_ingredient, path_so_far), Each path_so_far is a list showing the sequence of ingredients from start to current
    all_paths = []    # Store all valid paths found from ingredient1 to ingredient2
    intermediate_ingredients = set()

    while queue:
        current_ingredient, path = queue.pop(0)  # removes and returns the first element (FIFO queue behavior)
        if len(path) <= MAX_DEPTH:
            compatible_ingredients = get_all_compatible_ingredients(current_ingredient, compatibilityLevel)

            # Check each compatible ingredient
            for next_ingredient in compatible_ingredients:
                new_path = path.copy()
                new_path.append(next_ingredient)
                path_key = tuple(new_path)  # Convert path to tuple for hashing

                if next_ingredient == ingredient2 and len(new_path) <= MAX_DEPTH:
                    if path_key not in visited_paths:
                        visited_paths.add(path_key)
                        all_paths.append(new_path)
                        intermediate_ingredients.update(new_path[1:-1])  # Add all intermediate ingredients (excluding start and end)

                if len(new_path) <= MAX_DEPTH and path_key not in visited_paths:
                    visited_paths.add(path_key)
                    queue.append((next_ingredient, new_path))

    return intermediate_ingredients

