
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

//     var fieldCurrentValueId = '#current-' +    var fieldButtonId = '#' + this.id;
    // var inputFieldId = fieldButtonId.replace('#button-','#');
    // successSpanId = fieldButtonId.replace('#button-','#') + '-success';

    // settingName = fieldButtonId.replace('#button-','');
    // settingValue = $(inputFieldId).val(); inputFieldId.replace('#','');

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

function uploadPhoto(evt) {
        // var form_data = new FormData('file', $('#photo')[0]);

        var fileInput = document.getElementById("photo");
        console.log(fileInput);
        var file = fileInput.files[0];
        console.log(file);
        var formData = new FormData();
        console.log(formData);
        formData.append('file', file);
        console.log(formData['file']);


        $.ajax({
            type: 'POST',
            url: '/photos',
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
        });
    }

function processChart() {

    $.get('/analytics.json', function (analytics) {

        var month = analytics["month"];
        var week = analytics["week"];
        var day = analytics["day"];
        var filters = analytics["filters"];
        var allFilters = analytics["allfilters"];

        var key, innerKey, weekLabel, weekClickCount, dayLabel, dayClickCount, hourLabel, hourClickCount;

        for (i = 3; i > -1; i--) {
            weekLabel = month["week" + i][0];
            weekClickCount = month["week" + i][1];

            monthChartLabels.push(weekLabel);
            monthChartData.push(weekClickCount);
        }

        for (i = 6; i > -1; i--) {
            dayLabel = week["day" + i][0];
            dayClickCount = week["day" + i][1];

            weekChartLabels.push(dayLabel);
            weekChartData.push(dayClickCount);
        }

        for (i = 11; i > -1; i--) {
            hourLabel = day["hour" + i][0];
            hourClickCount = day["hour" + i][1];

            dayChartLabels.push(hourLabel);
            dayChartData.push(hourClickCount);
        }

        for (key in filters) {
            for (innerKey in key) {
                (window[key + "FiltersArrays"]).push([filters[key], filters[key], filters[key]]);
                console.log(key + " " + innerKey + " " + filters[key] + " " + filters[key][innerKey]);
            }
        }

        for (key in allFilters) {
            for (innerKey in key) {

            }
        }


    });

    setTimeout(function(){ generateLineChart(lineChartElement, dayChartLabels, dayChartData);
                           generatePieChart(filtersPieElement, dayFiltersArrays);
                           generatePieChart(allFiltersPieElement, dayAllFiltersArrays);
                        }, 500);

}

function generateLineChart(element, labelArray, dataArray) {

    var data = {
        labels: labelArray,
        datasets: [{
                label: "My First dataset",
                fillColor: "rgba(220,220,220,0.2)",
                strokeColor: "rgba(220,220,220,1)",
                pointColor: "rgba(220,220,220,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(220,220,220,1)",
                data: dataArray,
            }]
        };

    var ctx = element.getContext("2d");
    var myLineChart = new Chart(ctx).Line(data);
}

function generatePieChart(element, labelDataArrays) {

    var pieColors = { "1": ["#9C9C9C", "#C9C9C9"],
                      "2": ["#EAAB59", "#F2CD9D"],
                      "3": ["#D95757", "#F09999"],
                      "4": ["#A76FE0", "#D2B9EB"],
                      "5": ["#9C9C9C", "#C9C9C9"],
                      "6": ["#9C9C9C", "#C9C9C9"],
                      "7": ["#9C9C9C", "#C9C9C9"],
                      "8": ["#68DD94", "#A8EDC2"],
                      "9": ["#73B7E1", "#A7D6F2"],
                      "volunteers": ["#DBDBDB", "#EBEBEB"],
                      "none": ["#9C9C9C", "#C9C9C9"],

                     };
    var data = [];
    var pieSlice;

    for (i = 0; i < labelDataArrays.length; i++) {
        console.log(String(labelDataArrays[i][0]));
        labelDataArrays[i].push(pieColors[String(labelDataArrays[i][0])]);
        console.log(labelDataArrays);
        pieSlice = {
            value: labelDataArrays[i][2],
            color: labelDataArrays[i][3][0],
            highlight: labelDataArrays[i][3][1],
            label: labelDataArrays[i][1],
                    };
        data.push(pieSlice);
        }

    var ctx = element.getContext("2d");
    var myPieChart = new Chart(ctx).Pie(data, {animateScale: true});
}

function showChart(evt) {

    var buttonId = "#" + this.id;
    var chartId = this.id.replace('show-','');

    $('.show-chart').removeClass('btn-success');
    $(buttonId).addClass('btn-success');

    generateLineChart(lineChartElement, window[chartId + "ChartLabels"], window[chartId + "ChartData"]);
}




$('.click-to-edit').on("click", toggleSettingsField);
$('.click-to-save').on("click", saveOneField);
$('.show-chart').on("click", showChart);
// $('.click-to-save-radio').on("click", saveOneRadioField);
// $('#upload-photo').on("click", uploadPhoto);
