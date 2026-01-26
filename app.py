import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'mydevkey123'

SPOONACULAR_API_KEY = 'af307cfbe92e4047b0ef9c205d310b55'
SPOONACULAR_BASE_URL = 'https://api.spoonacular.com/recipes'


def search_recipes_by_ingredients(ingredients, number=10, ranking=1, ignore_pantry=True):

    if not SPOONACULAR_API_KEY or SPOONACULAR_API_KEY == 'YOUR_API_KEY_HERE':
        return {'error': 'API key not configured. Please set SPOONACULAR_API_KEY environment variable.'}
    
    ingredients_str = ','.join(ingredients)
    
    url = f"{SPOONACULAR_BASE_URL}/findByIngredients"
    
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'ingredients': ingredients_str,
        'number': number,
        'ranking': ranking,
        'ignorePantry': str(ignore_pantry).lower()
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Spoonacular API: {e}")
        return {'error': f'Failed to fetch recipes: {str(e)}'}


def get_recipe_information(recipe_id):
    if not SPOONACULAR_API_KEY or SPOONACULAR_API_KEY == 'YOUR_API_KEY_HERE':
        return {'error': 'API key not configured.'}
    
    url = f"{SPOONACULAR_BASE_URL}/{recipe_id}/information"
    params = {
        'apiKey': SPOONACULAR_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipe information: {e}")
        return {'error': f'Failed to fetch recipe details: {str(e)}'}


@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize session data if not exists
    if 'shopping_list' not in session:
        session['shopping_list'] = []
    if 'favorites' not in session:
        session['favorites'] = []
    if 'custom_recipes' not in session:
        session['custom_recipes'] = []
    
    recipes = []
    ingredients_list = []
    error_message = None
    filter_type = request.args.get('filter', 'all') 
    
    if request.method == 'POST':
        # Get ingredients
        if request.is_json:
            data = request.get_json()
            ingredients = data.get('ingredients', [])
        else:
            ingredients_input = request.form.get('ingredients', '')
            if ingredients_input:
                ingredients = [ing.strip() for ing in ingredients_input.split(',') if ing.strip()]
            else:
                ingredients = []
        
        if ingredients:
            session['last_search_ingredients'] = ingredients
            result = search_recipes_by_ingredients(ingredients, number=10)
            if 'error' in result:
                error_message = result['error']
            else:
                recipes = result if isinstance(result, list) else []
                ingredients_list = ingredients
        else:
            error_message = "Please provide at least one ingredient."

    if request.method == 'GET' and not ingredients_list:
        last_search = session.get('last_search_ingredients', [])
        if last_search and filter_type == 'all':
            result = search_recipes_by_ingredients(last_search, number=10)
            if 'error' not in result:
                recipes = result if isinstance(result, list) else []
                ingredients_list = last_search
    
    # Get shopping list and favorites from session
    shopping_list = session.get('shopping_list', [])
    favorites = session.get('favorites', [])
    custom_recipes = session.get('custom_recipes', [])

    if filter_type == 'favorites':
        if recipes:
            favorite_ids = [fav['id'] for fav in favorites]
            display_recipes = [r for r in recipes if r.get('id') in favorite_ids]
        else:
            display_recipes = favorites
    else:
        display_recipes = custom_recipes + recipes
        if not recipes and not ingredients_list and favorites:
            display_recipes = custom_recipes + favorites
    
    # Calculate shopping list stats
    total_items = len(shopping_list)
    done_items = sum(1 for item in shopping_list if item.get('checked', False))
    
    # If no recipes found and no ingredients searched, get random recipes for inspiration
    random_recipes = []
    if filter_type != 'favorites' and not display_recipes and not ingredients_list and request.method == 'GET':
        try:
            random_url = f"{SPOONACULAR_BASE_URL}/random"
            params = {'apiKey': SPOONACULAR_API_KEY, 'number': 5}
            response = requests.get(random_url, params=params, timeout=10)
            if response.status_code == 200:
                random_data = response.json()
                if isinstance(random_data, dict):
                    random_recipes = random_data.get('recipes', [])
                elif isinstance(random_data, list):
                    random_recipes = random_data
        except Exception as e:
            print(f"Error fetching random recipes: {e}")
            random_recipes = []
    
    return render_template(
        'index.html',
        recipes=recipes,
        display_recipes=display_recipes,
        ingredients_list=ingredients_list,
        error_message=error_message,
        shopping_list=shopping_list,
        favorites=favorites,
        filter_type=filter_type,
        total_items=total_items,
        done_items=done_items,
        random_recipes=random_recipes
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        print("=" * 50)
        print("FORM SUBMISSION RECEIVED:")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("=" * 50)
        
        return render_template('contact.html', success=True)
    
    return render_template('contact.html', success=False)


@app.route('/api/search', methods=['POST'])
def api_search():
 
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.get_json()
    ingredients = data.get('ingredients', [])
    
    if not ingredients:
        return jsonify({'error': 'Ingredients list is required'}), 400
    
    result = search_recipes_by_ingredients(ingredients, number=10)
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result)


@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    if 'favorites' not in session:
        session['favorites'] = []
    
    recipe_info = get_recipe_information(recipe_id)
    
    if 'error' in recipe_info:
        return render_template('error.html', error_message=recipe_info['error']), 500
    
    # is recipe in fav?
    favorites = session.get('favorites', [])
    is_favorite = any(fav.get('id') == recipe_id for fav in favorites)
    
    return render_template('recipe_detail.html', recipe=recipe_info, is_favorite=is_favorite)

@app.route('/recipes/custom/add', methods=['POST'])
def add_custom_recipe():
    if 'custom_recipes' not in session:
        session['custom_recipes'] = []

    title = request.form.get('title', '').strip()
    image = request.form.get('image', '').strip()
    description = request.form.get('description', '').strip()
    ready_in_minutes_raw = request.form.get('ready_in_minutes', '').strip()
    servings_raw = request.form.get('servings', '').strip()

    if not title:
        return redirect(request.referrer or url_for('index'))

    def _parse_int(value):
        try:
            return int(value) if value else None
        except ValueError:
            return None

    ready_in_minutes = _parse_int(ready_in_minutes_raw)
    servings = _parse_int(servings_raw)

    existing_ids = [
        recipe.get('id')
        for recipe in session['custom_recipes']
        if isinstance(recipe.get('id'), int)
    ]
    new_id = max(existing_ids, default=0) + 1

    session['custom_recipes'].append({
        'id': new_id,
        'title': title,
        'image': image,
        'description': description,
        'readyInMinutes': ready_in_minutes,
        'servings': servings,
        'is_custom': True
    })
    session.modified = True

    return redirect(request.referrer or url_for('index'))


@app.route('/recipes/custom/remove/<int:recipe_id>', methods=['POST'])
def remove_custom_recipe(recipe_id):
    if 'custom_recipes' in session:
        session['custom_recipes'] = [
            recipe for recipe in session['custom_recipes']
            if recipe.get('id') != recipe_id
        ]
        session.modified = True

    return_url = request.form.get('return_url', url_for('index'))
    return redirect(return_url)

# Shopping List Routes
@app.route('/shopping-list/add', methods=['POST'])
def add_shopping_item():

    if 'shopping_list' not in session:
        session['shopping_list'] = []
    
    item_name = request.form.get('item_name', '').strip()
    item_quantity = request.form.get('item_quantity', '').strip()
    
    if item_name:
        new_item = {
            'id': len(session['shopping_list']),
            'name': item_name,
            'quantity': item_quantity if item_quantity else '',
            'checked': False
        }
        session['shopping_list'].append(new_item)
        session.modified = True
        print(f"Added to shopping list: {item_name} ({item_quantity})")
    
    return redirect(url_for('index'))


@app.route('/shopping-list/remove/<int:item_id>', methods=['POST'])
def remove_shopping_item(item_id):

    if 'shopping_list' in session:
        session['shopping_list'] = [item for item in session['shopping_list'] if item.get('id') != item_id]
        session.modified = True
        print(f"Removed shopping list item ID: {item_id}")
    
    return redirect(url_for('index'))


@app.route('/shopping-list/toggle/<int:item_id>', methods=['POST'])
def toggle_shopping_item(item_id):
    if 'shopping_list' in session:
        for item in session['shopping_list']:
            if item.get('id') == item_id:
                item['checked'] = not item.get('checked', False)
                session.modified = True
                print(f"Toggled shopping list item ID: {item_id} to {item['checked']}")
                break
    
    return redirect(url_for('index'))


# Favs Routes
@app.route('/favorites/add', methods=['POST'])
def add_favorite():
    if 'favorites' not in session:
        session['favorites'] = []

    recipe_id = request.form.get('recipe_id')
    recipe_title = request.form.get('recipe_title', 'Untitled Recipe')
    recipe_image = request.form.get('recipe_image', '')

    if recipe_id:
        recipe_id = int(recipe_id)
        if not any(f.get('id') == recipe_id for f in session['favorites']):
            session['favorites'].append({
                'id': recipe_id,
                'title': recipe_title,
                'image': recipe_image
            })
            session.modified = True
            print(f"Added to favorites: {recipe_title} (ID: {recipe_id})")
        else:
            print(f"Recipe {recipe_id} already in favorites")

    return redirect(request.referrer or url_for('index'))



@app.route('/favorites/remove/<int:recipe_id>', methods=['POST'])
def remove_favorite(recipe_id):

    if 'favorites' in session:
        session['favorites'] = [fav for fav in session['favorites'] if fav.get('id') != recipe_id]
        session.modified = True
        print(f"Removed from favorites: Recipe ID {recipe_id}")
    
    return_url = request.form.get('return_url', url_for('index'))
    return redirect(return_url)


if __name__ == '__main__':
    # if API key is configured
    if not SPOONACULAR_API_KEY or SPOONACULAR_API_KEY == 'YOUR_API_KEY_HERE':
        print("\n⚠️  WARNING: SPOONACULAR_API_KEY not configured!")
    else:
        print(f"✓ Spoonacular API key configured")
    
    print("Press Ctrl+C to stop the server\n")
    app.run(debug=True)