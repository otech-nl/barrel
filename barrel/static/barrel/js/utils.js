"use strict";

String.prototype.ucfirst = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

function parse_DMY(text, dflt) {
    if(text) {
        text = text.split('-');
        return new Date(text[1]+'-'+text[0]+'-'+text[2]);
    } else {
        return dflt;
    }
}

Date.prototype.pretty_print = function(full) {
   var yyyy = this.getFullYear().toString();
   var mm = (this.getMonth()+1).toString(); // getMonth() is zero-based
   var dd  = this.getDate().toString();
   var result = yyyy +'-'+ (mm[1]?mm:"0"+mm[0]) +'-'+ (dd[1]?dd:"0"+dd[0]);

   if(full) {
       var h  = this.getHours().toString();
       var m  = this.getMinutes().toString();
       result += ' '+ (h[1]?h:"0"+h[0]) +':'+ (m[1]?m:"0"+m[0]); // padding
    }
    return result;
  };

function handle_period(start_element, end_element) {
    var today = new Date();

    start_element.datetimepicker({
        onShow: function(time, $input) {
            var end_val = end_element.val();
            if(end_val) {
                end_val = parse_DMY(end_val);
                $input.datetimepicker({
                    maxDate: end_val,
                });
            }
        }
    })
    if(!start_element.val()) {
        start_element.datetimepicker({
            value: new Date(today.getFullYear(), today.getMonth(), 1)
        });
    }
    end_element.datetimepicker({
        onShow: function(time, $input) {
            var start_val = start_element.val();
            if(start_val) {
                start_val = parse_DMY(start_val);
                $input.datetimepicker({
                    minDate: start_val
                });
            }
        }
    })
    if(!end_element.val()) {
        end_element.datetimepicker({
            value: new Date(today.getFullYear(), today.getMonth() + 1, 1)
        });
    }
}

$(document).ready(function () {
    var now = new Date();
    var options = {
        format: 'd-m-Y H:i',
        formatDate:'d-m-Y',
        formatTime:'H:i',
        lang: 'nl',
        // mask: true,
        defaultTime: now,
        defaultDate: now,
        dayOfWeekStart: 1,
        weeks: true,
    }
    $('[type=datetime]').attr('type','text').datetimepicker(options);
    // set type=text to disable default chrome datepicker

    $.extend(options, {
        closeOnDateSelect: true,
        format: 'd-m-Y',
        timepicker: false,
    })
    $('[type=date]').attr('type','text').datetimepicker(options);
})
