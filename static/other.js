
function toggleSettingsField(evt) {
    var editId = this.id;

    if (editId == 'edit-address') {
        if ($('#address1').hasClass("temp-hidden")) {
            $('#address1').val($('#current-address1').text());
            $('#address2').val($('#current-address2').text());
            $('#city').val($('#current-city').text());
            $('#state').val($('#current-state').text());
            $('#zipcode').val($('#current-zipcode').text());

            $('.address-field').removeClass("temp-hidden");
            $('#button-address').removeClass("temp-hidden");
            $('.current-address').addClass("temp-hidden");

        } else {
            $('.address-field').addClass("temp-hidden");
            $('#button-address').addClass("temp-hidden");
            $('.current-address').removeClass("temp-hidden");
        }
    }
    else {
    var inputFieldId = editId.replace('edit-','#');

    var fieldCurrentValueId = '#current-' + inputFieldId.replace('#','');
    var fieldCurrentValueText = $(fieldCurrentValueId).text();

    var fieldButtonId = '#button-' + inputFieldId.replace('#','');

    console.log(inputFieldId, fieldCurrentValueId, fieldCurrentValueText);

        if ($(inputFieldId).hasClass("temp-hidden")) {
                $(inputFieldId).val(fieldCurrentValueText);
                $(fieldButtonId).removeClass("temp-hidden");
                $(inputFieldId).removeClass("temp-hidden");
                $(fieldCurrentValueId).addClass("temp-hidden");
                if (inputFieldId == '#password'){
                    $('#password-mock').addClass("temp-hidden");
                }
            } else {
                $(inputFieldId).addClass("temp-hidden");
                $(fieldButtonId).addClass("temp-hidden");
                $(fieldCurrentValueId).removeClass("temp-hidden");
                if (inputFieldId == '#password'){
                    $('#password-mock').removeClass("temp-hidden");
                }
            }
    }
}

function saveOneField(evt) {

    var settingName, settingValue, successSpanId, fieldJSON;

    if (this.id == 'button-address'){

        settingValue = $('#address1').val() + '+' +
                            $('#address2').val() + '+' +
                            $('#city').val() + '+' +
                            $('#state').val() + '+' +
                            $('#zipcode').val();
        successSpanId = '#address-success';

        $('#current-address1').text($('#address1').val());
        $('#current-address2').text($('#address2').val());
        $('#current-city').text($('#city').val());
        $('#current-state').text($('#state').val());
        $('#current-zipcode').text($('#zipcode').val());

        $('.address-field').addClass("temp-hidden");
        $('#button-address').addClass("temp-hidden");
        $('.current-address').removeClass("temp-hidden");

        fieldJSON = $.get('/_update-settings', {
        'settingName': 'address',
        'settingValue': settingValue
      });

    showUpdateSuccess(successSpanId);

    } else {

    var fieldButtonId = '#' + this.id;
    var inputFieldId = fieldButtonId.replace('#button-','#');
    successSpanId = fieldButtonId.replace('#button-','#') + '-success';

    settingName = fieldButtonId.replace('#button-','');
    settingValue = $(inputFieldId).val();

    var fieldCurrentValueId = '#current-' + inputFieldId.replace('#','');

    if (inputFieldId == '#password') {
        $(fieldCurrentValueId).text('**********');
    }
    else {
        $(fieldCurrentValueId).text(settingValue);
    }
    $(inputFieldId).addClass("temp-hidden");
    $(fieldButtonId).addClass("temp-hidden");
    $(fieldCurrentValueId).removeClass("temp-hidden");

    fieldJSON = $.get('/_update-settings', {
        'settingName': settingName,
        'settingValue': settingValue
      });

    showUpdateSuccess(successSpanId);

    }


    // console.log(fieldJSON["responseText"]);
    // if (fieldJSON.success == 'yes') {
    
    // }
    // else {
    //     showUpdateFailure(successSpanId);
    // }
}

// function saveOneRadioField(evt) {
//     console.log(this);
//     var fieldButtonId = '#' + this.id;
//     var inputFieldId = fieldButtonId.replace('#button-','#');
//     var successSpanId = fieldButtonId.replace('#button-','#') + '-success';

//     var settingName = fieldButtonId.replace('#button-','');
//     var settingValue = $(inputFieldId).val();

//     var fieldCurrentValueId = '#current-' + inputFieldId.replace('#','');

//     $(fieldCurrentValueId).text(settingValue);
//     $(inputFieldId).addClass("temp-hidden");
//     $(fieldButtonId).addClass("temp-hidden");
//     $(fieldCurrentValueId).removeClass("temp-hidden");

//     var fieldJSON = $.get('/_update-settings', {
//         'settingName': settingName,
//         'settingValue': settingValue
//       });

//     // console.log(fieldJSON["responseText"]);
//     // if (fieldJSON.success == 'yes') {
//     showUpdateSuccess(successSpanId);
//     // }
//     // else {
//     //     showUpdateFailure(successSpanId);
//     // }
// }

function showUpdateSuccess(elementId) {
    $(elementId).html('<button type="button" class="btn btn-info btn-xs">Updated!</button>');
    $(elementId).fadeOut(2000);
    setTimeout(function(){
        console.log(elementId);
        $(elementId).html('');
        $(elementId).css('display', 'inline-block');
    },2000);

}

function showUpdateFailure(elementId) {
    $(elementId).html('<button type="button" class="btn btn-danger btn-xs">Error! Try again</button>');
    $(elementId).fadeOut(2000);
    setTimeout(function(){
        console.log(elementId);
        $(elementId).html('');
        $(elementId).css('display', 'inline-block');
    },2000);

}



$('.click-to-edit').on("click", toggleSettingsField);
$('.click-to-save').on("click", saveOneField);
// $('.click-to-save-radio').on("click", saveOneRadioField);
