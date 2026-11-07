import numpy as np
from scipy.stats import chi2_contingency
from statsmodels.stats.power import GofChisquarePower
from repository import MongoRepository


class StatsBuilder:
    def __init__(self):
        self.repo = MongoRepository()

    def calculate_n_obs(self, effect_size, alpha=0.05, power=0.8):
        analysis = GofChisquarePower()
        sample_size = analysis.solve_power(
            effect_size=effect_size,
            nobs=None,
            alpha=alpha,
            power=power,
            n_bins=2
        )
        return int(np.ceil(sample_size))


class Experiment:
    def __init__(self):
        self.repo = MongoRepository()

    def run_chi_square(self):
        matrix = self.repo.get_contingency_table()

        if matrix.empty or matrix.shape != (2, 2):
            return matrix, None, None

        chi2, p_value, dof, expected = chi2_contingency(matrix)
        return matrix, chi2, p_value