document.addEventListener("DOMContentLoaded", function(){

    loadBackupStatus();

    document.getElementById("backupButton").addEventListener("click", createBackup);

});


// =========================================================
// LOAD BACKUP STATUS
// =========================================================

async function loadBackupStatus(){

    try{

        const response = await fetch("/api/admin/backup/status");
        const result = await response.json();


        if(!response.ok || !result.success){
            document.getElementById("lastBackup").textContent = "Unavailable";
            document.getElementById("backupStatus").textContent = "Unknown";
            return;
        }


        if(!result.last_backup){

            document.getElementById("lastBackup").textContent = "No backups yet";
            document.getElementById("backupStatus").textContent = "Not created";

            return;
        }


        document.getElementById("lastBackup").textContent = result.last_backup.date;
        document.getElementById("backupStatus").textContent = result.last_backup.status;

    }
    catch(error){

        console.error("BACKUP STATUS ERROR:", error);

        document.getElementById("lastBackup").textContent = "Unavailable";
        document.getElementById("backupStatus").textContent = "Unknown";

    }

}


// =========================================================
// CREATE FULL BACKUP
// =========================================================

async function createBackup(){

    const button = document.getElementById("backupButton");
    const message = document.getElementById("backupMessage");

    const confirmed = confirm("Create a full EduPilot system backup?");


    if(!confirmed){
        return;
    }


    button.disabled = true;
    button.textContent = "Creating Backup...";

    message.textContent = "";
    message.className = "";


    try{

        const response = await fetch("/api/admin/backup/full", {
            method:"POST"
        });


        const result = await response.json();


        if(response.ok && result.success){

            message.textContent = result.message + " File: " + result.filename;
            message.className = "success";

            await loadBackupStatus();

        }
        else{

            message.textContent = result.message || "Could not create backup.";
            message.className = "error";

        }

    }
    catch(error){

        console.error("BACKUP ERROR:", error);

        message.textContent = "Could not connect to the backup service.";
        message.className = "error";

    }
    finally{

        button.disabled = false;
        button.textContent = "Create Full System Backup";

    }

}