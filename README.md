# Kitchen Helper

A Flask web application that helps you find recipes based on ingredients you have available, powered by the [Spoonacular Food API](https://spoonacular.com/food-api).

### Backend Routes

- `GET /` - Home page with recipe search
- `POST /` - Search recipes by ingredients (form submission)
- `GET /about` - About page
- `GET /contact` - Contact form page
- `POST /contact` - Submit contact form
- `GET /recipe/<recipe_id>` - View detailed recipe information
- `POST /api/search` - JSON API endpoint for searching recipes