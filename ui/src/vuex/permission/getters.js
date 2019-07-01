module.exports = {
	getPermissionRoutes(state) {
		return state.permission && state.permission.routes ? state.permission.routes : {};
	},
};
