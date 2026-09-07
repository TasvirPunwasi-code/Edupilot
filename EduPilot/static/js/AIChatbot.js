/* =========================================================
   CHATBOT FLASK ENDPOINT
========================================================= */

const CHATBOT_API = "/api/chatbot";

let waitingForResponse = false;


/* =========================================================
   SEND MESSAGE
========================================================= */

async function sendMessage(){

    const input = document.getElementById("chatInput");
    const message = input.value.trim();

    if(message === "" || waitingForResponse){
        return;
    }

    addUserMessage(message);

    input.value = "";

    setLoading(true);

    const typingMessage = addTypingMessage();


    try{

        const response = await fetch(CHATBOT_API, {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({message:message})
        });


        const result = await response.json();

        typingMessage.remove();


        if(!response.ok){

            addAIMessage(
                result.message ||
                "The assistant could not process your request."
            );

            return;
        }


        const assistantResponse = result.response || result.reply || result.message;

        if(assistantResponse){
            addAIMessage(assistantResponse);
        }
        else{
            addAIMessage("The chatbot returned an empty response.");
        }

    }
    catch(error){

        typingMessage.remove();

        console.error("CHATBOT ERROR:", error);

        addAIMessage(
            "I could not connect to the chatbot server. Make sure your Flask chatbot endpoint is running."
        );

    }
    finally{

        setLoading(false);

        input.focus();

    }

}


/* =========================================================
   USER MESSAGE
========================================================= */

function addUserMessage(message){

    const container = document.getElementById("chatContainer");

    const messageDiv = document.createElement("div");

    messageDiv.className = "message user-message";


    messageDiv.innerHTML = `
        <div class="message-content">
            <strong>You</strong>
            <p>${escapeHTML(message)}</p>
        </div>

        <div class="message-avatar user">
            T
        </div>
    `;


    container.appendChild(messageDiv);

    scrollChat();

}


/* =========================================================
   AI MESSAGE
========================================================= */

function addAIMessage(message){

    const container = document.getElementById("chatContainer");

    const messageDiv = document.createElement("div");

    messageDiv.className = "message ai-message";


    messageDiv.innerHTML = `
        <div class="message-avatar">
            🤖
        </div>

        <div class="message-content">
            <strong>EduPilot Assistant</strong>
            <p>${escapeHTML(message)}</p>
        </div>
    `;


    container.appendChild(messageDiv);

    scrollChat();

}


/* =========================================================
   TYPING MESSAGE
========================================================= */

function addTypingMessage(){

    const container = document.getElementById("chatContainer");

    const messageDiv = document.createElement("div");

    messageDiv.className = "message ai-message typing";


    messageDiv.innerHTML = `
        <div class="message-avatar">
            🤖
        </div>

        <div class="message-content">
            <strong>EduPilot Assistant</strong>
            <p>Thinking...</p>
        </div>
    `;


    container.appendChild(messageDiv);

    scrollChat();

    return messageDiv;

}


/* =========================================================
   SUGGESTION BUTTON
========================================================= */

function sendSuggestion(message){

    document.getElementById("chatInput").value = message;

    sendMessage();

}


/* =========================================================
   ENTER KEY
========================================================= */

document.getElementById("chatInput").addEventListener("keydown", function(event){

    if(event.key === "Enter" && !event.shiftKey){

        event.preventDefault();

        sendMessage();

    }

});


/* =========================================================
   LOADING STATE
========================================================= */

function setLoading(isLoading){

    waitingForResponse = isLoading;

    document.getElementById("sendButton").disabled = isLoading;

    document.getElementById("chatInput").disabled = isLoading;

}


/* =========================================================
   SCROLL CHAT
========================================================= */

function scrollChat(){

    const container = document.getElementById("chatContainer");

    container.scrollTop = container.scrollHeight;

}


/* =========================================================
   XSS PROTECTION
========================================================= */

function escapeHTML(text){

    const div = document.createElement("div");

    div.textContent = String(text ?? "");

    return div.innerHTML;

}


/* =========================================================
   NOTIFICATIONS
========================================================= */

function showNotifications(){

    alert("No new notifications.");

}


/* =========================================================
   LOGOUT
========================================================= */

function logout(){

    const confirmLogout = confirm("Are you sure you want to logout?");

    if(confirmLogout){
        window.location.href = "/logout";
    }

}

