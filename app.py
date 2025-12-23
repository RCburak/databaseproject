import os
from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    project_data = {
        "Domain": request.form.get('domain'),
        "Primary Entity Focus": request.form.get('primary_entity'),
        "Constraint/Rule": request.form.get('constraints'),
        "Advanced Feature / Trigger": request.form.get('advanced'),
        "Security / Access Control": request.form.get('security'),
        "Reporting Requirement": request.form.get('reporting'),
        "Common Tasks": request.form.get('tasks')
    }

    try:
        # BÖLÜM 1: Stage 2 & 3 (İş Kuralları ve Tablo Tanımları)
        p1 = f"Project: {project_data}. Provide Stage 2 (Business Rules Table) and Stage 3 (Table Definitions with PK/FK). Output ONLY Bootstrap HTML tables. No conversational text."
        res1 = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": p1}])
        part1 = res1.choices[0].message.content

        # BÖLÜM 2: Stage 4 (Eksik Kural Analizi)
        p_missing = f"Analyze for Stage 4: Missing or ambiguous rules for {project_data}. Output ONLY a Bootstrap table: Missing Rule, Related BR, Solution/Question."
        res_m = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": p_missing}])
        missing_rules = res_m.choices[0].message.content

        # BÖLÜM 3: Stage 5, 6 & 7 (Normalizasyon, ER ve SQL)
        p2 = f"""For {project_data}: 
        1. STAGE 5 - Normalization: 0NF to 3NF tables. 
        2. STAGE 6 - ER Diagram: Provide ONLY: <pre class='mermaid'>erDiagram [code]</pre>. 
        3. STAGE 7 - SQL: CREATE, TRIGGER, VIEW, ROLE, 3 SELECTs. 
        Output ONLY HTML tables and <pre> tags. No prose."""
        res2 = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": p2}])
        part2 = res2.choices[0].message.content

        # Markdown temizliği
        part1 = part1.replace("```html", "").replace("```", "")
        part2 = part2.replace("```html", "").replace("```", "")
        missing_rules = missing_rules.replace("```html", "").replace("```", "")

        return render_template('results.html', part1=part1, part2=part2, missing_rules=missing_rules)

    except Exception as e:
        return f"<div class='alert alert-danger'>Hata: {str(e)}</div>"

if __name__ == '__main__':
    app.run(debug=True)