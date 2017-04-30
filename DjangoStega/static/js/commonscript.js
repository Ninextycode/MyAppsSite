/**
 * Created by maxim on 4/18/2017.
 */

function resetfiles() {
    $("#containerFile").val(null);
    $("#keyFile").val(null);
    $("#secretFile").val(null);
}

$(document).ready(function(){
    $("#containerFile").change(function(){
        allowedExtentions = extentions[$("#actionSelector").find(":selected").val()];
        ext = $(this).val().split('.').pop();
        for(i in allowedExtentions) {
            if(ext === allowedExtentions[i] || allowedExtentions[i] === "*"){
                return;
            }
        }
        $(this).val(null);
        alert("Invalid file type");
    });

    $("#actionSelector").val("loslessstega");
    $("#actionSelector").trigger( "change" );
});