var $manageStaff = $("#manage-staff"),
    contentTypeId = $manageStaff.data("content_type_id"),
    objectId = $manageStaff.data("object_id");

var staffList = function(url){
 if(!url){
  url = "/django_roles/"+contentTypeId+"/"+objectId+"/staff_list/";
}
$.ajax({
  url: url,
  type: "GET",
  success: function(res){
    if(res.error) {
      console.log(res.error);
    }
    else{
      $("#staff-list").html(res);
    }
  }
});
}

var roleList = function(url){
 if(!url){
  url = "/django_roles/"+contentTypeId+"/"+objectId+"/role_list/";
}
$.ajax({
  url: url,
  type: "GET",
  success: function(res){
    if(res.error) {
      console.log(res.error);
    }
    else{
      $("#role-list").html(res);
    }
  }
});
}

$(function(){
  $(document).on("staff-opened", function(e, data) {
    if(data){
      staffList(data.url);
    }
    else{
      staffList();
    }
    console.log("staff tab opened");
  });

  $(document).on("roles-opened", function(e, data) {
    if(data){
      roleList(data.url);
    }
    else{
      roleList();
    }
    console.log("roles tab opened");
  });

  onLoad();

})