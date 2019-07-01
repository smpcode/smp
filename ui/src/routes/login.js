export default {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index'),
    hidden: true,
    meta: {
        title: "登录"
    }
};