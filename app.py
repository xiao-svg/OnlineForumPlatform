from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from config import db
import time
import config

app = Flask(__name__)

# 从对象中导入config
app.config.from_object(config)

# 登录状态保持
@app.context_processor
def login_status():
    # 从session中获取email
    email = session.get('email')
    # 如果有email信息，则证明已经登录了，我们从数据库中获取登陆者的昵称和用户类型，来返回到全局
    if email:
        try:
            cur = db.cursor()
            sql = "select nickname,type from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            if result:
                return {'email':email,'nickname':result[0] ,'user_type':result[1]}
        except Exception as e:
            raise e
    # 如果email信息不存在，则未登录，返回空
    return {}


# 主页
@app.route('/')
def index():
    return render_template('index.html')


# 注册页面
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        password_1 = request.form.get('password_1')
        password_2 = request.form.get('password_2')
        phone = request.form.get('phone')
        if not all([email,nickname,password_1,password_2,phone]):
            flash("信息填写不全，请将信息填写完整")
            return render_template('register.html')
        if password_1 != password_2:
            flash("两次密码填写不一致！")
            return render_template('register.html')
        password = generate_password_hash(password_1, method="pbkdf2:sha256", salt_length=8)
        try:
            cur = db.cursor()
            sql = "select * from UserInformation where email = '%s'"%email
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            if result is not None:
                flash("该Email已存在！")
                return render_template('register.html')
            else:
                create_time = time.strftime("%Y-%m-%d %H:%M:%S")
                sql = "insert into UserInformation(email, nickname, password, type, create_time, phone) VALUES ('%s','%s','%s','0','%s','%s')" %(email,nickname,password,create_time,phone)
                db.ping(reconnect=True)
                cur.execute(sql)
                db.commit()
                cur.close()
                return redirect(url_for('index'))
        except Exception as e:
            raise e

# 登录页面
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not all([email,password]):
            flash("请将信息填写完整！")
            return render_template('login.html')
        try:
            cur = db.cursor()
            sql = "select password from UserInformation where email = '%s'" % email
            db.ping(reconnect=True)
            cur.execute(sql)
            result = cur.fetchone()
            if result is None:
                flash("该用户不存在")
                return render_template('login.html')
            if check_password_hash(result[0],password):
                session['email'] = email
                session.permanent = True
                return redirect(url_for('index'))
            else:
                flash("密码错误！")
                return render_template('login.html')
        except Exception as e:
            raise e
# 用户注销
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for(('index')))


if __name__ == '__main__':
    app.run()
