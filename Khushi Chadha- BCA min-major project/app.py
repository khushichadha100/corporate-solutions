from flask import Flask , session, redirect, render_template, request, url_for , jsonify
from werkzeug.security import generate_password_hash, check_password_hash 
from pymongo import MongoClient 
import pickle
import pandas as pd
import numpy as np 


app = Flask(__name__)
app.secret_key = "khushi_c" 
 
#models/modules called:-
# Load the model for performance prediction
with open(r'C:\Users\lenovo 2020\OneDrive\Desktop\Khushi Chadha- BCA min-major project\models\emp_performance.pkl', 'rb') as f:
    emp_performance = pickle.load(f)

# Load the scaler used for standardization
with open(r'C:\Users\lenovo 2020\OneDrive\Desktop\Khushi Chadha- BCA min-major project\models\scaler.pkl', 'rb') as f:
    scaler1 = pickle.load(f)

# Load the saved model for sentiment analysis and TF-IDF vectorizer
model_filename = r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\sentiment_analysis_model.pkl'
tfidf_filename = r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\tfidf_sentiment.pkl'

with open(model_filename, 'rb') as f:
    sentiment_model = pickle.load(f)

with open(tfidf_filename, 'rb') as f:
    tfidf_vectorizer = pickle.load(f)

# Paths for marketing_campaign
svm_model_filename = r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\market_campaign.pkl'
scaler_filename = r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\campaign_scaler.pkl'

# Load model & scaler
with open(svm_model_filename, 'rb') as model_file:
    svm_model = pickle.load(model_file)
with open(scaler_filename, 'rb') as scaler_file:
    sc = pickle.load(scaler_file)

# Load model and scaler for customer segmentation
model_path = r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\cust_segmen_model.pkl'
scaler_path = r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\cust_segmen_scaler.pkl'

with open(model_path, 'rb') as f:
    model = pickle.load(f)

with open(scaler_path, 'rb') as f:
    scaler = pickle.load(f)

# Load the customer churn model
with open(r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\customer_churn_model.pkl', 'rb') as f:
    churn_model = pickle.load(f)

# Load the encoder
with open(r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\churn_encoder.pkl', 'rb') as f:
    churn_encoder = pickle.load(f)

# Load the model for emp attrition prediction
import pickle

# Load the Employee Attrition model
with open(r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\emp_attrition.pkl', 'rb') as f:
    emp_attrition_model = pickle.load(f)

# Load the scaler
with open(r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\emp_att_scaler.pkl', 'rb') as f:
    emp_attrition_scaler = pickle.load(f)

# Load the trained model for fraud payment detection
model_path = r'C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\fraud_detection_model.pkl'
with open(model_path, 'rb') as f:
    fraud_model = pickle.load(f)

#sales forecasting
with open('C:\\Users\\lenovo 2020\\OneDrive\\Desktop\\Khushi Chadha- BCA min-major project\\models\\sales_forecasting.pkl', 'rb') as f:
    model_pipeline = pickle.load(f)

# MongoDB Setup (connecting to local MongoDB instance)
client = MongoClient('mongodb://localhost:27017/')
db = client['corporate_solutions_db']  # Database name
users_collection = db['users']
scheduled_demos = db['scheduled_demos']
'''
peer_sentiment_collection = db['peer_sentiment_analysis']  # Collection name for Peer Sentiment
employee_performance_collection = db['employee_performance']  # Collection name for Employee Performance
strategy_recommendation_collection = db['strategy_recommendation']  # Collection for Strategy Recommendation
'''
# Home page route
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/get-started")
def get_started():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# Static Page Routes
@app.route('/services')
def services():
    return render_template('services.html')

@app.route("/demo")
def demo():
    if "username" in session:
        return redirect(url_for("dashboard", username=session["username"]))
    else:
        session["from_schedule_demo"] = True  # mark where user came from
        return redirect(url_for("register"))

# Route to render the form
@app.route('/schedule_demo', methods=['GET', 'POST'])
def schedule_demo():
    confirmation_message = ""  # Initialize confirmation message as empty
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        email = request.form['email']
        organization = request.form['organization']
        contact_number = request.form['contact_number']
        message = request.form.get('message', '')  # Optional message field

        # Process the data, save it to a database or print it (as a placeholder)
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Organization: {organization}")
        print(f"Contact Number: {contact_number}")
        print(f"Message: {message}")

        # Set confirmation message after form submission
        confirmation_message = "Thank you! We will contact you soon."

    return render_template('schedule_demo.html', confirmation_message=confirmation_message)

# Route to render the thank you page

@app.route('/pay_now', methods=['GET', 'POST'])
def pay_now():
    confirmation_message = None

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        amount = request.form['amount']
        
        # Add your payment processing logic here (e.g., payment gateway integration)
        
        confirmation_message = f"Thank you, your payment of ${amount} is received! We will contact you soon."

    return render_template('pay_now.html', confirmation_message=confirmation_message)

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    confirmation_message = ""  # Initialize confirmation message as empty
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        email = request.form['email']
        organization = request.form['organization']
        contact_number = request.form['contact_number']
        message = request.form.get('message', '')  # Optional message field

        # Process the data, save it to a database or print it (as a placeholder)
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Organization: {organization}")
        print(f"Contact Number: {contact_number}")
        print(f"Message: {message}")

        # Set confirmation message after form submission
        confirmation_message = "Thank you! We will contact you soon."

    return render_template('contact_us.html', confirmation_message=confirmation_message)

@app.route('/pricing')
def pricing():
    return render_template("pricing.html")

@app.route('/careers')
def careers():
    return render_template('careers.html')

@app.route('/free-trial', methods=['GET', 'POST'])
def free_trial():
    confirmation_message = ""  # Initialize confirmation message as empty
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        email = request.form['email']
        organization = request.form['organization']
        contact_number = request.form['contact_number']
        message = request.form.get('message', '')  # Optional message field

        # Process the data, save it to a database or print it (as a placeholder)
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Organization: {organization}")
        print(f"Contact Number: {contact_number}")
        print(f"Message: {message}")

        # Set confirmation message after form submission
        confirmation_message = "Thank you! Your Free Trial will be started soon !"

    return render_template('free-trial.html', confirmation_message=confirmation_message)

# Feature Pages
@app.route('/customer-segmentation', methods=['GET', 'POST'])
def customer_segmentation():
    prediction = None
    interpretation = ""
    family_size = " "
    age = " "
    children =" " 
    income = " "
    spent = " "
    is_parent = " "
    if request.method == 'POST':
        # Retrieve input values from the form
        family_size = float(request.form['family_size'])
        age = float(request.form['age'])
        children = float(request.form['children'])
        income = float(request.form['income'])
        spent = float(request.form['spent'])
        is_parent = float(request.form['is_parent'])

        # Prepare the input data
        input_data = np.array([[family_size, age, children, income, spent, is_parent]])

        # Scale the input data
        scaled_input_data = scaler.transform(input_data)

        # Make prediction
        prediction = model.predict(scaled_input_data)[0]

        # Interpretation for each cluster
        cluster_interpretation = {
            0: "The majority of these people are parents<br>At max have 3 members in the family<br>They majorly have one kid and typically not teenagers<br>Relatively younger<br>",
            1: "Definitely a parent<br>At max have 4 members in the family and at least 2<br>Most have a teenager in the home<br>Single parents are a subset of this group<br>Relatively older<br>",
            2: "Definitely not a parent<br>At max are only 2 members in the family.<br>A slight majority of couples over single people<br>Span all ages<br>High income and high spending<br>",
            3: "Definitely a parent<br>At max have 5 members in the family and at least 2<br>Majority of them have a teenager at home<br>Relatively older"
        }
        
        # Assign the interpretation based on the predicted cluster
        interpretation = cluster_interpretation.get(prediction, "Cluster interpretation not available.")

    return render_template('customer-segmentation.html', prediction=prediction, interpretation=interpretation,
                           family_size=family_size, age=age, children=children, income=income, spent=spent, is_parent=is_parent)


@app.route('/fraud-paym', methods=['GET', 'POST'])
def fraud_paym():
    prediction = None
    amount = ''
    oldbalanceOrg = ''
    
    if request.method == 'POST':
        amount = request.form['amount']
        oldbalanceOrg = request.form['oldbalanceOrg']

        # Convert to float for model
        input_data = np.array([[float(amount), float(oldbalanceOrg)]])

        # Make prediction
        result = fraud_model.predict(input_data)[0]
        prediction = "Yes, Fraud Detected" if result == 1 else "No, Not Fraudulent"

    return render_template('fraud-paym.html', prediction=prediction, amount=amount, oldbalanceOrg=oldbalanceOrg)

@app.route("/employee_performance", methods=["GET", "POST"])
def employee_performance():
    performance_prediction = None

    # Default values to retain inputs in form
    empenvironment = emplastsalary = empworklife = experience = currentrole = lastpromotion = currmanager = None

    if request.method == 'POST':
        empenvironment = int(request.form['empenvironment'])
        emplastsalary = int(request.form['emplastsalary'])
        empworklife = int(request.form['empworklife'])
        experience = int(request.form['experience'])
        currentrole = int(request.form['currentrole'])
        lastpromotion = int(request.form['lastpromotion'])
        currmanager = int(request.form['currmanager'])


        # Prepare input for prediction
        input_features = np.array([[empenvironment, emplastsalary,
                                    empworklife, experience, currentrole, lastpromotion, currmanager]])

        # Scale input
        scaled_input = scaler1.transform(input_features)

        # Predict
        performance_prediction = emp_performance.predict(scaled_input)[0]

    return render_template("employee_performance.html",
                           performance_prediction=performance_prediction,
                           empenvironment=empenvironment,
                           emplastsalary=emplastsalary,
                           empworklife=empworklife,
                           experience=experience,
                           currentrole=currentrole,
                           lastpromotion=lastpromotion,
                           currmanager=currmanager)




@app.route('/sales-forecast', methods=["GET", "POST"])
def sales_forecast():
    prediction = None
    category = None
    sub_category = None
    
    if request.method == "POST":
        # Get the user input from the form
        category = request.form['category']
        sub_category = request.form['sub_category']
        
        # Prepare the input data in a format expected by the model (as a DataFrame)
        input_data = pd.DataFrame({
            "Category": [category],
            "Sub-Category": [sub_category]
        })
        
        # Make prediction using the loaded model pipeline
        prediction_log = model_pipeline.predict(input_data)
        
        # Apply the inverse log transformation to get the original Sales value
        prediction = round(np.expm1(prediction_log[0]), 2)  # Inverse of log1p transformation
        
    return render_template("sales-forecast.html", prediction=prediction, category=category, sub_category=sub_category)

@app.route('/employee_attrition', methods=['GET', 'POST'])
def employee_attrition():
    attrition_prediction = None

    # Form defaults
    form_data = {
        'empenvironment': '',
        'emplastsalary': '',
        'empworklife': '',
        'experience': '',
        'currentrole': '',
        'lastpromotion': '',
        'currmanager': ''
    }

    if request.method == 'POST':
        try:
            # Fetch values from form
            for field in form_data:
                form_data[field] = request.form.get(field)

            # Convert inputs to float
            input_features = [
                float(form_data['empenvironment']),
                float(form_data['emplastsalary']),
                float(form_data['empworklife']),
                float(form_data['experience']),
                float(form_data['currentrole']),
                float(form_data['lastpromotion']),
                float(form_data['currmanager'])
            ]

            # Scale and predict
            scaled_input = emp_attrition_scaler.transform([input_features])
            attrition_prediction = emp_attrition_model.predict(scaled_input)[0]

        except Exception as e:
            print("Error in attrition prediction:", e)
            attrition_prediction = "Error"

    return render_template(
        'emp_attrition.html',
        attrition_prediction=attrition_prediction,
        **form_data
    )


@app.route("/sentiment_analysis", methods=["GET", "POST"])
def sentiment_analysis():
    sentiment_result = None
    text_input = ""  
    
    if request.method == "POST":
        text_input = request.form["text_input"]  # Get input text from the form
        
        # Transform the user input using the TF-IDF vectorizer
        input_vector = tfidf_vectorizer.transform([text_input])
        
        # Predict sentiment using the loaded model
        sentiment_prediction = sentiment_model.predict(input_vector)
        
        # Map numeric predictions back to sentiment labels
        sentiment_label = {0: "Negative", 1: "Neutral", 2: "Positive"}
        sentiment_result = sentiment_label.get(sentiment_prediction[0])

    return render_template("sentiment_analysis.html", sentiment_result=sentiment_result, text_input=text_input)

fields = ['Dependents', 'tenure', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'Contract', 'TotalCharges']

@app.route('/customer_churn', methods=['GET', 'POST'])
def customer_churn():
    prediction = None
    form_data = {field: '' for field in fields}  # Initialize form data dictionary with empty values

    if request.method == 'POST':
        # Populate form_data with the POST data
        for field in fields:
            form_data[field] = request.form.get(field, '')

        try:
            # Encode form data using churn_encoder
            encoded_data = [
                churn_encoder.transform([form_data['Dependents']])[0] if form_data['Dependents'] else 0,
                float(form_data['tenure']),
                churn_encoder.transform([form_data['OnlineSecurity']])[0] if form_data['OnlineSecurity'] else 0,
                churn_encoder.transform([form_data['OnlineBackup']])[0] if form_data['OnlineBackup'] else 0,
                churn_encoder.transform([form_data['DeviceProtection']])[0] if form_data['DeviceProtection'] else 0,
                churn_encoder.transform([form_data['TechSupport']])[0] if form_data['TechSupport'] else 0,
                churn_encoder.transform([form_data['Contract']])[0] if form_data['Contract'] else 0,
                float(form_data['TotalCharges']) if form_data['TotalCharges'] else 0.0
            ]

            # Make the prediction
            model_prediction = churn_model.predict([encoded_data])[0]

            # Map model's output (0 or 1) to 'No' or 'Yes'
            prediction = "Yes" if model_prediction == 1 else "No"

        except Exception as e:
            print("Prediction error:", e)
            prediction = "Error in prediction. Please check inputs."

    return render_template('customer_churn.html', prediction=prediction, form_data=form_data)

@app.route('/marketing_campaign', methods=['GET', 'POST'])
def marketing_campaign():
    prediction = None
    total_accepted = ''
    total_spent = ''
    num_catalog_purchases = ''

    if request.method == 'POST':
        total_accepted = request.form['total_accepted']
        total_spent = request.form['total_spent']
        num_catalog_purchases = request.form['num_catalog_purchases']

        input_data = np.array([[float(total_accepted), float(total_spent), float(num_catalog_purchases)]])
        input_scaled = sc.transform(input_data)
        raw_prediction = svm_model.predict(input_scaled)[0]
        prediction = 'Yes' if raw_prediction == 1 else 'No'

    return render_template('marketing_campaign.html',
                           prediction=prediction,
                           total_accepted=total_accepted,
                           total_spent=total_spent,
                           num_catalog_purchases=num_catalog_purchases)


#dynamic routing pages
# Dashboard page route 
@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect(url_for('register'))

    username = session['username']
    user_data = db['users'].find_one({"username": username})
    
    if user_data:
        designation = user_data.get('designation', 'Not specified')
        return render_template("dashboard.html", user=user_data, designation=designation)
    else:
        return redirect(url_for('register'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        designation = request.form.get("designation")
        
        user = users_collection.find_one({"username": username})
        if user:
            if check_password_hash(user["password"], password):
                session["username"] = username
                session["designation"] = user.get("designation", "Not specified")  # store designation
                # Check where user came from
                if session.get("from_schedule_demo"):
                    session.pop("from_schedule_demo")
                return redirect(url_for("dashboard"))
            else:
                message = "INVALID DETAILS !"
                return render_template("register.html",message=message)
        else:
            hashed_password = generate_password_hash(password)
            users_collection.insert_one({
                "username": username,
                "password": hashed_password,
                "designation": designation
            })
            session["username"] = username
            session["designation"] = designation  # store designation
            if session.get("from_schedule_demo"):
                session.pop("from_schedule_demo")
            return redirect(url_for("dashboard"))
    
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)

