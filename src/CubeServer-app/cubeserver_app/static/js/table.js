/*
 * Common DataTable setup JS code
 * 
 */

// Render nice-looking tables with DataTables:
$(document).ready( function () {
    $('.datatable:not(.leaderboardtable):not(.datapoints-table)').DataTable( {
        buttons: [
            'colvis', 'copy', 'csv', 'pdf', 'print'
        ],
        dom: 'Bfrtilp',
        responsive: true,
        lengthMenu: [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "All"] ],
        scrollY: true,
        scrollCollapse: true,
        scrollX: true,
        autoWidth : true,
        //fixedColumns:   {
        //    "leftColumns": 1
        //},
        //fixedHeader: true,
        keepConditions: true,
        stateSave: true
    } );

    $('.leaderboardtable').DataTable( {
        order: [[3, 'desc'], [4, 'asc']],
        dom: 'Bfrtilp',
        buttons: [
            'colvis', 'copy', 'csv', 'pdf', 'print'
        ],
        lengthMenu: [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "All"] ],
        colReorder: true,
        responsive: true,
        scrollY: true,
        scrollCollapse: true,
        scrollX: true,
        autoWidth : true,
        //fixedColumns:   {
        //    "leftColumns": 1
        //},
        //fixedHeader: true,
        keepConditions: true,
        stateSave: true
    } );

    $('.datapoints-table').DataTable( {
        dom: 'Bfrtilp',
        order: [[0, 'desc']],
        buttons: [
            'colvis', 'copy', 'csv', 'pdf', 'print'
        ],
        responsive: true,
        lengthMenu: [ [5, 10, 25, 50, 100, -1], [5, 10, 25, 50, 100, "All"] ],
        scrollY: true,
        scrollCollapse: true,
        scrollX: true,
        autoWidth : true,
        //fixedColumns:   {
        //    "leftColumns": 1
        //},
        //fixedHeader: true,
        keepConditions: true,
        stateSave: true
    } );

});
