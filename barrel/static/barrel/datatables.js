"use strict";

function form_modal_open(element, id) {
    $('div.modal-body').load("/"+element+"/"+id);
    $('#'+element+'Modal').modal('show');
}

function init_datatable(element, column_names, user_options) {
    var options = {
        // map column names
        columns: column_names.map(function(el) {
            return {data: el};
        }),
        // hide id column
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

    return options;
}

function create_datatable(element, options, register_click) {
    var table = $('table#'+element).DataTable(options);

    if(register_click) {
        table.on('click', 'tbody td', function() {
            var data = table.row(this).data();
            window.location = "/"+element+"/"+data.id;
        })
    }
    
    return table;
}
    
function json_datatable(element, column_names) {
    var options = init_datatable(element, column_names, {
        serverSide: true,
        processing: true,
        ajax: {
            url: '/api/'+element,
        }
    });
    return create_datatable(element, options, true);
}

function basic_datatable(element, column_names, user_options, disable_click) {
    var options = init_datatable(element, column_names, {
        'searching': false,
        'paging': false,
        'lengthChange': false,
        'info': false
    });
    Object.assign(options, user_options)
    return create_datatable(element, options, !disable_click);
}

