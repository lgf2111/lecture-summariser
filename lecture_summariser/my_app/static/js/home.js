if (window.history.replaceState) {
  window.history.replaceState(null, null, window.location.href);
}

const form = document.querySelector("#form");
const videoInput = document.querySelector("#video-input");
const video = document.querySelector("#video");
const source = document.querySelector("#source");
var uploadedVideo;

videoInput.addEventListener("change", function () {
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    uploadedVideo = reader.result;
    source.setAttribute("src", uploadedVideo);
    video.load();
    video.play();
  });
  reader.readAsDataURL(this.files[0]);
});

$(document).on("submit", "#form", function (e) {
  e.preventDefault();
  var formData = new FormData();
  formData.append("video", $("#video-input")[0].files[0]);
  formData.append(
    "csrfmiddlewaretoken",
    $("input[name=csrfmiddlewaretoken]").val()
  );
  $.ajax({
    type: "POST",
    url: "upload/",
    data: formData,
    processData: false,
    contentType: false,
    success: function (data, textStatus, XmlHttpRequest) {
      if (XmlHttpRequest.status == 200) {
        transcript = XmlHttpRequest.getResponseHeader("transcript");
        summary = XmlHttpRequest.getResponseHeader("summary").replace(
          /NEWLINE/i,
          "\n"
        );
        console.log(transcript);
        $("#text").text(summary);
        $(".qt-loading").css("display", "none");
      }
    },
  });
  $("#text").text("");
  $(".qt-loading").css("display", "block");
});
