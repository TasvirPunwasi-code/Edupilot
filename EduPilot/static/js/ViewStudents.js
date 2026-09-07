let allStudents = [];


// =========================================================
// PAGE LOAD
// =========================================================

document.addEventListener("DOMContentLoaded", function(){

    loadStudents();

    document.getElementById("classFilter").addEventListener("change", filterStudents);
    document.getElementById("searchStudent").addEventListener("input", filterStudents);

    document.getElementById("topSearch").addEventListener("input", function(){
        document.getElementById("searchStudent").value = this.value;
        filterStudents();
    });

    document.getElementById("modalClose").addEventListener("click", closeStudentModal);

    document.getElementById("studentModal").addEventListener("click", function(event){

        if(event.target === this){
            closeStudentModal();
        }

    });

});


// =========================================================
// LOAD STUDENTS
// =========================================================

async function loadStudents(){

    const table = document.getElementById("studentsTableBody");

    try{

        const response = await fetch("/api/teacher/students");
        const result = await response.json();

        if(!response.ok || !result.success){

            table.innerHTML = `
                <tr>
                    <td colspan="5">Could not load students.</td>
                </tr>
            `;

            console.error(result.message || "Could not load students.");

            return;
        }


        allStudents = result.students;


        const classFilter = document.getElementById("classFilter");

        result.classes.forEach(function(item){

            const option = document.createElement("option");

            option.value = item.class_name;
            option.textContent = item.class_name;

            classFilter.appendChild(option);

        });


        displayStudents(allStudents);

    }
    catch(error){

        console.error("LOAD STUDENTS ERROR:", error);

        table.innerHTML = `
            <tr>
                <td colspan="5">Could not connect to the server.</td>
            </tr>
        `;

    }

}


// =========================================================
// FILTER STUDENTS
// =========================================================

function filterStudents(){

    const selectedClass = document.getElementById("classFilter").value;
    const search = document.getElementById("searchStudent").value.trim().toLowerCase();


    const filteredStudents = allStudents.filter(function(student){

        const matchesClass = !selectedClass || student.class_name === selectedClass;

        const studentName = String(student.student_name || "").toLowerCase();
        const studentNumber = String(student.student_number || "").toLowerCase();

        const matchesSearch = studentName.includes(search) || studentNumber.includes(search);

        return matchesClass && matchesSearch;

    });


    displayStudents(filteredStudents);

}


// =========================================================
// PERFORMANCE STATUS
// =========================================================

function getPerformanceStatus(average){

    if(average === null || average === undefined){

        return {
            text:"No Data",
            className:"performance-none",
            rowClass:"",
            modalClass:""
        };

    }


    average = Number(average);


    if(average < 50){

        return {
            text:"Needs Support",
            className:"performance-danger",
            rowClass:"student-risk",
            modalClass:"modal-risk"
        };

    }


    if(average < 60){

        return {
            text:"Monitor",
            className:"performance-warning",
            rowClass:"student-warning",
            modalClass:"modal-warning"
        };

    }


    return {
        text:"On Track",
        className:"performance-good",
        rowClass:"student-good",
        modalClass:"modal-good"
    };

}


// =========================================================
// DISPLAY STUDENTS
// =========================================================

function displayStudents(students){

    const table = document.getElementById("studentsTableBody");
    const noResults = document.getElementById("noResults");
    const resultsCount = document.getElementById("resultsCount");

    table.innerHTML = "";

    resultsCount.textContent = students.length + (students.length === 1 ? " student found" : " students found");


    if(students.length === 0){

        noResults.style.display = "block";

        return;
    }


    noResults.style.display = "none";


    students.forEach(function(student){

        const status = getPerformanceStatus(student.current_average);

        const row = document.createElement("tr");

        if(status.rowClass){
            row.classList.add(status.rowClass);
        }


        const studentCell = document.createElement("td");

        const studentWrapper = document.createElement("div");
        studentWrapper.className = "student-avatar";

        const avatar = document.createElement("div");
        avatar.className = "avatar-circle";
        avatar.textContent = getInitials(student.student_name);

        const studentText = document.createElement("div");

        const studentName = document.createElement("strong");
        studentName.textContent = student.student_name;

        const studentNumber = document.createElement("div");
        studentNumber.textContent = student.student_number;
        studentNumber.style.color = "#777";
        studentNumber.style.fontSize = "12px";

        studentText.appendChild(studentName);
        studentText.appendChild(studentNumber);

        studentWrapper.appendChild(avatar);
        studentWrapper.appendChild(studentText);

        studentCell.appendChild(studentWrapper);


        const classCell = document.createElement("td");
        classCell.textContent = student.class_name;


        const statusCell = document.createElement("td");

        const statusBadge = document.createElement("span");
        statusBadge.className = "performance-status " + status.className;

        const led = document.createElement("span");
        led.className = "status-led";

        const statusText = document.createElement("span");
        statusText.textContent = status.text;

        statusBadge.appendChild(led);
        statusBadge.appendChild(statusText);

        statusCell.appendChild(statusBadge);


        const averageCell = document.createElement("td");

        const averageBadge = document.createElement("span");
        averageBadge.className = "mark-pill";


        if(student.current_average === null || student.current_average === undefined){

            averageBadge.textContent = "No Data";
            averageBadge.classList.add("mark-none");

        }
        else{

            const average = Number(student.current_average);

            averageBadge.textContent = average.toFixed(2) + "%";

            if(average < 50){
                averageBadge.classList.add("mark-low");
            }
            else if(average < 60){
                averageBadge.classList.add("mark-average");
            }
            else{
                averageBadge.classList.add("mark-good");
            }

        }


        averageCell.appendChild(averageBadge);


        const actionCell = document.createElement("td");

        const viewButton = document.createElement("button");

        viewButton.className = "view-btn";
        viewButton.textContent = "View";

        viewButton.addEventListener("click", function(){
            openStudentModal(student.student_id);
        });

        actionCell.appendChild(viewButton);


        row.appendChild(studentCell);
        row.appendChild(classCell);
        row.appendChild(statusCell);
        row.appendChild(averageCell);
        row.appendChild(actionCell);

        table.appendChild(row);

    });

}


// =========================================================
// OPEN STUDENT MODAL
// =========================================================

async function openStudentModal(studentId){

    try{

        const response = await fetch(`/api/teacher/students/${studentId}`);
        const result = await response.json();


        if(!response.ok || !result.success){

            alert(result.message || "Could not load student.");

            return;
        }


        const student = result.student;
        const status = getPerformanceStatus(student.current_average);


        document.getElementById("modalAvatar").textContent = getInitials(student.student_name);
        document.getElementById("modalName").textContent = student.student_name;
        document.getElementById("modalClass").textContent = student.class_name;
        document.getElementById("modalStudentNumber").textContent = student.student_number;


        if(student.current_average === null || student.current_average === undefined){
            document.getElementById("modalAverage").textContent = "No Data";
        }
        else{
            document.getElementById("modalAverage").textContent = Number(student.current_average).toFixed(2) + "%";
        }


        const modalStatus = document.getElementById("modalStatus");

        modalStatus.innerHTML = "";

        const badge = document.createElement("span");
        badge.className = "performance-status " + status.className;

        const led = document.createElement("span");
        led.className = "status-led";

        const statusText = document.createElement("span");
        statusText.textContent = status.text;

        badge.appendChild(led);
        badge.appendChild(statusText);

        modalStatus.appendChild(badge);


        const modalAvatar = document.getElementById("modalAvatar");

        modalAvatar.classList.remove("modal-risk", "modal-warning", "modal-good");

        if(status.modalClass){
            modalAvatar.classList.add(status.modalClass);
        }


        displaySubjectBreakdown(student.subjects);


        const hasMarks = student.subjects.some(function(subject){
            return subject.subject_average !== null;
        });


        document.getElementById("modalMarksSection").style.display = hasMarks ? "block" : "none";
        document.getElementById("noMarksMessage").style.display = hasMarks ? "none" : "block";

        document.getElementById("studentModal").classList.add("open");

    }
    catch(error){

        console.error("STUDENT DETAILS ERROR:", error);

        alert("Could not connect to the server.");

    }

}


// =========================================================
// SUBJECT BREAKDOWN
// =========================================================

function displaySubjectBreakdown(subjects){

    const container = document.getElementById("subjectBreakdown");

    container.innerHTML = "";


    subjects.forEach(function(subject){

        const card = document.createElement("div");
        card.className = "subject-performance-card";


        const header = document.createElement("div");
        header.className = "subject-performance-header";


        const subjectName = document.createElement("strong");
        subjectName.textContent = subject.subject_name;


        const subjectAverage = document.createElement("span");

        if(subject.subject_average === null){
            subjectAverage.textContent = "No Marks";
        }
        else{
            subjectAverage.textContent = Number(subject.subject_average).toFixed(2) + "%";
        }


        header.appendChild(subjectName);
        header.appendChild(subjectAverage);

        card.appendChild(header);


        card.appendChild(createMarkBar("Test", subject.test_average));
        card.appendChild(createMarkBar("Assignment", subject.assignment_average));
        card.appendChild(createMarkBar("Exam", subject.exam_average));


        container.appendChild(card);

    });

}


// =========================================================
// CREATE MARK BAR
// =========================================================

function createMarkBar(labelText, value){

    const row = document.createElement("div");
    row.className = "mini-bar-row";


    const label = document.createElement("div");
    label.className = "mini-bar-label";


    const name = document.createElement("span");
    name.textContent = labelText;


    const mark = document.createElement("span");

    if(value === null || value === undefined){
        mark.textContent = "--";
    }
    else{
        mark.textContent = Number(value).toFixed(2) + "%";
    }


    label.appendChild(name);
    label.appendChild(mark);


    const track = document.createElement("div");
    track.className = "mini-bar-track";


    const fill = document.createElement("div");
    fill.className = "mini-bar-fill";


    if(value === null || value === undefined){
        fill.style.width = "0%";
    }
    else{
        fill.style.width = Math.min(Math.max(Number(value), 0), 100) + "%";
    }


    track.appendChild(fill);

    row.appendChild(label);
    row.appendChild(track);


    return row;

}


// =========================================================
// CLOSE MODAL
// =========================================================

function closeStudentModal(){

    document.getElementById("studentModal").classList.remove("open");

}


// =========================================================
// INITIALS
// =========================================================

function getInitials(name){

    const parts = String(name || "").split(" ").filter(Boolean).slice(0, 2);

    return parts.map(function(part){
        return part.charAt(0);
    }).join("").toUpperCase();

}