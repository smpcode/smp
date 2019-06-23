import login from './login';
import notfound from './notfound';
import home from './home';
import admin from './admin';

// 所有的routes必须在error的前面
export const constantRouter = [
  login,
  home,
  notfound,
];

export const asyncRouter = [
  admin,
];

export default constantRouter;
