$(document).ready(function() {
    $('div.cup').click(function() {
        var id = $(this).attr('id');
        var beans = parseInt($(this).attr('beans'));
        //alert("I hear you");
        update_beans(id, beans);
    });
});

function update_beans(id, beans) {
    beans += 1
    $('#' + id).empty();

    if (beans <= 6) {
        $('#' + id).append("<img src='img/beans/"+beans+".png'>");
    } else {
        $('#' + id).append("<img src='img/beans/lots.png'>");
        $('#' + id).append("<div class='num'>"+beans+"</div>")
    }

    $('#' + id).attr('beans', beans);
};