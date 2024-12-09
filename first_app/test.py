import sqlite3

# Path to your SQLite database
db_path = r'C:\Users\jbarquez2\Documents\myProject\first_project\db.sqlite3'

# Connect to the SQLite database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# SQL query to delete all data from the table
sql_query = 'DELETE FROM first_app_attrition;'

# Execute the query
cursor.execute(sql_query)

# Commit the changes
connection.commit()

# Close the connection
cursor.close()
connection.close()

print("All data from the first_app_attrition table has been deleted.")