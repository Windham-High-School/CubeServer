/*
 * Common user-interface JS code
 * 
 */

// Toggle Theme:
$("#toggleTheme").click(function () {
    switch (Cookies.get('theme')) {
        case 'light':
            Cookies.set('theme', 'dark', { expires: 1000 });
            break;
        default:
        case undefined:  // TODO: Make this dependent upon the default theme as set by config.py
        case 'dark':
            Cookies.set('theme', 'light', { expires: 1000 });
            break;
    }
    location.reload();
})

// Form select input classing:
$("select").attr("aria-label", ".form-select-sm")
    .addClass("form-select")
    .addClass("form-select-sm");

// Open a new popup window with the specified address:
// TODO: Replace with JQueryUI Dialog?
let win_params = `scrollbars=no,resizable=no,status=no,location=no,toolbar=no,menubar=no,width=600,height=300,left=100,top=100`;
function open_popup(href) {
    window.open(href, "", win_params);
}
