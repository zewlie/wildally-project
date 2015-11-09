
function showSettingsField(evt) {
    var thisField = this.id;
    var inputField = thisField.replace('edit-','');
    inputField = document.getElementById(inputField);
    console.log(inputField);
    $('#email').removeAttr("hidden");
}





$('.click-to-edit').on("click", showSettingsField);