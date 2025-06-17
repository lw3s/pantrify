import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from recommender.exact_match import find_matching_ingredient
from recommender.compound_connections import bfs_connections_search
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sklearn.linear_model import LogisticRegression

from cuisines.build_training_data import make_trios
from cuisines.cuisines import Cuisine, cuisine_list


lr_models = [LogisticRegression(max_iter=1000, solver='lbfgs') for _ in range(len(cuisine_list))]
for i in range(len(lr_models)):
    trios = make_trios(i + 1)
    print(trios.values())
    lr_models[i].fit(list(trios.keys()), list(trios.values()))

with open("datasets/ingredients.json") as fp:
    ingredient_list = json.load(fp)

app = FastAPI()

app.mount("/static", StaticFiles(directory="FrontEnd"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("FrontEnd/index.html") as fp:
        return fp.read()


@app.get("/generate-ingredient")
def generate_filtered_ingredient(ingredient1: str, ingredient2: str, cuisine: str):
    res = generate_ingredient(ingredient1, ingredient2)
    if isinstance(res, str):
        return {"third_ingredient", res}
    if cuisine != "default":
        res = filter_by_cuisine(cuisine_list.index(cuisine) + 1, ingredient1, ingredient2, res)
    return {"third_ingredient", ",".join(res)}


def generate_ingredient(ingredient1: str, ingredient2: str):
    ingredient1 = ingredient1.strip()
    ingredient2 = ingredient2.strip()
    matches = find_matching_ingredient(ingredient1, ingredient2)
    if matches == -1:  # Direct connections
        return "Some of the entered ingredients are not found in the dataset"
    bfs_results = bfs_connections_search(ingredient1, ingredient2, 'highly')
    if matches:
        all_results = [matches[0][0]] + list(bfs_results)
        return ", ".join(all_results)
    if bfs_results:
        return ", ".join(bfs_results)
    return "No compatible combinations found, AI thingy goes here"


def filter_by_cuisine(cuisine: Cuisine, input1: str, input2: str, outputs: list[str]) -> list[str]:
    input1, input2 = ingredient_list.index(input1), ingredient_list.index(input2), [ingredient_list.index(output) for output in outputs]
    Xs = [[0] * len(ingredient_list) for _ in range(len(outputs))]
    for i in range(len(Xs)):
        Xs[i][input1] = 1
        Xs[i][input2] = 1
        Xs[i][outputs[i]] = 1
    predictions = lr_models[cuisine - 1].predict_proba(Xs)[:, 1]
    return [outputs[i] for i in range(len(outputs)) if predictions[i] > 0.25]

