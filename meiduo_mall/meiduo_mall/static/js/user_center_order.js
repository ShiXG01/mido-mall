var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        host: host,
    },
    mounted(){

    },
    methods: {
        oper_btn_click(order_id, status){
            if (status == '1') {
                // 待支付
                var url = this.host + '/payment/' + order_id + '/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.code == '0') {
                            location.href = response.data.alipay_url;
                        } else {
                            console.log(response.data);
                            alert(response.data.errmsg);
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    });
            } else if (status == '4') {
                // 待评价
                location.href = '/orders/comment/?order_id=' + order_id;
            } else {
                // 其他：待收货。。。
                // location.href = '/';
                var url = this.host + '/receive/?order_id=' + order_id;
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        status = response.status
                    })
                    .catch(error => {
                        console.log(error.response);
                    });
            }
        },
    }
});
function getCookie(name) {
    var dc = document.cookie;
    var prefix = name + "=";
    var begin = dc.indexOf(prefix);
    if (begin == -1) {
        begin = dc.indexOf(prefix);
        if (begin != 0) return null;
    }
    else
    {
        // begin += 2;
        var end = document.cookie.indexOf(";", begin);
        if (end == -1) {
        end = dc.length;
        }
    }
    return decodeURI(dc.substring(begin + prefix.length, end));
}
