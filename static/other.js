
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
            $(fieldCurrentValueId).attr("hidden", "true");
        } else {
            $(inputFieldId).addClass("temp-hidden");
            $(fieldButtonId).addClass("temp-hidden");
            $(fieldCurrentValueId).removeAttr("hidden");
        }
}





$('.click-to-edit').on("click", toggleSettingsField);