async function verifyPasswordOTP(){

    const otp = document.getElementById("otp").value.trim();
    const message = document.getElementById("message");

    message.textContent = "";
    message.className = "";

    if(!/^\d{6}$/.test(otp)){

        message.textContent = "Enter a valid 6-digit OTP.";
        message.className = "error";

        return;
    }

    try{

        const response = await fetch("/verify-password", {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                otp:otp
            })
        });

        const result = await response.json();

        if(result.status === "success"){

            message.textContent = "Verification successful.";
            message.className = "success";

            window.location.href = result.redirect;

        }else{

            message.textContent = result.message || "Incorrect verification code.";
            message.className = "error";
        }

    }catch(error){

        console.error("VERIFY PASSWORD OTP ERROR:", error);

        message.textContent = "Could not connect to the server.";
        message.className = "error";
    }
}


async function resendPasswordOTP(){

    const message = document.getElementById("message");

    message.textContent = "";

    try{

        const response = await fetch("/change-password/resend-otp", {
            method:"POST"
        });

        const result = await response.json();

        if(result.status === "success"){

            message.textContent = result.message;
            message.className = "success";

        }else{

            message.textContent = result.message || "Could not resend verification code.";
            message.className = "error";
        }

    }catch(error){

        console.error("RESEND PASSWORD OTP ERROR:", error);

        message.textContent = "Could not resend verification code.";
        message.className = "error";
    }
}


document.getElementById("otp").addEventListener("keydown", function(event){

    if(event.key === "Enter"){
        verifyPasswordOTP();
    }
});
