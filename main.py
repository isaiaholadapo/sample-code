import psycopg2
from environ import environ
from psycopg2 import Error

env = environ.Env()
env.read_env()


class User:
    def __init__(self, conn):
        self.conn = conn

    def save_to_database(self, name, age, email):
        # Validate input data
        if not self._validate_input(name, age, email):
            print("Invalid input data. Please provide valid values.")
            return

        try:
            with self.conn.cursor() as cursor:
                # Execute SQL query to insert user data into the database
                cursor.execute('CREATE TABLE IF NOT EXISTS users (name TEXT, age INTEGER, email TEXT)')
                cursor.execute('INSERT INTO users VALUES (%s, %s, %s)', (name, age, email))
                self.conn.commit()
        except Error as e:
            print(f"An error occurred while saving user to the database: {e}")

    def _validate_input(self, name, age, email):
        # Validate name
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name must be a non-empty string.")

        # Validate age
        if not isinstance(age, int) or age < 0:
            raise ValueError("Age must be a positive integer.")

        # Validate email
        if not isinstance(email, str) or not email.strip() or '@' not in email:
            raise ValueError("Email must be a non-empty string containing the '@' symbol.")

        return True

    def retrieve_from_database(self):
        try:
            with self.conn.cursor() as cursor:
                # Execute SQL query to retrieve all users from the database
                cursor.execute('SELECT * FROM users')
                users = cursor.fetchall()
                return users
        except Error as e:
            print(f"An error occurred while retrieving users from the database: {e}")
            return []

    def search_by_name(self, name):
        try:
            with self.conn.cursor() as cursor:
                # Execute SQL query to search users by name
                cursor.execute('SELECT * FROM users WHERE LOWER(name) LIKE %s', (f'%{name.lower()}%',))
                users = cursor.fetchall()
                return users
        except Error as e:
            print(f"An error occurred while searching users by name: {e}")
            return []

    def update_email(self, name, new_email):
        # Validate input data
        if not self._validate_input(name, 0, new_email):
            print("Invalid input data. Please provide valid values.")
            return

        try:
            with self.conn.cursor() as cursor:
                # Execute SQL query to update user email
                cursor.execute('UPDATE users SET email = %s WHERE LOWER(name) = %s', (new_email, name.lower()))
                self.conn.commit()
        except Error as e:
            print(f"An error occurred while updating user email: {e}")

    def delete_from_database(self, name):
        try:
            with self.conn.cursor() as cursor:
                # Execute SQL query to delete user from the database
                cursor.execute('DELETE FROM users WHERE name = %s', (name,))
                self.conn.commit()
        except Error as e:
            print(f"An error occurred while deleting user from the database: {e}")

    def calculate_user_count(self):
        try:
            with self.conn.cursor() as cursor:
                # Execute SQL query to calculate the total number of users
                cursor.execute('SELECT COUNT(*) AS user_count FROM users')
                user_count = cursor.fetchone()[0]
                return user_count
        except Error as e:
            print(f"An error occurred while calculating user count: {e}")
            return 0

    def calculate_average_age(self):
        try:
            with self.conn.cursor() as cursor:
                # Execute SQL query to calculate the average age of users
                cursor.execute('SELECT AVG(age) AS average_age FROM users')
                average_age = cursor.fetchone()[0]
                return average_age
        except Error as e:
            print(f"An error occurred while calculating average age: {e}")
            return 0


class Admin(User):
    def __init__(self, conn):
        super().__init__(conn)

    def save_to_database(self, name, age, email, role):
        if not self._validate_input(name, age, email):
            print("Invalid input data. Please provide valid values.")
            return

        try:
            with self.conn.cursor() as cursor:
                cursor.execute('CREATE TABLE IF NOT EXISTS admins (name TEXT, age INTEGER, email TEXT, role TEXT)')
                cursor.execute('INSERT INTO admins VALUES (%s, %s, %s, %s)', (name, age, email, role))
                self.conn.commit()
        except Error as e:
            print(f"An error occurred while saving admin to the database: {e}")

    def retrieve_from_database(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM admins')
                admins = cursor.fetchall()
                return admins
        except Error as e:
            print(f"An error occurred while retrieving admins from the database: {e}")
            return []

    def search_by_name(self, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('SELECT * FROM admins WHERE LOWER(name) LIKE %s', (f'%{name.lower()}%',))
                admins = cursor.fetchall()
                return admins
        except Error as e:
            print(f"An error occurred while searching admins by name: {e}")
            return []


def main():
    conn = psycopg2.connect(
        host=env('HOST'),
        database=env('DATABASE'),
        user=env('DATABASE_USER'),
        password=env('DATABASE_PASSWORD')
    )
    return conn


# Create a database connection
conn = main()

# Create an instance of the User class with the connection
user = User(conn)

# Save a user to the database with input validation
user.save_to_database('John Doe', 25, 'john.doe@example.com')
user.save_to_database('Janet Smith', 25, 'janet.smith@example.com')
user.save_to_database('Cole Deo', 5, 'cole.deo@example.com')

# Retrieve users from the database
users_from_db = user.retrieve_from_database()
for u in users_from_db:
    print(f"Name: {u[0]}, Age: {u[1]}, Email: {u[2]}")

# Search for users by name
search_results = user.search_by_name('John Doe')
if search_results:
    print("\nSearch Results:")
    for u in search_results:
        print(f"Name: {u[0]}, Age: {u[1]}, Email: {u[2]}")
else:
    print("\nNo users found.")

# Update user email with input validation
user.update_email('John Doe', 'new_email@example.com')

# Delete user from the database
user.delete_from_database("John Doe")

# Print the total number of users
print(user.calculate_user_count())

# Print the average age of users
print(user.calculate_average_age())

# Create an instance of the Admin class with the same connection
admin = Admin(conn)
admin.save_to_database('Admin User', 30, 'admin@example.com', 'superuser')

# Use the overridden search_by_name() method of the Admin class
search_results = admin.search_by_name('Admin')

if search_results:
    print("\nSearch Results:")
    for u in search_results:
        print(f"Name: {u[0]}, Age: {u[1]}, Email: {u[2]}, Role: {u[3]}")
else:
    print("\nNo users found.")

# Close the database connection
conn.close()
