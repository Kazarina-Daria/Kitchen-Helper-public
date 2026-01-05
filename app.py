import os
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY', 'af307cfbe92e4047b0ef9c205d310b55')
SPOONACULAR_BASE_URL = 'https://api.spoonacular.com/recipes'


def search_recipes_by_ingredients(ingredients, number=5):
    if not SPOONACULAR_API_KEY or SPOONACULAR_API_KEY == 'YOUR_API_KEY_HERE':
        return {'error': 'API key not configured.'}

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
        print(f"Error calling Spoonacular API: {e}")
        return {'error': f'Failed to fetch recipes: {str(e)}'}


@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page: shows recipes based on ingredients query parameter or form submission"""
    recipes = []
    error_message = None
    ingredients_list = []
    
    if request.method == 'POST':
        ingredients_input = request.form.get('ingredients', '')
    else:
        ingredients_input = request.args.get('ingredients', '')
    
    if ingredients_input:
        ingredients_list = [ing.strip() for ing in ingredients_input.split(',') if ing.strip()]
        if ingredients_list:
            result = search_recipes_by_ingredients(ingredients_list, number=5)
            if 'error' in result:
                error_message = result['error']
            else:
                recipes = result if isinstance(result, list) else []
    
 
    favorites = []  
    random_recipes = []  
    filter_type = 'all'  
    shopping_list = []  
    total_items = 0  
    done_items = 0  
    return render_template('index.html', 
                         recipes=recipes,
                         error_message=error_message,
                         ingredients_list=ingredients_list,
                         favorites=favorites,
                         random_recipes=random_recipes,
                         filter_type=filter_type,
                         shopping_list=shopping_list,
                         total_items=total_items,
                         done_items=done_items)



@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    return f"Recipe detail page for recipe ID: {recipe_id} (not implemented yet)"


@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    return redirect(request.referrer or url_for('index'))


@app.route('/remove_favorite/<int:recipe_id>', methods=['POST'])
def remove_favorite(recipe_id):
    return redirect(request.referrer or url_for('index'))


@app.route('/add_shopping_item', methods=['POST'])
def add_shopping_item():
    return redirect(request.referrer or url_for('index'))


@app.route('/toggle_shopping_item/<int:item_id>', methods=['POST'])
def toggle_shopping_item(item_id):
    return redirect(request.referrer or url_for('index'))


@app.route('/remove_shopping_item/<int:item_id>', methods=['POST'])
def remove_shopping_item(item_id):
    return redirect(request.referrer or url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)