$(document).ready(function(){
    $('input[type=date]').attr('type','text').datepicker({
        format: "yyyy-m-d",
        language: "nl"
    });
    // set type=text to disable default chrome datepicker
    $('input[type=time]').attr('type','text').timepicker({
        showMeridian: false,
        maxHours: 24
    });
})
