document.addEventListener("DOMContentLoaded", function(){

    loadTeacherOptions();

    document.getElementById("classSelect").addEventListener("change", loadStudentsIfReady);
    document.getElementById("subjectSelect").addEventListener("change", loadStudentsIfReady);
    document.getElementById("saveMarksButton").addEventListener("click", saveMarks);
    document.getElementById("clearMarksButton").addEventListener("click", clearMarks);

});


async function loadTeacherOptions(){

    const classSelect = document.getElementById("classSelect");
    const subjectSelect = document.getElementById("subjectSelect");

    try{

        const response = await fetch("/api/teacher/mark-options");

        const result = await response.json();

        if(!response.ok || !result.success){

            showMessage(
                result.message || "Could not load your classes and subjects.",
                "error"
            );

            return;
        }


        result.classes.forEach(function(item){

            const option = document.createElement("option");

            option.value = item.class_name;

            option.textContent = item.class_name;

            classSelect.appendChild(option);

        });


        result.subjects.forEach(function(subject){

            const option = document.createElement("option");

            option.value = subject.subject_id;

            option.textContent = subject.subject_name;

            subjectSelect.appendChild(option);

        });

    }
    catch(error){

        console.error("LOAD OPTIONS ERROR:", error);

        showMessage(
            "Could not connect to the server.",
            "error"
        );

    }

}


function loadStudentsIfReady(){

    const className = document.getElementById("classSelect").value;
    const subjectId = document.getElementById("subjectSelect").value;

    if(!className || !subjectId){

        document.getElementById("studentMarksTable").innerHTML = `
            <tr>
                <td colspan="3">
                    Select a class and subject to load students.
                </td>
            </tr>
        `;

        return;
    }

    loadStudents(className, subjectId);

}


async function loadStudents(className, subjectId){

    const table = document.getElementById("studentMarksTable");

    table.innerHTML = `
        <tr>
            <td colspan="3">
                Loading students...
            </td>
        </tr>
    `;


    try{

        const response = await fetch(
            `/api/teacher/mark-students?class_name=${encodeURIComponent(className)}&subject_id=${encodeURIComponent(subjectId)}`
        );

        const result = await response.json();


        if(!response.ok || !result.success){

            showMessage(
                result.message || "Could not load students.",
                "error"
            );

            table.innerHTML = "";

            return;
        }


        if(result.students.length === 0){

            table.innerHTML = `
                <tr>
                    <td colspan="3">
                        No students found for this class and subject.
                    </td>
                </tr>
            `;

            return;
        }


        table.innerHTML = "";


        result.students.forEach(function(student){

            const row = document.createElement("tr");

            const nameCell = document.createElement("td");
            nameCell.textContent = student.student_name;

            const numberCell = document.createElement("td");
            numberCell.textContent = student.student_number;

            const markCell = document.createElement("td");

            const input = document.createElement("input");

            input.type = "number";
            input.min = "0";
            input.max = "100";
            input.step = "0.01";
            input.className = "mark-input";
            input.dataset.studentId = student.student_id;

            markCell.appendChild(input);

            row.appendChild(nameCell);
            row.appendChild(numberCell);
            row.appendChild(markCell);

            table.appendChild(row);

        });

    }
    catch(error){

        console.error("LOAD STUDENTS ERROR:", error);

        showMessage(
            "Could not connect to the server.",
            "error"
        );

    }

}


async function saveMarks(){

    const className = document.getElementById("classSelect").value;
    const subjectId = document.getElementById("subjectSelect").value;
    const assessmentType = document.getElementById("assessmentSelect").value;
    const term = document.getElementById("termSelect").value;

    if(!className || !subjectId || !assessmentType || !term){

        showMessage(
            "Please select class, subject, assessment type and term.",
            "error"
        );

        return;
    }


    const inputs = document.querySelectorAll(".mark-input");

    if(inputs.length === 0){

        showMessage(
            "There are no students to save marks for.",
            "error"
        );

        return;
    }


    const marks = [];


    for(const input of inputs){

        const value = input.value.trim();

        if(value === ""){

            showMessage(
                "Please enter a mark for every student.",
                "error"
            );

            input.focus();

            return;
        }


        const numericMark = Number(value);


        if(numericMark < 0 || numericMark > 100){

            showMessage(
                "Marks must be between 0 and 100.",
                "error"
            );

            input.focus();

            return;
        }


        marks.push({
            student_id:Number(input.dataset.studentId),
            mark:numericMark
        });

    }


    try{

        const response = await fetch("/api/teacher/marks", {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                class_name:className,
                subject_id:Number(subjectId),
                assessment_type:assessmentType,
                term:Number(term),
                marks:marks
            })

        });


        const result = await response.json();


        if(response.ok && result.success){

            showMessage(
                result.message,
                "success"
            );

        }
        else{

            showMessage(
                result.message || "Could not save marks.",
                "error"
            );

        }

    }
    catch(error){

        console.error("SAVE MARKS ERROR:", error);

        showMessage(
            "Could not connect to the server.",
            "error"
        );

    }

}


function clearMarks(){

    const inputs = document.querySelectorAll(".mark-input");

    inputs.forEach(function(input){
        input.value = "";
    });

    showMessage("", "");

}


function showMessage(message, type){

    const messageElement = document.getElementById("marksMessage");

    messageElement.textContent = message;

    if(type === "success"){

        messageElement.style.color = "green";

    }
    else if(type === "error"){

        messageElement.style.color = "red";

    }
    else{

        messageElement.style.color = "";

    }

}