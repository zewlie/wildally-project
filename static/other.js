
function toggleSettingsField(evt) {
    var editId = this.id;
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
        } else {
            $(inputFieldId).addClass("temp-hidden");
            $(fieldButtonId).addClass("temp-hidden");
            $(fieldCurrentValueId).removeClass("temp-hidden");
        }
}

function saveOneField(evt) {
    var fieldButtonId = '#' + this.id;
    var inputFieldId = fieldButtonId.replace('#button-','#');
    var successSpanId = fieldButtonId.replace('#button-','#') + '-success';

    var settingName = fieldButtonId.replace('#button-','');
    var settingValue = $(inputFieldId).val();

    var fieldCurrentValueId = '#current-' + inputFieldId.replace('#','');

    $(fieldCurrentValueId).text(settingValue);
    $(inputFieldId).addClass("temp-hidden");
    $(fieldButtonId).addClass("temp-hidden");
    $(fieldCurrentValueId).removeClass("temp-hidden");

    var fieldJSON = $.get('/_update-settings', {
        'settingName': settingName,
        'settingValue': settingValue
      });

    // console.log(fieldJSON["responseText"]);
    // if (fieldJSON.success == 'yes') {
    showUpdateSuccess(successSpanId);
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
