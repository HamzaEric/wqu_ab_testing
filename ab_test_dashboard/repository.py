import os
import pandas as pd
import dns.resolver
import pycountry
from pymongo import MongoClient
from dotenv import load_dotenv

# Force dnspython to use Google's Public DNS to bypass local Windows/ISP DNS bugs
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

load_dotenv()


class MongoRepository:
    def __init__(self):
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')
        uri = f"mongodb+srv://{username}:{password}@applicants.wcr9gkl.mongodb.net/"

        self.client = MongoClient(uri)
        self.db = self.client["wqu_abtest"]
        self.collection = self.db["ds_applicants"]

    def get_nationality_value_counts(self, normalize=True):
        result = self.collection.aggregate([
            {"$group": {"_id": "$countryISO2", "count": {"$sum": 1}}}
        ])
        df = pd.DataFrame(list(result))
        if df.empty:
            return pd.DataFrame(columns=["country_iso2", "country_iso3", "country_name", "count"])

        df.rename(columns={"_id": "country_iso2"}, inplace=True)

        # Safely convert ISO2 codes using pycountry to avoid the Namibia 'NA' bug
        def get_iso3(code):
            country = pycountry.countries.get(alpha_2=code)
            return country.alpha_3 if country else code

        def get_name(code):
            country = pycountry.countries.get(alpha_2=code)
            return country.name if country else code

        df["country_iso3"] = df["country_iso2"].apply(get_iso3)
        df["country_name"] = df["country_iso2"].apply(get_name)

        if normalize:
            df["count"] = df["count"] / df["count"].sum()
        return df.sort_values("count", ascending=False)

    def get_ages(self):
        result = self.collection.aggregate([
            {"$project": {"age": {"$dateDiff": {"startDate": "$birthday", "endDate": "$$NOW", "unit": "year"}}}}
        ])
        df = pd.DataFrame(list(result))
        return df["age"].dropna().astype(int) if not df.empty else pd.Series(dtype=int)

    def get_ed_value_counts(self, normalize=False):
        result = self.collection.find({}, {"highestDegreeEarned": 1})
        df = pd.DataFrame(list(result))
        degrees = [
            "High School or Baccalaureate",
            "Some College (1-3 years)",
            "Bachelor's degree",
            "Master's degree",
            "Doctorate (e.g. PhD)"
        ]
        if df.empty:
            return pd.Series(0, index=degrees)
        return df["highestDegreeEarned"].value_counts(normalize=normalize).reindex(degrees).fillna(0)

    def get_contingency_table(self):
        result = self.collection.aggregate([
            {"$match": {"inExperiment": True, "group": {"$in": ["no email (control)", "email (treatment)"]}}},
            {"$group": {"_id": {"group": "$group", "admissionsQuiz": "$admissionsQuiz"}, "count": {"$sum": 1}}}
        ])
        data = list(result)
        if not data:
            return pd.DataFrame()

        df = pd.json_normalize(data)
        df.rename(columns={"_id.group": "group", "_id.admissionsQuiz": "admissionsQuiz"}, inplace=True)

        # Return as a wide-format matrix (perfect for both Plotly and SciPy)
        return df.pivot(index="group", columns="admissionsQuiz", values="count").fillna(0)