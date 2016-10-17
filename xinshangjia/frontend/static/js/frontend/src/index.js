var index=(function(config){
    return {
        showSome:function(){
            if($("#workList li.hidden").length!=0){
                $("#workList li.hidden").slice(0,config.perLoadCount.scroll).
                    removeClass("hidden");
            }else{
                return false;
            }

            return true;
        }
    }
})(config);

$(document).ready(function(){
    Functions.initShow(index.showSome);
    Functions.windowScroll(index.showSome);
});
