function clearOTP(){
    const otp=document.getElementById("otp");

    if(otp){
        otp.value="";
    }
}

window.addEventListener("pageshow",function(){
    clearOTP();
});

document.addEventListener("DOMContentLoaded",function(){
    clearOTP();

    const otp=document.getElementById("otp");

    otp.addEventListener("input",function(){
        this.value=this.value.replace(/\D/g,"").slice(0,6);
    });
});


async function verifyOTP(){

    const otp=document.getElementById("otp").value;
    const message=document.getElementById("message");

    if(otp.length!=6){

        message.textContent="Enter a valid 6-digit OTP.";

        return;
    }

    try{

        const response=await fetch("/verify",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                otp:otp
            })

        });

        const result=await response.json();

        if(result.status=="success"){

            clearOTP();

            window.location.replace(result.redirect);

        }

        else{

            clearOTP();

            message.textContent=result.message;

        }

    }

    catch(error){

        clearOTP();

        message.textContent="Could not verify OTP. Please try again.";

        console.error("OTP VERIFY ERROR:",error);

    }

}


async function resendOTP(){

    const message=document.getElementById("message");

    clearOTP();

    try{

        const response=await fetch("/resend-otp",{

            method:"POST"

        });

        const result=await response.json();

        message.textContent=result.message;

    }

    catch(error){

        message.textContent="Could not resend OTP. Please try again.";

        console.error("OTP RESEND ERROR:",error);

    }

}