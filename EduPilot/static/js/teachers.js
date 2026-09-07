let teachers = [];


/* =========================================================
   LOAD TEACHERS
========================================================= */

async function loadTeachers(){

    try{

        const response =
            await fetch(
                "/api/teachers"
            );


        const result =
            await response.json();


        if(!response.ok || !result.success){

            alert(
                result.message ||
                "Could not load teachers."
            );

            return;

        }


        teachers =
            result.teachers;


        displayTeachers(
            teachers
        );


        document
            .getElementById(
                "totalTeachers"
            )
            .textContent =
                teachers.length;


        document
            .getElementById(
                "activeTeachers"
            )
            .textContent =
                teachers.length;

    }
    catch(error){

        console.error(error);

    }

}


/* =========================================================
   DISPLAY TEACHERS
========================================================= */

function displayTeachers(data){

    const table =
        document.getElementById(
            "teacherTable"
        );


    table.innerHTML = "";


    data.forEach(
        function(teacher){

            const row =
                document.createElement(
                    "tr"
                );


            const subjects =
                Array.isArray(
                    teacher.subjects
                )
                ? teacher.subjects.join(", ")
                : teacher.subjects || "";


            const classes =
                Array.isArray(
                    teacher.classes
                )
                ? teacher.classes.join(", ")
                : teacher.classes || "";


            row.innerHTML = `

                <td>
                    ${escapeHTML(
                        teacher.name
                    )}
                </td>

                <td>
                    ${escapeHTML(
                        teacher.email
                    )}
                </td>

                <td>
                    ${escapeHTML(
                        subjects
                    )}
                </td>

                <td>
                    ${escapeHTML(
                        classes
                    )}
                </td>

                <td>

                    <button
                        class="view-btn"
                        onclick="viewTeacher(
                            ${teacher.teacher_id}
                        )">

                        View

                    </button>


                    <button
                        class="edit-btn"
                        onclick="editTeacher(
                            ${teacher.teacher_id}
                        )">

                        Edit

                    </button>


                    <button
                        class="remove-btn"
                        onclick="removeTeacher(
                            ${teacher.teacher_id}
                        )">

                        Remove

                    </button>

                </td>

            `;


            table.appendChild(
                row
            );

        }
    );

}


/* =========================================================
   ADD MODAL
========================================================= */

function openAddTeacherModal(){

    document
        .getElementById(
            "addTeacherModal"
        )
        .classList.add(
            "show"
        );

}


function closeAddTeacherModal(){

    document
        .getElementById(
            "addTeacherModal"
        )
        .classList.remove(
            "show"
        );


    document
        .getElementById(
            "teacherForm"
        )
        .reset();

}


/* =========================================================
   ADD TEACHER
========================================================= */

document
.getElementById(
    "teacherForm"
)
.addEventListener(
    "submit",
    async function(event){

        event.preventDefault();


        const name =
            document
            .getElementById(
                "teacherName"
            )
            .value
            .trim();
        const namePattern = /^[A-Za-z\s'-]+$/;

        if(!namePattern.test(name)){
            alert("Teacher name cannot contain numbers or special characters.");
        return;
}


        const email =
            document
            .getElementById(
                "teacherEmail"
            )
            .value
            .trim();
        const gmailPattern = /^[A-Za-z0-9._%+-]+@gmail\.com$/;

    if(!gmailPattern.test(email)){
        alert("Please enter a valid Gmail address ending in @gmail.com.");
        return;
    }


        const password =
            document
            .getElementById(
                "teacherPassword"
            )
            .value;


        const subjects =
            Array.from(
                document.querySelectorAll(
                    'input[name="subjects"]:checked'
                )
            ).map(
                checkbox =>
                    checkbox.value
            );


        const classes =
            Array.from(
                document.querySelectorAll(
                    'input[name="classes"]:checked'
                )
            ).map(
                checkbox =>
                    checkbox.value
            );


        if(subjects.length === 0){

            alert(
                "Select at least one subject."
            );

            return;

        }


        if(classes.length === 0){

            alert(
                "Select at least one class."
            );

            return;

        }


        try{

            const response =
                await fetch(
                    "/api/teachers",
                    {

                        method:"POST",

                        headers:{
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({

                                name:name,

                                email:email,

                                password:password,

                                subjects:subjects,

                                classes:classes

                            })

                    }
                );


            const result =
                await response.json();


            if(response.ok){

                alert(
                    "Teacher added successfully."
                );


                closeAddTeacherModal();


                loadTeachers();

            }
            else{

                alert(
                    result.message ||
                    "Could not add teacher."
                );

            }

        }
        catch(error){

            console.error(error);

            alert(
                "Could not connect to Flask."
            );

        }

    }
);


/* =========================================================
   VIEW TEACHER
========================================================= */

function viewTeacher(id){

    const teacher =
        teachers.find(
            t =>
                Number(
                    t.teacher_id
                ) === Number(id)
        );


    if(!teacher){
        return;
    }


    document
        .getElementById(
            "viewName"
        )
        .textContent =
            teacher.name;


    document
        .getElementById(
            "viewEmail"
        )
        .textContent =
            teacher.email;


    document
        .getElementById(
            "viewSubjects"
        )
        .textContent =
            Array.isArray(
                teacher.subjects
            )
            ? teacher.subjects.join(", ")
            : teacher.subjects || "None";


    document
        .getElementById(
            "viewClasses"
        )
        .textContent =
            Array.isArray(
                teacher.classes
            )
            ? teacher.classes.join(", ")
            : teacher.classes || "None";


    document
        .getElementById(
            "viewTeacherModal"
        )
        .classList.add(
            "show"
        );

}


function closeViewTeacherModal(){

    document
        .getElementById(
            "viewTeacherModal"
        )
        .classList.remove(
            "show"
        );

}


/* =========================================================
   EDIT TEACHER
========================================================= */

function editTeacher(id){

    const teacher =
        teachers.find(
            t =>
                Number(
                    t.teacher_id
                ) === Number(id)
        );


    if(!teacher){
        return;
    }


    document
        .getElementById(
            "editTeacherId"
        )
        .value =
            teacher.teacher_id;


    document
        .getElementById(
            "editTeacherName"
        )
        .value =
            teacher.name;


    document
        .getElementById(
            "editTeacherEmail"
        )
        .value =
            teacher.email;


    document
        .getElementById(
            "editTeacherPassword"
        )
        .value = "";


    let subjectArray = [];

    if(
        Array.isArray(
            teacher.subjects
        )
    ){

        subjectArray =
            teacher.subjects;

    }
    else if(
        teacher.subjects
    ){

        subjectArray =
            teacher.subjects
            .split(",")
            .map(
                item =>
                    item.trim()
            );

    }


    document
    .querySelectorAll(
        'input[name="editSubjects"]'
    )
    .forEach(
        function(checkbox){

            checkbox.checked =
                subjectArray.includes(
                    checkbox.value
                );

        }
    );


    let classArray = [];

    if(
        Array.isArray(
            teacher.classes
        )
    ){

        classArray =
            teacher.classes;

    }
    else if(
        teacher.classes
    ){

        classArray =
            teacher.classes
            .split(",")
            .map(
                item =>
                    item.trim()
            );

    }


    document
    .querySelectorAll(
        'input[name="editClasses"]'
    )
    .forEach(
        function(checkbox){

            checkbox.checked =
                classArray.includes(
                    checkbox.value
                );

        }
    );


    document
        .getElementById(
            "editTeacherModal"
        )
        .classList.add(
            "show"
        );

}


function closeEditTeacherModal(){

    document
        .getElementById(
            "editTeacherModal"
        )
        .classList.remove(
            "show"
        );

}


/* =========================================================
   SAVE EDIT
========================================================= */

document
.getElementById(
    "editTeacherForm"
)
.addEventListener(
    "submit",
    async function(event){

        event.preventDefault();


        const id =
            document
            .getElementById(
                "editTeacherId"
            )
            .value;


        const subjects =
            Array.from(
                document.querySelectorAll(
                    'input[name="editSubjects"]:checked'
                )
            ).map(
                checkbox =>
                    checkbox.value
            );


        const classes =
            Array.from(
                document.querySelectorAll(
                    'input[name="editClasses"]:checked'
                )
            ).map(
                checkbox =>
                    checkbox.value
            );


        const data = {

            name:
                document
                .getElementById(
                    "editTeacherName"
                )
                .value
                .trim(),

            email:
                document
                .getElementById(
                    "editTeacherEmail"
                )
                .value
                .trim(),

            password:
                document
                .getElementById(
                    "editTeacherPassword"
                )
                .value,

            subjects:
                subjects,

            classes:
                classes

        };


        try{

            const response =
                await fetch(
                    `/api/teachers/${id}`,
                    {

                        method:"PUT",

                        headers:{
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                data
                            )

                    }
                );


            const result =
                await response.json();


            if(response.ok){

                alert(
                    "Teacher updated successfully."
                );


                closeEditTeacherModal();


                loadTeachers();

            }
            else{

                alert(
                    result.message ||
                    "Could not update teacher."
                );

            }

        }
        catch(error){

            console.error(error);

        }

    }
);


/* =========================================================
   REMOVE TEACHER
========================================================= */

async function removeTeacher(id){

    const confirmed =
        confirm(
            "Are you sure you want to remove this teacher?"
        );


    if(!confirmed){
        return;
    }


    try{

        const response =
            await fetch(
                `/api/teachers/${id}`,
                {
                    method:"DELETE"
                }
            );


        const result =
            await response.json();


        if(response.ok){

            alert(
                "Teacher removed successfully."
            );


            loadTeachers();

        }
        else{

            alert(
                result.message ||
                "Could not remove teacher."
            );

        }

    }
    catch(error){

        console.error(error);

    }

}


/* =========================================================
   SEARCH
========================================================= */

document
.getElementById(
    "teacherSearch"
)
.addEventListener(
    "input",
    function(){

        const search =
            this.value
            .toLowerCase()
            .trim();


        const filtered =
            teachers.filter(
                function(teacher){

                    const subjects =
                        Array.isArray(
                            teacher.subjects
                        )
                        ? teacher.subjects.join(" ")
                        : teacher.subjects || "";


                    const classes =
                        Array.isArray(
                            teacher.classes
                        )
                        ? teacher.classes.join(" ")
                        : teacher.classes || "";


                    return (

                        teacher.name
                        .toLowerCase()
                        .includes(search)

                        ||

                        teacher.email
                        .toLowerCase()
                        .includes(search)

                        ||

                        subjects
                        .toLowerCase()
                        .includes(search)

                        ||

                        classes
                        .toLowerCase()
                        .includes(search)

                    );

                }
            );


        displayTeachers(
            filtered
        );

    }
);


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHTML(value){

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        String(
            value ?? ""
        );

    return div.innerHTML;

}


/* =========================================================
   DARK MODE
========================================================= */

function toggleDarkMode(){

    document
        .body
        .classList
        .toggle(
            "dark"
        );

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

    window.location.href =
        "/logout";

}


/* =========================================================
   CALENDAR
========================================================= */

let calendarDate =
    new Date();


function renderCalendar(){

    const calendar =
        document.getElementById(
            "calendar"
        );


    calendar.innerHTML = "";


    const year =
        calendarDate.getFullYear();


    const month =
        calendarDate.getMonth();


    const months = [
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


    document
        .getElementById(
            "calendarMonth"
        )
        .textContent =
            months[month] +
            " " +
            year;


    const headings =
        ["S","M","T","W","T","F","S"];


    headings.forEach(
        function(day){

            const div =
                document.createElement(
                    "div"
                );

            div.className =
                "calendar-day-name";

            div.textContent =
                day;

            calendar.appendChild(
                div
            );

        }
    );


    const firstDay =
        new Date(
            year,
            month,
            1
        ).getDay();


    const days =
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

        const div =
            document.createElement(
                "div"
            );

        div.className =
            "calendar-day empty";

        calendar.appendChild(
            div
        );

    }


    const today =
        new Date();


    for(
        let day = 1;
        day <= days;
        day++
    ){

        const div =
            document.createElement(
                "div"
            );


        div.className =
            "calendar-day";


        div.textContent =
            day;


        if(
            day === today.getDate() &&
            month === today.getMonth() &&
            year === today.getFullYear()
        ){

            div.classList.add(
                "today"
            );

        }


        calendar.appendChild(
            div
        );

    }

}


function previousMonth(){

    calendarDate.setMonth(
        calendarDate.getMonth() - 1
    );

    renderCalendar();

}


function nextMonth(){

    calendarDate.setMonth(
        calendarDate.getMonth() + 1
    );

    renderCalendar();

}


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function(){

        loadTeachers();

        renderCalendar();

    }
);
