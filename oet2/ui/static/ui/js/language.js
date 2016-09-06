$().ready(function(){
    $('.banner-links > a').on('click', function(e){
        e.preventDefault();
        var lang = $(this).attr('id');
        var $form = $('form#lang');
        var $input = $form.find('input[name="language"]');
        var $next = $form.find('input[name="next"]');
        $input.val(lang);
        $next.val('/' + window.location.pathname.substring(4));
        $form.submit();
    })
});