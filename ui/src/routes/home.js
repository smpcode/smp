import Layout from '@/layout'

export default {
    path: '/',
    name: '主界面',
    redirect: '/home/dashboard',
    component: Layout,
    children: [{
        path: '/home/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index'),
        meta: { title: '首页', icon: 'dashboard' }
    }]
};
