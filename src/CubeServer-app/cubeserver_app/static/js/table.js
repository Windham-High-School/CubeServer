/*
 * Common DataTable setup JS code
 * 
 */

// Render nice-looking tables with DataTables:
$(document).ready(function () {
    $('.datatable:not(.leaderboardtable):not(.datapoints-table):not(.beacontable)').DataTable({
        buttons: [
            'colvis', 'copy', 'csv', 'pdf', 'print'
        ],
        dom: 'Bfrtilp',
        responsive: true,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        scrollY: true,
        scrollCollapse: true,
        scrollX: true,
        autoWidth: true,
        //fixedColumns:   {
        //    "leftColumns": 1
        //},
        //fixedHeader: true,
        keepConditions: true,
        //stateSave: true
    });

    // Leaderboard:
    $('.leaderboardtable').DataTable({
        order: [[1, 'desc'], [2, 'desc']],
        dom: 'Bfrtilp',
        buttons: [
            'colvis', 'csv', 'print'
        ],
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        colReorder: true,
        responsive: true,
        scrollY: true,
        scrollCollapse: true,
        scrollX: true,
        autoWidth: true,
        //fixedColumns:   {
        //    "leftColumns": 1
        //},
        //fixedHeader: true,
        keepConditions: true//,
        //        stateSave: true
    });

    ajaxUrl = location.href.replace(location.hash, "");
    ajaxUrl += location.search ? "&ajax=true" : "?ajax=true";
    $('.datapoints-table').DataTable({
        dom: 'Bfrtilp',
        order: [[0, 'desc']],
        buttons: [
            'colvis', 'copy', 'csv', 'pdf', 'print'
        ],
        responsive: true,
        lengthMenu: [[5, 10, 25, 50, 100, -1], [5, 10, 25, 50, 100, "All"]],
        scrollY: true,
        scrollCollapse: true,
        scrollX: true,
        autoWidth: true,
        //fixedColumns:   {
        //    "leftColumns": 1
        //},
        //fixedHeader: true,
        keepConditions: true,
        //stateSave: true,
        processing: true,
        serverSide: true,
        ajax: ajaxUrl,
        searching: false,
    });

    $('.beacontable').DataTable({
        buttons: [
            'colvis', 'copy', 'csv', 'pdf', 'print'
        ],
        order: [[0, 'desc']],
        dom: 'Bfrtilp',
        responsive: true,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        scrollY: true,
        scrollCollapse: true,
        scrollX: true,
        autoWidth: true,
        //fixedColumns:   {
        //    "leftColumns": 1
        //},
        //fixedHeader: true,
        keepConditions: true,
        //stateSave: true
    });
});
