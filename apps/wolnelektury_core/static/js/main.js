$(document).ready(function() {

    function getParameterByName(name) {
        name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
        var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
            results = regex.exec(location.search);
        return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
    }

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

$('.question p:first-child').click(
function(e){      
$(this).siblings().toggle();
    });

    $('a.video-trigger').click(
        function(e) {
            var $link = $(this),
                vid_id = $link.data('youtube-video');

            e.preventDefault();

            if (!vid_id) {
                alert('#TODO');
                return false;
            }

            $link.parent('.screen').html('<iframe width="621" height="388" src="http://www.youtube.com/embed/' + vid_id + '?rel=0&autoplay=1" frameborder="0" allowfullscreen ></iframe>');
        }
    );

    var $contact_form = $('.contactform form');
    if ($contact_form.length) {
        var person = getParameterByName('person'),
            mail = getParameterByName('mail'),
            phone = getParameterByName('phone'),
            $person = $contact_form.find('input[name="person"]'),
            $mail = $contact_form.find('input[name="mail"]'),
            $phone = $contact_form.find('input[name="phone"]');


        if (person && !$person.val()) {
            $person.val(person);
        }
        if (mail && !$mail.val() && phone && !$phone.val()) {
            $mail.val(mail);
	    $phone.val(phone);
        }

        $(document).on('submit', '.contactform form',
            function(e) {
                var $contact_form = $(this);

                e.preventDefault();

                $.ajax(
                    {
                        url: $contact_form.attr('action'),
                        type: $contact_form.attr('method'),
                        data: $contact_form.serialize(),
                        dataType: 'json',
                        success: function(data) {
                            var errors = '',
                                key;

                            $contact_form.find('.errorlist').remove();
                            $contact_form.find('.with-error').removeClass('with-error');

                            if (!data.success) {
                                for (key in data.errors) {
                                    errors = '<ul class="errorlist">';
                                    for (var i = 0; i < data.errors[key].length; i++) {
                                        errors += '<li>' + data.errors[key][i] + '</li>';
                                    }
                                    errors += '</ul>';
                                    $contact_form.find('input[name="' + key + '"]').addClass('with-error').before(errors);
                                    $contact_form.find('textarea[name="' + key + '"]').addClass('with-error').before(errors);
                                }
                            } else {
                                $contact_form.get(0).reset();
                                alert('Wiadomość została wysłana. Dziękujemy.');
                            }
                        },
                        error: function() {
                            alert('Niestety wystąpił błąd. Przeładuj stronę i spróbuj ponownie.');
                        }
                    }
                );
            }
        );
    }

    var $comment_form = $('.commentform form');
    if ($comment_form.length) {
        $(document).on('submit', '.commentform form',
            function(e) {
                var $comment_form = $(this);

                e.preventDefault();

                $.ajax(
                    {
                        url: $comment_form.attr('action'),
                        type: $comment_form.attr('method'),
                        data: $comment_form.serialize(),
                        dataType: 'html',
                        success: function(data) {
                            if (data.indexOf('<p class="success">') == 0) {
                                $comment_form.get(0).reset();
                                document.location.reload();
                            }
                            $comment_form.replaceWith(data);
                        },
                        error: function() {
                            alert('Niestety wystąpił błąd. Przeładuj stronę i spróbuj ponownie.');
                        }
                    }
                );
            }
        );
    }

});
