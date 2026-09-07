# Imports tools for working with files, folders and environment variables
import os

# Imports tools for copying and deleting folders
import shutil

# Allows Python to run external programs such as mysqldump
import subprocess

# Allows temporary folders to be created during the backup
import tempfile

# Allows the system to create ZIP backup files
import zipfile

# Imports datetime for creating backup timestamps and displaying backup dates
from datetime import datetime

# Imports Flask tools for routes, HTML pages, JSON responses and user sessions
from flask import Blueprint, render_template, jsonify, session

# Imports the security check that allows only administrators
from routes.security import admin_required

# Creates a Blueprint for all system backup routes
backup_bp = Blueprint("backup", __name__)

# BACKUP PAGE

# Creates the route used to open the system backup page
@backup_bp.route("/admin/system-backup")

# Makes sure only an administrator can access the backup page
@admin_required
def backup_page():

    # Loads the system backup HTML page
    # Also sends the logged-in user's name and role to the page
    return render_template(
        "SystemBackup.html",
        user_name=session.get("name"),
        user_role=session.get("role")
    )

# GET LAST BACKUP

# Creates an API route used to check the latest system backup
@backup_bp.route("/api/admin/backup/status", methods=["GET"])

# Makes sure only an administrator can check the backup status
@admin_required
def backup_status():
    # Gets the folder where system backups are stored
    backup_folder = get_backup_folder()

    # Creates the backup folder if it does not already exist
    os.makedirs(backup_folder, exist_ok=True)

    # Creates an empty list that will store the backup files found
    backup_files = []

    # Loops through all files inside the backup folder
    for filename in os.listdir(backup_folder):
        # Checks that the file is an EduPilot full backup ZIP file
        if filename.endswith(".zip") and filename.startswith("EduPilot_Full_Backup_"):
            # Creates the full path to the backup file
            full_path = os.path.join(backup_folder, filename)
            # Adds the backup filename and modification time to the list
            backup_files.append({
                "filename": filename,
                "modified": os.path.getmtime(full_path)
            })

    # Checks if no backup files were found
    if not backup_files:
        # Returns a successful response showing that no previous backup exists
        return jsonify({
            "success": True,
            "last_backup": None
        }), 200

    # Finds the backup file with the most recent modification time
    latest = max(backup_files, key=lambda item: item["modified"])

    # Converts the backup timestamp into an easy-to-read date and time
    backup_date = datetime.fromtimestamp(latest["modified"]).strftime("%d %B %Y %H:%M")

    # Returns information about the latest successful backup
    return jsonify({
        "success": True,
        "last_backup": {
            "filename": latest["filename"],
            "date": backup_date,
            "status": "Successful"
        }
    }), 200

# CREATE FULL SYSTEM BACKUP

# Creates an API route used to create a new full system backup
@backup_bp.route("/api/admin/backup/full", methods=["POST"])

# Makes sure only an administrator can create a backup
@admin_required
def create_full_backup():
    # Finds the main EduPilot project folder
    project_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Gets the folder where backups should be saved
    backup_folder = get_backup_folder()

    # Creates the backup folder if it does not already exist
    os.makedirs(backup_folder, exist_ok=True)

    # Creates the current date and time for the backup filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Creates a unique backup filename using the timestamp
    backup_name = f"EduPilot_Full_Backup_{timestamp}.zip"

    # Creates the complete path where the backup ZIP will be saved
    backup_path = os.path.join(backup_folder, backup_name)

    # Creates a variable that will later store the temporary folder
    temp_folder = None

    # Starts error handling for the backup process
    try:
        # Creates a temporary folder for files needed during the backup
        temp_folder = tempfile.mkdtemp(prefix="edupilot_backup_")

        # Creates the path for a database folder inside the temporary folder
        database_folder = os.path.join(temp_folder, "database")

        # Creates the temporary database folder
        os.makedirs(database_folder, exist_ok=True)

        # Creates the path where the SQL database backup will be stored
        database_dump = os.path.join(database_folder, "edupilot_database.sql")

        # CREATE DATABASE DUMP

        # Exports the EduPilot MySQL database into an SQL file
        create_database_dump(database_dump)

        # CREATE FINAL ZIP

        # Creates the final compressed ZIP backup file
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Adds the EduPilot application files to the ZIP backup
            add_application_to_zip(zip_file, project_folder)

            # Adds the SQL database backup to the ZIP file
            zip_file.write(
                database_dump,
                "database/edupilot_database.sql"
            )

        # Returns a success message after the backup has been created
        # Status code 201 means a new resource was created
        return jsonify({
            "success": True,
            "message": "Full system backup created successfully.",
            "filename": backup_name
        }), 201

    # Catches any error that occurs while creating the backup
    except Exception as error:

        # Prints the actual backup error in the terminal for debugging
        print("FULL BACKUP ERROR:", error)

        # Checks if an incomplete backup ZIP file was created
        if os.path.exists(backup_path):

            # Deletes the incomplete backup file
            os.remove(backup_path)

        # Returns an error message if the backup could not be created
        return jsonify({
            "success": False,
            "message": "Could not create the full system backup."
        }), 500

    # This section always runs whether the backup succeeds or fails
    finally:
        # Checks if the temporary folder was created and still exists
        if temp_folder and os.path.exists(temp_folder):

            # Deletes the temporary folder and all files inside it
            shutil.rmtree(temp_folder, ignore_errors=True)

# DATABASE DUMP

# Creates a function that exports the MySQL database
def create_database_dump(output_file):
    # Gets the location of the mysqldump program from the environment variables
    dump_path = os.getenv("MYSQL_DUMP_PATH")

    # Gets the database host or uses localhost as the default
    db_host = os.getenv("DB_HOST", "localhost")

    # Gets the database username or uses root as the default
    db_user = os.getenv("DB_USER", "root")

    # Gets the database password or uses an empty password as the default
    db_password = os.getenv("DB_PASSWORD", "")

    # Gets the database name or uses edupilot as the default
    db_name = os.getenv("DB_NAME", "edupilot")

    # Checks if the mysqldump location has been configured
    if not dump_path:
        # Stops the backup and raises an error if it is not configured
        raise Exception("MYSQL_DUMP_PATH is not configured.")

    # Checks whether the mysqldump program actually exists
    if not os.path.exists(dump_path):
        # Stops the backup if mysqldump cannot be found
        raise Exception("mysqldump.exe could not be found.")

    # Creates the mysqldump command used to export the database
    command = [
        dump_path,
        "--host=" + db_host,
        "--user=" + db_user,

        # Creates a consistent database backup
        "--single-transaction",

        # Includes stored procedures and functions
        "--routines",

        # Includes database triggers
        "--triggers",

        # Specifies the database that must be backed up
        db_name
    ]

    # Creates a copy of the current system environment variables
    environment = os.environ.copy()

    # Checks if the database has a password
    if db_password:
        # Provides the password to mysqldump through an environment variable
        environment["MYSQL_PWD"] = db_password

    # Opens the SQL backup file in write mode
    with open(output_file, "w", encoding="utf-8") as sql_file:
        # Runs the mysqldump program to export the database
        result = subprocess.run(
            command,

            # Writes the database export directly into the SQL file
            stdout=sql_file,

            # Captures any error messages produced by mysqldump
            stderr=subprocess.PIPE,

            # Handles the command output as text
            text=True,

            # Passes the environment variables to mysqldump
            env=environment,

            # Runs the command directly without using the system shell
            shell=False
        )

    # Checks if mysqldump returned an error
    if result.returncode != 0:
        # Raises an exception containing the mysqldump error message
        raise Exception(result.stderr)

# ADD APPLICATION FILES TO ZIP

# Creates a function that adds the application files to the ZIP backup
def add_application_to_zip(zip_file, project_folder):
    # Lists folders that should not be included in the backup
    excluded_folders = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "backups",
        ".idea",
        ".vscode"
    }

    # Lists sensitive files that should not be included in the backup
    excluded_files = {

        # The .env file may contain passwords, API keys and other sensitive information
        ".env"
    }

    # Lists unnecessary compiled Python file extensions
    excluded_extensions = {
        ".pyc",
        ".pyo"
    }

    # Goes through all folders and files in the EduPilot project
    for root, folders, files in os.walk(project_folder):
        # Removes excluded folders so they are not added to the backup
        folders[:] = [
            folder
            for folder in folders
            if folder not in excluded_folders
        ]

        # Loops through every file found in the current folder
        for filename in files:

            # Checks if the file is on the excluded files list
            if filename in excluded_files:

                # Skips the file and moves to the next one
                continue

            # Checks if the file has an excluded extension
            if os.path.splitext(filename)[1].lower() in excluded_extensions:

                # Skips compiled Python files
                continue

            # Creates the complete path to the application file
            full_path = os.path.join(root, filename)

            # Creates the file path relative to the main project folder
            relative_path = os.path.relpath(full_path, project_folder)

            # Places the file inside the application folder in the ZIP
            archive_path = os.path.join("application", relative_path)

            # Adds the application file to the ZIP backup
            zip_file.write(full_path, archive_path)

# BACKUP FOLDER

# Creates a function that determines where backups should be stored
def get_backup_folder():
    # Finds the main EduPilot project folder
    project_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Gets the configured backup folder or uses "backups" as the default
    configured_folder = os.getenv("BACKUP_FOLDER", "backups")

    # Checks if the configured backup folder is already an absolute path
    if os.path.isabs(configured_folder):
        # Returns the configured absolute path
        return configured_folder

    # Creates and returns the backup path inside the EduPilot project folder
    return os.path.join(project_folder, configured_folder)
