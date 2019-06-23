/**
 * set button permission
 * @param store vuex对象,对应this.$store
 * @param route 每个页面的route对象，对应this.$route
 */
module.exports = {
    hasPermission(operation) {
        try {
            return this.$store.state.permission.permissionRoutes[this.$route.path].indexOf(operation) !== -1;
        } catch (err) {
            console.log("hasPermission check failed, err=", err.toString(),
                        ", path=", this.$route.path,
                        ", operation=", operation);
            return false;
        }
    }
};
