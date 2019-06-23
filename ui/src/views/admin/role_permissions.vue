<template>
  <div class="app-container">
    <div class="form" v-loading="formLoading">
      <el-form
        style="margin:20px;width:60%;min-width:600px;"
        label-width="100px"
        :model="data"
        ref="user_data"
      >
        <el-form-item class="edit-form" label="角色">
          <el-input :disabled="true" v-model="roleName"></el-input>
        </el-form-item>

        <el-form-item class="edit-form" label="筛选">
          <el-input placeholder="基于路由查找" v-model="filterText"></el-input>
        </el-form-item>

        <el-form-item class="edit-form" label="页面">
          <el-tree
            class="filter-tree"
            show-checkbox
            node-key="path"
            :data="datas.pageRouters"
            :props="props.pageRouters"
            ref="pageRouters"
            @node-click="handleNodeClick"
            @check-change="checkChange"
            :check-strictly="true"
            :default-checked-keys="datas.defaultCheckedKeys"
            :filter-node-method="filterNode"
          ></el-tree>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="setRolePermissions">设置权限</el-button>
        </el-form-item>
      </el-form>

      <!--按钮粒度权限管理-->
      <el-dialog :title="metaPermissionName" :visible.sync="dialogFormVisible">
        <el-checkbox-group v-model="metaPermissionsCheckList">
          <el-checkbox v-for="mp in metaPermissions" :label="mp.key" :key="mp.name">{{ mp.name }}</el-checkbox>
        </el-checkbox-group>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialogFormVisible = false">取 消</el-button>
          <el-button type="primary" @click="handleMetaPermission">确 定</el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import _ from "lodash";
import { asyncRouter } from "../../routes";
import { updatePermissionRoutes, getRolePermissions } from "../../api/archapi";

export default {
  name: "role_permissions",
  watch: {
    filterText(val) {
      this.$refs.pageRouters.filter(val);
    }
  },
  data() {
    return {
      formLoading: false,
      dialogFormVisible: false,
      metaPermissionName: "按钮权限控制",
      metaPermissions: {},
      metaPermissionsCheckList: [],
      metaPermissionsPath: "",
      roleId: "",
      roleName: "",
      filterText: "",
      checkeds: {
        addPageRouters: {},
        deletePageRouters: {}
      },
      props: {
        pageRouters: {
          children: "children",
          label: function(data, node) {
            return data.meta.title || data.name;
          }
        }
      },
      datas: {
        pageRouters: [],
        defaultCheckedKeys: []
      },
      data: {
        checkedPageRouters: "",
        checkedMetaRouterPermissions: {}
      }
    };
  },
  methods: {
    // 更新权限规则
    setRolePermissions() {
      // console.log("addPageRouters=", this.checkeds.addPageRouters);
      // console.log("deletePageRouters=", this.checkeds.deletePageRouters);
      this.formLoading = true;
      updatePermissionRoutes(
        this.roleId,
        this.checkeds.addPageRouters,
        this.checkeds.deletePageRouters
      )
        .then(res => {
          this.formLoading = false;
          this.$notify({
            title: "成功",
            message: "设置权限成功",
            type: "success",
            duration: 2000
          });
          let account = this.$store.state.user.userinfo.account;
          this.$store.dispatch("set_routes", { account });
        })
        .catch(err => {
          // console.log("updatePermissionRoutes failed, error=", err.toString());
          this.formLoading = false;
          this.$notify({
            title: "更新失败",
            message: "更新权限失败, " + err.toString(),
            type: "error",
            duration: 2000
          });
        });
    },
    filterNode(value, data) {
      if (!value) {
        return true;
      }
      return data.path.indexOf(value) != -1 || data.name.indexOf(value) != -1;
    },
    handleMetaPermission() {
      this.dialogFormVisible = false;
      this.$set(
        this.data.checkedMetaRouterPermissions,
        this.metaPermissionsPath,
        this.metaPermissionsCheckList
      );
      // 这里也需要设置添加和删除逻辑,选中的为添加，未选中的为删除
      // let removeMethods = _.difference(this.metaPermissions, this.metaPermissionsCheckList);
      let needDeleteKeys = [];
      _.each(this.metaPermissions, item => {
        if (_.indexOf(this.metaPermissionsCheckList, item.key) === -1) {
          needDeleteKeys.push(item.key);
        }
      });
      // console.log("button permission checkeds ", needDeleteKeys, this.metaPermissionsCheckList);
      this.$set(this.checkeds.addPageRouters, this.metaPermissionsPath, {
        name: this.metaPermissionName,
        methods: this.metaPermissionsCheckList
      });
      this.$set(this.checkeds.deletePageRouters, this.metaPermissionsPath, {
        name: this.metaPermissionName,
        methods: needDeleteKeys
      });
    },
    /**
     * 改变选项时触发
     * @param data  当前改变的对象
     * @param selfIsChecked 当前是否选中
     * @param childHasChecked 子元素是否被选中
     */
    checkChange(data, selfIsChecked, childHasChecked) {
      // console.log("checkChange data=", data, ",selfIsChecked=", selfIsChecked, ",childHasChecked=", childHasChecked);
      // 当前节点被选中时
      if (selfIsChecked === true) {
        this.$set(this.checkeds.addPageRouters, data.path, {
          name: data.name,
          methods: this.data.checkedMetaRouterPermissions[data.path] || [
            "index"
          ]
        });
        this.$delete(this.checkeds.deletePageRouters, data.path);
      } else {
        // 当前节点未被选中，但是子节点被选中
        if (childHasChecked === true) {
          this.$set(this.checkeds.addPageRouters, data.path, {
            name: data.name,
            methods: ["index"]
          });
          this.$delete(this.checkeds.deletePageRouters, data.path);
        } else {
          // 取消选中
          this.$set(this.checkeds.deletePageRouters, data.path, {
            name: data.name,
            methods: this.data.checkedMetaRouterPermissions[data.path] || [
              "index"
            ]
          });
          this.$delete(this.checkeds.addPageRouters, data.path);
        }
      }
    },
    handleNodeClick(data) {
      let checkedKeys = this.$refs.pageRouters.getCheckedKeys();
      // console.log("handleNodeClick: ", data);
      if (
        checkedKeys.indexOf(data.path) !== -1 &&
        _.has(data, "meta") &&
        _.has(data.meta, "operation")
      ) {
        this.metaPermissions = data.meta.operation;
        this.metaPermissionsPath = data.path;
        this.metaPermissionName = data.meta.title + " - 按钮权限控制";
        this.metaPermissionsCheckList = this.data.checkedMetaRouterPermissions[
          data.path
        ] || ["index"];
        this.dialogFormVisible = true;
      }
    },
    initPermissions(roleId) {
      this.datas.defaultCheckedKeys = [];
      this.data.checkedMetaRouterPermissions = {};
      let rolePermissionRoutes = this.$store.state.permission
        .rolePermissionRoutes;
      // console.log("rolePermissionRoutes=", rolePermissionRoutes);
      _.forEach(rolePermissionRoutes, (operations, path) => {
        this.datas.defaultCheckedKeys.push(path);
        this.$set(this.data.checkedMetaRouterPermissions, path, operations);
      });
    }
  },
  mounted() {
    this.roleId = this.$route.query.role_id;
    this.roleName = this.$route.query.role_name;
    this.datas.pageRouters = asyncRouter;
    this.initPermissions(this.roleId);
  }
};
</script>

<style>
</style>
