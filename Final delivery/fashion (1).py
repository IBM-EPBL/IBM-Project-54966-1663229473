from main import*
from flask  import Flask,request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
from werkzeug.utils import secure_filename
from base64 import b64encode, b64decode
import jinja2
import os
import ibm_db_sa
import ibm_db
import ibm_db_dbi


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" +os.path.join(basedir,'fashion.db')#app.config['SQLALCHEMY_DATABASE_URI'] = 'ibm_db_sa://zjy42473:cTQbTOHYiNA8jIpN@98538591-7217-4024-b027-8baa776ffad1.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud:30875/BLUDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Register(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    dob =db.Column(db.Integer,nullable = False)
    phone = db.Column(db.Integer, nullable = False)
    email =db.Column(db.String(50), nullable = False, unique = True)
    password = db.Column(db.Integer, nullable = False, unique = True)
    date_joined = db.Column(db.Date,default = datetime.utcnow)

    def __repr__(self):
        return f"<User : {self.email}>"

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    password = db.Column(db.Integer, nullable = False, unique = True)

    def __repr__(self):
        return f"<User : {self.name}>"
class imgg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.Text, nullable=False)
    img_name = db.Column(db.Text, nullable=False)
    img_type = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(50), nullable = False)
    price = db.Column(db.String(50), nullable=False)
    offers = db.Column(db.String(50), nullable=False)
    offer_price = db.Column(db.String(50), nullable=False)
    date_joined = db.Column(db.Date, default=datetime.utcnow)

    def __repr__(self):
        return f"<User : {self.image}>"

with app.app_context():

    db.create_all()

@app.route('/')
def home():

    posts = imgg.query.order_by(imgg.date_joined).all()

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    encode = jinja_env.filters['b64encode'] = b64encode
    decode = jinja_env.filters['b64decode'] = b64decode

    return render_template('index_main.html', posts=posts, encode = encode, decode = decode)

@app.route('/search', methods =['GET','POST'])
def search():
    if request.method=='POST':
        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
        encode = jinja_env.filters['b64encode'] = b64encode
        decode = jinja_env.filters['b64decode'] = b64decode
        tag = request.form['tag']
        query = imgg.query.filter(imgg.name.like("%"+tag+"%")).all()

        return render_template('search.html', posts=query, encode=encode, decode=decode)

@app.route('/reg_page')
def reg_page():
    return render_template("reg_page.html")

@app.route('/sign_page')
def sign_page():
    return render_template("sign_in.html")
@app.route('/sign_page/admin_page')
def admin_page():
    
    posts = imgg.query.order_by(imgg.date_joined).all()

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    encode = jinja_env.filters['b64encode'] = b64encode
    decode = jinja_env.filters['b64decode'] = b64decode

    return render_template('admin.html', posts=posts, encode = encode, decode = decode)

    # return render_template("admin.html")

@app.route('/upload')
def upload():
    return render_template("upload.html")



@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        dob = request.form.get('date')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        avail = bool(Register.query.filter_by(email = email).first())
        avail1 = bool(Register.query.filter_by(password=password).first())
        if avail:
            return render_template('reg_page.html', result = "email already exist")
        elif avail1:
            return render_template('reg_page.html', result = "password already exist")
        else:

            query = Register(name = name, dob = dob, phone = phone, email = email, password = password)
            db.session.add(query)
            db.session.commit()
            return redirect("/sign_page")
    else:
        return redirect("/")

@app.route('/signin',methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        name_v = request.form.get('name')
        password_v = request.form.get('password')
        login = Register.query.filter_by(name = name_v, password = password_v).first()
        # query = Admin(name='',password= "Jeffick")
        # db.session.add(query)
        # db.session.commit()
        admin = Admin.query.filter_by(name = name_v, password = password_v).first()
        if login  is not None:
            return redirect('/sign_page/main_page')
        elif admin is not None:
            return redirect('/sign_page/admin_page')
            #pass
        else:
            return render_template('admin.html', login_data="make sure u entr the coorrect pasword")

@app.route('/sign_page/main_page')
def main_page():
    posts = imgg.query.order_by(imgg.date_joined).all()

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    encode = jinja_env.filters['b64encode'] = b64encode
    decode = jinja_env.filters['b64decode'] = b64decode

    return render_template('main_page.html', posts=posts, encode=encode, decode=decode)



@app.route('/img',methods=['GET','POST'])
def image():
    if request.method == 'POST':
        pic = request.files['img']
        name = request.form['p_name']
        price = request.form['price']
        offer = request.form['offer']
        offerprice = request.form['offer_price']
        if not pic:
            return  render_template("upload.html" ,value ="no files upload")
        filename = secure_filename(pic.filename)
        mimetyype = pic.mimetype
        query = imgg(image = pic.read(),img_type =mimetyype, img_name=filename, name = name, price=price, offers = offer, offer_price=offerprice)
        db.session.add(query)
        db.session.commit()
        return render_template( "upload.html" ,value= "sucessfully uploaded")

@app.route('/updateform',methods = ['GET','POST'])
def updateform():
    if request.method == 'POST':
        id = request.form['id']
        updateform = imgg.query.filter_by(id=id).first()
        print(updateform.name)
        return render_template('update.html',datas = updateform)

@app.route('/update',methods = ['GET','POST'])
def updatedata():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['p_name']
        price = request.form['price']
        offer = request.form['offer']
        offerprice = request.form['offer_price']

        imgg.query.filter_by(id = id).update(dict( name = name, price=price, offers = offer, offer_price=offerprice))
        db.session.commit()
        return redirect('/sign_page/admin_page')

@app.route('/deleteform',methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        id = request.form.get('id')
        deleted = imgg.query.get(id)
        db.session.delete(deleted)
        db.session.commit()
        return redirect('/sign_page/admin_page')


@app.route('/customer_data')
def customerdata():
    data = Register.query.order_by(Register.date_joined).all()
    return render_template("customer_data.html", customer = data)

@app.route('/delete_customer',methods =['GET','POST'])
def deletecustomer():
    if request.method == 'POST':
        id = request.form.get('id')
        deleted = Register.query.get(id)
        db.session.delete(deleted)
        db.session.commit()
        return redirect('/customer_data')


if __name__ == '__main__':
    app.run(debug=True)
