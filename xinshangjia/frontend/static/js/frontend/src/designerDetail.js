var designerDetail=(function(config){
    return {
        showSome:function(){
            if($("#workList li.hidden").length!=0){
                $("#workList li.hidden").slice(0,config.perLoadCount.scroll).
                    removeClass("hidden");
            }else{
                $('#ownPagination').removeClass("hidden");
                return false;
            }

            return true;
        }
    }
})(config);
$(document).ready(function(){
    Functions.initShow(designerDetail.showSome);
    Functions.windowScroll(designerDetail.showSome);
    Functions.initPagination(config.pageUrls.designerDetail.replace(":id",designerId));
});
