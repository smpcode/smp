import * as types from './mutations_types';

import {
	store,
    utils
} from '../../common/';

module.exports = {
	[types.UPDATE_USERINFO](state, user_db) {
		state.userinfo = user_db.userinfo || {};
		store.set('userinfo', state.userinfo);
	},

	[types.SET_AVATAR](state, avatar) {
		state.avatar = avatar
	},

	[types.REMOVE_USERINFO](state) {
		store.remove('userinfo');
		state.userinfo = {};
	},

    [types.SET_USER_IP](state) {
        utils.getUserIP((ip) => {
            state.userIP = ip;
            store.set('user_ip', state.userIP);
            // console.log("set state userIP", ip);
        });
    },

	[types.UPDATE_REMMMBER](state, user_db) {
		state.remember.remember_flag = user_db.remember_flag;
		state.remember.remember_login_info = user_db.remember_login_info;

		store.set('remember_flag', state.remember.remember_flag);
		store.set('remember_login_info', state.remember.remember_login_info);
	},


	[types.REMOVE_REMEMBER](state) {
		store.remove('remember_flag');
		store.remove('remember_login_info');

		state.remember.remember_flag = false;
		state.remember.remember_login_info = {
			username: '',
			token: ''
		};
	},
};
