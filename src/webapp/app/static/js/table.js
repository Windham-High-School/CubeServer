/*
 * Common DataTable setup JS code
 * 
 */

// Render nice-looking tables with DataTables:
$(document).ready( function () {
    $('.datatable').DataTable( {
        colReorder: {
            enable: false
        },
        lengthMenu: [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "All"] ],
        scrollY: true,
        scrollCollapse: true,
        scrollX: true,
        autoWidth : true,
        fixedColumns:   {
            "leftColumns": 1
        }
    } );
});