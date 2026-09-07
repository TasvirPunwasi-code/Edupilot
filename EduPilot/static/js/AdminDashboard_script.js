
/* =========================================================
   ADMIN DASHBOARD CALENDAR
========================================================= */

let currentDate = new Date();


/* =========================================================
   LOAD CALENDAR
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    renderCalendar();

});


/* =========================================================
   DISPLAY CALENDAR
========================================================= */

function renderCalendar() {

    const calendar = document.getElementById("calendar");
    const calendarMonth = document.getElementById("calendarMonth");

    if (!calendar || !calendarMonth) {
        return;
    }


    /* Clear previous calendar */

    calendar.innerHTML = "";


    /* Get current month and year */

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();


    /* Display month and year */

    const monthName = currentDate.toLocaleString("default", {
        month: "long"
    });

    calendarMonth.textContent = monthName + " " + year;


    /* =====================================================
       DAY NAMES
    ===================================================== */

    const dayNames = [
        "Sun",
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat"
    ];


    dayNames.forEach(function (day) {

        const dayName = document.createElement("div");

        dayName.classList.add("calendar-day-name");

        dayName.textContent = day;

        calendar.appendChild(dayName);

    });


    /* =====================================================
       FIRST DAY OF MONTH
    ===================================================== */

    const firstDay =
        new Date(year, month, 1).getDay();


    /* =====================================================
       NUMBER OF DAYS IN MONTH
    ===================================================== */

    const daysInMonth =
        new Date(year, month + 1, 0).getDate();


    /* =====================================================
       EMPTY SPACES BEFORE FIRST DAY
    ===================================================== */

    for (let i = 0; i < firstDay; i++) {

        const emptyDay =
            document.createElement("div");

        emptyDay.classList.add(
            "calendar-day",
            "empty"
        );

        calendar.appendChild(emptyDay);

    }


    /* =====================================================
       CREATE DAYS
    ===================================================== */

    for (let day = 1; day <= daysInMonth; day++) {

        const dayElement =
            document.createElement("div");


        dayElement.classList.add("calendar-day");

        dayElement.textContent = day;


        /* =================================================
           HIGHLIGHT TODAY
        ================================================= */

        const today = new Date();


        if (
            day === today.getDate() &&
            month === today.getMonth() &&
            year === today.getFullYear()
        ) {

            dayElement.classList.add("today");

        }


        calendar.appendChild(dayElement);

    }

}


/* =========================================================
   PREVIOUS MONTH
========================================================= */

function previousMonth() {

    currentDate.setMonth(
        currentDate.getMonth() - 1
    );

    renderCalendar();

}


/* =========================================================
   NEXT MONTH
========================================================= */

function nextMonth() {

    currentDate.setMonth(
        currentDate.getMonth() + 1
    );

    renderCalendar();

}


/* =========================================================
   SHOW NOTIFICATION
========================================================= */

function showNotification() {

    alert("You have no new notifications.");

}


/* =========================================================
   DARK MODE
========================================================= */

function toggleDarkMode() {

    document.body.classList.toggle("dark-mode-active");


    const button =
        document.getElementById("darkModeButton");


    if (document.body.classList.contains("dark-mode-active")) {

        button.textContent = "☀️ Light Mode";

    }
    else {

        button.textContent = "🌙 Dark Mode";

    }

}

/* =========================================================
   OPEN ADD STUDENT MODAL
========================================================= */

function openAddStudentModal() {

    const modal =
        document.getElementById("studentModal");

    if (!modal) {
        return;
    }

    modal.style.display = "flex";

}


/* =========================================================
   CLOSE ADD STUDENT MODAL
========================================================= */

function closeAddStudentModal() {

    const modal =
        document.getElementById("studentModal");

    if (!modal) {
        return;
    }

    modal.style.display = "none";

}



/* =========================================================
   VIEW ANALYTICS
========================================================= */

function viewAnalytics() {

    window.location.href = "/admin/analytics";

}


/* =========================================================
   STUDENT FORM
========================================================= */

const studentForm = document.getElementById("studentForm");

if (studentForm) {

    studentForm.addEventListener("submit", function (event) {

        event.preventDefault();


        /* Get form values */

        const studentName =
            document.getElementById("studentName").value;

        const studentNumber =
            document.getElementById("studentNumber").value;

        const studentGrade =
            document.getElementById("studentGrade").value;

        const studentClass =
            document.getElementById("studentClass").value;

        const studentAverage =
            document.getElementById("studentAverage").value;

        const studentAttendance =
            document.getElementById("studentAttendance").value;


        /* Check that required information exists */

        if (
            !studentName ||
            !studentNumber ||
            !studentGrade
        ) {

            alert("Please complete all required fields.");

            return;

        }


        /* Temporary confirmation */

        alert(
            "Student added successfully!\n\n" +
            "Name: " + studentName + "\n" +
            "Student Number: " + studentNumber + "\n" +
            "Grade: " + studentGrade
        );


        /* Close the modal */

        closeAddStudentModal();


        /* Reset the form */

        studentForm.reset();

    });

}

/* =========================================================
   OPEN EVENT MODAL
========================================================= */

function openEventModal() {

    const modal =
        document.getElementById("eventModal");

    if (!modal) {
        return;
    }

    modal.style.display = "flex";

}


/* =========================================================
   CLOSE EVENT MODAL
========================================================= */

function closeEventModal() {

    const modal =
        document.getElementById("eventModal");

    if (!modal) {
        return;
    }

    modal.style.display = "none";

}

function toggleSidebar() {
    document.body.classList.toggle("sidebar-hidden");
}




