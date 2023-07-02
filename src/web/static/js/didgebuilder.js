
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
function reset_ui(){
    paint();
    initializeDragPoints();
    fillGeoTable(); 
}

// initialize the drag handles to change didge shape
function initializeDragPoints(){
    dragPoints = [];
    const coords = computeDidgeCoordinates(geo);
    keys = ["oben", "unten"];
    for( var i=0; i<keys.length; i++){
        for( var j=0; j<coords[keys[i]].length; j++){
            if( i==0 ) {
                dragPoints.push({
                    x: coords[keys[i]][j][0],
                    y: coords[keys[i]][j][1],
                    geo_index: j,
                    direction: "vertical_up"
                });
            }
            if( i==0 && j>0){
                y = 0.5*(coords[keys[0]][j][1] + coords[keys[1]][j][1]);
                dragPoints.push({
                    x: coords[keys[i]][j][0],
                    y: y,
                    geo_index: j,
                    direction: "horizontal"
                });
            }
        }
    }

    const transformed_geo_oben = coords["oben"];
    const transformed_geo_unten = coords["unten"];

}

// compute didgeridoo coordinates on the canvas
function computeDidgeCoordinates(){
    var canvas = document.getElementById("didge_canvas");

    scalingFactor = (canvas.offsetWidth-50) / geo[geo.length-1][0]

    transformed_geo_oben = [];
    transformed_geo_unten = [];

    var center_y = canvas.offsetHeight/2;
    for( var i_offset=0; i_offset<2; i_offset++){
        x = geo[0][0] * scalingFactor;
        y = geo[0][1]/2 * scalingFactor;

        if( i_offset == 0){
            y = center_y + y;
            transformed_geo_unten.push([x,y]);
        } else {
            y = center_y - y;
            transformed_geo_oben.push([x,y]);
        }

        for( var i=1; i<geo.length; i++){
            x = geo[i][0] * scalingFactor;
            y = 0.5*(geo[i][1]) * scalingFactor;
            if( i_offset == 0){
                y = center_y + y;
                transformed_geo_unten.push([x,y]);
            } else {
                y = center_y - y;
                transformed_geo_oben.push([x,y]);
            }
        }
    }

    return {
        oben: transformed_geo_oben,
        unten: transformed_geo_unten
    }
}

// draw the didgeridoo, drag points and select box
function paint(){

    // compute canvas height
    maxY = 0;
    for( var i=0; i<geo.length; i++){
        if(geo[i][1]>maxY) maxY=geo[i][1];
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
    for( var i=0; i<2; i++){
        var tg = null;
        if( i==0)
            tg = transformed_geo_oben;
        else
            tg = transformed_geo_unten;
        ctx.moveTo(tg[0][0], tg[0][1]);
        for( var j=1; j<geo.length; j++){
            ctx.lineTo(tg[j][0], tg[j][1]);
            ctx.stroke();
        }
    }

    ctx.lineWidth = 1;
    for( var j=0; j<geo.length; j++){
        p = transformed_geo_oben[j];
        ctx.moveTo(transformed_geo_oben[j][0], transformed_geo_oben[j][1]);
        ctx.lineTo(transformed_geo_unten[j][0], transformed_geo_unten[j][1]);
        ctx.stroke();
    }

    // helper function to draw a single drag point
    function drawDragPoint(i_point, color){
        const p = dragPoints[i_point];
        ctx.beginPath();
        ctx.arc(p.x, p.y, onDragRadius, 0, 2 * Math.PI, false);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.lineWidth = 1;
        ctx.strokeStyle = color;
        ctx.stroke();
    }
    // draw single drag point
    if( activeDragPoint != null){
        drawDragPoint(activeDragPoint, '#000000');
    }

}

function load_didge(){
    geo = [[0,32], [800,32], [900,38], [970,42], [1050, 40], [1180, 48], [1350, 60], [1390, 68], [1500, 72]]
    reset_ui();
}

// return the mouse position relative to the canvas
function getMousePositionOnCanvas(event){
    var rect = document.getElementById("didge_canvas").getBoundingClientRect();
    return {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    }
}

function getNearbyDragPoints(event){
    // compute distances of mouse to all drag poings
    var rect = document.getElementById("didge_canvas").getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;
    matches = [];
    for( var i=0; i<dragPoints.length; i++){
        const dragX = dragPoints[i].x;
        const dragY = dragPoints[i].y;
        const dX = dragX-mouseX;
        const dY = dragY-mouseY;
        var dist = Math.sqrt(dX*dX - dY*dY);
        if( dist<onDragRadius ){
            matches.push({
                dragPoint: i,
                dist: dist
            });
        }
    }
    matches.sort(function(x,y){
        return x.dist-y.dist;
    });

    return matches;
}

function dragPoint(iPoint, event){
    // drag a point
    var rect = document.getElementById("didge_canvas").getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    const dp = dragPoints[iPoint];
    if( dp.direction == "horizontal"){
        const dx = -1*(dp.x - mouseX) / scalingFactor;
        const newPos = Math.round(dp.x/scalingFactor + dx)
        if( newPos>0 &&
            (dp.geo_index==0 || newPos>geo[dp.geo_index-1][0] ) &&
            (dp.geo_index==geo.length-1 || newPos<geo[dp.geo_index+1][0] )){
            geo[dp.geo_index][0] = newPos;
        }
    }
    if( dp.direction == "vertical_up"){
        const dy = (dp.y - mouseY) / scalingFactor;
        const geoY = 2*(rect.height/2-dp.y) / scalingFactor;
        const newPos = Math.round(geoY + dy);
        if( newPos>0 && newPos<500 && newPos >-500){
            geo[dp.geo_index][1] = newPos;
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    load_didge();

    const canvas = document.getElementById("didge_canvas")
    // show drag handles
    canvas.addEventListener("mousemove", (event) => {
        if( dragState == DRAGSTATE_NONE ||
            dragState == DRAGSTATE_CAN_DRAG ){

            // mouse is not near a drag point
            activatePointBefore = activeDragPoint;
            matches = getNearbyDragPoints(event);
            if( matches.length == 0 ){
                if( dragState == DRAGSTATE_CAN_DRAG){
                    dragState = DRAGSTATE_NONE;
                    activeDragPoint = null;
                    paint();
                }
            } else {
                // set active drag point
                activeDragPoint = matches[0].dragPoint;
                if( dragState == DRAGSTATE_NONE || dragState == DRAGSTATE_CAN_DRAG){
                    dragState = DRAGSTATE_CAN_DRAG;
                } 
                if( activatePointBefore == activeDragPoint ){
                    paint();
                }
            }
        } else if( dragState == DRAGSTATE_IS_DRAGGING ){
            dragPoint(activeDragPoint, event);
            reset_ui()
        } 
    });
    canvas.addEventListener("mousedown", (event)=>{
        if( dragState == DRAGSTATE_CAN_DRAG ){
            // start to drag a single point
            dragState = DRAGSTATE_IS_DRAGGING;
        }
    });
    canvas.addEventListener("mouseup", (event)=>{
        if( dragState == DRAGSTATE_IS_DRAGGING ){
            dragState = DRAGSTATE_NONE;
            run_simulation_if_open();
        } 
    });
});