# 本地运行

## 安装依赖

```shell
pipenv install
```

## 安装卸载依赖

使用兼容pip

```shell
pipenv install [依赖名]
pipenv uninstall [依赖名]
```

## 进入虚拟环境

```txt
IDEA中选择 .venv/Scripts/python.exe 解释器
```

## 注意事项

```txt
本地启动，需要将此改成自己的redis地址
app.config['REDIS_URL'] = os.environ.get('REDIS_URL')
```

## 启动
以调试模式启动应用，并且在修改代码时可以自动重启服务器，只需刷新应用即可
```shell
flask --app spider run --debug
```

# 服务器部署
## docker 部署方式
### docker启动脚本
```shell
#! /bin/sh
#接收外部参数
service_name=[填服务名]
tag=main
open_port=[开放与容器外的端口号]
container_port=[服务启动的端口号]
env=REDIS_URL=[redis链接地址]
disk="-v /etc/localtime:/etc/localtime"

imageName=[镜像地址]
echo "准备部署的镜像地址=$imageName"

#查询容器是否存在，存在则删除
containerId=`docker ps -a | grep -w ${service_name}:${tag}  | awk '{print $1}'`
if [ "$containerId" !=  "" ] ; then
    #停掉容器
    docker stop $containerId

    #删除容器
    docker rm $containerId
	
	echo "成功删除容器"
fi

#查询镜像是否存在，存在则删除
imageId=`docker images | grep -w $service_name  | awk '{print $3}'`
if [ "$imageId" !=  "" ] ; then      
  # 删除镜像
  #docker rmi -f $imageId
  # 更新镜像
  docker pull $imageName
  echo "成功更新镜像"
fi

# 启动容器
echo "docker run -e $env $disk --name $service_name --net catguild -di -p $open_port:$container_port $imageName"
docker run -e $env $disk --name $service_name --net catguild -di -p $open_port:$container_port $imageName
echo "容器启动成功"
```

### 部署出错，显示进一步的错误信息

使用参数`--preload`

```dockerfile
CMD ["pipenv", "run", "gunicorn", "-c", "gunicorn.conf.py", "run:app", "--preload"]
```
