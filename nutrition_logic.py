"""
Nutrition calculations. Pure functions: no UI, no file access.

A "selection" is what the astronaut ate:
    {"breakfast": {"Scrambled eggs": 1.0, "Coffee": 2.0}, "lunch": {...}, ...}
(food name -> number of servings).
"""

from nutrition_data import MEALS, MENU, NUTRIENTS, ROTATION_LENGTH

LOW_BELOW = 70    # percent: under this a "min" nutrient is clearly low
MET_AT = 100      # percent: at or over this a "min" nutrient is met / a "max" one is hit


def rotation_day(mission_day):
    """Mission day 1..N -> menu day 1..8 (the menu repeats every 8 days)."""
    return (mission_day - 1) % ROTATION_LENGTH + 1


def menu_for_day(mission_day):
    """{"breakfast": [...], "lunch": [...], "dinner": [...], "snacks": [...]} for that day."""
    day = MENU[rotation_day(mission_day)]
    return {meal: list(day[meal]) for meal in MEALS}


def compute_intake(selection, foods):
    """
    Add up nutrients for everything selected.
    Returns (totals, missing): totals maps nutrient key -> amount; missing lists
    selected foods that have no data in `foods`, so the UI can warn about them.
    """
    totals = {key: 0.0 for key, *_ in NUTRIENTS}
    missing = []
    for meal in MEALS:
        for food, servings in selection.get(meal, {}).items():
            if servings <= 0:
                continue
            values = foods.get(food)
            if not values:
                if food not in missing:
                    missing.append(food)
                continue
            for key in totals:
                totals[key] += float(values.get(key) or 0) * servings
    return totals, missing


def status_for(percent, kind):
    """'low' / 'near' / 'met' for min-nutrients, 'ok' / 'over' for max-nutrients."""
    if kind == "max":
        return "over" if percent > MET_AT else "ok"
    if percent >= MET_AT:
        return "met"
    return "low" if percent < LOW_BELOW else "near"


def compare(totals):
    """One row per nutrient, in chart order: intake vs target as an amount and a percent."""
    rows = []
    for key, name_en, name_ar, unit, target, kind in NUTRIENTS:
        amount = totals.get(key, 0.0)
        percent = amount / target * 100
        rows.append({
            "key": key, "name_en": name_en, "name_ar": name_ar, "unit": unit,
            "kind": kind, "amount": amount, "target": target, "percent": percent,
            "status": status_for(percent, kind),
        })
    return rows
