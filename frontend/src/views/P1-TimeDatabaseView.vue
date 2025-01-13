<template>
    <div class="time-database-view">
    <h2>时间数据库管理</h2>

    <!-- 上方方框，显示所有数据库名称 -->
    <div class="database-list">
        <h3>选择时空数据库</h3>
        <div class="database-container">
        <div
            v-for="(db, index) in databases"
            :key="index"
            class="database-item"
            :class="{'selected': selectedDatabase === db.name}"
            @click="selectDatabase(db.name)"
        >
            {{ db.name }}
        </div>
        </div>
    </div>

    <!-- 下方大方框，显示所选数据库信息 -->
    <div v-if="selectedDatabase" class="database-info">
        <h3>数据库信息：{{ selectedDatabase }}</h3>
        <table v-if="databaseInfo && databaseInfo.length > 0">
        <thead>
            <tr>
            <th>字段名</th>
            <th>值</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(row, index) in databaseInfo" :key="index">
            <td>{{ row.field }}</td>
            <td>{{ row.value }}</td>
            </tr>
        </tbody>
        </table>
        <p v-else>没有数据可展示。</p>
    </div>
    </div>
</template>

<script>
export default {
    name: 'TimeDatabaseView',
    data() {
        return {
        // 模拟的数据库列表，实际数据需要从后端获取
            databases: [],
            selectedDatabase: null,
            databaseInfo: null, // 用来存储所选数据库的数据
        };
    },
    mounted() {
    // 组件加载时，获取数据库列表
        this.fetchDatabases();
    },
    methods: {
    // 获取时空数据库列表
        async fetchDatabases() {
            try {
                const response = await this.$http.get('/api/databases'); // 假设后端提供该API
                this.databases = response.data; // 假设返回的格式是 [{ name: "数据库1" }, { name: "数据库2" }]
            } catch (error) {
                console.error("获取数据库列表失败", error);
            }
    },

    // 选择一个数据库
    async selectDatabase(databaseName) {
        this.selectedDatabase = databaseName;
        this.fetchDatabaseInfo(databaseName);
    },

    // 获取所选数据库的数据
    async fetchDatabaseInfo(databaseName) {
        try {
        const response = await this.$http.get(`/api/database/${databaseName}/info`); // 假设后端提供该API
        this.databaseInfo = response.data; // 假设返回的格式是 [{ field: "字段1", value: "值1" }, ...]
        } catch (error) {
        console.error("获取数据库信息失败", error);
        }
    },
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
}

.database-container {
    display: flex;
    flex-wrap: wrap;
}

.database-item {
    border: 1px solid #ccc;
    padding: 10px;
    margin: 5px;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s;
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

table th, table td {
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
</style>
