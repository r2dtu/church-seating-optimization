$(document).ready(function() {

  $(':button').on('click', function () {
    $.ajax({
      url: 'upload',
      type: 'POST',
      data: new FormData($('form')[0]),

      // Tell jQuery not to process data or worry about content-type
      cache: false,
      contentType: false,
      processData: false,

      // Custom XMLHttpRequest
      xhr: function () {
        var myXhr = $.ajaxSettings.xhr();
        if (myXhr.upload) {
          // For handling the progress of the upload
          myXhr.upload.addEventListener('progress', function (e) {
            if (e.lengthComputable) {
              $('progress').attr({
                value: e.loaded,
                max: e.total,
              });
            }
          }, false);
        }
        return myXhr;
      },

      /* When we receive the response download file */
      success: function(result) {
        /* Because we're using Ajax, create a blob and use download attribute */
        const saveData = (function() {
            const a = document.createElement("a");
            document.body.appendChild(a);
            a.style = "display: none";
            return function (data, fileName) {
                const blob = new Blob([data], {type: "octet/stream"}),
                    url = window.URL.createObjectURL(blob);
                a.href = url;
                a.download = fileName;
                a.click();
                window.URL.revokeObjectURL(url);
            };
        }());

        saveData( result, "seating_arrangements.csv" );

        window.location.href = window.location.origin+window.location.pathname;
      }
    });
  });

});
