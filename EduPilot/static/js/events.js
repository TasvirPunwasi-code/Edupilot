let events = [];

async function loadEvents(){
    try{
        const response = await fetch("/api/events");
        const result = await response.json();

        if(!response.ok || !result.success){
            alert(result.message || "Could not load events.");
            return;
        }

        events = Array.isArray(result.events) ? result.events : [];
        renderEvents();
    }
    catch(error){
        console.error("LOAD EVENTS ERROR:", error);
        alert("Could not connect to the Flask server.");
    }
}

function getEventStatus(eventDate){
    const today = new Date();
    today.setHours(0,0,0,0);

    const date = new Date(eventDate + "T00:00:00");

    if(date < today){
        return "Completed";
    }

    if(date.getTime() === today.getTime()){
        return "Ongoing";
    }

    return "Upcoming";
}

function formatDate(dateString){
    const date = new Date(dateString + "T00:00:00");

    return date.toLocaleDateString(
        "en-ZA",
        {
            day:"2-digit",
            month:"short",
            year:"numeric"
        }
    );
}

function formatTime(time){
    if(!time){
        return "-";
    }

    const parts = time.split(":");
    let hour = parseInt(parts[0]);
    const minute = parts[1];
    const period = hour >= 12 ? "PM" : "AM";

    hour = hour % 12 || 12;

    return `${hour}:${minute} ${period}`;
}

function escapeHTML(value){
    const div = document.createElement("div");
    div.textContent = String(value ?? "");
    return div.innerHTML;
}

function renderEvents(){
    const table = document.getElementById("eventTableBody");
    const search = document.getElementById("searchInput").value.toLowerCase();
    const type = document.getElementById("typeFilter").value;
    const status = document.getElementById("statusFilter").value;

    table.innerHTML = "";

    const filteredEvents = events.filter(function(event){
        const eventStatus = getEventStatus(event.event_date);

        const matchesSearch =
            event.event_name.toLowerCase().includes(search) ||
            event.event_type.toLowerCase().includes(search) ||
            event.venue.toLowerCase().includes(search) ||
            event.organizer.toLowerCase().includes(search);

        const matchesType =
            type === "all" ||
            event.event_type === type;

        const matchesStatus =
            status === "all" ||
            eventStatus === status;

        return matchesSearch && matchesType && matchesStatus;
    });

    if(filteredEvents.length === 0){
        table.innerHTML = `
            <tr>
                <td colspan="8" class="empty-message">
                    No events found.
                </td>
            </tr>
        `;

        updateStats();
        return;
    }

    filteredEvents
        .sort(function(a,b){
            return new Date(a.event_date) - new Date(b.event_date);
        })
        .forEach(function(event){
            const eventStatus = getEventStatus(event.event_date);
            const statusClass = eventStatus.toLowerCase();
            const row = document.createElement("tr");

            row.innerHTML = `
                <td><strong>${escapeHTML(event.event_name)}</strong></td>
                <td>${escapeHTML(event.event_type)}</td>
                <td>${formatDate(event.event_date)}</td>
                <td>${formatTime(event.event_time)}</td>
                <td>${escapeHTML(event.venue)}</td>
                <td>${escapeHTML(event.organizer)}</td>
                <td>
                    <span class="status ${statusClass}">
                        ${eventStatus}
                    </span>
                </td>
                <td>
                    <button
                        class="delete-btn"
                        onclick="deleteEvent(${event.event_id})">
                        Delete
                    </button>
                </td>
            `;

            table.appendChild(row);
        });

    updateStats();
}

function updateStats(){
    const today = new Date();
    today.setHours(0,0,0,0);

    const upcoming = events.filter(function(event){
        return getEventStatus(event.event_date) === "Upcoming";
    }).length;

    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();

    const monthEvents = events.filter(function(event){
        const date = new Date(event.event_date + "T00:00:00");

        return (
            date.getMonth() === currentMonth &&
            date.getFullYear() === currentYear
        );
    }).length;

    document.getElementById("upcomingCount").textContent = upcoming;
    document.getElementById("monthCount").textContent = monthEvents;
    document.getElementById("totalCount").textContent = events.length;
}

function openModal(){
    const modal = document.getElementById("eventModal");
    const form = document.getElementById("eventForm");

    form.reset();

    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2,"0");
    const day = String(today.getDate()).padStart(2,"0");
    const todayString = `${year}-${month}-${day}`;

    document.getElementById("eventDate").min = todayString;
    modal.classList.add("show");
}

function closeModal(){
    document.getElementById("eventModal").classList.remove("show");
}

document.getElementById("eventForm").addEventListener(
    "submit",
    async function(e){
        e.preventDefault();

        const eventDate = document.getElementById("eventDate").value;

        const today = new Date();
        today.setHours(0,0,0,0);

        const selectedDate = new Date(eventDate + "T00:00:00");

        if(selectedDate < today){
            alert("You cannot add an event for a past date.");
            return;
        }

        const eventData = {
            event_name: document.getElementById("eventName").value.trim(),
            event_type: document.getElementById("eventType").value,
            event_date: eventDate,
            event_time: document.getElementById("eventTime").value,
            venue: document.getElementById("eventVenue").value.trim(),
            organizer: document.getElementById("eventOrganizer").value.trim()
        };

        if(
            !eventData.event_name ||
            !eventData.event_type ||
            !eventData.event_date ||
            !eventData.event_time ||
            !eventData.venue ||
            !eventData.organizer
        ){
            alert("Please complete all fields.");
            return;
        }

        try{
            const response = await fetch(
                "/api/events",
                {
                    method:"POST",
                    headers:{
                        "Content-Type":"application/json"
                    },
                    body:JSON.stringify(eventData)
                }
            );

            const result = await response.json();

            if(response.ok){
                closeModal();
                await loadEvents();
                alert("Event added successfully!");
            }
            else{
                alert(result.message || "Could not add event.");
            }
        }
        catch(error){
            console.error("ADD EVENT ERROR:", error);
            alert("Could not connect to the Flask server.");
        }
    }
);

async function deleteEvent(id){
    const event = events.find(function(event){
        return Number(event.event_id) === Number(id);
    });

    if(!event){
        return;
    }

    const confirmDelete = confirm(
        `Delete "${event.event_name}"?`
    );

    if(!confirmDelete){
        return;
    }

    try{
        const response = await fetch(
            `/api/events/${id}`,
            {
                method:"DELETE"
            }
        );

        const result = await response.json();

        if(response.ok){
            await loadEvents();
        }
        else{
            alert(result.message || "Could not delete event.");
        }
    }
    catch(error){
        console.error("DELETE EVENT ERROR:", error);
        alert("Could not connect to the Flask server.");
    }
}

document
    .getElementById("searchInput")
    .addEventListener("input", renderEvents);

document
    .getElementById("typeFilter")
    .addEventListener("change", renderEvents);

document
    .getElementById("statusFilter")
    .addEventListener("change", renderEvents);

function showNotifications(){
    alert("You have 3 new notifications.");
}

function logout(){
    const confirmLogout = confirm(
        "Are you sure you want to logout?"
    );

    if(confirmLogout){
        window.location.href = "/logout";
    }
}

document
    .getElementById("eventModal")
    .addEventListener(
        "click",
        function(e){
            if(e.target === this){
                closeModal();
            }
        }
    );

document.addEventListener(
    "keydown",
    function(e){
        if(e.key === "Escape"){
            closeModal();
        }
    }
);

document.addEventListener(
    "DOMContentLoaded",
    function(){
        loadEvents();
    }
);
