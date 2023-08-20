var displayMutantIndex = 0;
var populationSize;

/**
 * send ajax request to load general information
 * and trigger rendering the general info tab
 */
function loadMutant() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/api/get_mutant/" + displayMutantIndex, true);
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            // Response
            var response = JSON.parse(this.responseText);
            populationSize = response.population_size;
            buildIndividualUI(response);
        }
    };
    xhttp.send();
}

function changeSelectedMutant(n){
    displayMutantIndex+=n
    if(displayMutantIndex<0) displayMutantIndex=populationSize-1;
    else if(displayMutantIndex>=populationSize-1) displayMutantIndex=0;
    loadMutant();
}

function buildIndividualUI(response){
    individualsContainer = document.getElementById("individuals_container");
    individualsContainer.innerHTML = "";

    let h2 = document.createElement("h2");
    h2.innerHTML = `Individual ${displayMutantIndex+1} / ${response.population_size}`;
    individualsContainer.appendChild(h2);

    let button = document.createElement("button");
    button.innerHTML = "Show previous mutant";
    button.onclick = function(){changeSelectedMutant(-1)};
    individualsContainer.appendChild(button);
    
    individualsContainer.append(" ");

    button = document.createElement("button");
    button.innerHTML = "Show next mutant";
    button.onclick = function(){changeSelectedMutant(1)};
    individualsContainer.appendChild(button);

    let br = document.createElement("br");
    individualsContainer.append(br);
    br = document.createElement("br");
    individualsContainer.append(br);

    
    var table = document.createElement("table");
    var tr = document.createElement("tr");
    var tdLeft = document.createElement("td");
    tdLeft.classList.add("table_padding_left");
    tdLeft.setAttribute("name", "left");
    tr.appendChild(tdLeft);
    tdRight = document.createElement("td");
    tdRight.setAttribute("name", "right");
    tdRight.classList.add("table_padding_right");
    tr.appendChild(tdRight);
    table.appendChild(tr);
    individualsContainer.append(table);

    // draw didge
    geo = response.geo
    canvas = document.createElement("canvas");
    canvas.setAttribute("height", 300);
    canvas.setAttribute("width", 1000);
    canvas.setAttribute("id", "didge_canvas");
    tdRight.append(canvas);
    paint()

    // draw table of segments
    generateIndividualTable(response.geo);

    // create table to host tuning and loss table
    table = document.createElement("table");
    tr = document.createElement("tr");
    let tdTuning = document.createElement("td");
    tdTuning.setAttribute("name", "tuning_td");
    tdTuning.classList.add("table_padding_left");
    tr.appendChild(tdTuning);
    let tdLoss = document.createElement("td");
    tdLoss.setAttribute("name", "loss_td");
    tdLoss.classList.add("table_padding_right");
    tr.appendChild(tdLoss);
    table.appendChild(tr);
    tdRight.append(table);
    

    displayTuningTable(response.notes);

    displayLossTable(response.loss);

    div = document.createElement("div");
    div.setAttribute("id", "impedance_chart");
    individuals_container.appendChild(div);

    div = document.createElement("div");
    div.setAttribute("id", "groundtone_chart");
    individuals_container.appendChild(div);
    
    div = document.createElement("div");
    div.setAttribute("id", "overblow_chart");
    individuals_container.appendChild(div);

    displayIndividualsChart(
        "Impedance Spektrum", 
        response.spektra.freqs, 
        response.spektra.impedance, 
        "Impedance [MOhm]", 
        "impedance_chart"
    );
    displayIndividualsChart(
        "Ground Tone Spektrum", 
        response.spektra.freqs, 
        response.spektra.ground, 
        "dB", 
        "groundtone_chart"
    );
    displayIndividualsChart(
        "1st Overblow Spektrum", 
        response.spektra.freqs, 
        response.spektra.overblow, 
        "dB", 
        "overblow_chart"
    );
}
function generateIndividualTable(geo) {
    table = document.createElement("table");
    table.classList.add("table_margins");
    headings = ["i", "x", "y"];
    tr = document.createElement("tr");
    tr.classList.add("odd");
    for (var i = 0; i < headings.length; i++) {
        th = document.createElement("th");
        th.innerHTML = headings[i];
        tr.appendChild(th);
    }
    table.appendChild(tr);

    for (var i = 0; i < geo.length; i++) {
        var tr = document.createElement("tr");
        tr.classList.add(i % 2 == 0 ? "even" : "odd");
        var td = document.createElement("td");
        td.innerHTML = i+1;
        tr.appendChild(td);
        td = document.createElement("td");
        td.innerHTML = Math.round(geo[i][0]);
        tr.appendChild(td);
        td = document.createElement("td");
        td.innerHTML = Math.round(geo[i][1]);
        tr.appendChild(td);
        table.appendChild(tr);
    }
    table.appendChild(tr);
    container = document.querySelector("#individuals_container td[name=left]");
    container.appendChild(table);
}

// positions of all points that can be dragged
var dragPoints = []

// the size of the drag points
var onDragRadius = 7;

// the point that is currently being dragged
var activeDragPoint = null;

// keep track of which kind of drag is currently happening
const DRAGSTATE_NONE = 0;
const DRAGSTATE_CAN_DRAG = 1;
const DRAGSTATE_IS_DRAGGING = 2;
var dragState = DRAGSTATE_NONE;

// the factor by which the didgeridoo is scaled on the canvas
var scalingFactor = 1;

// update user interface. call this whenever the didgeridoo geometry changes.
function reset_ui() {
    paint();
    fillGeoTable();
    const transformed_geo_oben = coords["oben"];
    const transformed_geo_unten = coords["unten"];
}

// compute didgeridoo coordinates on the canvas
function computeDidgeCoordinates() {
    var canvas = document.getElementById("didge_canvas");

    scalingFactor = (canvas.offsetWidth - 50) / geo[geo.length - 1][0]

    transformed_geo_oben = [];
    transformed_geo_unten = [];

    var center_y = canvas.offsetHeight / 2;
    for (var i_offset = 0; i_offset < 2; i_offset++) {
        x = geo[0][0] * scalingFactor;
        y = geo[0][1] / 2 * scalingFactor;

        if (i_offset == 0) {
            y = center_y + y;
            transformed_geo_unten.push([x, y]);
        } else {
            y = center_y - y;
            transformed_geo_oben.push([x, y]);
        }

        for (var i = 1; i < geo.length; i++) {
            x = geo[i][0] * scalingFactor;
            y = 0.5 * (geo[i][1]) * scalingFactor;
            if (i_offset == 0) {
                y = center_y + y;
                transformed_geo_unten.push([x, y]);
            } else {
                y = center_y - y;
                transformed_geo_oben.push([x, y]);
            }
        }
    }

    return {
        oben: transformed_geo_oben,
        unten: transformed_geo_unten
    }
}

// draw the didgeridoo, drag points and select box
function paint() {

    // compute canvas height
    maxY = 0;
    for (var i = 0; i < geo.length; i++) {
        if (geo[i][1] > maxY) maxY = geo[i][1];
    }
    document.getElementById("didge_canvas").setAttribute("height", maxY + 50);

    // draw didge
    const coords = computeDidgeCoordinates(geo);
    const transformed_geo_oben = coords["oben"];
    const transformed_geo_unten = coords["unten"];

    var canvas = document.getElementById("didge_canvas");

    // set line stroke and line width
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 3;
    ctx.beginPath();

    // draw outer shape line
    for (var i = 0; i < 2; i++) {
        var tg = null;
        if (i == 0)
            tg = transformed_geo_oben;
        else
            tg = transformed_geo_unten;
        ctx.moveTo(tg[0][0], tg[0][1]);
        for (var j = 1; j < geo.length; j++) {
            ctx.lineTo(tg[j][0], tg[j][1]);
            ctx.stroke();
        }
    }

    ctx.lineWidth = 1;
    for (var j = 0; j < geo.length; j++) {
        p = transformed_geo_oben[j];
        ctx.moveTo(transformed_geo_oben[j][0], transformed_geo_oben[j][1]);
        ctx.lineTo(transformed_geo_unten[j][0], transformed_geo_unten[j][1]);
        ctx.stroke();
    }
}
// return the mouse position relative to the canvas
function getMousePositionOnCanvas(event) {
    var rect = document.getElementById("didge_canvas").getBoundingClientRect();
    return {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    }
}

function download_geo() {
    data = {
        "geo": geo
    }
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "didgemate_geometry .json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}

function displayTuningTable(data) {
    container = document.querySelector("#individuals_container td[name=tuning_td]");

    h3 = document.createElement("h3");
    h3.innerHTML = "Impedance Peaks";
    container.append(h3);

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

    container.appendChild(table);
}

function displayLossTable(data){
    container = document.querySelector("#individuals_container  td[name=loss_td]");

    h3 = document.createElement("h3");
    h3.innerHTML = "Loss Peaks";
    container.append(h3);

    table = document.createElement("table");
    table.classList.add("table_margins");
    tr = document.createElement("tr");
    tr.classList.add("odd");
    table.appendChild(tr);

    headings = ["Metric", "Loss"];
    for (var i = 0; i < headings.length; i++) {
        th = document.createElement("th");
        th.innerHTML = headings[i];
        tr.appendChild(th);
    }
    i=0;
    for (const [key, value] of Object.entries(data)) {
        tr = document.createElement("tr")
        tr.classList.add(i % 2 == 0 ? "even" : "odd");
        table.appendChild(tr);

        row = [
            key,
            Math.round(value),
        ]
        for (var j = 0; j < row.length; j++) {
            td = document.createElement("td");
            td.innerHTML = row[j];
            tr.appendChild(td);
        }
        i+=1;
    }

    container.appendChild(table);
}
function displayIndividualsChart(heading, xData, yData, yAxisLabel, divId) {
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
