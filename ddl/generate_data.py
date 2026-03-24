import random

import requests

API_KEY = "y0fyjw8neebyEYKO7eD2yauejiaTW0eHzU8RfGlV"

NUM_USERS = 50
NUM_FOODS = 20
NUM_RELATIONS = 100


#food data
def fetch_food_data():
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query=healthy&api_key={API_KEY}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    foods = []
    nutrients = []
    categories = {}
    category_counter = 1

    for item in data.get("foods", [])[:NUM_FOODS]:
        fdc_id = item["fdcId"]
        description = item["description"].replace("'", "''")
        data_type = item.get("dataType", "Unknown")
        category_name = item.get("foodCategory", "Unknown").replace("'", "''")

        if category_name not in categories:
            categories[category_name] = category_counter
            category_counter += 1

        category_id = categories[category_name]
        foods.append((fdc_id, data_type, description, category_id))

        for nutrient in item.get("foodNutrients", []):
            name = nutrient["nutrientName"].replace("'", "''")
            value = nutrient.get("value", 0) or 0
            nutrients.append((name, value, fdc_id))

    return foods, nutrients, categories


#users
def generate_users(n):
    users = []
    for i in range(1, n + 1):
        email = f"user{i}@gmail.com"
        password = "hashed_password"
        users.append((email, password))
    return users


#USER PREFERENCES
def generate_preferences(num_users):
    prefs = []
    for user_id in range(1, num_users + 1):
        prefs.append(("diet", random.choice(["vegan", "keto", "none"]), user_id))
    return prefs


#relations between users and foods
def generate_relations(users_count, foods, n):
    relations = []
    food_ids = [f[0] for f in foods]

    for i in range(n):
        user_id = random.randint(1, users_count)
        fdc_id = random.choice(food_ids)
        sort_order = i + 1
        relations.append((sort_order, fdc_id, user_id))

    return relations

#sql queries
def write_sql(foods, nutrients, categories, users, prefs, relations):
    with open("data.sql", "w", encoding="utf-8") as f:
        f.write("-- FOOD CATEGORY\n")
        for name, cid in categories.items():
            f.write(f"INSERT INTO food_category (category_id, name) VALUES ({cid}, '{name}');\n")

        f.write("\n-- FOOD\n")
        for food in foods:
            f.write(
                f"INSERT INTO food (fdc_id, data_type, description, category_id) VALUES ({food[0]}, '{food[1]}', '{food[2]}', {food[3]});\n"
            )

        f.write("\n-- FOOD NUTRIENTS\n")
        for nutrient in nutrients:
            f.write(
                f"INSERT INTO food_nutrient (nutrient, amount, fdc_id) VALUES ('{nutrient[0]}', {nutrient[1]}, {nutrient[2]});\n"
            )

        f.write("\n-- USERS\n")
        for user in users:
            f.write(
                f"INSERT INTO user_account (email, password) VALUES ('{user[0]}', '{user[1]}');\n"
            )

        f.write("\n-- USER PREFERENCES\n")
        for pref in prefs:
            f.write(
                f"INSERT INTO user_preference (preference_key, preference_value, user_id) VALUES ('{pref[0]}', '{pref[1]}', {pref[2]});\n"
            )

        f.write("\n-- SAVED COMPARISON FOOD\n")
        for relation in relations:
            f.write(
                f"INSERT INTO saved_comparison_food (sort_order, fdc_id, user_id) VALUES ({relation[0]}, {relation[1]}, {relation[2]});\n"
            )


#main function
def main():
    print("Fetching food data...")
    foods, nutrients, categories = fetch_food_data()

    print("Generating users...")
    users = generate_users(NUM_USERS)

    print("Generating preferences...")
    prefs = generate_preferences(NUM_USERS)

    print("Generating relations...")
    relations = generate_relations(NUM_USERS, foods, NUM_RELATIONS)

    print("Writing SQL file...")
    write_sql(foods, nutrients, categories, users, prefs, relations)

    print("data.sql generated successfully!")


if __name__ == "__main__":
    main()
