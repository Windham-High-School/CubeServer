/*
 * Common user-interface JS code
 * 
 */

// Toggle Theme:
$("#toggleTheme").click(function() {
    switch(Cookies.get('theme')) {
        case 'vapor':
            Cookies.set('theme', 'morph', { expires: 1000 });
            break;
        case 'morph':
            Cookies.set('theme', 'quartz', { expires: 1000 });
            break;
        default:
        case undefined:
        case 'quartz':
            Cookies.set('theme', 'vapor', { expires: 1000 });
    }
    location.reload();
})