# learn_flask
学习flask的项目
我在根据[The Flask Mega Tutorial](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh)学习flask编程，这个仓库用来存放学习过程中的项目代码。

notes:

1. 导入插件方法
    见[app模块的init文件](./app/__init__.py)
1. 配置文件
    1. 通过[config.py](./config.py)来配置
    1. 通过`app.config.from_object(Config)`导入
1. 数据库相关
    1. 使用flask_sqlalchemy和flask_migrate
    1. 通过[model文件](./app/models.py)进行数据建模（domain层）
    1. 建模修改后通过以下命令进行数据库迁移：
    ```bash
    flask db migrate -m "some desc"
    flask db upgrade
    ```
    1. ?(不确定)关于数据库的使用，在[model文件](./app/models.py)和[routes文件](./app/routes.py)中都有示例。注意，修改有两种：
        1. 对于当前用户，直接对current_user（使用flask_login）进行操作后，`db.session.cimmit()`即可原因：加载current_user的时候已经做了add操作
        1. 对于其他对象，需要先执行`db.session.add(Obj)`操作，再执行`db.session.commit()`

logs:

1. Feb.23 完成主页、数据库User和Posts模型(ch.1~4)
2. Feb.24 完善数据库，完成登陆(ch.4~5)
3. Feb.25 完成注册、个人主页(ch.5~6)