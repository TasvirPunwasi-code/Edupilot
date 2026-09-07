import os
import shutil
import subprocess
import tempfile
import zipfile

from datetime import datetime
from flask import Blueprint, render_template, jsonify, session
from routes.security import admin_required


backup_bp = Blueprint("backup", __name__)


# =========================================================
# BACKUP PAGE
# =========================================================

@backup_bp.route("/admin/system-backup")
@admin_required
def backup_page():

    return render_template(
        "SystemBackup.html", user_name=session.get("name"), user_role=session.get("role")
    )


# =========================================================
# GET LAST BACKUP
# =========================================================

@backup_bp.route("/api/admin/backup/status", methods=["GET"])
@admin_required
def backup_status():

    backup_folder = get_backup_folder()

    os.makedirs(backup_folder, exist_ok=True)

    backup_files = []

    for filename in os.listdir(backup_folder):

        if filename.endswith(".zip") and filename.startswith("EduPilot_Full_Backup_"):
            full_path = os.path.join(backup_folder, filename)
            backup_files.append({
                "filename": filename, "modified": os.path.getmtime(full_path)
            })


    if not backup_files:

        return jsonify({
            "success": True, "last_backup": None}), 200


    latest = max(backup_files, key=lambda item: item["modified"])

    backup_date = datetime.fromtimestamp(latest["modified"]).strftime("%d %B %Y %H:%M")


    return jsonify({
        "success": True,
        "last_backup": {
            "filename": latest["filename"],
            "date": backup_date,
            "status": "Successful"
        }
    }), 200


# =========================================================
# CREATE FULL SYSTEM BACKUP
# =========================================================

@backup_bp.route("/api/admin/backup/full", methods=["POST"])
@admin_required
def create_full_backup():

    project_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    backup_folder = get_backup_folder()

    os.makedirs(backup_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    backup_name = f"EduPilot_Full_Backup_{timestamp}.zip"
    backup_path = os.path.join(backup_folder, backup_name)


    temp_folder = None

    try:

        temp_folder = tempfile.mkdtemp(prefix="edupilot_backup_")

        database_folder = os.path.join(temp_folder, "database")
        os.makedirs(database_folder, exist_ok=True)

        database_dump = os.path.join(database_folder, "edupilot_database.sql")


        # =================================================
        # CREATE DATABASE DUMP
        # =================================================

        create_database_dump(database_dump)


        # =================================================
        # CREATE FINAL ZIP
        # =================================================

        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zip_file:

            add_application_to_zip(zip_file, project_folder)

            zip_file.write(
                database_dump,
                "database/edupilot_database.sql"
            )


        return jsonify({
            "success": True,
            "message": "Full system backup created successfully.",
            "filename": backup_name
        }), 201


    except Exception as error:

        print("FULL BACKUP ERROR:", error)


        if os.path.exists(backup_path):
            os.remove(backup_path)


        return jsonify({
            "success": False,
            "message": "Could not create the full system backup."
        }), 500


    finally:

        if temp_folder and os.path.exists(temp_folder):
            shutil.rmtree(temp_folder, ignore_errors=True)


# =========================================================
# DATABASE DUMP
# =========================================================

def create_database_dump(output_file):

    dump_path = os.getenv("MYSQL_DUMP_PATH")

    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "edupilot")


    if not dump_path:
        raise Exception("MYSQL_DUMP_PATH is not configured.")


    if not os.path.exists(dump_path):
        raise Exception("mysqldump.exe could not be found.")


    command = [
        dump_path,
        "--host=" + db_host,
        "--user=" + db_user,
        "--single-transaction",
        "--routines",
        "--triggers",
        db_name
    ]


    environment = os.environ.copy()

    if db_password:
        environment["MYSQL_PWD"] = db_password


    with open(output_file, "w", encoding="utf-8") as sql_file:

        result = subprocess.run(
            command,
            stdout=sql_file,
            stderr=subprocess.PIPE,
            text=True,
            env=environment,
            shell=False
        )


    if result.returncode != 0:
        raise Exception(result.stderr)


# =========================================================
# ADD APPLICATION FILES TO ZIP
# =========================================================

def add_application_to_zip(zip_file, project_folder):

    excluded_folders = {
        ".git",".venv", "venv","__pycache__","backups",".idea",".vscode"
    }

    excluded_files = {
        ".env"
    }

    excluded_extensions = {
        ".pyc",".pyo"
    }

    for root, folders, files in os.walk(project_folder):

        folders[:] = [
            folder
            for folder in folders
            if folder not in excluded_folders
        ]


        for filename in files:

            if filename in excluded_files:
                continue


            if os.path.splitext(filename)[1].lower() in excluded_extensions:
                continue


            full_path = os.path.join(root, filename)

            relative_path = os.path.relpath(full_path, project_folder)

            archive_path = os.path.join("application", relative_path)

            zip_file.write(full_path, archive_path)


# =========================================================
# BACKUP FOLDER
# =========================================================

def get_backup_folder():

    project_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    configured_folder = os.getenv("BACKUP_FOLDER", "backups")


    if os.path.isabs(configured_folder):
        return configured_folder


    return os.path.join(project_folder, configured_folder)