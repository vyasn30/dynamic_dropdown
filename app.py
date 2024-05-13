from flask_sqlalchemy  import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'dinuchakedi'  # Change this!   
app.config['SECRET_KEY'] = "dinuchakedi"

# sqlite config
# app.config['SQLALCHEMY_DATABASE_URI'] = 'localhost:5432'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/test_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# Bind the instance to the 'app.py' Flask application
db = SQLAlchemy(app)

class States(db.Model):
    __tablename__ = 'area' 
    state_id = db.Column(db.Integer, primary_key = True)
    state_name = db.Column(db.String(250))

    def __repr__(self):
    
        return '\n state_id: {0} state_name: {1}'.format(self.state_id, self.state_name)


    def __str__(self):

        return '\n state_id: {0} state_name: {1}'.format(self.state_id, self.state_name)

class Cities(db.Model):
    __tablename__ = 'positions' 
    city_id = db.Column(db.Integer, primary_key = True)
    state_id = db.Column(db.Integer)
    city_name = db.Column(db.String(250))

    def __repr__(self):
    
        return '\n city_id: {0} state_id: {1} city_name: {2}'.format(self.city_id, self.state_id, self.city_name)


    def __str__(self):

        return '\n city_id: {0} state_id: {1} city_name: {2}'.format(self.city_id, self.state_id, self.city_name)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = Users(username=request.form['username'],
                    email=request.form['email'],
                    password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('You are now registered!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Users.query.filter_by(email=request.form['email']).first()
        if user and user.verify_password(request.form['password']):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


def get_dropdown_values():

    states = States.query.all()
    # Create an empty dictionary
    myDict = {}
    for p in states:
    
        key = p.state_name
        state_id = p.state_id

        q = Cities.query.filter_by(state_id=state_id).all()
    
        lst_c = []
        for c in q:
            lst_c.append( c.city_name )
        myDict[key] = lst_c
    
    class_entry_relations = myDict
                        
    return class_entry_relations

@app.route("/area")
def show_area():
    updated_values = get_dropdown_values()
    states = updated_values.keys()
    # Create a table with HTML
    table_html = "<table><tr><th>States</th></tr>"
    for state in states:
        table_html += f"<tr><td>{state}</td></tr>"
    table_html += "</table>"
    return table_html

@app.route("/positions")
@login_required
def show_cities():
    updated_values = get_dropdown_values()  # This should return a dict like {'State1': ['City1', 'City2'], 'State2': ['City3', 'City4']}
    
    # Start the HTML for the table
    table_html = "<table border='1'><tr><th>Cities</th></tr>"
    
    # Loop through the dictionary and add each city as a new row
    for cities in updated_values.values():
        for city in cities:
            table_html += f"<tr><td>{city}</td></tr>"
    
    table_html += "</table>"
    return table_html

@app.route('/_update_dropdown')
def update_dropdown():

    # the value of the first dropdown (selected by the user)
    selected_class = request.args.get('selected_class', type=str)

    # get values for the second dropdown
    updated_values = get_dropdown_values()[selected_class]

    # create the value sin the dropdown as a html string
    html_string_selected = ''
    for entry in updated_values:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=html_string_selected)


@app.route('/_process_data')
def process_data():
    selected_class = request.args.get('selected_class', type=str)
    selected_entry = request.args.get('selected_entry', type=str)

    # process the two selected values here and return the response; here we just create a dummy string

    return jsonify(random_text="You selected the state: {} and the city: {}.".format(selected_class, selected_entry))


@app.route("/index")
def index():
    return render_template('index.html')


@app.route('/area_position')
@login_required
def select_area_position():

    """
    initialize drop down menus
    """

    class_entry_relations = get_dropdown_values()

    default_classes = sorted(class_entry_relations.keys())
    default_values = class_entry_relations[default_classes[0]]

    return render_template('index.html',
                       all_classes=default_classes,
                       all_entries=default_values)

@app.route('/admin/add_state', methods=['GET', 'POST'])
@login_required
def add_state():
    if not current_user.is_admin:
        return 'Access Denied', 403
    if request.method == 'POST':
        state_name = request.form['state_name']
        state = States(state_name=state_name)
        db.session.add(state)
        db.session.commit()
        flash('State added successfully!')
        return redirect(url_for('add_state'))
    return render_template('add_state.html')


@app.route('/admin/add_city', methods=['GET', 'POST'])
@login_required
def add_city():
    if not current_user.is_admin:
        return 'Access Denied', 403
    if request.method == 'POST':
        city_name = request.form['city_name']
        state_id = request.form['state_id']
        city = Cities(city_name=city_name, state_id=state_id)
        db.session.add(city)
        db.session.commit()
        flash('City added successfully!')
        return redirect(url_for('add_city'))
    states = States.query.all()
    return render_template('add_city.html', states=states)


if __name__ == '__main__':

    app.run(debug=True)
