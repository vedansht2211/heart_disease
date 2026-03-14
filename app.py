from flask import Flask, render_template, request, jsonify
import pandas as pd
import json

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('Heart_new2.csv')

# Convert categorical to numerical for calculations
df['HeartDisease'] = df['HeartDisease'].map({'Yes': 1, 'No': 0})
df['Smoking'] = df['Smoking'].map({'Yes': 1, 'No': 0})
df['Sex'] = df['Sex'].map({'Male': 1, 'Female': 0})

# For risk calculation, use averages
avg_bmi = df['BMI'].mean()
avg_smoking = df['Smoking'].mean()
# Since no cholesterol or BP, use BMI and Smoking

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    # Prepare data for charts
    # Full data for filtering
    df_json = df.to_json(orient='records')
    
    # Initial data (all)
    age_hd = df.groupby(['AgeCategory', 'HeartDisease']).size().unstack().fillna(0)
    age_hd_json = age_hd.to_json()

    bmi_values = df['BMI'].tolist()
    bmi_hist_json = json.dumps(bmi_values)

    bmi_hd = df[['BMI', 'HeartDisease']].to_dict('records')
    bmi_hd_json = json.dumps(bmi_hd)

    smoking_hd = df.groupby(['Smoking', 'HeartDisease']).size().unstack().fillna(0)
    smoking_hd_json = smoking_hd.to_json()

    gender_dist = df['Sex'].value_counts()
    gender_dist_json = gender_dist.to_json()

    ph_hd = df[['PhysicalHealth', 'HeartDisease']].to_dict('records')
    ph_hd_json = json.dumps(ph_hd)

    return render_template('dashboard.html', 
                           df_json=df_json,
                           age_hd=age_hd_json,
                           bmi_hist=bmi_hist_json,
                           bmi_hd=bmi_hd_json,
                           smoking_hd=smoking_hd_json,
                           gender_dist=gender_dist_json,
                           ph_hd=ph_hd_json)

@app.route('/dataset')
def dataset():
    # Show first 100 rows
    data = df.head(100).to_html(classes='table table-striped')
    return render_template('dataset.html', data=data)

@app.route('/risk', methods=['GET', 'POST'])
def risk():
    if request.method == 'POST':
        age = request.form.get('age')
        bmi = float(request.form.get('bmi'))
        smoking = int(request.form.get('smoking'))
        # Calculate risk
        risk_score = 0
        if bmi > avg_bmi:
            risk_score += 1
        if smoking == 1:
            risk_score += 1
        # Simple: if score >=1, high risk
        if risk_score >= 1:
            risk_level = 'High Risk'
        else:
            risk_level = 'Low Risk'
        return render_template('risk.html', risk_level=risk_level)
    return render_template('risk.html')

if __name__ == '__main__':
    app.run(debug=True)