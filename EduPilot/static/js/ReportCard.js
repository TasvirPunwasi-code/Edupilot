document.addEventListener("DOMContentLoaded", function(){
    loadStudents();

    document.getElementById("loadReportButton").addEventListener("click", loadReport);
    document.getElementById("printReportButton").addEventListener("click", generatePDF);
});

async function loadStudents(){
    try{
        const response = await fetch("/api/admin/report-card/students");
        const students = await response.json();
        const select = document.getElementById("studentSelect");

        students.forEach(function(student){
            const option = document.createElement("option");
            option.value = student.student_id;
            option.textContent = student.student_name + " - " + student.class_name;
            select.appendChild(option);
        });
    }
    catch(error){
        console.error("STUDENT LOAD ERROR:", error);
    }
}

async function loadReport(){
    const studentId = document.getElementById("studentSelect").value;
    const term = document.getElementById("termSelect").value;
    const message = document.getElementById("reportMessage");

    if(!studentId || !term){
        message.textContent = "Please select a student and term.";
        return;
    }

    try{
        const response = await fetch(`/api/admin/report-card/${studentId}?term=${term}`);
        const data = await response.json();

        if(!response.ok){
            message.textContent = data.message || "Could not load report.";
            return;
        }

        displayReport(data);
        message.textContent = "";
    }
    catch(error){
        console.error("REPORT ERROR:", error);
        message.textContent = "Could not load report.";
    }
}

function displayReport(data){
    document.getElementById("studentName").textContent = data.student.student_name;
    document.getElementById("studentNumber").textContent = data.student.student_number;
    document.getElementById("studentGrade").textContent = data.student.grade;
    document.getElementById("studentClass").textContent = data.student.class_name;
    document.getElementById("reportTerm").textContent = "Term " + data.term;
    document.getElementById("overallAverage").textContent = formatMark(data.overall_average);

    const body = document.getElementById("reportMarksBody");

    body.innerHTML = "";

    data.subjects.forEach(function(subject){
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${subject.subject_name}</td>
            <td>${formatMark(subject.test_average)}</td>
            <td>${formatMark(subject.assignment_average)}</td>
            <td>${formatMark(subject.exam_average)}</td>
            <td><strong>${formatMark(subject.final_mark)}</strong></td>
        `;

        body.appendChild(row);
    });

    document.getElementById("reportSection").style.display = "block";
}

function formatMark(mark){
    if(mark === null || mark === undefined){
        return "N/A";
    }

    return Number(mark).toFixed(2) + "%";
}

function generatePDF(){
    const studentId = document.getElementById("studentSelect").value;
    const term = document.getElementById("termSelect").value;

    if(!studentId || !term){
        return;
    }

    const form = document.createElement("form");

    form.method = "POST";
    form.action = `/admin/report-card/${studentId}/pdf`;
    form.target = "_blank";

    addFormField(form, "term", term);

    document.body.appendChild(form);

    form.submit();

    form.remove();
}

function addFormField(form, name, value){
    const input = document.createElement("input");

    input.type = "hidden";
    input.name = name;
    input.value = value;

    form.appendChild(input);
}