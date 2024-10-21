const openNewWindow = (editorUrl) => {
    const params = `scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no,width=700,height=500,top=200,left=400`;
    newWindow = window.open(editorUrl, 'sub', params);
};

function get_info(person_id){

}

var r_index = 2;
function add_row(){
    r_index += 1;
    document.getElementById('row'+r_index.toString()).style.display = 'table-row';
}