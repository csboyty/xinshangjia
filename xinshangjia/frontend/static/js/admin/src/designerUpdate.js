var designerUpdate=(function(config){

    return {
        submitForm:function(form){
            Functions.showLoading();
            $.ajax({
                url:config.ajaxUrls.designerUpdate,
                dataType:"json",
                type:"post",
                data:{
                    data:JSON.stringify($(form).serializeObject())
                },
                success:function(response){
                    if(response.success){
                        //Functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccRedirect);
                        Functions.timeoutRedirect("me/admin/account/designer");
                    }else{
                        Functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    Functions.ajaxErrorHandler();
                }
            });
        },
        pwdSubmitForm:function(form){
            Functions.showLoading();
            $(form).ajaxSubmit({
                dataType:"json",
                headers:{
                    "X-Requested-With":"XMLHttpRequest"
                },
                success:function(response){
                    if(response.success){
                        //Functions.hideLoading();
                        $().toastmessage("showSuccessToast",config.messages.optSuccRedirect);
                        Functions.timeoutRedirect("me/admin/account/designer");
                    }else{
                        Functions.ajaxReturnErrorHandler(response.error_code);
                    }
                },
                error:function(){
                    Functions.ajaxErrorHandler();
                }
            });
        },
        initEmailValid:function(){
            var emailRule={};
            var emailMessage={};
            if(!country){
                emailRule={
                    required:true,
                    maxlength:32,
                    email:true,
                    remote:config.ajaxUrls.emailExistOrNot
                };
                emailMessage={
                    required:config.validErrors.required,
                    maxlength:config.validErrors.maxLength.replace("${max}",32),
                    email:config.validErrors.email,
                    remote:config.validErrors.emailExist
                }
            }

            return {
                emailRule:emailRule,
                emailMessage:emailMessage
            }
        }
    };
})(config);

$(document).ready(function(){

    var emailValid=designerUpdate.initEmailValid();
    $("#country").val(country?country:"CN");

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
                if(data.width==500&&data.height==500){
                    $("#imageUrl").val(path);

                    $("#image").attr("src",path);

                    $(".error[for='imageUrl']").remove();
                }else{
                    $().toastmessage("showErrorToast",config.messages.imageNot500x500);
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
            email:emailValid.emailRule,
            nick_name:{
                required:true,
                maxlength:32
            },
            first_name:{
                required:true,
                maxlength:32
            },
            last_name:{
                required:true,
                maxlength:32
            },
            tel:{
                required:true,
                maxlength:32
            },
            description:{
                required:true,
                maxlength:1024
            },
            address:{
                required:true,
                maxlength:128
            }
        },
        messages:{
            image_url:{
                required:config.validErrors.required
            },
            email:emailValid.emailMessage,
            nick_name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            first_name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            last_name:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            tel:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",32)
            },
            description:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",1024)
            },
            address:{
                required:config.validErrors.required,
                maxlength:config.validErrors.maxLength.replace("${max}",128)
            }
        },
        submitHandler:function(form) {
            designerUpdate.submitForm(form);
        }
    });

    $("#pwdForm").validate({
        ignore: [],
        rules:{
            password:{
                required:true
            },
            confirmPwd:{
                required:true,
                equalTo:"#editPwd"
            }
        },
        messages:{
            password:{
                required:config.validErrors.required
            },
            confirmPwd:{
                required:config.validErrors.required,
                equalTo:config.validErrors.pwdNotEqual
            }
        },
        submitHandler:function(form) {
            designerUpdate.pwdSubmitForm(form);
        }
    })

});


