/*
 * JS code for the frontend of the admin panel
 * 
 */


// API Functions
function deleteItem(item, id) {
    // TODO: Replace confirm() and alert() with a nice-looking Bootstrap modal
    var confirmationMessage = `Are you certain you wish to DELETE object #${id} FOREVER?\n
This action is PERMANANT and CANNOT BE UNDONE!`;
    var secondConfirmationMessage = `FINAL CHANCE-- There's no going back after this!\n
Are you ABSOLUTELY CERTAIN?`;
    if (confirm(confirmationMessage) && confirm(secondConfirmationMessage)) {
        $.ajax({
            url: `table_endpoint/${item}/${id}/*`,
            type: 'DELETE',
            success: function(result) {
                alert("Team deleted.");
                location.reload();
            },
            fail: function(result) {
                alert("Uh... There was an issue...\nIt probably didn't work");
                location.reload();
            }
        });
    } else {
        alert("Action Canceled.");
    }
}
