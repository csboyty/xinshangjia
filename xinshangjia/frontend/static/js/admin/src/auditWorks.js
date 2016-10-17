var auditWorks=(function(config,Functions){
    var loadedData={},
        currentWorksId=0;

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource": config.ajaxUrls.getAllAuditWorks,
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
                { "mDataProp": "title"},
                { "mDataProp": "toAuditDate"},
                { "mDataProp": "status",
                    "fnRender":function(oObj){
                        return config.auditTxt[oObj.aData.status];
                    }
                },
                { "mDataProp": "memo"},
                { "mDataProp": "opt",
                    "fnRender":function(oObj){
                        return '<a href="'+oObj.aData.id+'" class="audit">审核</a>';
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    "name": "searchContent",
                    "value":  $("#searchContent").val()
                },{
                    "name": "searchStatus",
                    "value":  $("#searchStatus").val()
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
                                loadedData[response.aaData[i].id]=response.aaData[i];
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
        audit:function(id){
            var data=loadedData[id],
                html;
            var tpl=$("#worksTpl").html();
            currentWorksId=id;
            html=juicer(tpl,{
                title:data.title,
                description:data.description,
                assets:data.assets,
                thumbUrl:data.thumb_url
            });
            $("#worksDetail").html(html);
            $("#auditDesignerModal").modal("show");
        },
        submitForm:function(form){
            var me=this;
            Functions.showLoading();
            $(form).ajax({
                url:"#",
                dataType:"json",
                type:"post",
                data:{
                    data:JSON.stringify($(form).serializeObject())
                },
                success:function(response){
                    if(response.data.success){
                        Functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        form.reset();
                        me.tableRedraw();
                        $("#auditDesignerModal").modal("hide");
                    }else{
                        Functions.ajaxReturnErrorHandler(response.data.error_code);
                    }
                },
                error:function(){
                    Functions.ajaxErrorHandler();
                }
            });
        }
    }
})(config,Functions);

$(document).ready(function(){

    auditWorks.createTable();

    $("#myTable").on("click","a.audit",function(){
        auditWorks.audit($(this).attr("href"));
        return false;
    });

    $("#formSubmit").click(function(){
        //判断描述是否填写
        if($("#memo").val()==""&&$("#auditStatus").val()==2){
            $(".error[for='memo']").removeClass("hidden");
        }else{
            $(".error[for='memo']").addClass("hidden");
            auditWorks.submitForm(this);
        }
        return false;
    });

    $("#auditStatus").change(function(){
        if($(this).val()==2){
            $("#memoRow").removeClass("hidden");
        }else{
            $("#memoRow").addClass("hidden");
        }
    });
});

