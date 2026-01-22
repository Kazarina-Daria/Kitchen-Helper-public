import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'mydevkey123'

SPOONACULAR_API_KEY = 'af307cfbe92e4047b0ef9c205d310b55'
SPOONACULAR_BASE_URL = 'https://api.spoonacular.com/recipes'


def search_recipes_by_ingredients(ingredients, number=8):
    """Search recipes by ingredients using Spoonacular API."""
    if not SPOONACULAR_API_KEY:
        return {'error': 'API key missing.'}

    ingredients_str = ','.join(ingredients)
    url = f"{SPOONACULAR_BASE_URL}/findByIngredients"
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'ingredients': ingredients_str,
        'number': number
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error calling Spoonacular API:", e)
        return {'error': f'Failed to fetch recipes: {e}'}


def get_recipe_information(recipe_id):
    """Fetch full recipe info by ID."""
    if not SPOONACULAR_API_KEY:
        return {'error': 'API key missing.'}

    url = f"{SPOONACULAR_BASE_URL}/{recipe_id}/information"
    params = {'apiKey': SPOONACULAR_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching recipe info:", e)
        return {'error': f'Failed to fetch recipe info: {e}'}


@app.route('/', methods=['GET', 'POST'])
def index():
    recipes = []
    error_message = None
    ingredients_list = []

    # Initialize session data
    for key in ['ingredients', 'favorites', 'shopping_list']:
        if key not in session:
            session[key] = []

    if request.method == 'POST':
        ingredients_input = request.form.get('ingredients', '')
        if ingredients_input:
            ingredients_list = [i.strip() for i in ingredients_input.split(',') if i.strip()]
            session['ingredients'] = ingredients_list
        else:
            error_message = "Please enter at least one ingredient."
    else:
        ingredients_list = session.get('ingredients', [])

    if ingredients_list:
        result = search_recipes_by_ingredients(ingredients_list)
        if 'error' in result:
            error_message = result['error']
        else:
            recipes = result if isinstance(result, list) else []

    favorites = session.get('favorites', [])
    shopping_list = session.get('shopping_list', [])
    total_items = len(shopping_list)
    done_items = sum(1 for item in shopping_list if item.get('checked', False))

    return render_template(
        'index.html',
        recipes=recipes,
        error_message=error_message,
        ingredients_list=ingredients_list,
        favorites=favorites,
        random_recipes=[],
        filter_type=request.args.get('filter', 'all'),
        shopping_list=shopping_list,
        total_items=total_items,
        done_items=done_items
    )


@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    if 'favorites' not in session:
        session['favorites'] = []

    recipe_id = request.form.get('recipe_id')
    recipe_title = request.form.get('recipe_title', 'Untitled Recipe')
    recipe_image = request.form.get('recipe_image', '')

    if recipe_id:
        if not any(f.get('id') == int(recipe_id) for f in session['favorites']):
            session['favorites'].append({
                'id': int(recipe_id),
                'title': recipe_title,
                'image': recipe_image
            })
            session.modified = True
            print(f"Added to favorites: {recipe_title}")

    return redirect(request.referrer or url_for('index'))


@app.route('/remove_favorite/<int:recipe_id>', methods=['POST'])
def remove_favorite(recipe_id):
    if 'favorites' in session:
        session['favorites'] = [f for f in session['favorites'] if f.get('id') != recipe_id]
        session.modified = True
        print(f"Removed favorite ID: {recipe_id}")
    return redirect(request.referrer or url_for('index'))


@app.route('/add_shopping_item', methods=['POST'])
def add_shopping_item():
    if 'shopping_list' not in session:
        session['shopping_list'] = []

    item_name = request.form.get('item_name', '').strip()
    item_quantity = request.form.get('item_quantity', '').strip()

    if item_name:
        new_item = {
            'id': len(session['shopping_list']),
            'name': item_name,
            'quantity': item_quantity,
            'checked': False
        }
        session['shopping_list'].append(new_item)
        session.modified = True
        print(f"Added shopping item: {item_name}")
    return redirect(request.referrer or url_for('index'))


@app.route('/toggle_shopping_item/<int:item_id>', methods=['POST'])
def toggle_shopping_item(item_id):
    if 'shopping_list' in session:
        for item in session['shopping_list']:
            if item.get('id') == item_id:
                item['checked'] = not item.get('checked', False)
                break
        session.modified = True
    return redirect(request.referrer or url_for('index'))


@app.route('/remove_shopping_item/<int:item_id>', methods=['POST'])
def remove_shopping_item(item_id):
    if 'shopping_list' in session:
        session['shopping_list'] = [i for i in session['shopping_list'] if i.get('id') != item_id]
        session.modified = True
    return redirect(request.referrer or url_for('index'))


@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    data = get_recipe_information(recipe_id)
    if 'error' in data:
        return render_template('error.html', message=data['error']), 500
    return render_template('recipe_detail.html', recipe=data)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        print(f"Message from {name} ({email}): {message}")
        return render_template('contact.html', success=True)
    return render_template('contact.html', success=False)


if __name__ == '__main__':
    print("Starting Flask app (v2.4 — recipe details + pages)")
    app.run(debug=True, host='0.0.0.0', port=5000)
