import * as api from './api';
import _ from "lodash";

const apiPrefix = "smp";

// 登录接口
export const doLogin = params => {
    return api.doPost(`${apiPrefix}/account/login`, params).then(res => res);
};

// 修改密码接口
export const doUpdatePassword = params => {
    return api.doPost(`${apiPrefix}/account/password`, params).then(res => res);
};

// 创建资源
export const createResource = (db, table, params) => {
    let postData = {
        data: JSON.stringify(params)
    };
    return api.doPost(`${apiPrefix}/resource/${db}/${table}`, postData)
        .then(res => res);
};

// 获取资源详情
export const getResourceDetail = (db, table, params) => {
    return api.doGet(`${apiPrefix}/resource/${db}/${table}`, params)
        .then(res => res);
};

// 获取分页资源
export const getResourceListPage = (db, table, params) => {
    return api.doGet(`${apiPrefix}/resource/${db}/${table}`, params)
        .then(res => res);
};

// 更新资源
export const updateResource = (db, table, params) => {
    let putData = {
        data: JSON.stringify(params)
    };
    return api.doPut(`${apiPrefix}/resource/${db}/${table}`, putData)
        .then(res => res);
};

// 删除资源
export const deleteResource = (db, table, params) => {
    // console.log(db, table, params);
    return api.doDelete(`${apiPrefix}/resource/${db}/${table}`, params)
        .then(res => res);
};

// 更新资源&权限
export const updatePermissionRoutes = (roleId, addPageRouters, deletePageRouters) => {
    let params = {
        'role_id': roleId,
        'add_routes': JSON.stringify(addPageRouters),
        'delete_routes': JSON.stringify(deletePageRouters)
    };
    // console.log("updatePermissionRoutes params=", params);
    return api.doPost(`${apiPrefix}/rbac/acls`, params).then(res => res);
};

export const getPermissionRoutes = (account) => {
    let params = {
        account: account
    };
    return api.doGet(`${apiPrefix}/rbac/acls`, params).then(res => res);
};

// 更新角色对应的用户列表
export const addRoleUsers = (roleId, userIds) => {
    let params = {
        'role_id': roleId,
        'user_ids': JSON.stringify(userIds)
    };
    return api.doPost(`${apiPrefix}/rbac/user/role`, params).then(res => res);
};

// 获取部门列表信息
export const getDeptNodes = () => {
    return api.doGet(`${apiPrefix}/dept/nodes`).then(res => res);
};

// 获取按钮权限列表
export const getButtonPermissions = (account, path) => {
    let params = {
        account: account,
        resource: path,
    };
    return api.doGet(`${apiPrefix}/rbac/user/resource`, params).then(res => res);
};

// 获取角色权限列表
export const getRolePermissions = (roleId) => {
    let params = {
        role_id: roleId,
    };
    return api.doGet(`${apiPrefix}/rbac/role/resource`, params).then(res => res);
};


// 更新数据字典表
export const updateDictData = (parent, children) => {
    let params = {
        parent: parent,
        children: JSON.stringify(children),
    };
    return api.doPost(`${apiPrefix}/dict`, params).then(res => res);
};

// 获取角色对应的研发组列表
export const getRoleGroups = params => {
    return api.doGet(`${apiPrefix}/kv`, params);
};
