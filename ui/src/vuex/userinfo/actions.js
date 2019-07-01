import * as types from './mutations_types';

module.exports = {
	update_userinfo: ({
		commit
	}, {
		userinfo
	}) => {
		return new Promise((resolve, reject) => {
			commit(types.UPDATE_USERINFO, {
				userinfo
			});
			resolve();
		});
	},

	remove_userinfo: ({
		commit
	}) => {
		return new Promise((resolve, reject) => {
			commit(types.REMOVE_USERINFO);
			resolve();
		});
	},

    set_user_ip: ({
		commit
	}) => {
		return new Promise((resolve, reject) => {
			commit(types.SET_USER_IP);
			resolve();
		});
	},

	set_avatar: ({
		commit
	}) => {
		return new Promise((resole, reject) => {
			commit(types.SET_AVATAR);
			resolve();
		})
	},

	update_remember: ({
		commit
	}, {
		remember_flag,
		remember_login_info
	}) => {
		return new Promise((resolve, reject) => {
			commit(types.UPDATE_REMEMBER, {
				remember_flag,
				remember_login_info
			});
			resolve();
		});
	},

	remove_remember: ({
		commit
	}) => {
		return new Promise((resolve, reject) => {
			commit(types.REMOVE_REMEMBER);
			resolve();
		});
	}
};
