import matplotlib.pyplot as plt
from numpy.random import RandomState, permutation
from pandas import Series

from survey.questions import RankedChoiceQuestion

RandomState(0)
choices = [f'Option {choice}' for choice in range(1, 11)]
perms = [
    permutation(choices) for _ in range(100)
]
data = Series(['\n'.join(perm) for perm in perms])

question = RankedChoiceQuestion(
    name='ranked_choice_question',
    text='Ranked Choice Question',
    categories=choices,
    data=data
)
ax = question.plot_distribution(significance=True, sig_values=(0.6, 0.4))
plt.show()
print(question.significance__one_vs_any())
