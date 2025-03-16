#!/bin/bash

# 获取当前远程仓库URL
CURRENT_URL=$(git remote get-url origin)
echo "当前远程仓库URL: $CURRENT_URL"

# 检查是否是HTTPS URL
if [[ $CURRENT_URL == https://github.com/* ]]; then
    # 提取用户名和仓库名
    REPO_PATH=${CURRENT_URL#https://github.com/}
    REPO_PATH=${REPO_PATH%.git}
    
    # 构建SSH URL
    SSH_URL="git@github.com:$REPO_PATH.git"
    
    # 更新远程仓库URL
    git remote set-url origin $SSH_URL
    echo "远程仓库URL已更新为: $SSH_URL"
    echo "注意: 确保你已经设置了SSH密钥并添加到GitHub账户中"
    echo "如果尚未设置SSH密钥，请执行以下步骤:"
    echo "1. 生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email@example.com\""
    echo "2. 启动ssh-agent: eval \"\$(ssh-agent -s)\""
    echo "3. 添加SSH密钥: ssh-add ~/.ssh/id_ed25519"
    echo "4. 复制公钥: cat ~/.ssh/id_ed25519.pub"
    echo "5. 将公钥添加到GitHub账户: https://github.com/settings/keys"
else
    echo "当前远程仓库URL不是HTTPS格式，无需转换"
fi 