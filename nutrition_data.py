"""
Nutrition data for the Space Health app: the 8-day menu rotation, the list of
micronutrients, and the daily targets. No logic lives here, only data and loading.

Real food values are NOT hard-coded. They are loaded from food_nutrients.json
(see load_food_nutrients). Format:

    {
      "Scrambled eggs": {"vitamin_a": 80.0, "iron": 0.9, ...},   # per 1 serving
      ...
    }

Keys are the food names used in MENU below. Any nutrient left out counts as unknown.
"""

import json
import re
from pathlib import Path

FOOD_FILE = Path(__file__).with_name("food_nutrients.json")

MEALS = ["breakfast", "lunch", "dinner", "snacks"]
ROTATION_LENGTH = 8


# ------------------------------------------------------------------ nutrients + targets
# kind "min": aim to reach the target.  kind "max": stay at or under the limit.
# Targets are general adult reference values (common RDA / AI figures, rounded).
# They are PLACEHOLDERS: replace with the values your mission requires.
NUTRIENTS = [
    # key,          English,              Arabic,                unit,  target, kind
    ("vitamin_a",   "Vitamin A",          "فيتامين أ",           "µg",   900,  "min"),
    ("vitamin_c",   "Vitamin C",          "فيتامين ج",           "mg",    90,  "min"),
    ("vitamin_d",   "Vitamin D",          "فيتامين د",           "µg",    15,  "min"),
    ("vitamin_e",   "Vitamin E",          "فيتامين هـ",          "mg",    15,  "min"),
    ("vitamin_k",   "Vitamin K",          "فيتامين ك",           "µg",   120,  "min"),
    ("thiamin",     "Thiamin (B1)",       "الثيامين (ب1)",       "mg",   1.2,  "min"),
    ("riboflavin",  "Riboflavin (B2)",    "الريبوفلافين (ب2)",   "mg",   1.3,  "min"),
    ("niacin",      "Niacin (B3)",        "النياسين (ب3)",       "mg",    16,  "min"),
    ("vitamin_b6",  "Vitamin B6",         "فيتامين ب6",          "mg",   1.3,  "min"),
    ("folate",      "Folate (B9)",        "الفولات (ب9)",        "µg",   400,  "min"),
    ("vitamin_b12", "Vitamin B12",        "فيتامين ب12",         "µg",   2.4,  "min"),
    ("calcium",     "Calcium",            "الكالسيوم",           "mg",  1000,  "min"),
    ("iron",        "Iron",               "الحديد",              "mg",     8,  "min"),
    ("magnesium",   "Magnesium",          "المغنيسيوم",          "mg",   400,  "min"),
    ("potassium",   "Potassium",          "البوتاسيوم",          "mg",  3400,  "min"),
    ("phosphorus",  "Phosphorus",         "الفوسفور",            "mg",   700,  "min"),
    ("zinc",        "Zinc",               "الزنك",               "mg",    11,  "min"),
    ("selenium",    "Selenium",           "السيلينيوم",          "µg",    55,  "min"),
    ("copper",      "Copper",             "النحاس",              "mg",   0.9,  "min"),
    ("iodine",      "Iodine",             "اليود",               "µg",   150,  "min"),
    ("sodium",      "Sodium",             "الصوديوم",            "mg",  2300,  "max"),
]
NUTRIENT_KEYS = [n[0] for n in NUTRIENTS]


# ------------------------------------------------------------------ the 8-day menu
# One entry per rotation day. "kcal" is the planned daily total (not charted).
MENU = {
    1: {"kcal": 2650,
        "breakfast": ["Scrambled eggs", "Breakfast sausage", "Flour tortilla", "Orange juice", "Coffee"],
        "lunch": ["Beef stew", "Wheat flatbread", "Broccoli au gratin", "Lemonade"],
        "dinner": ["Shrimp cocktail", "Macaroni and cheese", "Spicy green beans", "Apricot cobbler", "Tea"],
        "snacks": ["Almonds", "Dried fruit"]},
    2: {"kcal": 2700,
        "breakfast": ["Granola with blueberries", "Strawberry breakfast drink", "Cocoa"],
        "lunch": ["Chicken a la king", "Brown rice", "Asparagus", "Mango-peach smoothie"],
        "dinner": ["Barbecued beef brisket", "Mashed potatoes", "Corn", "Chocolate pudding", "Apple cider"],
        "snacks": ["Cashews", "Granola bar"]},
    3: {"kcal": 2600,
        "breakfast": ["Vegetable quiche", "Ham slice", "Pineapple drink", "Coffee"],
        "lunch": ["Cream of mushroom soup", "Tuna salad", "Flour tortilla", "Tropical fruit salad", "Lemonade"],
        "dinner": ["Beef tips with mushrooms", "Noodles", "Carrot coins", "Brownies", "Tea"],
        "snacks": ["Peanut butter and strawberry jam on tortilla"]},
    4: {"kcal": 2750,
        "breakfast": ["Oatmeal with raisins", "Vanilla breakfast drink", "Coffee"],
        "lunch": ["Chicken fajitas", "Black beans", "Flour tortilla", "Mango salad", "Apple cider"],
        "dinner": ["Grilled chicken breast", "Cauliflower with cheese", "Tomatoes and eggplant",
                   "Shortbread cookies", "Tea"],
        "snacks": ["Trail mix", "Candy-coated chocolates"]},
    5: {"kcal": 2680,
        "breakfast": ["Scrambled eggs", "Ham slice", "Wheat flatbread", "Orange juice", "Coffee"],
        "lunch": ["Chicken noodle soup", "Smoked turkey", "Couscous with nuts", "Lemonade"],
        "dinner": ["Beef steak", "Baked beans", "Creamed spinach", "Vanilla flan", "Tea"],
        "snacks": ["Almonds", "Peach ambrosia"]},
    6: {"kcal": 2720,
        "breakfast": ["Granola with blueberries", "Breakfast sausage", "Chocolate breakfast drink"],
        "lunch": ["Chicken and rice", "Green beans with mushrooms", "Tropical fruit salad", "Pineapple drink"],
        "dinner": ["Beef ravioli", "Butternut squash", "Cornbread dressing", "Cake", "Apple cider"],
        "snacks": ["Cashews", "Dried pears"]},
    7: {"kcal": 2640,
        "breakfast": ["Vegetable quiche", "Flour tortilla with honey", "Orange juice", "Coffee"],
        "lunch": ["Chicken consommé", "Chicken pineapple salad", "Wheat flatbread", "Mango-peach smoothie"],
        "dinner": ["Beef fajita strips", "Macaroni and cheese", "Broccoli au gratin", "Butter cookies", "Tea"],
        "snacks": ["Chocolate spread on tortilla", "Almonds"]},
    8: {"kcal": 2760,
        "breakfast": ["Oatmeal", "Breakfast sausage", "Strawberry breakfast drink", "Coffee"],
        "lunch": ["Space cheeseburger", "Corn", "Lemonade"],
        "dinner": ["Caribbean chicken", "Candied yams", "Asparagus", "Chocolate pudding", "Apple cider"],
        "snacks": ["Trail mix", "Cookies"]},
}


# ------------------------------------------------------------------ helpers
def food_id(name):
    """Stable id for a food name, e.g. 'Mango-peach smoothie' -> 'mango-peach-smoothie'."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def all_food_names():
    """Every distinct food on the menu, sorted. Handy for filling in the backend file."""
    return sorted({f for day in MENU.values() for m in MEALS for f in day[m]})


def load_food_nutrients(path=FOOD_FILE):
    """Read the per-serving nutrient table. Returns {} if the file does not exist yet."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {name: vals for name, vals in data.items() if not name.startswith("_")}
