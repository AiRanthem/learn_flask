# learn_flask
学习flask的项目
我在根据[The Flask Mega Tutorial](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh)学习flask编程，这个仓库用来存放学习过程中的项目代码。

notes:

1. 导入插件方法
    见[app模块的init文件](./app/__init__.py)
2. 配置文件
    1. 通过[config.py](./config.py)来配置
    2. 通过`app.config.from_object(Config)`导入
3. 数据库相关
    ### 很多复杂的数据库操作在第七章中找到例子
    1. 使用flask_sqlalchemy和flask_migrate
    2. 通过[model文件](./app/models.py)进行数据建模（domain层）
    3. 建模修改后通过以下命令进行数据库迁移：
    ```bash
    flask db migrate -m "some desc"
    flask db upgrade
    ```
    4. ?(不确定)关于数据库的使用，在[model文件](./app/models.py)和[routes文件](./app/routes.py)中都有示例。注意，修改有两种：
        1. 对于当前用户，直接对current_user（使用flask_login）进行操作后，`db.session.cimmit()`即可原因：加载current_user的时候已经做了add操作
        1. 对于其他对象，需要先执行`db.session.add(Obj)`操作，再执行`db.session.commit()`
    5. 关于表单的验证：在表单类中定义一个 validate_<field_name>(self, field)的函数即可自动实现验证（传入的是表单项，不是它的data）
    6. 关系 relationship的使用，示例：
    **注意：正反关系的lazy都要设置，只有设置lazy为‘dynamic’才能把关系对象当作一个列表来使用！**
    ``` python
    # 对应关系：左表 - 关联表 - 右表
    # 在这里的关系是 左 关注 右
    followed = db.relationship( # 左表就是自己
        'User', # 右表名
        secondary = followers, # 关联表对象
        primaryjoin = (followers.c.follower_id == id), #关联表关联到左侧实体的条件
        secondaryjoin = (followers.c.followed_id == id), #关联表关联到右侧实体的条件
        lazy = 'dynamic',
        backref = db.backref('followers', lazy='dynamic')
    )
    ```
    在这之中，可以将关系属性作为一个列表，通过列表操作来进行关系的增加和删除
    ``` python
    user1.followed.append(user2)
    user1.followed.remove(user2)
    ```
    关系的查询示例：
    ``` python
    # 这里的过滤：左侧是自己User，右侧是传入的user对象
    # in class User
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    ```
    联表查询示例：
    ``` python
    # 联表查询，获得post表中，user_id是自己关注的user的id的post记录
    def followed_posts(self):
        followed = Post.query.join(followers,(followers.c.followed_id == Post.user_id)) \
                         .filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    ```
4. 单元测试：通过unittest包。参看示例[test.py](./app/test.py)


logs:

1. Feb.23 完成主页、数据库User和Posts模型(ch.1~4)
2. Feb.24 完善数据库，完成登陆(ch.4~5)
3. Feb.25 完成注册、个人主页、错误处理和日志(ch.5~7)
4. Feb.26 完成关注，添加单元测试(ch.8)