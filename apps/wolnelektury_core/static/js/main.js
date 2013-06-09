$(document).ready(function() {

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    $('.shelf-actions a.ajaxable').click(
        function(e) {
            var $link = $(this);
            e.preventDefault();
            $.ajax(
                {
                    url: $link.attr('href'),
                    type: 'POST',
                    dataType: 'json',
                    success: function(data) {
                        if (data.success) {
                            if (data.like) {
                                $link.parent('.shelf-actions').removeClass('not-on-shelf').addClass('on-shelf');
                            } else {
                                $link.parent('.shelf-actions').addClass('not-on-shelf').removeClass('on-shelf');
                            }
                        }
                    }
                }
            );
        }
    );

    $('a.video-trigger').click(
        function(e) {
            var $link = $(this),
                vid_id = $link.data('youtube-video');

            e.preventDefault();

            if (!vid_id) {
                alert('#TODO');
                return false;
            }

            $link.parent('.screen').html('<iframe width="621" height="388" src="http://www.youtube.com/embed/' + vid_id + '?rel=0" frameborder="0" allowfullscreen ></iframe>');
        }
    );

});