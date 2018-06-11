toastr.options = {
  "closeButton": false,
  "debug": false,
  "newestOnTop": false,
  "progressBar": false,
  "positionClass": "toast-top-right",
  "preventDuplicates": true,
  "onclick": null,
  "showDuration": "300",
  "hideDuration": "1000",
  "timeOut": "5000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
};
$(document).ready(function () {
  for (var i=0; i<flashed_messages.length; i++) {
    var category = flashed_messages[i][0],
      message = flashed_messages[i][1];
    if (toastr.hasOwnProperty(category)) {
      toastr[category](message);
    } else {
      toastr.info(message)
    }
  }
})
