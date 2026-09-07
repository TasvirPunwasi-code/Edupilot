

/* =========================================================
   ADD STUDENT MODAL
========================================================= */

function openAddStudentModal(){

    document
        .getElementById("addStudentModal")
        .classList.add("show");

    document
        .getElementById("studentName")
        .focus();

}


function closeAddStudentModal(){

    document
        .getElementById("addStudentModal")
        .classList.remove("show");

    document
        .getElementById("studentForm")
        .reset();

}


/* =========================================================
   CLOSE MODAL OUTSIDE
========================================================= */

document
    .getElementById("addStudentModal")
    .addEventListener(
        "click",
        function(event){

            if(event.target === this){

                closeAddStudentModal();

            }

        }
    );


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHTML(value){

    const div =
        document.createElement("div");

    div.textContent =
        String(value ?? "");

    return div.innerHTML;

}


/* =========================================================
   LOAD STUDENTS
========================================================= */

async function loadStudents(){

    const table =
        document.getElementById(
            "studentTable"
        );

    const emptyMessage =
        document.getElementById(
            "emptyMessage"
        );


    try{

        const response =
            await fetch(
                "/api/students"
            );


        const result =
            await response.json();


        if(
            !response.ok ||
            !result.success
        ){

            throw new Error(
                result.message ||
                "Could not load students."
            );

        }


        table.innerHTML = "";


        if(
            !result.students ||
            result.students.length === 0
        ){

            emptyMessage.style.display =
                "block";

            document
                .getElementById("totalStudents")
                .textContent = "0";

            return;

        }


        emptyMessage.style.display =
            "none";


        result.students.forEach(
            function(student){

                const row =
                    document.createElement("tr");


                row.innerHTML = `

                    <td>
                        ${escapeHTML(
                            student.student_name
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            student.student_number
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            student.grade
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            student.class_name
                        )}
                    </td>

                    <td>
                        ${escapeHTML(
                            student.subjects || ""
                        )}
                    </td>

                    <td>

                        ${escapeHTML(
                            student.emergency_contact_name || ""
                        )}

                        ${
                            student.emergency_contact_number
                            ? " - " +
                              escapeHTML(
                                  student.emergency_contact_number
                              )
                            : ""
                        }

                    </td>

                    <td>
                        ${escapeHTML(
                            student.allergy_details || ""
                        )}
                    </td>

                    <td>

                        <button
                            type="button"
                            class="delete-btn"
                            onclick="deleteStudent(
                                ${Number(student.student_id)}
                            )">

                            Delete

                        </button>

                    </td>

                `;


                table.appendChild(row);

            }
        );


        document
            .getElementById("totalStudents")
            .textContent =
            result.students.length;


    }
    catch(error){

        console.error(
            "Load students error:",
            error
        );

        table.innerHTML = "";

        emptyMessage.style.display =
            "block";

        emptyMessage.textContent =
            "Could not load students.";

    }

}


/* =========================================================
   ADD STUDENT
========================================================= */

document
    .getElementById("studentForm")
    .addEventListener(
        "submit",
        async function(event){

            event.preventDefault();


            /* ---------------------------------------------
               GET VALUES
            --------------------------------------------- */

            const studentName =
                document
                    .getElementById("studentName")
                    .value
                    .trim();


            const studentNumber =
                document
                    .getElementById("studentNumber")
                    .value
                    .trim();


            const grade =
                document
                    .getElementById("studentGrade")
                    .value;


            const className =
                document
                    .getElementById("studentClass")
                    .value
                    .trim();


            const emergencyContactName =
                document
                    .getElementById(
                        "emergencyContactName"
                    )
                    .value
                    .trim();


            const emergencyContactNumber =
                document
                    .getElementById(
                        "emergencyContactNumber"
                    )
                    .value
                    .trim();


            const allergyDetails =
                document
                    .getElementById(
                        "allergyDetails"
                    )
                    .value
                    .trim();

            const namePattern = /^[A-Za-z\s'-]+$/;
            const studentNumberPattern = /^[0-9]+$/;

            if(!namePattern.test(studentName)){
                alert("Student name cannot contain numbers or special characters.");
            return;
            }

            if(!studentNumberPattern.test(studentNumber)){
                alert("Student number must contain numbers only.");
            return;
            }

            if(!namePattern.test(emergencyContactName)){
                alert("Emergency contact name cannot contain numbers or special characters.");
            return;
            }
            if(!studentNumberPattern.test(emergencyContactNumber)){
                alert("Emergency contact number must contain numbers only.");
            return;
            }


            /* ---------------------------------------------
               GET SUBJECTS
            --------------------------------------------- */

            const subjects =
                Array.from(
                    document.querySelectorAll(
                        'input[name="subjects"]:checked'
                    )
                ).map(
                    function(checkbox){

                        return checkbox.value;

                    }
                );


            /* ---------------------------------------------
               CLIENT VALIDATION
            --------------------------------------------- */

            if(
                !studentName ||
                !studentNumber ||
                !grade ||
                !className
            ){

                alert(
                    "Please complete all required fields."
                );

                return;

            }


            try{

                const response =
                    await fetch(
                        "/api/students",
                        {

                            method:"POST",

                            headers:{
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    student_name:
                                        studentName,

                                    student_number:
                                        studentNumber,

                                    grade:
                                        grade,

                                    class_name:
                                        className,

                                    subjects:
                                        subjects,

                                    emergency_contact_name:
                                        emergencyContactName,

                                    emergency_contact_number:
                                        emergencyContactNumber,

                                    allergy_details:
                                        allergyDetails

                                })

                        }
                    );


                const result =
                    await response.json();


                if(response.ok){

                    alert(
                        "Student added successfully."
                    );


                    closeAddStudentModal();


                    /*
                       Reload from MySQL so the
                       new record appears in the table.
                    */

                    loadStudents();

                }

                else{

                    alert(
                        result.message ||
                        "Could not add student."
                    );

                }

            }

            catch(error){

                console.error(
                    "Add student error:",
                    error
                );

                alert(
                    "Could not connect to the Flask server."
                );

            }

        }
    );


/* =========================================================
   DELETE STUDENT
========================================================= */

async function deleteStudent(studentId){

    const confirmed =
        confirm(
            "Are you sure you want to delete this student?"
        );


    if(!confirmed){

        return;

    }


    try{

        const response =
            await fetch(
                `/api/students/${studentId}`,
                {
                    method:"DELETE"
                }
            );


        const result =
            await response.json();


        if(response.ok){

            alert(
                "Student deleted successfully."
            );


            /*
               Reload the table from MySQL.
            */

            loadStudents();

        }

        else{

            alert(
                result.message ||
                "Could not delete student."
            );

        }

    }

    catch(error){

        console.error(
            "Delete student error:",
            error
        );

        alert(
            "Could not connect to the Flask server."
        );

    }

}


/* =========================================================
   SEARCH STUDENTS
========================================================= */

document
    .getElementById("studentSearch")
    .addEventListener(
        "input",
        function(){

            const search =
                this.value
                    .toLowerCase()
                    .trim();


            const rows =
                document.querySelectorAll(
                    "#studentTable tr"
                );


            rows.forEach(
                function(row){

                    const text =
                        row.textContent
                            .toLowerCase();


                    row.style.display =
                        text.includes(search)
                        ? ""
                        : "none";

                }
            );

        }
    );


/* =========================================================
   DARK MODE
========================================================= */

function toggleDarkMode(){

    document
        .body
        .classList
        .toggle("dark");

}


/* =========================================================
   NOTIFICATION
========================================================= */

function showNotification(){

    alert(
        "No new notifications."
    );

}


/* =========================================================
   LOGOUT
========================================================= */

function logout(){

    const confirmed =
        confirm(
            "Are you sure you want to logout?"
        );


    if(!confirmed){

        return;

    }


    /*
       Change this later to your
       Flask logout route.
    */

    window.location.href =
        "/logout";

}


/* =========================================================
   CALENDAR
========================================================= */

let currentDate =
    new Date();


function renderCalendar(){

    const calendar =
        document.getElementById(
            "calendar"
        );

    const monthLabel =
        document.getElementById(
            "calendarMonth"
        );


    const year =
        currentDate.getFullYear();


    const month =
        currentDate.getMonth();


    const monthNames = [

        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"

    ];


    monthLabel.textContent =
        monthNames[month] +
        " " +
        year;


    calendar.innerHTML = "";


    const dayNames = [

        "S",
        "M",
        "T",
        "W",
        "T",
        "F",
        "S"

    ];


    dayNames.forEach(
        function(day){

            const element =
                document.createElement("div");

            element.className =
                "calendar-day-name";

            element.textContent =
                day;

            calendar.appendChild(element);

        }
    );


    const firstDay =
        new Date(
            year,
            month,
            1
        ).getDay();


    const daysInMonth =
        new Date(
            year,
            month + 1,
            0
        ).getDate();


    for(
        let i = 0;
        i < firstDay;
        i++
    ){

        const empty =
            document.createElement("div");

        empty.className =
            "calendar-day empty";

        calendar.appendChild(empty);

    }


    const today =
        new Date();


    for(
        let day = 1;
        day <= daysInMonth;
        day++
    ){

        const element =
            document.createElement("div");


        element.className =
            "calendar-day";


        element.textContent =
            day;


        if(
            day === today.getDate() &&
            month === today.getMonth() &&
            year === today.getFullYear()
        ){

            element.classList.add(
                "today"
            );

        }


        calendar.appendChild(element);

    }

}


function previousMonth(){

    currentDate.setMonth(
        currentDate.getMonth() - 1
    );

    renderCalendar();

}


function nextMonth(){

    currentDate.setMonth(
        currentDate.getMonth() + 1
    );

    renderCalendar();

}


/* =========================================================
   PAGE LOAD
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function(){

        loadStudents();

        renderCalendar();

    }
);