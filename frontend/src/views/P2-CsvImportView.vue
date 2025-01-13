<template>
	<div>
		<h2>文件导入</h2>
		<!-- 文件选择和显示区域 -->
		<div class="file-upload-container">
			<input
				type="file"
				accept=".csv"
				@change="handleFileChange"
				ref="fileInput"
				class="file-input"
			/>
			<div class="file-name" v-if="fileName">{{ fileName }}</div>
			<button @click="uploadFile" class="upload-btn">上传</button>
			<button @click="resetPage" class="refresh-btn">刷新</button>

		</div>

		<!-- 上传状态显示区域 -->
		<div v-if="uploadStatus.length" class="status-box">
			<div v-for="(status, index) in uploadStatus" :key="index" class="status-message" v-html="status"></div>
		</div>

		<!-- 显示进度条和上传状态 -->
		<div v-if="isUploading" class="upload-progress">
			<p>正在上传...</p>
			<progress :value="uploadProgress" max="100"></progress>
		</div>

		<!-- 时空数据库列表 -->
		<div class="database-list-container">
			<h3>现有时空数据库</h3>
			<ul>
				<li v-for="(db, index) in timeDatabases" :key="index">{{ db }}</li>
			</ul>
			<!-- 加载失败的提示 -->
			<div v-if="loadDatabasesError" class="error-message">
				加载时空数据库失败，请重试。
			</div>
		</div>
	</div>
</template>

<script>
	export default {
		name: "CsvImportView",
		data() {
			return {
				file: null, // 存储文件对象
				fileName: "", // 存储文件名
				uploadStatus: [], // 上传状态信息
				timeDatabases: [], // 存储时空数据库列表
				uploadProgress: 0, // 上传进度
				isUploading: false, // 是否正在上传
				loadDatabasesError: false, // 是否加载时空数据库失败
				backendUrl: process.env.VUE_APP_BACKEND_URL, // 载入后端地址
			};
		},
		methods: {
			// 选择文件时触发的函数
			handleFileChange(event) {
				const file = event.target.files[0];
				if (file && file.type === "text/csv") {
					this.file = file;
					this.fileName = file.name; // 更新文件名显示
				} else {
					alert("请选择一个有效的CSV文件");
					this.file = null;
					this.fileName = "";
				}
			},

			// 重置页面
			resetPage() {
				this.file = null; // 清空文件
				this.fileName = ""; // 清空文件名
				this.uploadStatus = []; // 清空上传状态
				this.timeDatabases = []; // 清空数据库列表
				this.$refs.fileInput.value = ""; // 清空文件选择框
			},

			// 上传文件至后端
			async uploadFile() {
				console.log("当前选择的文件:", this.file);
				if (!this.file) {
					alert("请先选择一个文件");
					return;
				}

				const formData = new FormData();
				formData.append("file", this.file);

				try {
					this.isUploading = true; // 开始上传
					// 发送上传请求到后端
					const response = await this.$axios.post(`${this.backendUrl}/api/upload_csv`, formData, {
						headers: {
							"Content-Type": "multipart/form-data",
						},
						onUploadProgress: (progressEvent) => {
							this.uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
						},
					});
					console.log("Upload successful:", response.data);

					// 处理上传后的响应
					if (response.data.code === 0) {
						const currentTime = new Date().toLocaleString();
						this.uploadStatus.push(`<span style="font-weight: bold; color: blue;">[${currentTime}]</span> 文件上传成功`);
					} else {
						const currentTime = new Date().toLocaleString();
						this.uploadStatus.push(`<span style="font-weight: bold; color: blue;">[${currentTime}]</span> 文件上传失败，原因：${response.data.message}`);
					}
				} catch (error) {
					console.error("上传文件时出错:", error);
					const currentTime = new Date().toLocaleString();
					this.uploadStatus.push(`<span style="font-weight: bold; color: blue;">[${currentTime}]</span> 上传文件时出错，请重试`);
				} finally {
					this.isUploading = false; // 上传完成
				}
			},

		// 加载时空数据库列表（从数据库查询表格）
		async loadDatabases() {
			try {
				const response = await this.$axios.get("/api/get_databases");
				if (response.data.code === 0) {
					this.timeDatabases = response.data.databases;
					this.loadDatabasesError = false; // 如果加载成功，重置错误标志
					} else {
					this.loadDatabasesError = true; // 加载失败
					}
				} catch (error) {
					console.error("加载时空数据库失败:", error);
					this.loadDatabasesError = true; // 加载失败
				}
			},
		},

		mounted() {
			this.loadDatabases(); // 页面加载时获取时空数据库列表
		},
	};
</script>

<style scoped>
	.file-upload-container {
		display: flex;
		align-items: center; /* 垂直居中对齐 */
		justify-content: flex-start; /* 将所有内容对齐到右边 */
		margin: 20px 0;
		padding: 20px;
		border: 1px solid #ddd;
		background-color: #f9f9f9;
	}

	.file-name {
		margin-top: 10px;
		font-size: 14px;
		color: #666;
	}

	.file-choose-btn {
		margin-right: 20px; /* 让文件选择按钮和上传按钮有间隔 */
		padding: 10px 20px;
		background-color: #4caf50;
		color: white;
		border: none;
		cursor: pointer;
		white-space: nowrap;
	}

	.file-choose-btn:hover {
		background-color: #45a049;
	}

	.upload-btn,
	.refresh-btn {
		padding: 10px 20px;
		border: none;
		cursor: pointer;
		white-space: nowrap;
		margin-left: 10px; /* 设置按钮之间的间隔 */
	}

	.upload-btn {
		background-color: #4caf50;
		color: white;
	}

	.upload-btn:hover {
		background-color: #45a049;
	}

	.refresh-btn {
		background-color: #f44336;
		color: white;
	}

	.refresh-btn:hover {
		background-color: #e53935;
	}

	.status-box {
		margin-top: 20px;
		padding: 10px;
		border: 1px solid #ddd;
		background-color: #f1f1f1;
	}
	.status-message {
		margin-bottom: 10px;
		font-size: 14px;
		color: #333;
	}

	.upload-progress {
		margin-top: 20px;
		padding: 10px;
		border: 1px solid #ddd;
		background-color: #f9f9f9;
	}

	.upload-progress p {
		font-size: 16px;
		color: #333;
	}

	progress {
		width: 100%;
		height: 20px;
	}

	.database-list-container {
		margin-top: 20px;
		padding: 20px;
		border: 1px solid #ddd;
		background-color: #f9f9f9;
	}
	.database-list-container h3 {
		margin-bottom: 15px;
	}
	.database-list-container ul {
		list-style-type: none;
		padding-left: 0;
	}
	.database-list-container li {
		padding: 5px;
		font-size: 14px;
		color: #333;
		border-bottom: 1px solid #ddd;
	}
</style>
