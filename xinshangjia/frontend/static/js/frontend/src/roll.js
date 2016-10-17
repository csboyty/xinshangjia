var roll=(function(){
    var totalCount=0;
    var currentIndex=0;
    var interval=null;
    var prevEl=null;
    function animation(){
        var currentEl=$("#rollList li").eq(currentIndex);
        prevEl.animate({
            "opacity":0,
            "zIndex":1
        },500);
        currentEl.animate({
            "opacity":1,
            "zIndex":3
        },700,function(){
            $("#numberList .active").removeClass("active");
            $("#numberList td").eq(currentIndex).find("a").addClass("active");
            prevEl=currentEl;
            if(interval==null){
                intervalRoll();
            }
        });
    }
    function toNumber(number){
        clearInterval(interval);
        interval=null;
        currentIndex=number;
        animation();
    }

    function intervalRoll(){
        interval=setInterval(function(){
            if(currentIndex==totalCount-1){
                currentIndex=-1;
            }
            ++currentIndex;
            animation();
        },6000);
    }
    return {
        init:function(){
            totalCount=$("#rollList li").length;
            prevEl=$("#rollList li").eq(0);
        },
        intervalRoll:intervalRoll,
        toNumber:toNumber
    }
})();
$(document).ready(function(){
    roll.init();
    roll.intervalRoll();
    $("#rollList img:last").on("load",function(){
        //console.log($(this).height());
        $("#rollList").height($(this).height());
    }).each(function() {
        //防止缓存触发此事件
        if(this.complete){
            $(this).load();
        }
    });
    $(window).resize(function(){
        $("#rollList").height($("#rollList img").eq(0).height());
    });

    $("#numberList a").click(function(){
        roll.toNumber($(this).parent().index());
        return false;
    });
});

