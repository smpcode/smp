<template>
  <div class="app-container">
    <section>
      <!--工具条-->
      <el-col :span="24" class="toolbar" style="padding-bottom: 0px;" v-loading="colLoading">
        <el-form :inline="true">
          <el-form-item>
            <el-input :disabled="true" v-model="roleName"></el-input>
          </el-form-item>

          <el-select
            v-model="addUsers"
            multiple
            filterable
            remote
            placeholder="添加用户"
            :remote-method="getOptionUsers"
            :loading="queryLoading"
          >
            <el-option
              v-for="item in optionUsers"
              :key="item.account"
              :label="item.realname"
              :value="item.id"
            ></el-option>
          </el-select>

          <el-button
            class="filter-item"
            style="margin-left: 10px;"
            @click="handleCreate"
            type="primary"
            icon="edit"
          >添加</el-button>
        </el-form>
      </el-col>

      <!--表格-->
      <el-table :data="objects" highlight-current-row style="width: 100%;" v-loading="listLoading">
        <el-table-column prop="id" label="#" width="90">
          <template scope="scope">
            <span>{{scope.row.id}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="250">
          <template scope="scope">
            <span>{{scope.row.role.role}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色描述" width="250">
          <template scope="scope">
            <span>{{scope.row.role.name}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="account" label="账户" width="250">
          <template scope="scope">
            <span>{{scope.row.user.account}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="realname" label="姓名" min-width="250">
          <template scope="scope">
            <span>{{scope.row.user.realname}}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="150">
          <template scope="scope">
            <el-button type="danger" icon="delete" size="small" @click="handleDelete(scope.row)"></el-button>
          </template>
        </el-table-column>
      </el-table>

      <!--分页显示-->
      <div v-show="!listLoading" class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page.sync="listQuery.page"
          :page-sizes="[10,20,30,50,100]"
          :page-size="listQuery.limit"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          style="float:right;"
        ></el-pagination>
      </div>
    </section>
  </div>
</template>

<script>
import {
  getResourceListPage,
  addRoleUsers,
  deleteResource
} from "../../api/archapi";
import CryptoJS from "crypto-js";

export default {
  data() {
    return {
      roleId: "",
      roleName: "",
      addUsers: [],
      optionUsers: [],
      listQuery: {
        page: 1,
        limit: 20,
        sort: "+id"
      },
      queryLoading: false,
      colLoading: false,
      listLoading: true,
      objects: [],
      total: null
    };
  },
  mounted() {
    this.roleId = this.$route.query.role_id;
    this.roleName = this.$route.query.role_name;
    this.getList();
  },
  methods: {
    getList() {
      this.listLoading = true;
      let param = {
        role__eq: this.roleId,
        limit: this.listQuery.limit,
        page: this.listQuery.page,
        ordering: this.listQuery.sort
      };
      getResourceListPage("archapi", "user_role", param)
        .then(res => {
          this.objects = res.data.objects;
          this.total = res.data.meta.total;
          this.listLoading = false;
        })
        .catch(err => {
          console.log(err.toString());
          this.objects = [];
          this.total = 0;
          this.listLoading = false;
        });
    },
    getOptionUsers(query) {
      if (query !== "") {
        this.queryLoading = true;
        // 如果输入为中文自动匹配realname，否则匹配account
        let regChinese = new RegExp("[\\u4E00-\\u9FFF]+", "g");
        let param = {};
        if (regChinese.test(query)) {
          param.realname__like = "%" + query + "%";
        } else {
          param.account__like = "%" + query + "%";
        }
        getResourceListPage("archapi", "user", param)
          .then(res => {
            this.optionUsers = res.data.objects;
            this.queryLoading = false;
          })
          .catch(err => {
            console.log(err.toString());
            this.optionUsers = [];
            this.queryLoading = false;
          });
      }
    },
    handleCreate() {
      console.log("addUsers=", this.addUsers);
      this.colLoading = true;
      addRoleUsers(this.roleId, this.addUsers)
        .then(res => {
          this.getList();
          this.colLoading = false;
          this.$notify({
            title: "成功",
            message: "添加成功",
            type: "success",
            duration: 2000
          });
        })
        .catch(err => {
          this.colLoading = false;
          console.log("addRoleUsers failed, error=", err.toString());
          this.$notify({
            title: "失败",
            message: "添加失败, " + err.toString(),
            type: "error",
            duration: 2000
          });
        });
    },
    handleDelete(row) {
      console.log("handleDelete:", row.id, row.account);
      let param = {
        pk: row.id
      };
      deleteResource("archapi", "user_role", param)
        .then(res => {
          // 页面上删除
          const index = this.objects.indexOf(row);
          this.objects.splice(index, 1);
          this.$notify({
            title: "成功",
            message: "删除成功",
            type: "success",
            duration: 2000
          });
        })
        .catch(err => {
          console.log("deleteResource failed, error=", err.toString());
          this.$notify({
            title: "失败",
            message: "删除失败",
            type: "error",
            duration: 2000
          });
        });
    },
    // 处理页码变更事件，参数为页码数
    handleSizeChange(size) {
      this.listQuery.limit = size;
      this.getList();
    },
    handleCurrentChange(currentPage) {
      this.listQuery.page = currentPage;
      this.getList();
    }
  }
};
</script>
