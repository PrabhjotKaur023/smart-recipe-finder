import requests # Used to send HTTP requests to the API

def search_recipes_by_ingredient(ingredient):
    """
    //Searches for recipes containing a main ingredient using TheMealDB API.
    """
    # The URL for the API endpoint to search by ingredient
    api_url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    
    try:
        # Send a request to the API
        response = requests.get(api_url)
        # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()
        
        # Convert the JSON response into a Python dictionary
        data = response.json()
        
        # The API returns a dictionary with a 'meals' key, which is a list of recipes.
        # If 'meals' is None (or the key is missing), it means no recipes were found.
        if data.get('meals'):
            return data['meals']
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        # Handle network-related errors (e.g., no internet connection, DNS failure)
        print(f"An error occurred: {e}")
        return None

# --- Main part of the program where execution starts ---
if __name__ == "__main__":
    print("Welcome to the Smart Recipe Finder! 🍲")
    print("Enter a main ingredient to find recipes for (e.g., chicken, beef, flour).")
    
    # Get user input and remove any leading/trailing whitespace and convert to lowercase
    user_ingredient = input("> ").strip().lower()

    if user_ingredient:
        print(f"\nSearching for recipes with '{user_ingredient}'...")
        # Call our function to get recipes from the API
        recipes = search_recipes_by_ingredient(user_ingredient)
        
        print("\n------------------------------------")
        if recipes:
            print("Here are some recipes we found:")
            # Loop through the list of recipes and print their names
            for recipe in recipes:
                # The recipe name is stored in the 'strMeal' key
                print(f"- {recipe['strMeal']}")
        else:
            print(f"Sorry, no recipes found for '{user_ingredient}'. Please try another ingredient.")
        print("------------------------------------")
    else:
        print("No ingredient entered. Please run the program again.")