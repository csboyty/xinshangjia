var userMgr=(function(config){

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.getAllDesigners,
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
                { "mDataProp": "nick_name"},
                { "mDataProp": "email"},
                { "mDataProp":"active",
                    "fnRender":function(oObj){
                        return config.activeTxt[oObj["aData"]["active"]];
                    }},

                { "mDataProp":"opt",
                    "fnRender":function(oObj) {
                        var string="<a href='users/"+oObj.aData.id+"/update'>禁言</a>";

                        return  string;
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    "name": "searchContent",
                    "value":  $("#searchContent").val()
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
                url:config.ajaxUrls.deleteUser.replace(":userId",id),
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

    userMgr.createTable();

    $("#myTable").on("click","a.remove",function(){
        if(confirm("确定删除吗？")){
            userMgr.remove($(this).attr("href"));
        }

        return false;
    });
});
