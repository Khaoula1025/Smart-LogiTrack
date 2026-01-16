from google import generativeai as genai
import json 
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def create_prompt(probability,employee):
    prompt = f"""Agis comme un expert RH expérimenté.

Voici les informations sur l’employé :
- Âge : {employee['Age']}
- Genre : {employee['Gender']}
- Situation matrimoniale : {employee['MaritalStatus']}
- Département : {employee['Department']}
- Rôle : {employee['JobRole']}
- Niveau du poste : {employee['JobLevel']}
- Domaine d’éducation : {employee['EducationField']}
- Niveau d’éducation : {employee['Education']}
- Années d’expérience totale : {employee['TotalWorkingYears']}
- Ancienneté dans l’entreprise : {employee['YearsAtCompany']}
- Années dans le poste actuel : {employee['YearsInCurrentRole']}
- Années depuis la dernière promotion : {employee['YearsSinceLastPromotion']}
- Relation avec le manager (ancienneté) : {employee['YearsWithCurrManager']}

Conditions de travail :
- Voyages professionnels : {employee['BusinessTravel']}
- Distance domicile–travail : {employee['DistanceFromHome']}
- Heures supplémentaires : {employee['OverTime']}
- Salaire mensuel : {employee['MonthlyIncome']}
- Augmentation salariale (%) : {employee['PercentSalaryHike']}
- Stock options : {employee['StockOptionLevel']}

Indicateurs RH :
- Satisfaction au travail : {employee['JobSatisfaction']}
- Satisfaction environnement de travail : {employee['EnvironmentSatisfaction']}
- Satisfaction relationnelle : {employee['RelationshipSatisfaction']}
- Implication dans le travail : {employee['JobInvolvement']}
- Équilibre vie professionnelle / personnelle : {employee['WorkLifeBalance']}
- Performance : {employee['PerformanceRating']}

Contexte :
Ce salarié présente un risque élevé de départ volontaire ("probability") selon le modèle de Machine Learning{f" ({probability:.2%})" if probability is not None else ""}.

Tâche :
Propose exactement 3 actions concrètes, personnalisées et priorisées pour retenir ce salarié.
Les actions doivent :
- Être adaptées à son rôle, son ancienneté et son niveau
- Prendre en compte la satisfaction, la performance et l’équilibre vie pro / vie perso
- Être immédiatement actionnables par un manager RH

Format attendu :
- Action 1 : …
- Action 2 : …
- Action 3 : …

Contraintes :
- Français professionnel
- Pas de généralités
- Pas de théorie RH
- Pas de markdown
"""
    return prompt

def gemini_analyse(probability, employeData):
    if probability > 0.50:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')

            response = model.generate_content(
                create_prompt(probability,employeData)
            )

            return {
                "churn_probability": probability,
                "retention_actions": response.text
            }

        except Exception as e:
            return {
                "error": "Gemini analysis failed",
                "details": str(e)
            }
    else:
        return {
            "churn_probability": probability,
            "message": "Risque faible — aucune action de rétention requise"
        }

test_data_low_risk = {
  "Age": 32,
  "BusinessTravel": "Travel_Rarely",
  "DailyRate": 1100,
  "Department": "Research & Development",
  "DistanceFromHome": 18,
  "Education": 3,
  "EducationField": "Life Sciences",
  "EnvironmentSatisfaction": 2,
  "Gender": "Female",
  "JobInvolvement": 2,
  "JobLevel": 2,
  "JobRole": "Research Scientist",
  "JobSatisfaction": 2,
  "MaritalStatus": "Single",
  "MonthlyIncome": 4200,
  "MonthlyRate": 14500,
  "NumCompaniesWorked": 3,
  "OverTime": "Yes",
  "PercentSalaryHike": 11,
  "PerformanceRating": 3,
  "RelationshipSatisfaction": 2,
  "StockOptionLevel": 0,
  "TotalWorkingYears": 8,
  "WorkLifeBalance": 2,
  "YearsAtCompany": 4,
  "YearsInCurrentRole": 3,
  "YearsSinceLastPromotion": 3,
  "YearsWithCurrManager": 2
}

#print(gemini_analyse(0.70,test_data_low_risk))