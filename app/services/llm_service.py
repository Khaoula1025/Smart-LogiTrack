# function to use probaModel 
import joblib
import pandas as pd 
model=joblib.load('ml/models/probModel.pkl')
#print(model.classes_)
print(model.feature_names_in_)

def predict_probability(data):
    data=pd.DataFrame([data])
    result=model.predict_proba(data)
    return result[0][1]
    
test_data_low_risk = {
    "Age": 35,
    "BusinessTravel": "Travel_Rarely",
    "DailyRate": 1200,
    "Department": "Research & Development",
    "DistanceFromHome": 5,
    "Education": 4,
    "EducationField": "Life Sciences",
    "EnvironmentSatisfaction": 4,
    "Gender": "Male",
    "JobInvolvement": 3,
    "JobLevel": 3,
    "JobRole": "Research Scientist",
    "JobSatisfaction": 4,
    "MaritalStatus": "Married",
    "MonthlyIncome": 8000,
    "MonthlyRate": 20000,
    "NumCompaniesWorked": 2,
    "OverTime": "No",
    "PercentSalaryHike": 18,
    "PerformanceRating": 4,
    "RelationshipSatisfaction": 4,
    "StockOptionLevel": 2,
    "TotalWorkingYears": 15,
    "WorkLifeBalance": 3,
    "YearsAtCompany": 8,
    "YearsInCurrentRole": 5,
    "YearsSinceLastPromotion": 2,
    "YearsWithCurrManager": 6
}
#print(predict_probability(test_data_low_risk))