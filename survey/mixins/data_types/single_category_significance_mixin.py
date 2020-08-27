from itertools import product
from pandas import Series, DataFrame, pivot_table
from probability.distributions import BetaBinomial
from typing import List


class SingleCategorySignificanceMixin(object):

    @property
    def categories(self) -> List[str]:
        raise NotImplementedError

    @property
    def data(self) -> DataFrame:
        raise NotImplementedError

    def significance_one_vs_all(self) -> Series:
        """
        Return the probabilities that a random respondent is more likely to
        answer each one category than all others combined.
        """
        results = []
        for category in self.categories:
            try:
                category_count = self.data.value_counts()[category]
            except KeyError:
                category_count = 0
            num_responses = len(self.data.dropna())
            bb_category = BetaBinomial(1, 1,
                                       num_responses,
                                       category_count)
            bb_rest = BetaBinomial(1, 1,
                                   num_responses,
                                   num_responses - category_count)
            results.append({'category': category,
                            'p': bb_category.posterior() > bb_rest.posterior()})
        return DataFrame(results).set_index('category')['p']

    def significance_one_vs_any(self) -> Series:
        """
        Return the probability that a random respondent is more likely to answer
        one category than a randomly selected other category.
        """
        sums = self.data.value_counts()
        sums = sums.reindex(self.categories).fillna(0).astype(int)
        results = []
        for category in self.categories:
            anys = [c for c in self.categories if c != category]
            n_one = len(self.data)
            m_one = sums[category]
            n_any = len(self.data)
            m_any = sums[anys].mean()
            results.append({
                'category': category,
                'p': (
                    BetaBinomial(1, 1, n_one, m_one).posterior() >
                    BetaBinomial(1, 1, n_any, m_any).posterior()
                )
            })
        return DataFrame(results).set_index('category')['p']

    def significance_one_vs_one(self) -> DataFrame:
        """
        Return the probability that a random respondent is more likely to answer
        each category than each other.
        """
        results = []
        for category_1, category_2 in product(self.categories, self.categories):
            try:
                category_1_count = self.data.value_counts()[category_1]
            except KeyError:
                category_1_count = 0
            try:
                category_2_count = self.data.value_counts()[category_2]
            except KeyError:
                category_2_count = 0
            num_responses = len(self.data.dropna())
            bb_category_1 = BetaBinomial(1, 1, num_responses, category_1_count)
            bb_category_2 = BetaBinomial(1, 1, num_responses, category_2_count)
            results.append({
                'category_1': category_1,
                'category_2': category_2,
                'p': bb_category_1.posterior() > bb_category_2.posterior()}
            )
        results_data = DataFrame(results)
        pt = pivot_table(data=results_data,
                         index='category_1', columns='category_2',
                         values='p')
        return pt
