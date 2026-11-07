import plotly.express as px
from repository import MongoRepository


class GraphBuilder:
    def __init__(self):
        self.repo = MongoRepository()
        self.font_config = dict(family="JetBrains Mono", size=14)

    def build_nat_choropleth(self):
        df = self.repo.get_nationality_value_counts(normalize=True)
        fig = px.choropleth(
            df, locations="country_iso3", color="count",
            hover_name="country_name", title="Applicant Nationalities"
        )
        fig.update_layout(font=self.font_config)
        return fig

    def build_age_hist(self):
        ages = self.repo.get_ages()
        fig = px.histogram(
            ages, nbins=30, title="Distribution of Applicant Ages",
            labels={"value": "Age"}
        )
        fig.update_layout(showlegend=False, font=self.font_config)
        return fig

    def build_ed_bar(self):
        degrees = self.repo.get_ed_value_counts(normalize=False)
        fig = px.bar(
            degrees, title="Applicants by Highest Degree Earned",
            labels={"index": "Highest Degree", "value": "Number of Applicants"}
        )
        fig.update_layout(showlegend=False, font=self.font_config)
        return fig

    def build_contingency_bar(self):
        df = self.repo.get_contingency_table()
        if df.empty:
            return px.bar(title="Not enough data for Contingency Table")

        # Passing the wide-format matrix directly bypasses the pandas GroupBy bug
        fig = px.bar(
            df, barmode="group",
            title="Quiz Completion by Experiment Group",
            labels={"value": "Count", "group": "Experiment Group", "admissionsQuiz": "Quiz Status"}
        )
        fig.update_layout(font=self.font_config)
        return fig