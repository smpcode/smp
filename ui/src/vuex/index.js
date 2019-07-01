import Vue from 'vue';
import Vuex from 'vuex';
Vue.use(Vuex);

import user from './userinfo';
import permission from './permission';
import app from './app';
import tagsView from './tagsView';
import settings from './settings';
import getters from './getters'

module.exports = new Vuex.Store({
  modules: {
    user,
    permission,
    app,
    tagsView,
    settings,
  },
  getters
});
