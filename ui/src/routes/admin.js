import Layout from '@/layout'

export default {
  path: '/admin',
  component: Layout,
  name: 'Admin',
  meta: {
    title: '系统管理',
    icon: 'guide'
  },
  children: [
    {
      path: '/admin/dept',
      name: 'AdminDept',
      component: () => import('@/views/admin/dept'),
      meta: { title: '部门管理' }
    },
    {
      path: '/admin/user',
      name: 'AdminUser',
      component: () => import('@/views/admin/user'),
      meta: { title: '用户管理' }
    },
    {
      path: '/admin/role',
      name: 'AdminRole',
      component: () => import('@/views/admin/role'),
      meta: {
        title: '角色管理',
        operation: {
          bCreate: {
            key: 'create',
            name: '新增',
          },
          bUpdate: {
            key: 'update',
            name: '更新',
          },
          bDelete: {
            key: 'delete',
            name: '删除',
          },
        }
      }
    },
    {
      path: '/admin/data',
      component: () => import('@/views/admin/data'),
      name: 'AdminData',
      meta: {
        title: "数据字典",
        operation: {
          bCreate: {
            key: 'create',
            name: '新增',
          },
          bUpdate: {
            key: 'update',
            name: '更新',
          },
          bDelete: {
            key: 'delete',
            name: '删除',
          },
        }
      }
    },
    {
      path: '/admin/role/permissions',
      component: () => import('@/views/admin/role_permissions'),
      name: 'AdminRolePermissions',
      hidden: true,
      meta: { title: '角色权限' }
    },
    {
      path: '/admin/role/users',
      component: () => import('@/views/admin/role_users'),
      name: 'AdminRoleUsers',
      hidden: true,
      meta: { title: '角色用户' }
    }
  ]
}
