import Vue from 'vue'

import VueRouter from 'vue-router';
import _ from "lodash";


import 'normalize.css/normalize.css' // A modern alternative to CSS resets

import ElementUI from 'element-ui'
import ncformStdComps from '@ncform/ncform-theme-elementui'
import locale from 'element-ui/lib/locale/lang/zh-CN' // lang i18n

import 'font-awesome/css/font-awesome.min.css';
import '@/styles/index.scss' // global css
import './mixin';

import App from './App'
import store from './vuex';
import { constantRouter } from './routes';

import '@/icons' // icon

// set ElementUI lang to ZH
Vue.use(ElementUI, { locale })
Vue.use(VueRouter);

Vue.config.productionTip = false


let routes = _.cloneDeep(constantRouter);
const router = new VueRouter({
    routes
});
let constantRoutes = {};
_.each(constantRouter, router => {
    constantRoutes[router.path] = ['index'];
    if (router.children && router.children.length > 0) {
        _.each(router.children, child => {
            constantRoutes[child.path] = ["index"];
        });
    }
});

router.beforeEach(async (to, from, next) => {
    // console.log("beforeEach ", to.path);
    // 设置用户登录IP
    let userIP = store.state.user.userIP;
    if (!userIP) {
        store.dispatch('set_user_ip');
    }
    let userinfo = store.state.user.userinfo || {};
    let account = userinfo.account;
    if (!account && to.path !== '/login') {
        next('/login');
    } else {
        // 验证权限
        // login页面不做检查,其他页面统一进行权限检查
        // 解决刷新页面时获取权限失败问题,使用持久化的进行验证
        // 使用userinfo.routes存在的问题是没有默认权限页面,因此附加常量权限
        await router.app.$store.dispatch('set_routes', { account })  //初始化permission router
        let permissionRoutes = store.state.permission.permissionRoutes || userinfo.routes || {};
        // console.log("permissionRoutes init = ", permissionRoutes);
        if (!constantRoutes[to.path] && !permissionRoutes[to.path] && to.path !== "/login") {
            ElementUI.MessageBox.alert('您没有权限访问此页面！', '访问错误', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                if (!store.state.user.userinfo.account) {
                    next('/login');
                } else {
                    // 停留在当前页面
                    next(from.path);
                }
            });
        } else {
            // console.log("state isLoadRoutes", store.state.permission.isLoadRoutes);
            next();
            // 更新权限路由
            if (!store.state.permission.isLoadRoutes || store.state.permission.addRoutes.length === 0) {
                store.dispatch("set_routes", {
                    account
                }).then(() => {
                    store.dispatch('generate_routes').then(() => {
                        // console.log("addRoutes=", store.state.permission.addRoutes);
                        router.addRoutes(store.state.permission.addRoutes);
                        for (let route of store.state.permission.addRoutes) {
                            // console.log("let me see the children ", route.children);
                            router.options.routes.push(route);
                        }
                    });
                });
            }
        }
    }
});


new Vue({
    el: '#app',
    router,
    store,
    render: h => h(App)
})
