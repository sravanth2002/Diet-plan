from flask import Flask, render_template, request
import http.client
import json
import re
# from db_config import connect_db

app = Flask(__name__)
app.secret_key = 'your_secret_key'

rapidapi_key = 'c96095ab6fmsh8aef27ede081c79p16bc1djsn06537ad6130c'

nameF=""
emailF=""
ageF=0
genderF=""
hfF=0
hiF=0
weightF=0
nicotine_symptomsF=""
medical_conditionsF=""


@app.route('/')
def main():
    return render_template('main.html', response='')


@app.route('/nameEmail', methods=['GET', 'POST'])
def nameEmail():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        global nameF, emailF
        nameF = name
        emailF = email
        print(nameF,emailF)
        return render_template('nameEmail.html', name=name, email=email)
    else:
        return render_template('nameEmail.html')


@app.route('/one')
def one():
    if request.method == 'POST':
        age = request.form['age']
        gender = request.form['gender']
        hf = request.form['height-feet']
        hi = request.form['height-inches']
        weight= request.form['weight']
        nicotine_symptoms=request.form['nicotine-symptoms']
        medical_conditions=request.form['medical-conditions']


        global ageF, genderF, hfF, hiF , weightF, nicotine_symptomsF, medical_conditionsF
        ageF = age
        genderF = gender
        hfF = hf
        hiF= hi
        weightF= weight
        nicotine_symptomsF= nicotine_symptoms
        medical_conditionsF= medical_conditions
        return render_template('one.html', age=age, gender=gender, hf=hf, hi=hi, weight=weight, nicotine_symptoms= nicotine_symptoms, medical_conditions= medical_conditions)
    else:
        return render_template('one.html')

@app.route('/two',methods = ['GET','POST'])
def two():
    return render_template('two.html')


## three vars
diff_to_eatF = ""
appetite_levelF = ""
appeal_when_app_lowF = ""
fuller_fasterF = ""
times_app_lowF = ""


@app.route('/three',methods = ['GET','POST'])
def three():
    if request.method == 'POST':
        diff_to_eat = request.form['diff-to-eat']
        appetite_level = request.form['appetite-level']
        appeal_when_app_low = request.form['appeal-when-app-low']
        fuller_faster = request.form['fuller-faster']
        times_app_low = request.form['times-app-low']

        global diff_to_eatF, appetite_levelF, appeal_when_app_lowF, fuller_fasterF, times_app_lowF

        diff_to_eatF = diff_to_eat
        appetite_levelF = appetite_level
        appeal_when_app_lowF = appeal_when_app_low
        fuller_fasterF = fuller_faster
        times_app_lowF = times_app_low
        
    return render_template('three.html')
print(diff_to_eatF)

@app.route('/four')
def four():
    return render_template('four.html')


@app.route('/five')
def five():
    return render_template('five.html')

@app.route('/six')
def six():
    return render_template('six.html')

@app.route('/result')
def result():
    return render_template('result.html')



@app.route('/get_diet_plan', methods=['POST'])
def get_diet_plan():
    email = request.form['email']
    age = request.form['age']
    goals = request.form['goals']
    dietary_restrictions = request.form['dietary_restrictions']

    prompt = f"Give me a weekly diet plan for a {age}-year-old with goals to {goals}. Dietary preferences include {dietary_restrictions}."

    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    })

    conn = http.client.HTTPSConnection("chat-gpt26.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': "chat-gpt26.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    try:
        conn.request("POST", "/", payload, headers)
        res = conn.getresponse()
        data = res.read()
        response_data = json.loads(data.decode("utf-8"))

        diet_plan_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No diet plan found.")

        # Split the diet plan text by days using regular expression
        day_blocks = re.split(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', diet_plan_text)
        
        diet_plan = []
        current_day = None
        current_meals = {}

        # Process each block to structure the diet plan
        for block in day_blocks:
            block = block.strip()
            if block in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                if current_day:
                    diet_plan.append({"day": current_day, "meals": current_meals})
                current_day = block
                current_meals = {}
            elif current_day and block:
                # Remove any leading colon from the block if it exists
                if block.startswith(":"):
                    block = block[1:].strip()
                
                meal_lines = block.splitlines()
                for line in meal_lines:
                    if ":" in line:
                        meal, desc = line.split(":", 1)
                        current_meals[meal.strip()] = desc.strip()

        if current_day:
            diet_plan.append({"day": current_day, "meals": current_meals})

        diet_plan_str = json.dumps(diet_plan)

        # Store diet plan in the database
        db = connect_db()
        if db:
            cursor = db.cursor()
            cursor.execute("REPLACE INTO plans (email, plan) VALUES (%s, %s)", (email, diet_plan_str))
            db.commit()
            cursor.close()
            db.close()

    except Exception as e:
        diet_plan = f"Error fetching diet plan: {e}"

    return render_template('exb.html', response=diet_plan)

@app.route('/get_existing_diet_plan', methods=['POST'])
def get_existing_diet_plan():
    email_existing = request.form['email_existing']

    previous_diet_plan = None
    try:
        # Connect to the database and fetch the existing diet plan
        db = connect_db()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT plan FROM plans WHERE email = %s", (email_existing,))
            result = cursor.fetchone()

            if result:
                # Parse the stored JSON diet plan
                stored_plan = result[0]

                # Convert the JSON string back to a Python object (list of dictionaries)
                diet_plan_data = json.loads(stored_plan)

                # Send the structured data to the template
                return render_template('exb.html', previous_diet_plan=diet_plan_data)

            cursor.close()
            db.close()

    except Exception as e:
        previous_diet_plan = f"Error retrieving diet plan: {e}"

    return render_template('exb.html', previous_diet_plan=previous_diet_plan)




if __name__ == '__main__':
    app.run(debug=True)