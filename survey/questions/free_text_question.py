from matplotlib.axes import Axes
from mpl_format.axes.axis_utils import new_axes
from mpl_format.text.text_utils import wrap_text
from nltk import RegexpTokenizer, WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize.api import TokenizerI
from pandas import Series, DataFrame, concat
from typing import List, Optional, Set, Union

from survey.mixins.data_mixins import ObjectDataMixin
from survey.mixins.data_types.textual_mixin import TextualMixin
from survey.mixins.named import NamedMixin
from survey.questions._abstract.question import Question
from survey.utils.nlp import pre_process_text_series


class FreeTextQuestion(NamedMixin, ObjectDataMixin, TextualMixin, Question):
    """
    A Question with a Free-Text response.
    """
    def __init__(self, name: str, text: str, data: Optional[Series] = None):
        """
        Create a new FreeText Question.

        :param name: A pythonic name for the question.
        :param text: The text of the question.
        :param data: Optional pandas Series of responses.
        """
        self._set_name_and_text(name, text)
        self.data = data

    def _validate_data(self, data: Series):
        pass

    def plot_distribution(self, data: Optional[Series] = None,
                          transpose: bool = False,
                          top: int = 25,
                          title: bool = True,
                          x_label: bool = True, y_label: bool = True,
                          ax: Optional[Axes] = None) -> Axes:
        """
        Plot the distribution of top words in answers to the Question.

        :param data: The answers given by Respondents to the Question.
        :param transpose: Whether to transpose the labels to the y-axis.
        :param top: Number of most frequent words to plot.
        :param title: Whether to add a title to the plot.
        :param x_label: Whether to add a label to the x-axis.
        :param y_label: Whether to add a label to the y-axis.
        :param ax: Optional matplotlib axes to plot on.
        """
        data = data if data is not None else self._data
        if data is None:
            raise ValueError('No data!')
        words = pre_process_text_series(data)
        value_counts = Series(words).value_counts()[:top]
        plot_type = 'barh' if transpose else 'bar'
        ax = ax or new_axes()
        value_counts.index = wrap_text(value_counts.index)
        value_counts.plot(kind=plot_type, ax=ax)
        if title:
            ax.set_title(self.text)
        if transpose:
            x_label_value = '# Respondents'
            y_label_value = data.name
        else:
            x_label_value = data.name
            y_label_value = '# Respondents'
        if x_label:
            ax.set_xlabel(x_label_value)
        else:
            ax.set_xlabel('')
        if y_label:
            ax.set_ylabel(y_label_value)
        else:
            ax.set_ylabel('')

        return ax

    @staticmethod
    def word_counts(data: Series,
                    stop_words: Union[Set[str], str] = 'english',
                    tokenizer: Union[TokenizerI, str] = r'\w+',
                    lemmatizer=None) -> Series:
        """
        Return a count of each word in the series of responses.

        :param data: Series containing response texts.
        :param stop_words: Set of stop words or language.
        :param tokenizer: TokenizerI or string to pass to RegexpTokenizer.
        :param lemmatizer: Optional Lemmatizer. Defaults to WordNetLemmatizer.
        """
        if isinstance(stop_words, str):
            stop_words = set(stopwords.words(stop_words))
        if isinstance(tokenizer, str):
            tokenizer = RegexpTokenizer(tokenizer)
        if lemmatizer is None:
            lemmatizer = WordNetLemmatizer()

        def process(response: str) -> List[str]:
            """
            Process a single string.
            """
            words = tokenizer.tokenize(response.lower())
            words = [w for w in words if w not in stop_words]
            words = [lemmatizer.lemmatize(w) for w in words]
            return words

        processed = data.map(process)
        word_counts = Series([
            word for _, response in processed.iteritems()
            for word in response
        ]).value_counts()

        return word_counts

    def distribution_table(
        self, data: Optional[Series] = None,
            top: int = 25,
    ) -> DataFrame:
        """
        Return a table of the top words found in answers given to the Question.

        :param data: Optional Series containing response texts.
        :param top: Number of words to return counts for.
        """
        data = data if data is not None else self._data
        if data is None:
            raise ValueError('No data!')
        words = pre_process_text_series(data)
        value_counts = Series(words).value_counts()[:top].rename('Count')
        value_counts.index.name = 'Word'
        word_counts = (
            value_counts.reset_index()
                        .sort_values('Word')
                        .sort_values('Count', ascending=False)
                        .reset_index()
        )
        word_counts = word_counts.sort_values(
            ['Count', 'Word'], ascending=[False, True]
        ).reset_index()[['Word', 'Count']]
        return word_counts

    def stack(self, other: 'FreeTextQuestion',
              name: Optional[str] = None,
              text: Optional[str] = None) -> 'FreeTextQuestion':

        if self.data.index.names != other.data.index.names:
            raise ValueError('Indexes must have the same names.')
        new_data = concat([self.data, other.data])
        new_question = FreeTextQuestion(
            name=name or self.name,
            text=text or self.text,
            data=new_data
        )
        new_question.survey = self.survey
        return new_question

    def __repr__(self):

        return (
            f"FreeTextQuestion(\n"
            f"\tname='{self.name}',\n"
            f"\ttext='{self.text}'\n"
            f")"
        )
