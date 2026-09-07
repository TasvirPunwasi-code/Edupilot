# Imports the os module to access database settings stored in environment variables
import os

# Imports the MySQL Connector library to allow Python to communicate with MySQL
import mysql.connector

# Creates a reusable function that connects EduPilot to the MySQL database
def get_db_connection():
    # Creates and returns a connection to the MySQL database
    return mysql.connector.connect(
        # Gets the MySQL server address from the environment variables
        host=os.getenv("DB_HOST"),
        # Gets the MySQL username from the environment variables
        user=os.getenv("DB_USER"),
        # Gets the MySQL password from the environment variables
        password=os.getenv("DB_PASSWORD"),
        # Gets the name of the EduPilot database from the environment variables
        database=os.getenv("DB_NAME")
    )
