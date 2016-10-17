var postUpdate=(function(){
    /**
     * 显示步骤对应的面板
     * @param {Number} stepId 需要显示的面板的id
     */
    function showStepPanel(stepId){
        $(".zyupStepPanel").addClass("zyupHidden");
        $(stepId).removeClass("zyupHidden");
        $(".zyupStepCurrent").removeClass("zyupStepCurrent");
        $(".zyupStep[href='"+stepId+"']").addClass("zyupStepCurrent");
    }
    return {
        uploadedMedia:{},
        uploadHandler:null,
        preview:function(){
            var tpl=$("#previewTpl").html(),
                files=[],html="";
            for(var obj in this.uploadedMedia){
                files.push(this.uploadedMedia[obj])
            }
            html=juicer(tpl,{
                title:$("#zyupTitleInput").val(),
                description:$("#zyupDescriptionTxt").val(),
                assets:files
            });
            $("#zyupPreview").html(html);
        },
        createThumbUploader:function(){
            Functions.createQiNiuUploader({
                size:config.upload.sizes.all,
                filter:config.upload.filters.img,
                btn:"zyupThumbUploadBtn",
                multipartParams:null,
                domain:config.qiNiu.uploadDomain,
                container:"zyupThumbContainer",
                upTokenUrl:config.ajaxUrls.upTokenUrl,
                fileAddedCallback:function(up,files){

                },
                beforeUploadCallback:null,
                progressCallback:function(file){

                },
                uploadedCallback:function(file,path){

                    //判断是否是1：1
                    $.get(path+"?imageInfo",function(data){
                        //console.log(data);
                        if(data.width==data.height&&data.width>=500&&data.width<=800){
                            $("#zyupThumb").attr("src",path);
                            $("#zyupThumbUrl").val(path);
                        }else{
                            $().toastmessage("showErrorToast",
                                config.messages.imageNotSquareAndWRE.replace("${min}",500).replace("${max}",800));
                        }

                    });
                }
            });
        },
        createFileUploader:function(){
            Functions.createQiNiuUploader({
                size:config.upload.sizes.all,
                filter:config.upload.filters.zip,
                btn:"zyupFileUploadBtn",
                multipartParams:null,
                domain:config.qiNiu.uploadDomain,
                container:"zyupFileContainer",
                upTokenUrl:config.ajaxUrls.upTokenUrl,
                fileAddedCallback:function(up,files){

                },
                beforeUploadCallback:null,
                progressCallback:function(file){
                    $("#zyupFilename").text(file.name+"----"+file.percent+"%");
                },
                uploadedCallback:function(file,path){
                    $("#zyupFilename").text(file.name);
                    $("#zyupFilenameValue").val(file.name);
                    $("#zyupFileUrl").val(path);

                }
            });
        },
        createUploader:function(){
            var me=this;
            me.uploadHandler=Functions.createQiNiuUploader({
                size:config.upload.sizes.all,
                filter:config.upload.filters.img,
                btn:"zyupUploadBtn",
                multipartParams:null,
                domain:config.qiNiu.uploadDomain,
                container:"zyupStep2",
                upTokenUrl:config.ajaxUrls.upTokenUrl,
                fileAddedCallback:function(up,files){
                    var tpl=$("#mediaItemTpl").html(),
                        html="";
                    if($("#zyupMediaList li").length+files.length<=4){
                        html=juicer(tpl,{
                            fileId:files[0]["id"],
                            filename:files[0]["name"]
                        });

                        $("#zyupMediaList").append(html);
                    }else{
                        $().toastmessage("showErrorToast",config.messages.imageMoreThan4);
                        up.removeFile(files[0]);
                        up.stop();
                    }

                },
                beforeUploadCallback:null,
                progressCallback:function(file){
                    $(".zyupUnCompleteLi[data-file-id='"+file.id+"']").find(".zyupPercent").text(file.percent+"%");
                },
                uploadedCallback:function(file,path){
                    $.get(path+"?imageInfo",function(data){
                        //console.log(data);
                        if(data.width>=800&&data.width<=1200){
                            $(".zyupUnCompleteLi[data-file-id='"+file.id+"']").find(".zyupPercent").
                                html("<img style='width:100px' src='"+path+"'>").
                                end().addClass("zyupMediaItem").removeClass("zyupUnCompleteLi");
                            $(".zyupDelete.zyupHidden").removeClass("zyupHidden");
                            me.uploadedMedia[file["id"]]={
                                media_filename:file.name,
                                media_file:path
                            }
                        }else{
                            $().toastmessage("showErrorToast",config.messages.imageWidthRangeError.
                                replace("${filename}",file.name).replace("${min}",800).replace("${max}",1200));
                            $(".zyupUnCompleteLi[data-file-id='"+file.id+"']").remove();
                        }
                    });

                }
            });
        },
        deleteFile:function(el){
            var parentLi=$(el).parent("li"),
                fileId=parentLi.data("file-id");
            parentLi.remove();
            this.uploadedMedia[fileId]=undefined;
            delete this.uploadedMedia[fileId];
        },
        stepHandler:function(stepId){
            if(stepId!="#zyupStep1"){
                if($("#zyupTitleInput").val()==""||
                    $("#zyupDescriptionTxt").val()==""||$("#zyupAnalysisTxt").val()==""||
                    $("#zyupThumbUrl").val()==""||!$("#zyupCategorySel").val()){
                    $().toastmessage("showErrorToast",config.messages.stepOneUnComplete);
                    return false;
                }
            }

            if(stepId=="#zyupStep3"){

                //判断第二中的内容是否都已经填写完整。
                if($(".zyupMediaItem").length==0||$(".zyupUnCompleteLi").length!=0){
                    $().toastmessage("showErrorToast",config.messages.stepTwoUnComplete);
                    return false;
                }


                //显示
                this.preview();
            }

            showStepPanel(stepId);

        },
        formSubmit:function(form){
            Functions.showLoading();
            var files=[];
            var formObj=$(form).serializeObject();
            for(var obj in this.uploadedMedia){
                files.push(this.uploadedMedia[obj]);
            }
            formObj.assets=files;
            formObj.material_ids=$("#zyupCategorySel").val();
            $.ajax({
                url:config.ajaxUrls.workUpdate,
                dataType:"json",
                type:"post",
                data:{
                    data:JSON.stringify(formObj)
                },
                success:function(response){
                    if(response.success){
                        //Functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccRedirect);
                        Functions.timeoutRedirect("me/admin/artifact");
                    }else{
                        Functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    Functions.ajaxErrorHandler();
                }
            });
        },
        getPost:function(id){
            var me=this;
            $.ajax({
                url:config.ajaxUrls.workGetAssets.replace(":id",id),
                dataType:"json",
                type:"get",
                success:function(response){
                    if(response.success){
                        var length=response.assets.length;
                        for(var i=0;i<length;i++){
                            me.uploadedMedia[i+1]=response.assets[i];
                        }
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
})();

$(document).ready(function(){
    if(postId){
        postUpdate.getPost(postId);
    }

    //步骤控制
    $("#zyupTab a").click(function(){
        postUpdate.stepHandler($(this).attr("href"));

        return false;
    });

    $("#zyupMediaList").on("click",".zyupDelete",function(){
        postUpdate.deleteFile($(this));
    });

    postUpdate.createUploader();
    postUpdate.createFileUploader();
    postUpdate.createThumbUploader();

    $("#zyupForm").submit(function(){
        postUpdate.formSubmit($(this));
        return false;
    }).on("keydown",function(event){
            if(event.keyCode==13){
                return false;
            }
        })
});