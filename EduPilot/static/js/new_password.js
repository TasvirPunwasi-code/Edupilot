const form = document.getElementById("newPasswordForm");

form.addEventListener("submit", async function(event){

    event.preventDefault();

    const newPassword = document.getElementById("newPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const message = document.getElementById("message");
    const changeButton = document.getElementById("changeButton");

    message.textContent = "";
    message.className = "message";

    if(newPassword.length < 8){

        message.textContent = "Password must be at least 8 characters.";
        message.className = "message error";

        return;
    }

    if(newPassword !== confirmPassword){

        message.textContent = "Passwords do not match.";
        message.className = "message error";

        return;
    }

    changeButton.disabled = true;
    changeButton.textContent = "Updating...";

    try{

        const response = await fetch("/new-password", {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                password:newPassword,
                confirm_password:confirmPassword
            })
        });

        const result = await response.json();

        if(result.status === "success"){

            message.textContent = result.message || "Password changed successfully.";
            message.className = "message success";

            setTimeout(function(){
                window.location.href = result.redirect || "/login";
            }, 1200);

        }else{

            message.textContent = result.message || "Could not change password.";
            message.className = "message error";

            changeButton.disabled = false;
            changeButton.textContent = "Change Password";
        }

    }catch(error){

        console.error("PASSWORD UPDATE ERROR:", error);

        message.textContent = "Could not connect to the server.";
        message.className = "message error";

        changeButton.disabled = false;
        changeButton.textContent = "Change Password";
    }

});
