var slideUpdate=(function(config){

    return {
        submitForm:function(form){
            Functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.slideUpdate,
                dataType:"json",
                type:"post",
                data:{
                    data:JSON.stringify($(form).serializeObject())
                },
                success:function(response){
                    if(response.success){
                        //Functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccRedirect);
                        Functions.timeoutRedirect("me/admin/banner");
                    }else{
                        Functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    Functions.ajaxErrorHandler();
                }
            });
        }

    };
})(config);

$(document).ready(function(){
    Functions.createQiNiuUploader({
        size:config.upload.sizes.img,
        filter:config.upload.filters.img,
        btn:"uploadBtn",
        multipartParams:null,
        domain:config.qiNiu.uploadDomain,
        container:"uploadContainer",
        upTokenUrl:config.ajaxUrls.upTokenUrl,
        fileAddCallback:null,
        progressCallback:null,
        uploadedCallback:function(file,path){

            $.get(path+"?imageInfo",function(data){
                //console.log(data);
                if(data.width==1920&&data.height==600){
                    $("#imageUrl").val(path);

                    $("#image").attr("src",path);

                    $(".error[for='imageUrl']").remove();
                }else{
                    $().toastmessage("showErrorToast",config.messages.imageNot1920x600);
                }
            });
        }
    });

    $("#myForm").validate({
        ignore: [],
        rules:{
            image_url:{
                required:true
            },
            caption:{
                required:true,
                maxlength:32
            },
            ordering:{
                required:true,
                number:true,
                range:[1,10]
            },
            link_url:{
                required:true,
                maxlength:128
            }
        },
        messages:{
            image_url:{
                required:config.validErrors.required
            },
            caption:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            ordering:{
                required:config.validErrors.required,
                number:config.validErrors.number,
                rang:config.validErrors.rang.replace("${min}",1).replace("${max}",10)
            },
            link_url:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",128)
            }
        },
        submitHandler:function(form) {
            slideUpdate.submitForm(form);
        }
    });

});


