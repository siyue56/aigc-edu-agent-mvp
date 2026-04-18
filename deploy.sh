#!/bin/bash
# 高校学习智能体 AIGC 应用 - 自动化部署脚本

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> 正在服务器 (81.71.2.37) 开始部署 aigc-edu-agent-mvp 项目...${NC}"

# 1. 检查目录权限
if [ ! -d "secrets" ]; then
  echo -e "${GREEN}>>> 初始化 secrets 目录...${NC}"
  mkdir -p secrets
fi

# 2. 检查 JWT 密钥是否存在
if [ ! -f "secrets/jwt_secret.txt" ]; then
  echo -e "${RED}>>> 未检测到 jwt_secret.txt，正在生成随机密钥...${NC}"
  openssl rand -hex 32 > secrets/jwt_secret.txt
  echo -e "${GREEN}>>> 已生成密钥: secrets/jwt_secret.txt${NC}"
fi

# 3. 更新代码
echo -e "${GREEN}>>> 正在拉取最新的 main 分支代码...${NC}"
git pull origin main

# 4. 构建并重启 Docker 容器
echo -e "${GREEN}>>> 正在停止旧容器...${NC}"
docker-compose down

echo -e "${GREEN}>>> 正在构建并启动新容器...${NC}"
docker-compose up -d --build

# 5. 检查运行状态
echo -e "${GREEN}>>> 检查服务运行状态...${NC}"
docker-compose ps

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}>>> 部署成功！${NC}"
echo -e "前端 Web 地址: http://81.71.2.37:80 (如果未使用 Nginx)"
echo -e "后端 API 地址: http://81.71.2.37:8000/docs"
echo -e "注意: 生产环境建议通过 Nginx 绑定域名并配置 HTTPS (详见部署文档)"
echo -e "${GREEN}==========================================${NC}"
