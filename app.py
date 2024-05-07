from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId from bson

app = Flask(__name__)
app.secret_key = 'secret_key_here'

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['recipe_database']
recipes_collection = db['recipes']

# Define routes and views
@app.route('/')
def index():
    # Fetch and display recipes from MongoDB
    recipes = list(recipes_collection.find())
    return render_template('index.html', recipes=recipes)

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        
        recipe_data = {
            'title': title,
            'description': description,
            'ingredients': ingredients,
            'instructions': instructions
        }
        
        # Insert recipe data into MongoDB
        recipes_collection.insert_one(recipe_data)
        flash("Recipe added successfully!", "success")
        return redirect(url_for('index'))
    
    return render_template('add_recipe.html')

# Add routes for update and delete
@app.route('/update_recipe/<recipe_id>', methods=['GET', 'POST'])
def update_recipe(recipe_id):
    recipe = recipes_collection.find_one({'_id': ObjectId(recipe_id)})
    if recipe:
        if request.method == 'POST':
            # Update recipe data in MongoDB
            recipes_collection.update_one(
                {'_id': ObjectId(recipe_id)},
                {'$set': {
                    'title': request.form['title'],
                    'description': request.form['description'],
                    'ingredients': request.form['ingredients'],
                    'instructions': request.form['instructions']
                }}
            )
            flash("Recipe updated successfully!", "success")
            return redirect(url_for('index'))
        return render_template('update_recipe.html', recipe=recipe)
    flash("Recipe not found!", "error")
    return redirect(url_for('index'))


# Add routes for update and delete
@app.route('/delete_recipe/<recipe_id>', methods=['POST', 'GET'])  # Include POST and GET methods
def delete_recipe(recipe_id):
    if request.method == 'POST':  # Check if the request method is POST
        if request.form.get('_method') == 'DELETE':  # Check if the method override is DELETE
            recipes_collection.delete_one({'_id': ObjectId(recipe_id)})
            flash("Recipe deleted successfully!", "success")
            return redirect(url_for('index'))
    elif request.method == 'GET':  # Handle GET requests for the delete confirmation page
        recipe = recipes_collection.find_one({'_id': ObjectId(recipe_id)})
        if recipe:
            return render_template('delete_recipe.html', recipe=recipe)
    return methodNotAllowed(['POST', 'GET'])  # type: ignore # Return method not allowed for other methods




if __name__ == '__main__':
    app.run(debug=True)
