import _ from "lodash";
import * as types from './mutations_types';
import {
    constantRouter,
    asyncRouter,
    errorRouter
} from '../../routes';


function hasPermission(routes, route) {
    // console.log("check permission_routes ", route);
    if (_.has(routes, route.path)) {
        // console.log("hasPermission: ", route.path);
        return true;
    }
    return false;
}

module.exports = {
    [types.GENERATE_ROUTES](state) {
        // console.log("permission_routes=", data.permission_routes);
        // 如果有状态数据优先使用状态值
        const routes = state.permissionRoutes || {};
        if (Object.keys(routes).length) {
            let filterRouter = _.cloneDeep(asyncRouter);
            const accessRoutes = filterRouter.filter(route => {
                if (hasPermission(routes, route)) {
                    if (route.children && route.children.length > 0) {
                        route.children = route.children.filter(child => {
                            if (hasPermission(routes, child)) {
                                return child;
                            }
                            return false;
                        });
                    }
                    return route;
                }
                return false;
            });
            // console.log("do check accessRoutes=", accessRoutes);
            // console.log("do check asyncRouter=", asyncRouter);
            state.addRoutes = accessRoutes;
            state.isLoadRoutes = true;
            // console.log("hahahah constantRouter=", constantRouter);
            state.routes = _.concat(constantRouter, accessRoutes, errorRouter);
            // 避免重复添加
            state.routes = _.uniqBy(state.routes, 'path');
        }
    },
    [types.SET_ROUTES](state, { permissionRoutes }) {
        _.each(constantRouter, router => {
            permissionRoutes[router.path] = ["index"];
            if (router.children && router.children.length > 0) {
                _.each(router.children, child => {
                    permissionRoutes[child.path] = ["index"];
                });
            }
        });
        state.permissionRoutes = permissionRoutes;
        // console.log("dynamic getPermissionRoutes result=", state.permissionRoutes);
    },
    [types.SET_ROLE_ROUTES](state, { permissionRoutes }) {
        state.rolePermissionRoutes = permissionRoutes;
        // console.log("dynamic getRolePermissions result=", state.rolePermissionRoutes);
    },
    [types.REMOVE_ROUTES](state) {
        state.isLoadRoutes = false;
        state.routes = [];
        // console.log("remove_routes--------->constantRouter", constantRouter);
        state.addRoutes = [];
        state.permissionRoutes = {};
        state.rolePermissionRoutes = {};
    },
};
