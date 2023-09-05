from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# Get MongoDB URI, DB and Collection from Atlas Service, Environment
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")

# Configuring MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
expenses_collection = db[MONGODB_COLLECTION_NAME]

# Index
@app.route('/')
def index():
    expenses = expenses_collection.find()
    return render_template('index.html', expenses=expenses)

# Add Expense
@app.route('/add', methods=['POST'])
def add_expense():
    expense = {
        'category': request.form.get('category'),
        'price': float(request.form.get('price')),
    }
    expenses_collection.insert_one(expense)
    return redirect(url_for('index'))

# Edit Expense
@app.route('/edit/<expense_id>', methods=['GET', 'POST', 'PUT'])
def edit_expense(expense_id):
    if request.method == 'POST':
        new_category = request.form.get('new_category')
        new_price = float(request.form.get('new_price'))
        updateResult = expenses_collection.update_one({'_id': ObjectId(expense_id)}, {'$set': {'category': new_category, 'price': new_price}})
        print("UpdateResult: ", updateResult.raw_result)
        return redirect(url_for('index'))

    expense = expenses_collection.find_one({'_id': ObjectId(expense_id)})
    return render_template('edit.html', expense=expense)

# Delete Expense
@app.route('/delete/<expense_id>', methods=['GET', 'POST'])
def delete_expense(expense_id):
    deleteResult = expenses_collection.delete_one({'_id': ObjectId(expense_id)})
    print("DeleteResult -> ", deleteResult.raw_result)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')