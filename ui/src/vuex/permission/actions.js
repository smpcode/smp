import * as types from './mutations_types';
import {
    getPermissionRoutes,
    getRolePermissions
} from '../../api/archapi';


module.exports = {
    // 生成路由规则
	generate_routes: ({
		commit
	}) => {
		return new Promise((resolve, reject) => {
			commit(types.GENERATE_ROUTES);
			resolve();
		});
	},
    remove_routes: ({
		commit
	}) => {
		return new Promise((resolve, reject) => {
			commit(types.REMOVE_ROUTES);
			resolve();
		});
	},
    // 生成路由规则
    set_routes: ({
        commit
    }, {
        account
    }) => {
        return new Promise((resolve, reject) => {
            if (account) {
                getPermissionRoutes(account).then(res => {
                    let permissionRoutes = res.data;
                    commit(types.SET_ROUTES, {
                        permissionRoutes
                    });
                    resolve();
                }).catch(err => {
                    console.log("getPermissionRoutes error=", err.toString());
                    let permissionRoutes = {};
                    commit(types.SET_ROUTES, {
                        permissionRoutes
                    });
                    resolve();
                });
            } else {
                let permissionRoutes = {};
                commit(types.SET_ROUTES, {
                    permissionRoutes
                });
                resolve();
            }
        });
    },
    // 生成角色路由规则
    set_role_routes: ({
        commit
    }, {
        role
    }) => {
        return new Promise((resolve, reject) => {
            if (role) {
                getRolePermissions(role).then(res => {
                    let permissionRoutes = res.data;
                    commit(types.SET_ROLE_ROUTES, {
                        permissionRoutes
                    });
                    resolve();
                }).catch(err => {
                    console.log("getRolePermissions error=", err.toString());
                    let permissionRoutes = {};
                    commit(types.SET_ROLE_ROUTES, {
                        permissionRoutes
                    });
                    resolve();
                });
            } else {
                let permissionRoutes = {};
                commit(types.SET_ROLE_ROUTES, {
                    permissionRoutes
                });
                resolve();
            }
        });
    },
};
