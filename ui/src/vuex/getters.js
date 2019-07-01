const getters = {
    sidebar: state => state.app.sidebar,
    device: state => state.app.device,
    avatar: state => state.user.avatar,
    name: state => state.user.name,
    roles: state => state.user.roles,
    permission_routes: state => state.permission.routes,
    errorLogs: state => state.errorLog.logs
  }
  export default getters