import os
from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükle
load_dotenv()

app = Flask(__name__)

# API Anahtarını çevre değişkenlerinden güvenli bir şekilde al
# GitHub'a yüklerken bu kısım hata vermez çünkü anahtar kodun içinde değil
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Stage 1: Kullanıcıdan proje tanımı girdilerini al [cite: 10, 11]
    project_data = {
        "Domain": request.form.get('domain'),
        "Primary Entity Focus": request.form.get('primary_entity'),
        "Constraint/Rule": request.form.get('constraints'),
        "Advanced Feature / Trigger": request.form.get('advanced'),
        "Security / Access Control": request.form.get('security'),
        "Reporting Requirement": request.form.get('reporting'),
        "Common Tasks": request.form.get('tasks')
    }

    # Stage 2-7: Tüm süreci yöneten detaylı komut (Prompt) [cite: 32, 35]
    prompt = f"""
    You are a database design assistant. Please process the following project description:
    {project_data}

    Provide the output in HTML format using Bootstrap classes for tables. Follow these stages exactly:

    1. STAGE 2 - Extraction of Business Rules: Create a table with columns: BR-ID, Type (S, O, T, Y), Rule Statement, ER Component (E, R, A, C), Implementation Tip, and Rationale. [cite: 35, 36, 37, 38, 39, 40, 41, 42, 43]
    
    2. STAGE 3 & 4 - Table Definitions and Missing Rules: Define tables (plural English names) with attributes, data types, and constraints (PK, FK, UNIQUE, CHECK, NOT NULL). Identify any missing or ambiguous rules in a separate table. [cite: 46, 48, 49, 50, 51, 52, 53, 56, 59]
    
    3. STAGE 5 - Normalization Process: Show the transformation of tables from 0NF to 1NF, 2NF, and 3NF. Explain each step in tabular form. [cite: 61, 62, 63, 64, 65, 66]
    
    4. STAGE 7 - SQL Code Generation: Provide the following SQL code:
       - CREATE TABLE and ALTER TABLE statements. [cite: 71, 72]
       - TRIGGER, VIEW, and ROLE definitions based on Operational (O) and Authorization (Y) rules. [cite: 54, 55, 73]
       - At least three sample SELECT queries for reporting requirements. [cite: 74]
    """

    try:
        # ChatGPT API çağrısı
        response = client.chat.completions.create(
            model="gpt-4o", # En iyi analiz performansı için
            messages=[{"role": "user", "content": prompt}]
        )
        # HTML çıktısını al
        final_output = response.choices[0].message.content
        
        # Markdown işaretlerini (```html ... ```) temizle
        if "```html" in final_output:
            final_output = final_output.split("```html")[1].split("```")[0]
            
    except Exception as e:
        final_output = f"<div class='alert alert-danger'>Hata oluştu: {str(e)}</div>"

    return render_template('results.html', final_output=final_output)

if __name__ == '__main__':
    # Uygulamayı debug modunda başlat
    app.run(debug=True)