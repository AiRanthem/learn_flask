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
    7. 分页查询：
    ``` python
    user.followed_posts.paginate(page, limit, error_process)
    ```
    第三个参数为True，找不到时会返回404；否则返回空列表。
    paginate返回的是Pagination对象，有五个比较重要的属性：
    * items：查询到的对象列表
    * has_next：有后续页面为真
    * has_prev：有前置页面为真
    * next_num：后续页码
    * prev_num：前置页码
    8. 

4. 单元测试：通过unittest包。参看示例[test.py](./app/test.py)
5. 发送邮件
    使用flask_mail插件。导入见__init__，发送邮件的代码如下：
    ``` python
    from flask_mail import Message
    from app import mail
    msg = Message('test subject', sender=app.config['ADMINS'][0],
    recipients=['your-email@example.com'])
    msg.body = 'text body'
    msg.html = '<h1>HTML body</h1>'
    mail.send(msg)

    ```
6. JWT：```import jwt```
    1. 生成JWT:
        ``` python
        token = jwt.encode({'a': 'b'}, # claim
        'my-secret',# secret key
        algorithm='HS256')
        ```
7. 渲染模板
    * render_template可以生成任何字符串内容，甚至用于发送邮件
    * url_for的参数 *_external* 设置为True则可以生成绝对路径。否则是相对路径 
8. 异步处理。示例：
    ``` python
    from threading import Thread
    # ...

    def send_async_email(app, msg):
        with app.app_context():
            mail.send(msg)

    def send_email(subject, sender, recipients, text_body, html_body):
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        Thread(target=send_async_email, args=(app, msg)).start()
    ```
    新的线程不共享上下文，需要传递app对象

logs:

1. Feb.23 完成主页、数据库User和Posts模型(ch.1~4)
2. Feb.24 完善数据库，完成登陆(ch.4~5)
3. Feb.25 完成注册、个人主页、错误处理和日志(ch.5~7)
4. Feb.26 完成关注，添加单元测试(ch.8)
5. Feb.27 完成分页显示(ch.9)
6. Feb.28 完成邮件支持，JWT，异步发送邮件(ch.10)