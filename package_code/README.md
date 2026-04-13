# 项目使用说明

## 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 5+

## 后端依赖安装与运行
1) 进入后端目录：
```bash
cd backend
```
2) 创建并激活虚拟环境：
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```
3) 安装依赖：
```bash
pip install -r requirements.txt
```
4) 配置数据库连接（任选其一）：
- 方式A：编辑 `backend/.env`，确保 `MYSQL_URL` 正确
- 方式B：设置环境变量 `MYSQL_URL`

示例：
```
MYSQL_URL=mysql+pymysql://root:你的密码@127.0.0.1:3306/learning_path?charset=utf8mb4
```

5) 初始化数据库：
```bash
# 创建数据库
mysql -uroot -p你的密码 -e "CREATE DATABASE IF NOT EXISTS learning_path DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
# 导入表结构（PowerShell）
Get-Content schema.sql | mysql -uroot -p你的密码 learning_path
# 写入种子数据
python seed.py
```

6) 启动后端：
```bash
python run.py
```
默认接口地址：`http://127.0.0.1:5000/api`

## 前端依赖安装与运行
1) 进入前端目录：
```bash
cd frontend
```
2) 安装依赖：
```bash
npm install
```
3) 启动开发服务器：
```bash
npm run dev
```
默认访问地址：`http://127.0.0.1:5173`

## 生产部署
- 后端：使用 `python run.py` 或由你们的进程管理工具托管（如 Windows 服务或进程守护）。
- 前端：
```bash
npm run build
```
将 `frontend/dist` 部署到静态服务器即可。

## 默认账号（种子数据）
- 学生：student / student123
- 教师：teacher / teacher123
- 管理员：admin / admin123
