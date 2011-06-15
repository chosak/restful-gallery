$(function() {
    $('.api-call form').each(function() {
        $(this).submit(function() {
            var urlparams = {}
            $(this).siblings('.urlparam').each(function() {
                urlparams[$(this).attr('name')] = $(this).val();
            });
            var resultsPre = $(this).siblings('.api-call-results:first');
            var options = {
                url: $.tmpl($(this).attr('action'), urlparams).text(),
                complete: function(xhr) {
                    var results = xhr.status + ' ' + xhr.statusText + '\n' + xhr.responseText; 
                    var prettyResults = results;
                    var regex = /url": "([\w\-\\\/\.]+)"/g;
                    link = regex.exec(results);
                    while (link != null) {
                        var url = link[1];
                        prettyResults = prettyResults.replace(url, '<a href="' + url.replace(/\\\//g, '/') + '" target="_blank">' + url + '</a>');
                        link = regex.exec(results);
                    }
                    resultsPre.html(prettyResults);
                },
            };
            if ($(this).attr('method').toUpperCase() == 'POST') {
                options.dataType = 'json';
                options.iframe = true;
            }
            $(this).ajaxSubmit(options); 
            return false;
        });
    });
});
