/*
 * JS code for the frontend of the admin panel
 * 
 */


// TODO: Rewrite to have less repeated code:

// For restoring scroll position after changes:
document.addEventListener("DOMContentLoaded", function(event) { 
    var scrollpos = localStorage.getItem('scrollpos');
    if (scrollpos) window.scrollTo(0, scrollpos);
    localStorage.removeItem('scrollpos');
});

// API Functions
function deleteItem(item, id) {
    // TODO: Replace confirm() and alert() with a nice-looking Bootstrap modal
    var confirmationMessage = `Are you certain you wish to DELETE object #${id} FOREVER?\n
This action is PERMANANT and CANNOT BE UNDONE!`;
//var comment = prompt("Please comment on this change.");  // TODO: Add comment in case of deleted objects also
    var secondConfirmationMessage = `FINAL CHANCE-- There's no going back after this!\n
Are you ABSOLUTELY CERTAIN?`;
    if (confirm(confirmationMessage) && confirm(secondConfirmationMessage)) {
        $.ajax({  // TODO: Generate these URLs better so stuff is less likely to break:
            url: `/admin/table_endpoint/${item}/${id}/*`,
            type: 'DELETE',
            success: function(result) {
                alert("Object deleted.");
                localStorage.setItem('scrollpos', window.scrollY);
                location.reload();
            },
            fail: function(result) {
                alert("Uh... There was an issue...\nIt probably didn't work");
                localStorage.setItem('scrollpos', window.scrollY);
                location.reload();
            }
        });
    } else {
        alert("Action Canceled.");
    }
}

function recompute_score(item, id) {
    // TODO: Replace confirm() and alert() with a nice-looking Bootstrap modal
    var confirmationMessage = `Are you certain you wish to RECOMPUTE object #${id}'s score?\n
All/the datapoint(s) will be re-evaluated under the current scoring rules and multiplier.\n
All manual score increments on this object will be lost.\n
This action is PERMANANT and CANNOT BE UNDONE!`
//var comment = prompt("Please comment on this change.");  // TODO: Add comment in case of deleted objects also
    var secondConfirmationMessage = `FINAL CHANCE-- There's no going back after this!\n
Are you ABSOLUTELY CERTAIN?`;
    if (confirm(confirmationMessage) && confirm(secondConfirmationMessage)) {
        $.ajax({  // TODO: Generate these URLs better so stuff is less likely to break:
            url: `/admin/table_endpoint/${item}/${id}/score_recomputation`,
            type: 'POST',
            success: function(result) {
                alert("Score recomputed.");
                localStorage.setItem('scrollpos', window.scrollY);
                location.reload();
            },
            fail: function(result) {
                alert("Uh... There was an issue...\nIt probably didn't work...\n:/");
                localStorage.setItem('scrollpos', window.scrollY);
                location.reload();
            }
        });
    } else {
        alert("Action Canceled.");
    }
}

function adjustScore(item, id) {
    // TODO: Replace confirm() and alert() with a nice-looking Bootstrap modal
    var promptMessage = "Enter the value to offset this score by.\n(A negative number indicates a penalty)\n";
    var amt = prompt(promptMessage, "0");
    var comment = prompt("Please comment on this change.");
    if (isNaN(amt) || isNaN(parseFloat(amt))) {
        alert("You did not enter a number.\nCanceling.");
        return;
    }
    $.ajax({  // TODO: Generate these URLs better so stuff is less likely to break:
        url: `/admin/table_endpoint/${item}/${id}/score_increment`,
        type: 'POST',
        data: {'item': amt, 'comment': comment},
        success: function(result) {
            alert("Done.");
            localStorage.setItem('scrollpos', window.scrollY);
            location.reload();
        },
        fail: function(result) {
            alert("Uh... There was an issue...\nIt probably didn't work");
            localStorage.setItem('scrollpos', window.scrollY);
            location.reload();
        }
    });
}

function verify(item, id) {
    var comment = prompt("Please comment (will be sent to the user)");
    $.ajax({  // TODO: Generate these URLs better so stuff is less likely to break:
        url: `/admin/table_endpoint/${item}/${id}/verified`,
        type: 'POST',
        data: {'item': "True", 'comment': comment},
        success: function(result) {
            alert("Done.");
            localStorage.setItem('scrollpos', window.scrollY);
            location.reload();
        },
        fail: function(result) {
            alert("Uh... There was an issue...\nIt probably didn't work");
            localStorage.setItem('scrollpos', window.scrollY);
            location.reload();
        }
    });
}

// Adds a datapoint of the specified class to the team with the given id:
function add_datapoint(id, dataClass, isBoolean) {
    var promptMessageNonBoolean = "Enter the value of this datapoint:";
    var promptMessageBoolean    = "Is this datapoint True?"
    var value;
    if(isBoolean) value = confirm(promptMessageBoolean);
    else value = prompt(promptMessageNonBoolean);
    $.ajax({  // TODO: Generate these URLs better so stuff is less likely to break:
        url: `manually_score/${id}/${dataClass}`,
        type: 'POST',
        data: {'item': value},
        success: function(result) {
            alert("Done.");
            localStorage.setItem('scrollpos', window.scrollY);
            location.reload();
        },
        fail: function(result) {
            alert("Uh... There was an issue...\nIt probably didn't work");
            localStorage.setItem('scrollpos', window.scrollY);
            location.reload();
        }
    });
}
