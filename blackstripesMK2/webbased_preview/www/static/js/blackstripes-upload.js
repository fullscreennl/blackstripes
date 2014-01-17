var wizardIdMap = {}
wizardIdMap['crops'] = {'title':'Selecteer de beste uitsnede.','nav':""};
wizardIdMap['colors'] = {'title':'Selecteer de mooiste afbeelding.','nav':""};
wizardIdMap['preview'] = {'title':'Hopakee!',
                            'nav':"<br/><a class='btn btn-default btn-lg' href=''>Andere foto proberen.</a> <a class='btn btn-success btn-lg' href=''>Hij is mooi, Bestellen!</a>"};


function loadColoredImages(nexturl){
    $.getJSON( nexturl, function( data ) {
        displayImages(data);
    });
}

function displayImages(data){

    $("#image-options").empty();

    var options = data["options"];
    var endpoint = data["endpoint"];
    var imagepath = data["imagepath"];
    var imtype = data["imtype"];
    var next = data["next"];
    var version = data["version"];
    var id = data["id"];

    var title = wizardIdMap[id]['title'];
    var nav = wizardIdMap[id]['nav'];

    var htmlstr = "<h1>"+title+"</h1>";

    var l = options.length;
    for(var i=0; i<l; i++){
        var imageurl = endpoint+imagepath+options[i]+imtype;
        var nexturl = endpoint+version+next+options[i];
        htmlstr += "<a href='javascript:loadColoredImages(\""+nexturl+"\")'><img class='preview-image' src='"+imageurl+"' /></a>";
    }

    htmlstr += nav;

    console.log(htmlstr);
    $("#image-options").append(htmlstr);

}

$(function () {
    'use strict';
    var url = "/"+VERSION+"/images/upload";
    console.log(url);
    $('#fileupload').fileupload({
        url: url,
        dataType: 'json',

        disableImageResize: /Android(?!.*Chrome)|Opera/
        .test(window.navigator && navigator.userAgent),
        imageMaxWidth: 800,
        imageMaxHeight: 800,
        imageCrop: false,

        done: function (e, data) {
            $(".container").hide();
            displayImages(data.result);
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#progress .progress-bar').css(
                'width',
                progress + '%'
            );
        }

    }).prop('disabled', !$.support.fileInput)
        .parent().addClass($.support.fileInput ? undefined : 'disabled');
});

console.log("VERSION: "+VERSION);