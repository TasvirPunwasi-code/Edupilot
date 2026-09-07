document.addEventListener("DOMContentLoaded", function(){

    loadAnalyticsOptions();

    document.getElementById("classFilter").addEventListener("change", loadAnalytics);
    document.getElementById("subjectFilter").addEventListener("change", loadAnalytics);
    document.getElementById("termFilter").addEventListener("change", loadAnalytics);

});


// =========================================================
// LOAD TEACHER CLASSES AND SUBJECTS
// =========================================================

async function loadAnalyticsOptions(){

    try{

        const response = await fetch("/api/teacher/analytics/options");
        const result = await response.json();

        if(!response.ok || !result.success){

            console.error(result.message || "Could not load analytics options.");

            return;
        }


        const classFilter = document.getElementById("classFilter");
        const subjectFilter = document.getElementById("subjectFilter");


        result.classes.forEach(function(item){

            const option = document.createElement("option");

            option.value = item.class_name;
            option.textContent = item.class_name;

            classFilter.appendChild(option);

        });


        result.subjects.forEach(function(item){

            const option = document.createElement("option");

            option.value = item.subject_id;
            option.textContent = item.subject_name;

            subjectFilter.appendChild(option);

        });


        loadAnalytics();

    }
    catch(error){

        console.error("ANALYTICS OPTIONS ERROR:", error);

    }

}


// =========================================================
// LOAD ANALYTICS
// =========================================================

async function loadAnalytics(){

    const className = document.getElementById("classFilter").value;
    const subjectId = document.getElementById("subjectFilter").value;
    const term = document.getElementById("termFilter").value;


    const parameters = new URLSearchParams();

    if(className){
        parameters.append("class_name", className);
    }

    if(subjectId){
        parameters.append("subject_id", subjectId);
    }

    if(term){
        parameters.append("term", term);
    }


    try{

        const response = await fetch(`/api/teacher/analytics?${parameters.toString()}`);
        const result = await response.json();


        if(!response.ok || !result.success){

            console.error(result.message || "Could not load analytics.");

            return;
        }


        // =================================================
        // STATISTICS
        // =================================================

        document.getElementById("totalStudents").textContent = result.summary.total_students;


        if(result.summary.average_mark === null){

            document.getElementById("averageMark").textContent = "--";

        }else{

            document.getElementById("averageMark").textContent = Number(result.summary.average_mark).toFixed(2) + "%";

        }


        if(result.summary.highest_average === null){

            document.getElementById("highestAverage").textContent = "--";

        }else{

            document.getElementById("highestAverage").textContent = Number(result.summary.highest_average).toFixed(2) + "%";

        }


        document.getElementById("atRisk").textContent = result.summary.at_risk;


        // =================================================
        // ATTENTION TABLE
        // =================================================

        displayAttentionStudents(result.attention_students);


        // =================================================
        // RELOAD ALL 4 MATPLOTLIB GRAPHS
        // =================================================

        loadGraphs(parameters);

    }
    catch(error){

        console.error("LOAD ANALYTICS ERROR:", error);

    }

}


// =========================================================
// LOAD MATPLOTLIB GRAPHS
// =========================================================

function loadGraphs(parameters){

    const query = parameters.toString();
    const cacheBuster = Date.now();

    document.getElementById("classPerformanceGraph").src = `/api/teacher/analytics/graph/class-performance?${query}&v=${cacheBuster}`;

    document.getElementById("subjectPerformanceGraph").src = `/api/teacher/analytics/graph/subject-performance?${query}&v=${cacheBuster}`;

    document.getElementById("assessmentPerformanceGraph").src = `/api/teacher/analytics/graph/assessment-performance?${query}&v=${cacheBuster}`;

    document.getElementById("performanceDistributionGraph").src = `/api/teacher/analytics/graph/performance-distribution?${query}&v=${cacheBuster}`;

}


// =========================================================
// ATTENTION STUDENTS
// =========================================================

function displayAttentionStudents(students){

    const table = document.getElementById("attentionTable");
    const count = document.getElementById("attentionCount");

    table.innerHTML = "";

    count.textContent = students.length + (students.length === 1 ? " Student" : " Students");


    if(students.length === 0){

        table.innerHTML = `
            <tr>
                <td colspan="4" class="no-attention">
                    No students currently require academic attention.
                </td>
            </tr>
        `;

        return;
    }


    students.forEach(function(student){

        const row = document.createElement("tr");


        const studentCell = document.createElement("td");

        const studentInfo = document.createElement("div");
        studentInfo.className = "student-info";

        const avatar = document.createElement("div");
        avatar.className = "student-avatar";
        avatar.textContent = getInitials(student.student_name);

        const name = document.createElement("strong");
        name.textContent = student.student_name;

        studentInfo.appendChild(avatar);
        studentInfo.appendChild(name);

        studentCell.appendChild(studentInfo);


        const classCell = document.createElement("td");
        classCell.textContent = student.class_name;


        const averageCell = document.createElement("td");
        averageCell.textContent = Number(student.average_mark).toFixed(2) + "%";


        const riskCell = document.createElement("td");

        const risk = document.createElement("div");
        risk.className = "risk-student";

        const led = document.createElement("span");
        led.className = "risk-led";

        const riskText = document.createElement("span");
        riskText.className = "status status-danger";
        riskText.textContent = "Needs Support";

        risk.appendChild(led);
        risk.appendChild(riskText);

        riskCell.appendChild(risk);


        row.appendChild(studentCell);
        row.appendChild(classCell);
        row.appendChild(averageCell);
        row.appendChild(riskCell);

        table.appendChild(row);

    });

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