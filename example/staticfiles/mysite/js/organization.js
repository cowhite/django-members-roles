var organizationsList = function(){
    var url = $("#organizations-list").data('url'),
        $templateId = $("#organizations-list");
    $.ajax({
        url: url,
        type: "GET",
        success: function(res){
            if(res.error) {
                console.log(res.error);
            }
            else{
                $templateId.html(res);
            }
        }
    });
}

$(function(){
    $(document).on("organizations-opened", function(e, data) {
        organizationsList();
        console.log("organizations tab opened");
    });
    onLoad();
});