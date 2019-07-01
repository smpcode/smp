module.exports = {
	getUserinfo(state) {
		return state.userinfo;
	},

    getUserIP(state) {
        return state.userIP;
    },

	getRouets(state) {
		return state.userinfo && state.userinfo.routes ? state.userinfo.routes : {};
	},

	getRemember(state){
		return state.remember;
	}
};
