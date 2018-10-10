$(function(){
    $('.captcha').css({
        'cursor': 'pointer'
    });
    $('.captcha').click(function(){
        console.log('click');
        $.getJSON("/captcha/refresh/",
            function (result) {
            $('.captcha').attr('src',result['image_url']);
            $('#id_captcha_0').val(result['key']);
        });});
    // ajax动态验证
    $('#id_captcha1_1').blur(function () {
        json_data={
            'response':$('#id_captcha1_1').val(),
            'hashkey':$('#id_captcha1_0').val()
        }
        $('#captcha_status').remove();
        $.getJSON('/login/ajax_val', json_data, function (data) {
            if (data['status']) {
                $('#id_captcha1_1').after('<span id="captcha_status">验证码正确</span>')
            }else {
                $('#id_captcha1_1').after('<span id="captcha_status">验证码错误</span>')
            };});});
})