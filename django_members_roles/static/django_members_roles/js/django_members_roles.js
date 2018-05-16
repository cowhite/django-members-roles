var $manageStaff = $("#manage-staff");

var staffList = function(url){
 if(!url){
  url = $manageStaff.data("staff_list_url");
  //url = "/django_members_roles/"+contentTypeId+"/"+objectId+"/staff_list/";
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
  url = $manageStaff.data("role_list_url");
  //url = "/django_members_roles/"+contentTypeId+"/"+objectId+"/role_list/";
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

  $(document).on("change", ".select-role", function(){
    var roleId = $(this).val(),
        url = $(this).data('url'),
        userId = $(this).data('user-id');
    data = {
      "csrfmiddlewaretoken": csrfmiddlewaretoken,
      "user_id":userId,
      "role_id": roleId
    }
    $.ajax({
      url: url,
      data: data,
      type: "POST",
      success: function(res){
        if(res.error) {
          console.log(res.error);
        }
        else{
          staffList();
        }
      }
    });
  });
  onLoad();

})