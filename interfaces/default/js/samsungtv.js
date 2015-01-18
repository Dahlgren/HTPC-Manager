$(document).ready(function() {
    var tvs = $('#tvs').change(function() {
    $.get(WEBDIR + 'samsungtv/changeserver?id='+$(this).val(), function(data) {
            notify('kodi','TV changed '+ data, 'info');
        });
    });

    $.get(WEBDIR + 'samsungtv/gettvs', function(data) {
        if (data==null) return;
        $.each(data.tvs, function(i, item) {
        	console.log(item)
            tv = $('<option>').text(item.name).val(item.id);
            if (item.name == data.current) tv.attr('selected','selected');
            tvs.append(tv);
        });
    }, 'json');
 });

    $('[data-player-control]').click(function () {
        var action = $(this).attr('data-player-control');
        $.get(WEBDIR + 'samsungtv/sendkey?action='+action);
    });

    $(document).on('click', '.send', function() {
        var action = $('#msg').val();
        $.get(WEBDIR + 'samsungtv/sendkey?action='+action);
    });