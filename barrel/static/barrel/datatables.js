"use strict";

function form_modal_open(element, id) {
    $('div.modal-body').load("/"+element+"/"+id);
    $('#'+element+'Modal').modal('show');
}

function init_datatable(column_names, table_options, user_options) {
    var columnDefs = false;
    if(user_options && ('columnDefs' in user_options)) {
        columnDefs = user_options.columnDefs;
        delete user_options.columnDefs;
    }
    var options = {
        // map column names
        columns: column_names.map(function(el) {
            return {data: el};
        }),
        // hide id column
        columnDefs: [{
            targets: [0],
            visible: false
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
    _.extend(options, table_options);
    _.extend(options, user_options);
    if(columnDefs) {
        options.columnDefs = options.columnDefs.concat(columnDefs);
    }

    return options;
}

function create_datatable(table_id, element, column_names, table_options, user_options, register_click) {
    var options = init_datatable(column_names, table_options, user_options);
    var table = $('table#'+table_id).DataTable(options);

    if(register_click) {
        table.on('click', 'tbody td', function() {
            var data = table.row(this.parentElement).data();
            window.location = "/"+element+"/"+data.id;
        });
    }

    return table;
}

function json_datatable(table_id, element, column_names, user_options) {
    return create_datatable(table_id, element, column_names, {
        serverSide: true,
        processing: true,
        ajax: {
            url: '/api/'+element
        }
    }, user_options, true);
}

function basic_datatable(table_id, element, column_names, user_options, disable_click) {
    return create_datatable(table_id, element, column_names, {
        searching: false,
        paging: false,
        lengthChange: false,
        info: false,
        sorting: []
    }, user_options, !disable_click);
}
