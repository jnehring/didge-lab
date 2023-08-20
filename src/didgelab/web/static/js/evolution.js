
/**
 * send ajax request to load general information
 * and trigger rendering the general info tab
 */
function loadGeneralInformation() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/api/general_evolution_info", true);
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            // Response
            var response = JSON.parse(this.responseText);
            
            evolutionContainer = document.getElementById("evolution_tab_container");
            evolutionContainer.innerHTML = "";
            var table = document.createElement("table");
            var tr = document.createElement("tr");
            var tdLeft = document.createElement("td");
            tdLeft.setAttribute("name", "left");
            tr.appendChild(tdLeft);
            tdRight = document.createElement("td");
            tdRight.setAttribute("name", "right");
            tr.appendChild(tdRight);
            table.appendChild(tr);
            evolutionContainer.append(table);

            generateEvolutionTable(response);
            //console.log(response);
            displayChart(
                "Losses",
                response.losses

            );
        }
    };
    xhttp.send();
}

function generateEvolutionTable(data) {
    let container = document.querySelector("#evolution_tab_container td[name=left]");
    let table = document.createElement("table");
    table.classList.add("table_margins");
    let tr = document.createElement("tr");
    tr.classList.add("odd");
    let th = document.createElement("th");
    th.innerHTML = "Property";
    tr.appendChild(th);
    th = document.createElement("th");
    th.innerHTML = "Value";
    tr.appendChild(th);
    table.appendChild(tr);

    let i=0;
    for (const [key, value] of Object.entries(data.general)) {
        let tr = document.createElement("tr");
        tr.classList.add(i % 2 == 0 ? "even" : "odd");
        let td = document.createElement("td");
        td.innerHTML = key;
        tr.appendChild(td);
        td = document.createElement("td");
        td.innerHTML = Math.round(100 * parseFloat(value)) / 100;
        tr.appendChild(td);
        table.appendChild(tr);
        i+=1;
    }
    container.appendChild(table);
}

function displayChart(heading, losses) {
    let container = document.querySelector("#evolution_tab_container td[name=right]");
    var div = document.createElement("div");
    div.setAttribute("id", "loss_chart");
    container.appendChild(div);

    var data = [];

    for (const [key, value] of Object.entries(losses)) {
        if( key=="generation") continue;
        var trace1 = {
            x: losses.generation,
            y: value,
            type: 'line',
            name: key
        };
        data.push(trace1);
    }

    var layout = {
        title: heading,
        xaxis: {
            title: {
                text: 'Generation',
            },
            fixedrange: true
        },
        yaxis: {
            title: {
                text: "Loss",
            },
            fixedrange: true
        }
    };

    var config = {
        displayModeBar: false
    };
    Plotly.newPlot("loss_chart", data, layout, config);
}
