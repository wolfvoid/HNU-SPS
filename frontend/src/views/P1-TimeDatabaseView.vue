<template>
  <div class="time-database-view">
    <h2>时间数据库管理</h2>

    <!-- 上方方框，显示所有数据库名称 -->
    <div class="database-list">
      <h3>选择时空数据库</h3>
      <div class="database-container">
        <div
          v-for="(table_name, index) in timeDatabases"
          :key="index"
          class="database-item"
          :class="{'selected': selectedDatabase === table_name}"
          @click="selectDatabase(table_name)"
        >
          {{ table_name }}
        </div>
      </div>
    </div>

    <!-- 下方大方框，显示所选数据库信息 -->
    <div v-if="selectedDatabase" class="database-info">
      <h3>数据库信息：{{ selectedDatabase }}</h3>
      <div v-if="loading">加载中...</div>

<!-- 显示数据 -->
<table v-if="databaseInfo && databaseInfo.length > 0">
  <thead>
    <tr>
      <th v-for="(field, index) in fieldNames" :key="index">{{ field }}</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="(row, rowIndex) in databaseInfo" :key="rowIndex">
      <td v-for="(value, colIndex) in row" :key="colIndex">{{ value }}</td>
    </tr>
  </tbody>
</table>

<p v-else>没有数据可展示。</p>



      <!-- 分页 -->
      <div class="pagination">
        <button @click="changePage('prev')" :disabled="currentPage === 1">上一页</button>
        <span>第 {{ currentPage }} 页</span>
        <button @click="changePage('next')" :disabled="databaseInfo.length < pageSize">下一页</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "TimeDatabaseView",
  data() {
    return {
      timeDatabases: [], // 时空数据库列表
      selectedDatabase: null, // 选中的数据库名称
      fieldNames: [], // 存储字段信息
      databaseInfo: [], // 存储所选数据库的数据
      currentPage: 1, // 当前页
      pageSize: 50, // 每页显示的记录数
      loading: false, // 数据加载状态
      backendUrl: process.env.VUE_APP_BACKEND_URL, // 后端地址
    };
  },

  methods: {
    // 获取时空数据库列表
    async fetchDatabases() {
      this.loading = true;
      try {
        const response = await this.$axios.get(`${this.backendUrl}/api/get_databases`);
        if (response.data.code === 0) {
          this.timeDatabases = response.data.databases;
        } else {
          console.error("加载时空数据库失败");
        }
      } catch (error) {
        console.error("加载时空数据库失败:", error);
      } finally {
        this.loading = false;
      }
    },

    // 选择一个数据库，获取其字段信息和数据
    async selectDatabase(databaseName) {
      this.selectedDatabase = databaseName;
      await this.fetchDatabaseInfo(databaseName);
    },

    // 获取所选数据库的信息
    async fetchDatabaseInfo(databaseName) {
      this.loading = true;
      try {
        const start = (this.currentPage - 1) * this.pageSize;
        const end = this.currentPage * this.pageSize;
        const response = await this.$axios.get(
          `${this.backendUrl}/api/database/${databaseName}/info?start=${start}&end=${end}`
        );

        console.log(response.data.code)
        if (response.data.code === 0) {
          this.fieldNames = response.data.fieldNames; // 假设返回字段名
            this.databaseInfo = response.data.data; // 假设返回数据
          console.log(this.databaseInfo)
        } else {
          console.error("获取数据库信息失败");
        }
      } catch (error) {
        console.error("获取数据库信息失败", error);
      } finally {
        this.loading = false;
      }
    },

    // 分页控制
    changePage(direction) {
      if (direction === "prev" && this.currentPage > 1) {
        this.currentPage -= 1;
      } else if (direction === "next" && this.databaseInfo.length === this.pageSize) {
        this.currentPage += 1;
      }
      this.fetchDatabaseInfo(this.selectedDatabase);
    },
  },

  mounted() {
    this.fetchDatabases(); // 组件加载时获取数据库列表
  },
};
</script>

<style scoped>
.time-database-view {
  padding: 20px;
  font-family: Arial, sans-serif;
}

h2 {
  color: #2C3E50;
  font-size: 28px;
  margin-bottom: 20px;
}

.database-list {
  margin-bottom: 20px;
  width: 100%;
}

.database-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  max-height: 500px;
  overflow-y: auto;
}

.database-item {
  border: 1px solid #ccc;
  padding: 15px;
  margin: 5px;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.3s;
  background-color: #fff;
  width: calc(33.33% - 10px);
  box-sizing: border-box;
  text-align: center;
  font-size: 16px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 40px;
}

.database-item.selected {
  background-color: #87CEFA;
}

.database-info {
  margin-top: 30px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

table th,
table td {
  padding: 10px;
  border: 1px solid #ddd;
}

table th {
  background-color: #f4f4f4;
}

p {
  font-size: 16px;
  color: #555;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.pagination button {
  padding: 5px 15px;
  margin: 0 10px;
  font-size: 16px;
}

.pagination button:disabled {
  background-color: #ddd;
  cursor: not-allowed;
}
</style>
