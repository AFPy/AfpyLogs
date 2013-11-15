jQuery(document).ready(
function(e) {
    $('#logs_navigation dt').each(function () {
        var dt=$(this);
        var dd = dt.next('dd');
        if (!dt.hasClass('active')) {
            dd.hide();
        }
        dt.click(function (e) {
            dd.slideToggle();
            e.preventDefault();
        })
    });
});
