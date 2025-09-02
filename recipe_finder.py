import requests

def search_recipes_by_ingredient(ingredient):
    """Searches for recipes by a main ingredient."""
    api_url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data.get('meals')
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def get_recipe_details(meal_id):
    """Fetches the full details for a specific recipe by its ID."""
    api_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        # The result is a list containing a single recipe dictionary
        return data['meals'][0] if data.get('meals') else None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def display_recipe(recipe):
    """Formats and displays the full recipe details."""
    print(f"\n--- Recipe: {recipe['strMeal']} ---")
    
    # Display Ingredients and Measures
    print("\nIngredients:")
    # The API returns up to 20 ingredients and measures
    for i in range(1, 21):
        ingredient = recipe.get(f'strIngredient{i}')
        measure = recipe.get(f'strMeasure{i}')
        # Check if the ingredient exists and is not an empty string
        if ingredient:
            print(f"- {measure} {ingredient}")
        else:
            # Stop when we run out of ingredients
            break
            
    # Display Instructions
    print("\nInstructions:")
    # Print instructions, ensuring proper line breaks
    instructions = recipe['strInstructions'].split('\r\n')
    for step in instructions:
        if step: # Avoid printing empty lines
            print(f"{step}\n")

# --- Main part of the program ---
if __name__ == "__main__":
    print("Welcome to the Smart Recipe Finder! 🍲")
    print("Enter a main ingredient to find recipes for (e.g., chicken, beef, flour).")
    
    user_ingredient = input("> ").strip().lower()

    if user_ingredient:
        print(f"\nSearching for recipes with '{user_ingredient}'...")
        recipes = search_recipes_by_ingredient(user_ingredient)
        
        if recipes:
            print("\nHere are the dishes we found. Please choose one:")
            for i, recipe in enumerate(recipes):
                print(f"{i + 1}. {recipe['strMeal']}")
            
            # Ask the user to choose a dish
            try:
                choice = int(input("\nEnter the number of the dish you want to see: "))
                if 1 <= choice <= len(recipes):
                    # Get the ID of the chosen dish
                    chosen_dish = recipes[choice - 1]
                    meal_id = chosen_dish['idMeal']
                    
                    print(f"\nFetching details for {chosen_dish['strMeal']}...")
                    full_recipe = get_recipe_details(meal_id)
                    
                    if full_recipe:
                        display_recipe(full_recipe)
                    else:
                        print("Sorry, could not fetch the recipe details.")
                else:
                    print("Invalid choice. Please enter a number from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else:
            print(f"\nSorry, no recipes found for '{user_ingredient}'.")