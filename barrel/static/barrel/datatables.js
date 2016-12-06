"use strict";

function form_modal_open(element, id) {
    $('div.modal-body').load("/"+element+"/"+id);
    $('#'+element+'Modal').modal('show');
}

function init_datatables(element, column_names, user_options) {
    var options = {
        columns: column_names.map(function(el) {
            return {data: el};
        }),
        columnDefs: [{
            targets: [0],
            visible: false,
        }],
        language: {
            emptyTable: "Tabel is leeg",
            info: "_START_ tot _END_ van _TOTAL_ resultaten",
            infoEmpty: "Niets gevonden",
            infoFiltered: " (gefilterd uit _MAX_ resultaten)",
            infoPostFix: "",
            thousands: ".",
            lengthMenu: "_MENU_ resultaten weergeven",
            loadingRecords: "Een moment geduld aub - bezig met laden...",
            processing: "Bezig...",
            search: "Zoeken:",
            zeroRecords: "Geen resultaten gevonden",
            paginate: {
                first: "Eerste",
                last: "Laatste",
                next: "Volgende",
                previous: "Vorige"
            },
            aria: {
                sortAscending:  ": sorteer oplopend",
                sortDescending: ": sorteer aflopend"
            }
        }
    };
    Object.assign(options, user_options)
    var table = $('table#'+element).DataTable(options);

    table.on('click', 'tbody td', function() {
        var data = table.row(this).data();
        window.location = "/"+element+"/"+data.id;
        // form_modal_open(element, data.id);
    })

    return table;
}
    
function json_datatables(element, column_names) {
    var options = {
        serverSide: true,
        processing: true,
        ajax: {
            url: '/api/'+element,
        }
    }
    return init_datatables(element, column_names, options);
}

function basic_datatables(element, column_names) {
    var options ={'searching': false, 'paging': false, 'lengthChange': false, 'info': false};
    return init_datatables(element, column_names, options);
}

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
