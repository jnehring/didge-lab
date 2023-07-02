function addSegmentBelow(i){
    new_s = [geo[i][0]+1, geo[i][1]];
    for( var j=i+1; j<geo.length; j++){
        if( geo[j][0] == new_s[0]){
            new_s[0]+=1;
        } else{
            break
        }
    }
    geo.splice(i+1,0,new_s);
    geo.sort(function(x,y){
        return x[0]-y[0];
    });

    reset_ui();
}

function deleteSegment(i){
    if(geo.length==1) return;
    geo.splice(i,1);
    reset_ui()
}

function submitGeoTable(){
    // submit geo table
    new_geo = [];
    for( var i=0; i<geo.length; i++){
        var x=0;
        if(i>0){
            x=document.querySelector("#geo_table input[name=x" +i + "]").value.trim();
        }
        y=document.querySelector("#geo_table input[name=y" +i + "]").value.trim();
        x = parseFloat(x);
        y = parseFloat(y);
        if( isNaN(x) ||isNaN(y)){
            return;
        }
        new_geo.push([x,y]);
    }
    geo=new_geo;
    reset_ui()
}

function fillGeoTable(){
    table = document.getElementById("geo_table");
    table.innerHTML = "<tr>" +
        "<th>pos</th>" +
        "<th>diameter</th>" + 
        "<th>Functions</th>" + 
        "</tr>";
    for( var i=0; i<geo.length; i++){
        x = '<input name="x' + i + '" type="text" size="4" value="' + geo[i][0] + '"/>';
        y = '<input name="y' + i + '" type="text" size="4" value="' + geo[i][1] + '"/>';
        if( i==0 ){
            x = geo[i][0]
        }
        innerHTML = "<tr>"
            + "<td>" + x + "</td>"
            + "<td>" + y + "</td>"
            + "<td>"
            + '<button onclick="addSegmentBelow(' + i + ')">add below</button> ';
        
        if( i>0 ){
            innerHTML += '<button onclick="deleteSegment(' + i + ')">delete</button>' 
        }
        innerHTML += "</td></tr>";
        table.innerHTML += innerHTML;
    }
}

