$(function() {
    $('.api-call form').each(function() {
        $(this).submit(function() {
            var urlparams = {}
            $(this).siblings('.urlparam').each(function() {
                urlparams[$(this).attr('name')] = $(this).val();
            });
            var resultsPre = $(this).siblings('.api-call-results:first');
            
            var action = $.tmpl($(this).attr('action'), urlparams).text();
            var url = window.location.protocol + '//' + window.location.host + action;
            var method = $(this).attr('method').toUpperCase();

            var oauth_params = {};
            var form_params = OAuth.decodeForm($(this).serialize());
            for (var p = 0; p < form_params.length; p++) {
                oauth_params[form_params[p][0]] = form_params[p][1];
            }
            oauth_params.oauth_version = '1.0';
            oauth_params.oauth_consumer_key = $('#oauth-consumer').val();
            oauth_params.oauth_timestamp = OAuth.timestamp();
            oauth_params.oauth_nonce = OAuth.nonce(8);
            oauth_params.oauth_signature_method = 'HMAC-SHA1';

            var oauth_message = { method: method, action: url, parameters: oauth_params };
            var oauth_user = { consumerSecret: $('#oauth-secret').val() }
            OAuth.SignatureMethod.sign(oauth_message, oauth_user); 
            
            var options = {
                url: url,
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
                headers: {
                    'Authorization': OAuth.getAuthorizationHeader('', oauth_message.parameters),
                },
            };
            if (method == 'POST') {
                options.dataType = 'json';
                options.iframe = true;
                /* Can't send Authorization header with iframe POST. */
                options.data = oauth_message.parameters;
            }
            $(this).ajaxSubmit(options); 
            return false;
        });
    });
});
