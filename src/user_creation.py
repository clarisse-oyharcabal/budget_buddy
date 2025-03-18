import re
import bcrypt                               # Install bcrypt with "pip install bcrypt"
import mysql.connector
from datetime import datetime

# Password validation function
def validate_password(password):
    if (len(password) < 10 or
        not re.search(r'[A-Z]', password) or
        not re.search(r'[a-z]', password) or
        not re.search(r'[0-9]', password) or
        not re.search(r'[\W_]', password)):
        raise ValueError("The password must be at least 10 characters long, including one uppercase, one lowercase, one number and one special character.")

# User creation function
def create_user(name, last_name, email, password):
    validate_password(password)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    conn = mysql.connector.connect(
        host="localhost",
        user="root",                        # Change to your MySQL username
        password="123456789",               # Change to your MySQL password
        database="dB_budget_buddy",
        auth_plugin='mysql_native_password'  # Specify the authentication plugin
    )
    cursor = conn.cursor()
    
    inscription_date = datetime.now().strftime('%Y-%m-%d')
    query = """
    INSERT INTO user (name, last_name, email, password, inscription_date)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, last_name, email, hashed_password, inscription_date))
    conn.commit()
    
    cursor.close()
    conn.close()

# Example of user creation
try:
    create_user("Cherry", "Lindon", "cherry.lindon@example.com", "Password123!")
    print("User successfully created.")
except ValueError as e:
    print(f"Error: {e}")
except mysql.connector.Error as err:
    print(f"Database error: {err}")