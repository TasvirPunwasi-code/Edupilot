document.addEventListener("DOMContentLoaded", function(){

    loadTeacherOptions();

    document.getElementById("classSelect").addEventListener("change", loadMarksIfReady);
    document.getElementById("subjectSelect").addEventListener("change", loadMarksIfReady);
    document.getElementById("assessmentSelect").addEventListener("change", loadMarksIfReady);
    document.getElementById("termSelect").addEventListener("change", loadMarksIfReady);
    document.getElementById("searchStudent").addEventListener("input", searchStudents);
    document.getElementById("saveMarks").addEventListener("click", saveAllChanges);

});


async function loadTeacherOptions(){

    try{

        const response = await fetch("/api/teacher/mark-options");
        const result = await response.json();

        if(!response.ok || !result.success){
            showMessage(result.message || "Could not load classes and subjects.", "error");
            return;
        }

        const classSelect = document.getElementById("classSelect");
        const subjectSelect = document.getElementById("subjectSelect");


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

        showMessage("Could not connect to the server.", "error");

    }

}


function loadMarksIfReady(){

    const className = document.getElementById("classSelect").value;
    const subjectId = document.getElementById("subjectSelect").value;
    const assessmentType = document.getElementById("assessmentSelect").value;
    const term = document.getElementById("termSelect").value;


    if(!className || !subjectId || !assessmentType || !term){

        document.getElementById("marksTable").innerHTML = `
            <tr>
                <td colspan="5">
                    Select class, subject, assessment and term to load marks.
                </td>
            </tr>
        `;

        return;
    }


    loadMarks(className, subjectId, assessmentType, term);

}


async function loadMarks(className, subjectId, assessmentType, term){

    const table = document.getElementById("marksTable");

    table.innerHTML = `
        <tr>
            <td colspan="5">Loading marks...</td>
        </tr>
    `;


    try{

        const url = `/api/teacher/edit-marks?class_name=${encodeURIComponent(className)}&subject_id=${encodeURIComponent(subjectId)}&assessment_type=${encodeURIComponent(assessmentType)}&term=${encodeURIComponent(term)}`;

        const response = await fetch(url);

        const result = await response.json();


        if(!response.ok || !result.success){

            showMessage(result.message || "Could not load marks.", "error");
            table.innerHTML = "";

            return;
        }


        if(result.marks.length === 0){

            table.innerHTML = `
                <tr>
                    <td colspan="5">
                        No captured marks were found for this selection.
                    </td>
                </tr>
            `;

            return;
        }


        table.innerHTML = "";


        result.marks.forEach(function(item){

            const row = document.createElement("tr");

            row.dataset.markId = item.mark_id;


            const studentCell = document.createElement("td");
            studentCell.textContent = item.student_name;


            const numberCell = document.createElement("td");
            numberCell.textContent = item.student_number;


            const currentCell = document.createElement("td");
            currentCell.textContent = `${item.mark}%`;
            currentCell.className = "current-mark";


            const newMarkCell = document.createElement("td");

            const input = document.createElement("input");

            input.type = "number";
            input.min = "0";
            input.max = "100";
            input.step = "0.01";
            input.value = item.mark;
            input.className = "edit-mark-input";
            input.dataset.markId = item.mark_id;

            newMarkCell.appendChild(input);


            const actionCell = document.createElement("td");

            const actions = document.createElement("div");
            actions.className = "action-buttons";


            const updateButton = document.createElement("button");

            updateButton.className = "update-btn";
            updateButton.textContent = "Update";

            updateButton.addEventListener("click", function(){
                updateSingleMark(item.mark_id, input);
            });


            const deleteButton = document.createElement("button");

            deleteButton.className = "delete-btn";
            deleteButton.textContent = "Delete";

            deleteButton.addEventListener("click", function(){
                deleteMark(item.mark_id);
            });


            actions.appendChild(updateButton);
            actions.appendChild(deleteButton);

            actionCell.appendChild(actions);


            row.appendChild(studentCell);
            row.appendChild(numberCell);
            row.appendChild(currentCell);
            row.appendChild(newMarkCell);
            row.appendChild(actionCell);

            table.appendChild(row);

        });

    }
    catch(error){

        console.error("LOAD MARKS ERROR:", error);

        showMessage("Could not connect to the server.", "error");

    }

}


async function updateSingleMark(markId, input){

    const mark = Number(input.value);


    if(input.value === "" || mark < 0 || mark > 100){

        showMessage("Mark must be between 0 and 100.", "error");

        return;
    }


    try{

        const response = await fetch(`/api/teacher/marks/${markId}`, {

            method:"PUT",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                mark:mark
            })

        });


        const result = await response.json();


        if(response.ok && result.success){

            showMessage(result.message, "success");

            loadMarksIfReady();

        }
        else{

            showMessage(result.message || "Could not update mark.", "error");

        }

    }
    catch(error){

        console.error("UPDATE MARK ERROR:", error);

        showMessage("Could not connect to the server.", "error");

    }

}


async function saveAllChanges(){

    const inputs = document.querySelectorAll(".edit-mark-input");


    if(inputs.length === 0){

        showMessage("There are no marks to update.", "error");

        return;
    }


    const marks = [];


    for(const input of inputs){

        const mark = Number(input.value);


        if(input.value === "" || mark < 0 || mark > 100){

            showMessage("All marks must be between 0 and 100.", "error");

            input.focus();

            return;
        }


        marks.push({
            mark_id:Number(input.dataset.markId),
            mark:mark
        });

    }


    try{

        const response = await fetch("/api/teacher/marks/bulk-update", {

            method:"PUT",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                marks:marks
            })

        });


        const result = await response.json();


        if(response.ok && result.success){

            showMessage(result.message, "success");

            loadMarksIfReady();

        }
        else{

            showMessage(result.message || "Could not update marks.", "error");

        }

    }
    catch(error){

        console.error("SAVE ALL ERROR:", error);

        showMessage("Could not connect to the server.", "error");

    }

}


async function deleteMark(markId){

    const confirmed = confirm("Are you sure you want to delete this mark?");

    if(!confirmed){
        return;
    }


    try{

        const response = await fetch(`/api/teacher/marks/${markId}`, {
            method:"DELETE"
        });


        const result = await response.json();


        if(response.ok && result.success){

            showMessage(result.message, "success");

            loadMarksIfReady();

        }
        else{

            showMessage(result.message || "Could not delete mark.", "error");

        }

    }
    catch(error){

        console.error("DELETE MARK ERROR:", error);

        showMessage("Could not connect to the server.", "error");

    }

}


function searchStudents(){

    const search = document.getElementById("searchStudent").value.toLowerCase();

    const rows = document.querySelectorAll("#marksTable tr");


    rows.forEach(function(row){

        const studentCell = row.querySelector("td");

        if(!studentCell){
            return;
        }

        const studentName = studentCell.textContent.toLowerCase();

        row.style.display = studentName.includes(search) ? "" : "none";

    });

}


function showMessage(message, type){

    const element = document.getElementById("editMessage");

    element.textContent = message;

    if(type === "success"){
        element.style.color = "green";
    }
    else if(type === "error"){
        element.style.color = "red";
    }
    else{
        element.style.color = "";
    }

}