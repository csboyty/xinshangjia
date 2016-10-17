/**
 * Created with JetBrains WebStorm.
 * User: ty
 * Date: 14-10-13
 * Time: 上午9:26
 * To change this template use File | Settings | File Templates.
 */
var Functions=(function(config){

    return {
        /**
         * 3秒跳转
         * @param url 需要跳转到的url
         */
        timeoutRedirect:function(url){
            setTimeout(function(){
                window.location.href=url;
            },3000);
        },
        /**
         * 获取文件的信息
         * @param fileName
         * @returns {{filePath: string, filename:string, ext: string}}
         */
        getFileInfo:function(fileName){
            var extPos=fileName.lastIndexOf(".");
            var pathPost=fileName.lastIndexOf("/");
            return {
                filePath:pathPost!=-1?fileName.substring(0,pathPost+1):"",
                filename:fileName.substring(pathPost+1,extPos),
                ext:fileName.substring(extPos+1)
            }
        },
        /**
         * 显示loading遮盖层
         */
        showLoading:function(){
            $("#loading").removeClass("hidden");
        },
        /**
         * 隐藏loading遮盖层
         */
        hideLoading:function(){
            $("#loading").addClass("hidden");
        },
        /**
         * ajax网络错误处理
         */
        ajaxErrorHandler:function(){
            this.hideLoading();
            $().toastmessage("showErrorToast",config.messages.networkError);
        },
        /**
         * ajax后台返回错误处理
         * @param errorCode {string} 错误代码
         */
        ajaxReturnErrorHandler:function(errorCode){
            var me=this;
            var message="";
            switch(errorCode){
                case "UNAUTHORIZED":
                    message=config.messages.timeout;
                    this.timeoutRedirect("./",true);
                    break;
                case "NOT_FOUND":
                    message=config.messages.notFound;
                    me.timeoutRedirect("./");
                    break;
                case "EMAIL_EXIST":
                    message=config.validErrors.emailExist;
                    break;
                default :
                    message=config.messages.systemError;
                    break;
            }
            this.hideLoading();
            $().toastmessage("showErrorToast",message);
        },

        /**
         * plupload版本1.2.1,采用all版本，需要使用qiniu.js
         * @param params
         * @returns {*}
         */
        createQiNiuUploader:function(params){
            var uploader = Qiniu.uploader({
                runtimes: 'html5,flash',    //上传模式,依次退化
                browse_button: params.btn,       //上传选择的点选按钮，**必需**
                uptoken_url:  params.upTokenUrl,
                multi_selection:false,
                domain:params.domain,
                container: params.container,           //上传区域DOM ID，默认是browser_button的父元素，
                filters: {
                    mime_types : [
                        { title : "media files", extensions : params.filter }
                    ]
                },
                multipart_params:params.multipartParams,
                max_file_size: params.size,
                flash_swf_url: config.upload.swfUrl,  //引入flash,相对路径
                max_retries: 3,                   //上传失败最大重试次数
                chunk_size: '4mb',                //分块上传时，每片的体积
                auto_start: true,                 //选择文件后自动上传，若关闭需要自己绑定事件触发上传
                init: {
                    'Init':function(up,info){
                        //console.log(up.getOption("max_file_size"));
                    },
                    'FilesAdded': function(up, files) {
                        if(typeof params.fileAddedCallback === "function"){
                            params.fileAddedCallback(up,files);
                        }
                    },
                    'BeforeUpload':function(up,file){
                        if(typeof params.beforeUploadCallback === "function"){
                            params.beforeUploadCallback(up,file);
                        }
                    },
                    'UploadProgress': function(up, file) {
                        if(typeof params.progressCallback ==="function"){
                            params.progressCallback(file);
                        }
                    },
                    'FileUploaded': function(up, file, info) {
                        if(typeof params.uploadedCallback === "function"){
                            var res = JSON.parse(info);
                            var path = config.qiNiu.bucketDomain + res.key; //获取上传成功后的文件的Url
                            params.uploadedCallback(file,path);
                        }
                    },
                    'Error': function(up, err, errTip) {
                        $().toastmessage("showErrorToast",errTip);
                        up.refresh();
                    },
                    'Key': function(up, file) {

                        // 若想在前端对每个文件的key进行个性化处理，可以配置该函数
                        // 该配置必须要在 unique_names: false , save_key: false 时才生效
                        var random=Math.floor(Math.random()*10+1)*(new Date().getTime());
                        var filename=file.name;
                        var extPos=filename.lastIndexOf(".");


                        // do something with key here
                        return random+filename.substring(extPos);

                        //return file.name;
                    }
                }
            });

            return uploader;

        }
    }

})(config);
