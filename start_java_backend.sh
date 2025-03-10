#!/bin/bash
cd /home/m/resume_revision/backend_of_java_for_save
# 设置变量
APP_JAR="target/resume-service-1.0.0.jar"
CONFIG_PATH="file:///home/m/resume_revision/backend_of_java_for_save/src/main/resourses/application.properties"

# 检查JAR文件是否存在
if [ ! -f "$APP_JAR" ]; then
    echo "构建应用程序..."
    mvn clean package
fi

# 检查MySQL是否运行
if ! systemctl is-active --quiet mysql; then
    echo "启动MySQL服务..."
    sudo service mysql start
fi

# 启动应用
echo "正在启动简历后端服务..."
java -jar $APP_JAR --spring.config.location=$CONFIG_PATH 