console.log(99);
function switchTab(tab) {
  console.log("Switching tab to "+tab);
  var url, $section;

  if(!tab) {
    if(typeof(defaultTab) == "undefined") {
      defaultTab = "";
    }
    tab = defaultTab;
  }
  if(!tab) {
    return;
  }

  if(tab[0] == "!") {
    return;
  }
  if(!$("#"+tab+"-section").length){
    return;
  }
  $(".each-section").addClass("hide");

  $section = $("#"+tab+"-section");
  $section.removeClass("hide");
  $(document).trigger(tab+"-opened");

  url = $section.data("url");
  if(url) {
    $.get(url, function(res) {
      $("#"+tab+"-content").html(res);
    });
  }

}
function getObjFromUrlHash() {
  var hash = window.location.hash,
  obj = {}, hashName, hashArr, hashParams, hashParamsArr, hashParamsObj = {};

  if(!hash) {
    return {};
  }
  hashArr = hash.split("?");
  if(hashArr.length) {
    hashName = hashArr[0];
    hashName = hashName.substr(1, hashName.length);
  }
  if(hashArr.length > 1) {
    hashParams = hashArr[1];
  }

  if (hashParams){
    hashParamsObj = {};
    hashParamsArr = hashParams.split("&");
    for(var i=0; i<hashParamsArr.length; i++){
      temp = hashParamsArr[i].split("=");
      hashParamsObj[temp[0]] = temp[1];
    }
  }
  res = {
    "name": hashName,
    "params": hashParamsObj
  }
  return res;

}

function onLoad() {
  var hashObj = getObjFromUrlHash();
  console.log("hashObj")
  console.log(hashObj)
  switchTab(hashObj.name);
}

var submitForm = function($this){
  var modal = $('.form-modal'), showFormBtnId, $showFormBtn, url,
  id, form, formContentId, modal, aftersuccess, type;

  if($this.hasClass("btn-submit-form")) {
    showFormBtnId = "#"+modal.find(".btn.btn-primary").data("btn-show-form-id");
    $showFormBtn = $(showFormBtnId);
  }else{
    modal.find(".btn.btn-primary").data("btn-show-form-id", $this.attr('id'));
  }

  if($this.hasClass("form-in-popup")) {
    formContentId = $this.data("form-id");
  }else{
    formContentId = modal.find(".modal-body");
  }
  form = modal.find(".modal-body form");

  if(showFormBtnId){
    url = $showFormBtn.data('url'),
    id = showFormBtnId,
    afterSuccess = $showFormBtn.data('aftersuccess'),
    type = "POST";
  }else{
    url = $this.data('url'),
    id = $this.data('id'),

    afterSuccess = $this.data('aftersuccess'),
    type = "GET";
  }

  var data = new FormData($(form)[0]);

  var width = $this.data("width");
  if (!width){ width = "150px"; }

  $.ajax({
    url: url,
    type: type,
    data: data,
    processData: false,
    contentType: false,
    success: function(res) {
      if(res.error) {
        $(formContentId).html(res.html);
      }
      else{

        if($this.hasClass("btn-submit-form")){
          $(modal).modal('hide');
          eval(afterSuccess)();
        }
        else{
          $(formContentId).html(res);
        }
        if(type == 'GET') {
          modal.modal("show");
        }
      }
    }
  });
}

$(function(){

  //onLoad();
  $(window).on("hashchange", function() {
    var hash = window.location.hash;
    if(hash) {
      hash = hash.split("?")[0];
      hash = hash.substr(1, hash.length);
      switchTab(hash);
    }
  });

  $(document).on("click",".btn-show-submit-form", function(){
    submitForm($(this));
  });

  $(document).on("click", ".btn-action", function(){
    var $this = $(this),
    url = $this.data("url"),
    requestType = $this.data("request-type"),
    data = {"csrfmiddlewaretoken": csrfmiddlewaretoken };

    if($this.hasClass("btn-action-delete")) {
      var confirmDelete = confirm("Are you sure want to delete ?");
      if(!confirmDelete) { return; }
    }

    if(!requestType) {
      requestType = "GET";
    }


    $.ajax({
      url: url,
      type: requestType,
      success: function(res) {
        $this.remove();
      }
    });
  })

});