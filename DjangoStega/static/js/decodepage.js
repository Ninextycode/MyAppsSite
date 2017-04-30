var extentions = {};
extentions["plaincrypto"] = ["*"];
extentions["loslessstega"] = ["png", "bmp"];
extentions["jpegstega"] = ["jpeg", "jpg"];

$(document).ready(function(){
    $("#actionSelector").change(function(){
        selected = $(this).find(":selected").val();
        joinedextentions =  "." +extentions[selected].join(",.");
        $("#containerFile").attr("accept", joinedextentions);
        resetfiles();
    });
});