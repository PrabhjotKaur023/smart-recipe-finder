"""
Smart Recipe Finder: Your Personal Recipe Finder (API Edition)

This script helps you find recipes based on the ingredients you have at home
by searching a live online database. It aims to reduce food waste.

NOTE: This script requires the 'requests' library to be installed.
You can install it by running: pip install requests
"""

import requests
import textwrap
import sys

# API endpoints for TheMealDB
SEARCH_BY_INGREDIENT_URL = "https://www.themealdb.com/api/json/v1/1/filter.php"
LOOKUP_BY_ID_URL = "https://www.themealdb.com/api/json/v1/1/lookup.php"

def get_main_ingredient():
    """
    Gets the main ingredient from the user.
    Returns:
        A single cleaned ingredient string.
    """
    while True:
        print("\nWhat is your main ingredient?")
        main_ingredient = input("> ").strip().lower()
        if main_ingredient:
            return main_ingredient
        else:
            print("Please enter a main ingredient.")

def get_available_ingredients():
    """
    Gets a list of other available ingredients from the user.
    Returns:
        A list of cleaned ingredient strings.
    """
    print("\nWhat other ingredients do you have available? (optional, separate with a comma)")
    user_input = input("> ")
    # Clean the input: lowercase, strip whitespace from each ingredient
    ingredients = [ingredient.strip().lower() for ingredient in user_input.split(',') if ingredient.strip()]
    return ingredients

def search_recipes_online(primary_ingredient):
    """
    Searches for recipes online using a primary ingredient.
    Args:
        primary_ingredient (str): The main ingredient to search for.
    Returns:
        A list of recipe dictionaries (name and id), or None if an error occurs.
    """
    print(f"\n--- Searching for recipes with '{primary_ingredient}' as a main ingredient... ---")
    try:
        response = requests.get(SEARCH_BY_INGREDIENT_URL, params={'i': primary_ingredient})
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        return data.get('meals')
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the recipe API: {e}")
        return None

def get_recipe_details(meal_id):
    """
    Fetches the full details for a specific recipe by its ID.
    Args:
        meal_id (str): The ID of the meal to look up.
    Returns:
        A dictionary containing the full recipe details, or None.
    """
    try:
        response = requests.get(LOOKUP_BY_ID_URL, params={'i': meal_id})
        response.raise_for_status()
        data = response.json()
        return data.get('meals', [None])[0]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipe details: {e}")
        return None

def filter_and_rank_recipes(recipes, user_ingredients_set):
    """
    Filters and ranks recipes based on how many user ingredients they contain.
    This function makes an API call for each recipe to get its full details.

    Args:
        recipes (list): A list of recipe summaries from the initial search.
        user_ingredients_set (set): A set of ingredients the user has.

    Returns:
        A list of recipe dictionaries, sorted by the number of matching ingredients.
    """
    if not recipes:
        return []
        
    ranked_recipes = []
    total_recipes = len(recipes)
    print(f"\n--- Analyzing {total_recipes} recipes to match all your ingredients... ---")

    for i, recipe_summary in enumerate(recipes, 1):
        # Update progress on a single line
        progress_text = f"Checking recipe {i}/{total_recipes}: {recipe_summary['strMeal'][:30]}..."
        sys.stdout.write('\r' + progress_text.ljust(60))
        sys.stdout.flush()

        details = get_recipe_details(recipe_summary['idMeal'])
        if not details:
            continue

        recipe_ingredients_from_api = set()
        for j in range(1, 21):
            ingredient = details.get(f'strIngredient{j}')
            if ingredient and ingredient.strip():
                recipe_ingredients_from_api.add(ingredient.strip().lower())
            else:
                break
        
        # Check for matches. We check if the user's ingredient is a substring
        # of any ingredient in the recipe's list. e.g., "chicken" matches "chicken breast".
        matched_ingredients = set()
        for user_ingredient in user_ingredients_set:
            for recipe_ingredient in recipe_ingredients_from_api:
                if user_ingredient in recipe_ingredient:
                    matched_ingredients.add(user_ingredient)
                    break 
        
        match_count = len(matched_ingredients)

        if match_count > 0:
            details['match_count'] = match_count
            details['total_user_ingredients'] = len(user_ingredients_set)
            ranked_recipes.append(details)
    
    # Clear the progress line
    sys.stdout.write('\r' + ' ' * 60 + '\r')
    sys.stdout.flush()
    print("--- Analysis complete! ---")

    # Sort recipes by match count, descending
    ranked_recipes.sort(key=lambda r: r['match_count'], reverse=True)
    return ranked_recipes


def display_recipe_details(recipe):
    """
    Prints a formatted, complete view of a single recipe.
    """
    if not recipe:
        print("Could not retrieve recipe details.")
        return

    print("\n" + "="*70)
    print(f"Recipe: {recipe.get('strMeal', 'N/A')}")
    print(f"Category: {recipe.get('strCategory', 'N/A')}")
    print(f"Cuisine: {recipe.get('strArea', 'N/A')}")
    print("="*70)

    print("\nIngredients:")
    # The API stores ingredients in separate fields (strIngredient1, strMeasure1, etc.)
    for i in range(1, 21):
        ingredient = recipe.get(f'strIngredient{i}')
        measure = recipe.get(f'strMeasure{i}')
        if ingredient and ingredient.strip():
            # Ensure measure is a string before printing
            measure_str = measure.strip() if measure and measure.strip() else ""
            print(f"  - {measure_str} {ingredient}")
        else:
            # Stop when we run out of ingredients
            break

    print("\nInstructions:")
    instructions = recipe.get('strInstructions', '')
    
    # Split instructions into steps based on new lines and filter out any empty ones
    steps = [step.strip() for step in instructions.split('\n') if step.strip()]

    if not steps:
        print("  No instructions available.")
    else:
        for i, step in enumerate(steps, 1):
            print(f"\n--- Step {i} ---")
            # Use textwrap for readability of each individual step
            for line in textwrap.wrap(step, width=70):
                print(f"  {line}")
        
        print("\n\n--- Recipe complete! Enjoy your meal! ---")

    print("\n" + "="*70)


def main():
    """
    Main function to run the recipe finder application.
    """
    print("="*50)
    print("     Welcome to the Smart Recipe Finder!    ")
    print("   Your personal guide to fighting food waste.  ")
    print("="*50)

    while True:
        primary_ingredient = get_main_ingredient()
        available_ingredients = get_available_ingredients()
        
        # Combine all ingredients for the ranking logic
        all_user_ingredients = [primary_ingredient] + available_ingredients
        user_ingredients_set = set(all_user_ingredients)
        
        initial_recipes = search_recipes_online(primary_ingredient)
        ranked_recipes = filter_and_rank_recipes(initial_recipes, user_ingredients_set)

        if not ranked_recipes:
            print(f"\nSorry, couldn't find any recipes that match your ingredients.")
            print("Try using a different ingredient first, or check your spelling.")
        else:
            print("\nHere are the best matches for your ingredients:\n")
            for i, recipe in enumerate(ranked_recipes, 1):
                match_info = f"({recipe['match_count']}/{recipe['total_user_ingredients']} of your ingredients)"
                print(f"  {i}. {recipe['strMeal']} {match_info}")

            try:
                print("\nEnter the number of the recipe you want to see, or type 'new' to start over.")
                choice = input("> ")
                if choice.lower() == 'new':
                    continue
                
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(ranked_recipes):
                    # Display the recipe and then exit the program
                    display_recipe_details(ranked_recipes[choice_index])
                    print("\nHappy cooking! Thanks for fighting food waste.\n")
                    break
                else:
                    print("Invalid number. Please try again.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter a number from the list or 'new'.")

        print("\nWhat would you like to do next?")
        print("1. Search with new ingredients")
        print("2. Exit")
        next_action = input("> ")
        if next_action == '2':
            print("\nHappy cooking! Thanks for fighting food waste.\n")
            break

if __name__ == "__main__":
    main()

