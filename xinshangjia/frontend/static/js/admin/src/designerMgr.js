var designerMgr=(function(config){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.userGetAll,
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
                        return "<img class='peopleThumb' src='"+oObj["aData"]["image_url"]+"'>";
                    }
                },
                { "mDataProp": "nick_name"},
                { "mDataProp": "email"},
                { "mDataProp": "secret_info",
                    "fnRender":function(oObj){
                        return oObj.aData.secret_info.tel;
                    }
                    },
                { "mDataProp":"opt",
                    "fnRender":function(oObj) {
                        var string="<a href='users/"+oObj.aData.id+"/update'>主页</a>&nbsp;" +
                            "<a href='me/admin/account/update-designer/"+oObj.aData.id+"'>修改/查看</a>&nbsp;"+
                            "<a href='"+oObj.aData.id+"' class='remove'>删除</a>";

                        return  string;
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    "name": "account_email",
                    "value":  $("#searchContent").val()
                },{
                    "name": "account_type",
                    "value":  config.userType.designer
                },{
                    "name": "account_country",
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
                url:config.ajaxUrls.designerDelete.replace(":id",id),
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

    designerMgr.createTable();

    $("#myTable").on("click","a.remove",function(){
        if(confirm("确定删除吗？")){
            designerMgr.remove($(this).attr("href"));
        }

        return false;
    });

    $("#searchBtn").click(function(){
        designerMgr.tableRedraw();
        return false;
    });
});
