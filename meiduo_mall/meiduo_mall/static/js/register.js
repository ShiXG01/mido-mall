let vm = new Vue({
    el: '#app', //绑定html内容
    delimiters: ['[[', ']]'],
    data:{ // 数据对象
        username:'',
        password:'',
        password2:'',
        mobile:'',
        image_code_url:'',
        image_code:'',
        sms_code:'',
        sms_code_tip: '获取短信验证码',
        allow:'',
        uuid:'',
        send_flag:'',

        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_image_code: false,
        error_sms_code: false,
        error_allow: false,

        error_name_message:'',
        error_mobile_message:'',
        error_image_code_message:'',
        error_sms_code_message:'',
    },
    mounted(){
        this.generate_image_code();
    },
    methods:{ //定义和实现事件的方法
        check_username(){
            let re = /^[a-zA-Z\d_-]{5,20}$/; //定义正则
            if (re.test(this.username)) { //匹配用户数据
                // 匹配成功，不展示错误提示信息
                this.error_name = false;
            } else {
                // 匹配失败，展示错误提示信息
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            }

            if (this.error_name == false){
                let url = '/usernames/' + this.username + '/count/';
                axios.get(url, { responseType: 'json' })
                    .then(response =>{
                        if (response.data.count == 1){
                            this.error_name_message = '用户名已存在';
                            this.error_name = true;
                        }
                        else{
                            this.error_name = false;
                        }
                    })
                    .catch(error =>{
                        console.log(error.response);
                    })
            }
        },
        check_password(){
            let re = /^[\dA-Za-z]{8,20}$/;
            // this.error_password = !re.test(this.password);
            this.error_password = !re.test(this.password);
        },
        check_password2(){
            this.error_password2 = this.password != this.password2;
        },
        check_mobile(){
            let re = /^1[3-9]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_message = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }

            if (this.error_mobile == false){
                let url = '/mobile/' + this.mobile + '/count/';
                axios.get(url, { responseType: 'json' })
                    .then(response =>{
                        if (response.data.count == 1){
                            this.error_mobile_message = '手机号已注册';
                            this.error_mobile = true;
                        }
                        else{
                            this.error_mobile = false;
                        }
                    })
                    .catch(error =>{
                        console.log(error.response);
                    })
            }
        },
        check_image_code(){
            if (this.image_code.length != 4){
                this.error_image_code_message = '请输入图形验证码';
                this.error_image_code = true;
            }
            else{
                this.error_image_code = false;
            }
        },
        generate_image_code(){
            this.uuid = generateUUID();
            this.image_code_url = '/image_code/'+ this.uuid + '/';
        },
        check_sms_code(){
            if (this.sms_code.length != 6){
                this.error_sms_code_message = '请填写短信验证码'
                this.error_sms_code = true;
            }
            else {
                this.error_sms_code = false;
            }
        },
        send_sms_code(){

            if (this.send_flag == true){
                return;
            }
            this.send_flag =true;

            this.check_mobile();
            this.check_image_code();
            if (this.error_mobile == true || this.error_image_code == true){
                this.send_flag = false;
                return;
            }

            let url = '/sms_code/'+this.mobile+'/?image_code='+this.image_code+'&uuid='+this.uuid;
            axios.get(url, { responseType: 'json' })
                .then(response =>{
                    if (response.data.code == 0){
                        let num = 60;
                        this.error_sms_code_message = response.data.errmsg;
                        let t =setInterval(() =>{
                            if (num == 1){
                                clearInterval(t);
                                this.sms_code_tip = '获取短信验证码';
                                this.generate_image_code();
                                this.send_flag = false;
                            }else{
                                num -= 1;
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000)
                    }else{
                        if (response.data.code == 4001){
                            this.error_image_code_message = response.data.errmsg;
                            this.error_image_code = true;
                        }else {
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                        }
                        this.send_flag = false;
                    }
                })
                .catch(error =>{
                    console.log(error.response);
                    this.send_flag = false;
                })
        },
        check_allow(){
            this.error_allow = !this.allow;
        },
        on_submit(){
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_allow();

            // 在校验之后，注册数据中，只要有错误，就禁用掉表单的提交事件
            if (this.error_name == true || this.error_password == true || this.error_password2 == true || this.error_mobile == true || this.error_sms_code ==true || this.error_allow == true) {
                // 禁用掉表单的提交事件
                window.event.returnValue = false;}
        },
    },
})