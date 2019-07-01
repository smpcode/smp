export default {
    path: '/404',
    name: 'notfound',
    component: () => import('@/views/404'),
    hidden: true,
    meta: {
        title: "404"
    }
};
