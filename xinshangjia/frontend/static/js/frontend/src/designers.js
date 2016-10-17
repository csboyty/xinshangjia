var designers=(function(config){
    return {
        showSome:function(){
            if($("#designerList li.hidden").length!=0){
                $("#designerList li.hidden").slice(0,config.perLoadCount.scroll).
                    removeClass("hidden").addClass("active");
            }else{
                $('#ownPagination').removeClass("hidden");
                return false;
            }
            return true;
        }
    }
})(config);
$(document).ready(function(){
    Functions.initShow(designers.showSome);
    Functions.windowScroll(designers.showSome);
    Functions.initPagination(config.pageUrls.designer);
});
