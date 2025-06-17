import pandas as pd


compatibility_scores = {
    "Highly Compatible": 3,
    "Moderately Compatible": 2,
    "Compatible": 1
}
df = pd.read_csv("datasets/taste_trios.csv")
df["Score"] = df["Classification Output"].map(compatibility_scores)
df = df.sort_values("Score", ascending=False).drop(columns=["Classfication Output", "Score"])


def find_matching_ingredient(ingredientOne: str, ingredientTwo: str) -> list[str]:
    if not (df == ingredientOne).any().any() or not (df == ingredientTwo).any().any():
        return -1
    compatible_ingredients = []
    for row in df.iterrows():
        ingredients = tuple(row)
        if ingredientOne in ingredients and ingredientTwo in ingredients:
            third = [i for i in ingredients if i not in (ingredientOne, ingredientTwo)][0]
            compatible_ingredients.append(third)

    return compatible_ingredients

