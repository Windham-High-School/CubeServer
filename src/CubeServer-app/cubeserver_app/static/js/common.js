/*
 * Common user-interface JS code
 * 
 */

// Default popup window params:
let win_params = `scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no,width=600,height=300,left=100,top=100`;

// Toggle Theme:
$("#toggleTheme").click(function() {
    switch(Cookies.get('theme')) {
        case 'vapor':
            Cookies.set('theme', 'morph', { expires: 1000 });
            break;
        case 'quartz':
            Cookies.set('theme', 'vapor', { expires: 1000 });
            break;
        default:
        case undefined:  // TODO: Make this dependent upon the default theme as set by config.py
        case 'morph':
            Cookies.set('theme', 'quartz', { expires: 1000 });
    }
    location.reload();
})

// Form select input classing:
$("select").attr("aria-label", ".form-select-sm")
    .addClass("form-select")
    .addClass("form-select-sm");

// Open a new popup window with the specified address:
// TODO: Replace with JQueryUI Dialog?
function open_popup(href) {
    window.open(href, "", win_params);
}
