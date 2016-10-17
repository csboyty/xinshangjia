var Functions=(function(config){
    return {
        timer:null,
        /**
         * 页面进入显示的卡片数量
         * @param callback
         */
        initShow:function(callback){
            var hasMore=callback();

            //再次调用一下,防止加载一次还是无滚动条
            if($("body").height()<$(window).height()&&hasMore){
                this.initShow(callback);
            }

        },
        /**
         * 初始化分页插件
         */
        initPagination:function(pageUrl){
            $('#ownPagination').jqPagination({
                max_page:Math.ceil(parseInt(maxCount)/config.perLoadCount.page),
                current_page:parseInt(currentPage),
                page_string:" {current_page} / {max_page}",
                paged: function(page) {
                    window.location.href=pageUrl+page;
                }
            });
        },
        /**
         * 绑定window滚动事件
         * @param callback
         */
        windowScroll:function(callback){
            if(this.timer){
                clearTimeout(this.timer);
                this.timer=null;
            }
            this.timer=setTimeout(function(){
                $(window).scroll(function(){
                    if(($(document).height()-$(window).height()<=$(window).scrollTop()+10)){
                        callback();
                    }
                });
            },200);
        }
    }
})(config);

$(document).ready(function(){
    $("#menu a[data-menu-page="+pageName+"]").addClass("active");
});