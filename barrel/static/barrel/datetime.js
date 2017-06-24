function init_date_and_timepicker() {
    // for bootstrap-datepicker and bootstrap-timepicker

    $('input[type=date]').attr('type','text').datepicker({
        format: "yyyy-m-d",
        language: "nl"
    });
    // set type=text to disable default chrome datepicker
    $('input[type=time]').attr('type','text').timepicker({
        showMeridian: false,
        maxHours: 24
    });
};

function init_datetimepicker(user_options) {
    // for jquery-datetimepicker

    var now = new Date();
    var options = {
        format: 'Y-m-d H:i',
        formatDate:'Y-m-d',
        formatTime:'H:i',
        // lang: 'en',
        // mask: true,
        defaultTime: now,
        defaultDate: now,
        dayOfWeekStart: 1,
        weeks: true
    };
    Object.assign(options, user_options);
    $('[type=datetime]').attr('type','text').datetimepicker(options);
    // set type=text to disable default chrome datepicker

    $.extend(options, {
        closeOnDateSelect: true,
        format: 'd-m-Y',
        timepicker: false
    });
    $('[type=date]').attr('type','text').datetimepicker(options);
};
