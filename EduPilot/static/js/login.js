/* =========================================================
   LOGIN
========================================================= */

const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", async function(event){

    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");

    message.textContent = "";
    message.className = "message";

    try{

        const response = await fetch("/login", {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                email:email,
                password:password
            })
        });

        const result = await response.json();

        if(result.status === "otp"){

            window.location.href = "/verify";

        }else{

            message.textContent = result.message || "Login failed.";
            message.className = "message error";

        }

    }catch(error){

        console.error("LOGIN ERROR:", error);

        message.textContent = "Could not connect to the server.";
        message.className = "message error";

    }

});


/* =========================================================
   OPEN CHANGE PASSWORD POPUP
========================================================= */

function openPasswordModal(){

    const modal = document.getElementById("passwordModal");
    const loginEmail = document.getElementById("email").value.trim();

    modal.classList.add("show");

    if(loginEmail){
        document.getElementById("changeEmail").value = loginEmail;
    }

    document.getElementById("changeEmail").focus();
}


/* =========================================================
   CLOSE CHANGE PASSWORD POPUP
========================================================= */

function closePasswordModal(){

    document.getElementById("passwordModal").classList.remove("show");

    document.getElementById("changePasswordForm").reset();

    document.getElementById("changePasswordMessage").textContent = "";
}


/* =========================================================
   CLOSE POPUP WHEN CLICKING OUTSIDE
========================================================= */

document.getElementById("passwordModal").addEventListener("click", function(event){

    if(event.target === this){
        closePasswordModal();
    }

});


/* =========================================================
   START PASSWORD CHANGE
========================================================= */

document.getElementById("changePasswordForm").addEventListener("submit", async function(event){

    event.preventDefault();

    const email = document.getElementById("changeEmail").value.trim();
    const message = document.getElementById("changePasswordMessage");

    message.textContent = "";
    message.className = "message";

    try{

        const response = await fetch("/change-password/request", {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                email:email
            })
        });

        const result = await response.json();

        if(result.status === "otp"){

            window.location.href = "/verify-password";

        }else{

            message.textContent = result.message || "Could not continue.";
            message.className = "message error";

        }

    }catch(error){

        console.error("CHANGE PASSWORD ERROR:", error);

        message.textContent = "Could not connect to the server.";
        message.className = "message error";

    }
	
	

});

const quotes = [
    {
        text: "Who cares?",
        author: "— Dylan Mothilall"
    },
    {
        text: "“YOUR FUTURE IS WHATEVER YOU MAKE IT! SO MAKE IT A GOOD ONE!”",
        author: "— Doc Brown(Back To The Future)"
    },
    {
        text: "Education is the passport to the future.",
        author: "— Malcolm X"
    },
    {
        text: "But it ain't about how hard ya hit. It's about how hard you can get hit and keep moving forward, how much you can take and keep moving forward.",
        author: "— Rocky Balboa(Rocky)"
    },
    {
        text: "Change will not come if we wait for some other person, or if we wait for some other time. We are the ones we've been waiting for. We are the change that we seek.",
        author: "— Barack Obama"
    },
    {
        text: "'I'm not afraid of failing. I don't like to fail. I hate to fail. But I'm not afraid of it.' Embracing the distinct possibility of failure is a necessary stepping stone on the path to high-level achievement.",
        author: "— Vince Mchmahon"
    },
    {
        text: "A strong man doesn't need to read the future, he makes his own",
        author: "— Solid Snake(Metal Gear Solid)"
    },
    {
        text: "The secret of getting ahead is getting started.",
        author: "— Mark Twain"
    },
	{
        text: "Stay Safe, Play Safe",
        author: "— Sharen Singh"
    }
];

const quoteContainer = document.querySelector(".quote-container");
const quoteText = document.getElementById("quote");
const quoteAuthor = document.getElementById("quote-author");

let currentQuote = -1;

function showRandomQuote(){

    let newQuote;

    do {
        newQuote = Math.floor(Math.random() * quotes.length);
    } while(newQuote === currentQuote && quotes.length > 1);

    currentQuote = newQuote;

    quoteContainer.style.opacity = "0";

    setTimeout(() => {

        quoteText.textContent = `"${quotes[currentQuote].text}"`;
        quoteAuthor.textContent = quotes[currentQuote].author;

        quoteContainer.style.opacity = "1";

    }, 500);
}

showRandomQuote();

setInterval(showRandomQuote, 10000);


