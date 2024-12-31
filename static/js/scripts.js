const openNewWindow = (editorUrl) => {
    const params = `scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no,width=700,height=500,top=200,left=400`;
    newWindow = window.open(editorUrl, 'sub', params);
};

function get_info(person_id){
    var data
    trig = true
    $.getJSON('/get_info?id='+person_id, function(data) {
        $('#result').text(data);
        for(k in data){
            trig = false;
            elem = document.getElementById(k);
            if (elem){
                elem.value = data[k];
            }
        }
        if (trig){
            if (confirm("לא נמצא במערכת\nלהוסיף חדש?")) {
                document.getElementById('add_new').value = 'true';
            } else {
              document.getElementById('add_new').value = 'false';
            }
        }
    });
}
function scroll_to_row(text){
    var rows = document.querySelectorAll('#inv_tb th');
    for (r in rows){
        if (rows[r].innerHTML.indexOf(text) != -1){
            rows[r].scrollIntoView({behavior: 'smooth',block: 'center'});
            break;
        }
    }
}

var r_index = 2;
function add_row(){
    r_index += 1;
    document.getElementById('row'+r_index.toString()).style.display = 'table-row';
}

function add_required(elem_id, cur_val){
    element = document.getElementById(elem_id)
    if (element){
        if (items.hasOwnProperty(cur_val)){
            element.required = true;
            element.setAttribute('max', items[cur_val])
            element.setAttribute('min', 1)

        }
        else{
            console.log(!cur_val);
            window.alert('פריט לא נמצא במלאי')
        }
    }
}

function close(){
    if(window.opener!==null){
        window.close();
    }
    else{
        window.location.replace("/");
    }
}

function  gas_qnty(){
    start_s = document.getElementById('serial_s').value;
    end_s = document.getElementById('serial_e').value;
    length = end_s.length;
    if (start_s && end_s){
        if (start_s.length < end_s.length){length = start_s.length}
        qnt = parseInt(end_s.substring(0,length)) - parseInt(start_s.substring(0,length)) + 1;
        document.getElementById('quantity').value = qnt;
    }
}

function sign_doc(){
    if (confirm("מאשר שעברתי על רשימת הציוד שהתקבל")) {
        document.getElementById('main_form').submit();
    }
}