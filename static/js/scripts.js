const openNewWindow = (editorUrl) => {
    const params = `scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no,width=700,height=500,top=200,left=400`;
    newWindow = window.open(editorUrl, 'sub', params);
};

function get_info(person_id,docs=''){
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
        if (data.hasOwnProperty(docs)){
            console.log(data.docs)
        }
        if (trig){
            an = document.getElementById('add_new');
            if (an){
                if (confirm("לא נמצא במערכת\nלהוסיף חדש?")) {
                    an.value = 'true';
                }
                else {
                  an.value = 'false';
                }
            }
        }
        else{
            sn = document.getElementById('search_name');
            if (sn){
                sn.value = data.name + ' ' + data.last_name;
            }
            elems = document.getElementsByClassName('need_id');
            for (let e = 0; e < elems.length; e++){
            console.log(elems[e])
               elems[e].style.display = 'table-row';
            }
        }
    });
}

var search = '';
var idx = -1;
function scroll_to_row(text){
    var rows = document.querySelectorAll('#main_tb th');
    for (let r = 0; r < rows.length; r++){
        if (rows[r].innerHTML.indexOf(text) != -1 && r != idx){
            rows[r].scrollIntoView({behavior: 'smooth',block: 'center'});
            idx = r;
            break;
        }
    }
    var rows = document.querySelectorAll('#main_tb td');
    for (let r = 0; r < rows.length; r++){
        if (rows[r].innerHTML.indexOf(text) != -1 && r != idx){
            rows[r].scrollIntoView({behavior: 'smooth',block: 'center'});
            idx = r;
            break;
        }
    }
    search = text;
}

var r_index = 2;
function add_row(){
    r_index += 1;
    document.getElementById('row'+r_index.toString()).style.display = 'table-row';
}

function add_required(elem_id, cur_val){
    element = document.getElementById(elem_id)
    if (element){
        element.required = true;
        if (items){
            if (!items.hasOwnProperty(cur_val)){window.alert('פריט לא נמצא במלאי')}
            //if (items.hasOwnProperty(cur_val)){
            //    element.setAttribute('max', items[cur_val])
            //    element.setAttribute('min', 1)
            //}
            //else{
            //    window.alert('פריט לא נמצא במלאי')
            //}
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

function  _gas_qnty(){
    start_s = document.getElementById('serial_s').value;
    end_s = document.getElementById('serial_e').value;
    length = end_s.length;
    if (start_s && end_s){
        if (start_s.length < end_s.length){length = start_s.length}
        qnt = parseInt(end_s.substring(0,length)) - parseInt(start_s.substring(0,length)) + 1;
        document.getElementById('quantity').value = qnt;
    }
}

function update_gas_max(){
    ctype = document.getElementById('type')
    liters = document.getElementById('liter')
    if (ctype && liters){
        if (ctype.value && liters.value){
            max = 0;
            if (gas_store.hasOwnProperty(ctype.value)){
                max = gas_store[ctype.value][liters.value];
            }
            if (!max){
                    alert('כרטיס לא במלאי')
                    lit = document.getElementById('liter');
                    if(lit){
                        lit = lit.options;
                        for(var i = 0; i < lit.length; i++){
                            lit[i].selected = false;
                        }
                    }
            }
            document.getElementById('quantity').setAttribute('max', max);
        }
    }
}

function sign_doc(){
    if (confirm("מאשר שעברתי על רשימת הציוד שהתקבל")) {
        document.getElementById('main_form').submit();
    }
}

function delete_personal(pid){
    if (confirm("לחיצה על אישור תוביל למחיקת איש הקשר")) {
        window.location.href='/personal?delete=&id='+pid;
    }
}

if (typeof pid !== 'undefined'){
    get_info(pid);
}

function update_id(pid){
    if (pid){
        document.getElementById('id').value = pid;
        get_info(pid);
    }
}

var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}

function copy_to_clipboard(element_id, name) {
  var copyText = document.getElementById(element_id);
  copyText.select();
  copyText.setSelectionRange(0, 99999);
  //document.execCommand('copy')
  navigator.clipboard.writeText(copyText.innerHTML);
  alert("רשימת ציוד של "+name+" הועתקה: ");
}

if (typeof onload_id !== 'undefined'){
    update_id(onload_id)
}
