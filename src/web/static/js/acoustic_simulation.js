function run_acoustic_simulation() {
    document.getElementById("acoustic_sim_content").innerHTML = "";
    run_request();
}

function run_simulation_if_open(){
    acoustic_open = document.querySelector("#acoustic_sim_tab").style.display == "block";
    if(acoustic_open){
        run_acoustic_simulation()
    }
}

// send geometry to api and get response
function run_request() {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "../api/acoustic_simulation");
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            data = JSON.parse(xhr.responseText);
            displayTuningTable(data.notes);
            displayChart(
                "Impedance Spektrum", 
                data.spektra.freqs, 
                data.spektra.impedance, 
                "Impedance [MOhm]", 
                "impedance_chart"
            );
            displayChart(
                "Ground Tone Spektrum", 
                data.spektra.freqs, 
                data.spektra.ground, 
                "dB", 
                "groundtone_chart"
            );
            displayChart(
                "1st Overblow Spektrum", 
                data.spektra.freqs, 
                data.spektra.overblow, 
                "dB", 
                "overblow_chart"
            );
        }
    };

    let data = {
        "geo": geo
    }
    data = JSON.stringify(data);

    xhr.send(data);
}

function displayChart(heading, xData, yData, yAxisLabel, divId) {
    father_div = document.getElementById("acoustic_sim_content");

    var div = document.createElement("div");
    div.setAttribute("id", divId);
    father_div.appendChild(div);

    var trace1 = {
        x: xData,
        y: yData,
        type: 'line'
    };

    var data = [trace1];

    var layout = {
        title: heading,
        xaxis: {
            title: {
                text: 'Frequency',
            },
            fixedrange: true
        },
        yaxis: {
            title: {
                text: yAxisLabel,
            },
            fixedrange: true
        }
    };

    var config = {
        displayModeBar: false
    };
    Plotly.newPlot(divId, data, layout, config);
}

function displayTuningTable(data) {
    father_div = document.getElementById("acoustic_sim_content");

    h3 = document.createElement("h3");
    h3.innerHTML = "Impedance Peaks";
    father_div.append(h3);

    table = document.createElement("table");
    table.classList.add("table_margins");
    tr = document.createElement("tr");
    tr.classList.add("odd");
    table.appendChild(tr);

    headings = ["Frequency (Hz)", "Note", "Impedance", "Tuning (Cent)"];
    for (var i = 0; i < headings.length; i++) {
        th = document.createElement("th");
        th.innerHTML = headings[i];
        tr.appendChild(th);
    }

    for (var i = 0; i < data.length; i++) {
        tr = document.createElement("tr")
        tr.classList.add(i % 2 == 0 ? "even" : "odd");
        table.appendChild(tr);

        row = [
            data[i]["freq"],
            data[i]["note-name"],
            data[i]["impedance"].toExponential(2),
            Math.round(data[i]["cent-diff"]),
        ]
        for (var j = 0; j < row.length; j++) {
            td = document.createElement("td");
            td.innerHTML = row[j];
            tr.appendChild(td);
        }
    }

    father_div.appendChild(table);
}