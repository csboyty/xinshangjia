var slideMgr=(function(config){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.slideGetALL,
            "bInfo":true,
            "bLengthChange": false,
            "bFilter": false,
            "bSort":false,
            "bAutoWidth": false,
            "iDisplayLength":config.perLoadCount.table,
            "sPaginationType":"full_numbers",
            "oLanguage": {
                "sUrl":config.dataTable.langUrl
            },
            "aoColumns": [
                { "mDataProp": "image_url",
                    "fnRender":function(oObj){
                        return "<img class='slideThumb' src='"+oObj["aData"]["image_url"]+"'>";
                    }
                },
                { "mDataProp": "caption",
                    "fnRender":function(oObj){
                        return oObj.aData.caption+"&nbsp;&nbsp;"+
                            "<a href='"+oObj.aData.link_url+"' target='_blank'>链接</a>";
                    }
                },
                { "mDataProp":"status",
                    "fnRender":function(oObj){
                        return config.statusTxt[oObj["aData"]["status"]];
                    }},
                { "mDataProp": "locale",
                    "fnRender":function(oObj){
                        return config.lang[oObj.aData.locale];
                    }
                },
                { "mDataProp": "ordering"},
                { "mDataProp":"opt",
                    "fnRender":function(oObj) {
                        var string="<a href='me/admin/banner/update-banner/"+oObj.aData.id+"'>修改</a>&nbsp;"+
                            "<a href='"+oObj.aData.id+"' class='remove'>删除</a>&nbsp;";

                        return  string;
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    "name": "banner_caption",
                    "value":  ""
                });
            },
            "fnServerData": function(sSource, aoData, fnCallback) {

                //回调函数
                $.ajax({
                    "dataType":'json',
                    "type":"get",
                    "url":sSource,
                    "data":aoData,
                    "success": function (response) {
                        if(response.success===false){
                            Functions.ajaxReturnErrorHandler(response.error_code);
                        }else{
                            var json = {
                                "sEcho" : response.sEcho
                            };
                            for (var i = 0, iLen = response.aaData.length; i < iLen; i++) {
                                response.aaData[i].opt="opt";
                            }

                            json.aaData=response.aaData;
                            json.iTotalRecords = response.iTotalRecords;
                            json.iTotalDisplayRecords = response.iTotalDisplayRecords;
                            fnCallback(json);
                        }

                    }
                });
            },
            "fnFormatNumber":function(iIn){
                return iIn;
            }
        });

        return ownTable;
    }

    return {
        ownTable:null,
        createTable:function(){
            this.ownTable=createTable();
        },
        tableRedraw:function(){
            this.ownTable.fnSettings()._iDisplayStart=0;
            this.ownTable.fnDraw();
        },
        remove:function(id){
            Functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.slideDelete.replace(":id",id),
                type:"post",
                dataType:"json",
                success:function(response){
                    if(response.success){
                        Functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        me.ownTable.fnDraw();
                    }else{
                        Functions.ajaxReturnErrorHandler(response.error_code);
                    }

                },
                error:function(){
                    Functions.ajaxErrorHandler();
                }
            });
        }
    }
})(config);

$(document).ready(function(){

    slideMgr.createTable();

    $("#myTable").on("click","a.remove",function(){
        if(confirm(config.messages.confirmDelete)){
            slideMgr.remove($(this).attr("href"));
        }

        return false;
    });
});
