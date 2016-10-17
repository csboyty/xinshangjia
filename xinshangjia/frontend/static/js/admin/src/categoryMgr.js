var categoryMgr=(function(config){
    var currentId=0;

    /**
     * 创建datatable
     * @returns {*|jQuery}
     */
    function createTable(){

        var ownTable=$("#myTable").dataTable({
            "bServerSide": true,
            "sAjaxSource":config.ajaxUrls.categoryGetAll,
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
                { "mDataProp": "more",
                    "fnRender":function(oObj) {
                        if(oObj.aData.translations.length!=0){
                            return '<span class="more glyphicon glyphicon-plus"></span>';
                        }
                        return "";
                    }
                },
                { "mDataProp": "name"},
                { "mDataProp": "description"},
                { "mDataProp": "locale",
                    "fnRender":function(oObj){
                        return config.lang[oObj.aData.locale];
                    }
                },
                { "mDataProp":"opt",
                    "fnRender":function(oObj) {
                        var string="<a href='"+oObj.aData.id+"' class='addLang'>追加语言</a>&nbsp;&nbsp;" +
                            "<a href='"+oObj.aData.id+"' class='remove'>删除</a>";

                        return  string;
                    }
                }
            ] ,
            "fnServerParams": function ( aoData ) {
                aoData.push({
                    "name": "material_name",
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
                                var primary=response.aaData[i].translations[0];
                                response.aaData[i].opt="opt";
                                response.aaData[i].more="more";
                                response.aaData[i].name=primary.name;
                                response.aaData[i].locale=primary.locale;
                                response.aaData[i].description=primary.description;
                                response.aaData[i].translations=response.aaData[i].translations.slice(1);
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
        formSubmit:function(form){
            Functions.showLoading();
            var me=this;
            var url=$(form).attr("id")=="addForm"?config.ajaxUrls.categoryUpdate:
                config.ajaxUrls.categoryAddLang.replace(":id",currentId);
            $.ajax({
                url:url,
                dataType:"json",
                type:"post",
                data:{
                    data:JSON.stringify($(form).serializeObject())
                },
                success:function(response){
                    if(response.success){
                        Functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccess);
                        $("#addLangModal").modal("hide");
                        me.tableRedraw();
                    }else{
                        Functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    Functions.ajaxErrorHandler();
                }
            });
        },
        moreContent:function(data){
            var records=data.translations;
            var string='<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;width:100%">';

            //for循环添加tr
            for(var i= 0,length=records.length;i<length;i++){
                string+="<tr><td style='width: 30%'>"+records[i].name+"</td>" +
                    "<td style='width: 40%'>"+records[i].description+"</td>" +
                    "<td style='width: 10%'>"+config.lang[records[i].locale]+"</td>" +
                    "<td><a class='removeChild' href='"+records[i].locale+"/"+data.id+"'>删除</a></td></tr>";
            }

            return string+"</table>";
        },
        showMore:function(el){
            var me=this,
                tr = el.closest('tr')[0],
                data;

            if ( this.ownTable.fnIsOpen(tr) ){
                el.removeClass('shown glyphicon-minus').addClass("glyphicon-plus");
                this.ownTable.fnClose( tr );
            }else{
                data=this.ownTable.fnGetData(tr);

                el.addClass('shown glyphicon-minus').removeClass("glyphicon-plus");
                me.ownTable.fnOpen( tr, me.moreContent(data), 'details' );

            }
        },
        removeChild:function(el){
            var args=el.attr("href").split("/"),
                lang=args[0],
                id=args[1],
                me=this;

            Functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.categoryRemoveLang.replace(":id",id),
                type:"post",
                dataType:"json",
                data:{
                    locale:lang
                },
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
        },
        remove:function(id){
            Functions.showLoading();
            var me=this;
            $.ajax({
                url:config.ajaxUrls.categoryDelete.replace(":id",id),
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
        },
        addLang:function(el){
            var tr = el.closest('tr')[0],
                data=this.ownTable.fnGetData(tr),
                me=this;

            currentId=data.id;
            $("#oldName").text(data.name);
            $("#oldDescription").text(data.description);
            $("#addLangForm")[0].reset();

            $("#langSel").rules("remove","remote");
            $("#langSel").rules("add",{
                remote: config.ajaxUrls.categoryLangExistOrNot.replace(":id",currentId)
            });



            $("#addLangModal").modal("show");
        }
    }
})(config);

$(document).ready(function(){

    categoryMgr.createTable();

    $("#myTable").on("click","a.remove",function(){
        if(confirm(config.messages.confirmDelete)){
            categoryMgr.remove($(this).attr("href"));
        }
        return false;
    }).on("click",".more",function(){
        categoryMgr.showMore($(this));
    }).on("click",".addLang",function(){
            categoryMgr.addLang($(this));
            return false;
    }).on("click",".removeChild",function(){
            if(confirm(config.messages.confirmDelete)){
                categoryMgr.removeChild($(this));
            }
            return false;
    });

    $("#searchBtn").click(function(){
        categoryMgr.tableRedraw();
        return false;
    });

    $("#addForm").validate({
        rules:{
            name:{
                required:true,
                maxlength:32,
                remote:config.ajaxUrls.categoryExistOrNot
            }
        },
        messages:{
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32),
                remote:config.validErrors.contentExist
            }
        },
        submitHandler:function(form) {
            categoryMgr.formSubmit(form);
        }
    });

    $("#addLangForm").validate({
        rules:{
            name:{
                required:true,
                maxlength:32,
                remote:config.ajaxUrls.categoryExistOrNot
            },
            locale:{
                required:true,
                remote:config.ajaxUrls.categoryLangExistOrNot
            }
        },
        messages:{
            name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32),
                remote:config.validErrors.contentExist
            },
            locale:{
                required:config.validErrors.required,
                remote:config.validErrors.langExist
            }
        },
        submitHandler:function(form) {
            categoryMgr.formSubmit(form);
        }
    });
});
