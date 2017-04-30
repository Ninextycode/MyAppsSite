/**
 * Created by maxim on 4/18/2017.
 */
var extentions = {};
extentions["plaincrypto"] = [];
extentions["loslessstega"] = ["png", "bmp"];
extentions["jpegstega"] = ["jpeg", "jpg"];

$(document).ready(function(){
    $("#actionSelector").change(function(){
        selected = $(this).find(":selected").val();
        containerField = $("#containerField");
        if (selected === "plaincrypto") {
            containerField.slideUp("fast");
        } else {
            containerField.slideDown("fast");
        }
        joinedextentions =  "." +extentions[selected].join(",.");
        $("#containerFile").attr("accept", joinedextentions);
        resetfiles();
    });
});