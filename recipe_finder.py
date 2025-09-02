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
        if ingredient and ingredient.strip():
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
    print("Enter all the ingredients you have, separated by a comma (e.g., chicken, onion, garlic).")
    
    user_input = input("> ").strip().lower()
    user_ingredients = [item.strip() for item in user_input.split(',')]

    if not user_ingredients or user_ingredients == ['']:
        print("No ingredients entered. Goodbye!")
    else:
        # Ask user to choose a primary ingredient for the initial search
        print("\nWhich of these is your main ingredient?")
        primary_ingredient = input(f"Choose from: {', '.join(user_ingredients)}\n> ").strip().lower()

        if primary_ingredient not in user_ingredients:
            print("Invalid choice. The main ingredient must be from your list.")
        else:
            print(f"\nSearching for recipes with '{primary_ingredient}' as the main ingredient...")
            recipes = search_recipes_by_ingredient(primary_ingredient)
            
            if recipes:
                # --- NEW: Scoring and Sorting Logic ---
                scored_recipes = []
                print("Now scoring recipes based on all your ingredients...")

                # Limit to checking the top 10 results for speed
                for dish in recipes[:10]:
                    details = get_recipe_details(dish['idMeal'])
                    if details:
                        recipe_ingredients = set()
                        for i in range(1, 21):
                            ingredient = details.get(f'strIngredient{i}')
                            if ingredient and ingredient.strip():
                                recipe_ingredients.add(ingredient.lower())
                        
                        # Score is the number of user ingredients found in the recipe
                        match_count = len(set(user_ingredients).intersection(recipe_ingredients))
                        scored_recipes.append({
                            'name': dish['strMeal'],
                            'id': dish['idMeal'],
                            'score': match_count
                        })
                
                # Sort the recipes by the highest score
                sorted_recipes = sorted(scored_recipes, key=lambda x: x['score'], reverse=True)
                
                print("\nHere are the best matches we found. Please choose one:")
                for i, recipe in enumerate(sorted_recipes[:5]): # Show top 5
                    print(f"{i + 1}. {recipe['name']} (Matching Ingredients: {recipe['score']})")
                
                # Ask the user to choose a dish
                try:
                    choice = int(input("\nEnter the number of the dish you want to see: "))
                    if 1 <= choice <= len(sorted_recipes[:5]):
                        # Get the ID of the chosen dish from our new sorted list
                        chosen_dish_id = sorted_recipes[choice - 1]['id']
                        chosen_dish_name = sorted_recipes[choice - 1]['name']
                        
                        print(f"\nFetching details for {chosen_dish_name}...")
                        full_recipe = get_recipe_details(chosen_dish_id)
                        
                        if full_recipe:
                            display_recipe(full_recipe)
                        else:
                            print("Sorry, could not fetch the recipe details.")
                    else:
                        print("Invalid choice. Please enter a number from the list.")
                except (ValueError, IndexError):
                    print("Invalid input. Please enter a number.")
            else:
                print(f"\nSorry, no recipes found for '{primary_ingredient}'.")