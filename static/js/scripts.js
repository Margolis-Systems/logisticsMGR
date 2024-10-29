const openNewWindow = (editorUrl) => {
    const params = `scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no,width=700,height=500,top=200,left=400`;
    newWindow = window.open(editorUrl, 'sub', params);
};

function get_info(person_id){
    var data
    $.getJSON('/get_info?id='+person_id, function(data) {
        $('#result').text(data);
        for(k in data){
            console.log(k, data[k])
            elem = document.getElementById(k);
            if (elem){
                elem.value = data[k];
            }
        }
    });
}

var r_index = 2;
function add_row(){
    r_index += 1;
    document.getElementById('row'+r_index.toString()).style.display = 'table-row';
}

function add_required(elem_id, cur_val){
    console.log(cur_val)
    element = document.getElementById(elem_id)
    if (element){
        if (cur_val){
            element.required = true;
        }
        else{
            element.required = false;
        }
    }
}