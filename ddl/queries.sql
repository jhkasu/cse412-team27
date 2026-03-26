
------------------------- ADMIN CONTROLS -----------------------------------
--Checking db users --
select 'Find number of keto users in database';
select count(*) as keto_users from user_preference where preference_value = 'keto';
select 'Find number of vegan users in database';
select count(*) as vegan_users from user_preference where preference_value = 'vegan';

select 'Find number of users in database';
select count(*) as total_users from user_account;

-- INSERT/DELETE food from db --
select 'Inserting and deleting food from db';
select count (distinct fdc_id) as total_foods_in_db from food;
INSERT INTO food (fdc_id, data_type, description, category_id) VALUES (1, 'SR Legacy', 'temp_food, canned', 1);
select count (distinct fdc_id) as total_foods_in_db from food;
delete from food where fdc_id = 1;


---------------------------- USER CONTROLS ---------------------------------
-- Create account --
select 'Create user account';
INSERT INTO user_account (email, password) VALUES ('temp_user@gmail.com', 'hashed_password');

-- Viewing user preferences --
select 'viewing user preferences';
SELECT ua.email, up.preference_key, up.preference_value
FROM user_account ua
JOIN user_preference up ON ua.user_id = up.user_id
WHERE ua.email = 'user1@gmail.com';

-- Updating user preferences (diet) --
select 'updating user diet preferences';
UPDATE user_preference up 
SET preference_value = 'vegan'
FROM user_account ua
WHERE up.user_id = ua.user_id
AND ua.email = 'user1@gmail.com'
AND up.preference_key = 'diet';

-- deleting accounts --
delete from user_account where email = 'user1@gmail.com';

-- Checking saved food in saved food comparison table --
select 'see all food in saved food comparison table';
SELECT scf.food_comparison_id,
       scf.sort_order,
       f.description
FROM saved_comparison_food scf
JOIN food f ON scf.fdc_id = f.fdc_id
ORDER BY scf.sort_order;

----------------------------------- DB general queries ---------------------------

-- Inventory search and filtering ---
select 'See all available food, sorted alphabetically';
select * from food order by description ASC;

select 'Find number of specific food category: breads and buns';
select * from food where category_id = 4 order by description ASC;

select 'Find number of food in each category';
select category_id, COUNT(*) AS num_of_food_per_category from food group by category_id;

select 'Find number of distinct foods in database';
select count (distinct fdc_id) as total_foods_in_db from food;

select 'find food by specific name with partial matching';
select * from food where description ILIKE '%HEALTHY%' limit 5;

-- sorting food ---
select 'Find 10 lowest carbs/protein in food database';
select f.description, n.amount as carbs from food_nutrient n join food f on n.fdc_id = f.fdc_id where
n.nutrient = 'Carbohydrate, by difference' order by n.amount ASC limit 10;

select f.description, n.amount as Protein from food_nutrient n join food f on n.fdc_id = f.fdc_id where
n.nutrient = 'Protein' order by n.amount ASC limit 10;



