from flask_sqlalchemy  import SQLAlchemy

# app.py

from flask import Flask, render_template, request, jsonify

# Initialize the Flask application
app = Flask(__name__)
    
app.config['SECRET_KEY'] = "dinuchakedi"

# sqlite config
# app.config['SQLALCHEMY_DATABASE_URI'] = 'localhost:5432'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/test_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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




@app.route('/area_position')
def index():

    """
    initialize drop down menus
    """

    class_entry_relations = get_dropdown_values()

    default_classes = sorted(class_entry_relations.keys())
    default_values = class_entry_relations[default_classes[0]]

    return render_template('index.html',
                       all_classes=default_classes,
                       all_entries=default_values)


if __name__ == '__main__':

    app.run(debug=True)
