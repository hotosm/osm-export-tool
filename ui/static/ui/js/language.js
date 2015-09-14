$().ready(function(){
    $('.banner-links > a').on('click', function(e){
        e.preventDefault();
        var lang = $(this).attr('id');
        var $form = $('form#lang');
        var $input = $form.find('input[name="language"]');
        $input.val(lang);
        $form.submit();
    })
});