import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from nltk import word_tokenize, PorterStemmer, WordNetLemmatizer, \
    RegexpTokenizer
from nltk.corpus import stopwords
from nltk.tokenize.api import TokenizerI
from numpy import ndarray
from numpy.ma import argsort, squeeze
from pandas import DataFrame, Series
from typing import List, Tuple, Optional, Set
from wordcloud import WordCloud

from mpl_format.utils.io_utils import save_plot


def stem_sentence(sentence: str) -> str:
    """
    Stem input string using porter stemmer from nltk package.
    """
    token_words = word_tokenize(sentence)
    stemmed_sentence = []
    for word in token_words:
        stemmed_sentence.append(PorterStemmer().stem(word))
        stemmed_sentence.append(' ')
    return ''.join(stemmed_sentence)


def create_corpus(col_split: str, col_text: str, data: DataFrame):
    """
    Create a list of strings by grouping answers of same category together.

    :param col_split: demographic column to group text answers of same category.
    :param col_text: text answer column.
    :param data: DataFrame containing survey data.
    :return: list of strings for each joined texts for each category.
    """
    corpus = []
    for col_value in data[col_split].unique():
        string = [answer for answer in [
            data.loc[data[col_split] == col_value, col_text].tolist()
        ][0]]
        string = ' '.join(string)
        corpus.append(string)
    return corpus


def top_words_in_doc(doc_term_frequency: ndarray, features: list,
                     row_id: int, top_n: int = 20) -> List[Tuple[str, str]]:
    """
    Top TF IDF features in specific document (matrix row).

    :param doc_term_frequency: Document-term frequency matrix.
    :param features: Feature names for the document term matrix.
    :param row_id: Row index of the document.
    :param top_n: Top number of words to display on wordcloud.
    :return: List[(word, tf_idf)]
    """
    row = squeeze(doc_term_frequency[row_id].toarray())
    top_n_ids = argsort(row)[::-1][:top_n]
    return [(features[i], row[i]) for i in top_n_ids]


def create_wordcloud_from_tf_idf(
        top_words: List, col_split: str, col_split_value: str,
        save_fig: bool = False, ax: Optional[Axes] = None
) -> Axes:
    """
    Create wordcloud from the top words with highest TF IDF scores.

    :param top_words: DataFrame returned from top_words_in_doc function.
    :param col_split: Demographic column to be analyzed.
    :param col_split_value: Demographic column value.
    :param save_fig: Option to save plot to file.
    :param ax: Optional matplotlib axes to plot on.
    """
    # create figure and axes
    if ax is None:
        fig = plt.figure(1, figsize=(20, 20))
        ax = fig.gca()
    else:
        fig = ax.figure
    fig.suptitle(f'{col_split}: {col_split_value} top words by tf-idf scores',
                 fontsize=20)
    fig.subplots_adjust(top=2.3)
    # create word cloud
    d = {a: x for a, x in top_words if x > 0}
    wordcloud = WordCloud()
    wordcloud.generate_from_frequencies(frequencies=d)
    # show word cloud
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    if save_fig:
        file_path = f'{col_split}_{col_split_value}_tf_idf_wordcloud.png'
        save_plot(ax, file_path)

    return ax


def create_wordcloud_from_tf(
        survey_data: DataFrame,
        col_text: str, col_split: str,
        col_split_value: str,
        save_fig: bool = False, title: bool = True
) -> Axes:
    """
    Create wordcloud from original survey data.
    """
    wordcloud = WordCloud(
        background_color='white',
        max_words=100,
        max_font_size=40,
        random_state=1,
        collocations=False,
        normalize_plurals=True,
        scale=3
    ).generate(' '.join(
        survey_data[survey_data[col_split] == col_split_value][col_text]
    ))
    fig = plt.figure(1, figsize=(20, 20))
    if title:
        fig.suptitle(f'{col_split}: {col_split_value} wordcloud',
                     fontsize=20)
    fig.subplots_adjust(top=2.3)
    ax = fig.gca()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    if save_fig:
        file_path = f'{col_split}_{col_split_value}_tf_idf_wordcloud.png'
        save_plot(ax, file_path)
    return ax


def pre_process_text_series(
        data: Series,
        tokenizer: TokenizerI = None,
        stop_words: Set[str] = None,
        lemmatizer: WordNetLemmatizer = None
) -> List[str]:
    """
    Clean up given Series column to turn all texts to lowercase,
    remove stopwords, tokenize, and lemmatize.

    :param data: Series with text that needs to be pre-processed.
    :param tokenizer: nltk tokenizer to break text paragraph into words.
    :param stop_words: List of stop words.
    :param lemmatizer: nltk lemmatizer to reduce words to their base words.
    """
    if tokenizer is None:
        tokenizer = RegexpTokenizer(r'\w+')
    if stop_words is None:
        stop_words = set(stopwords.words('english'))
    if lemmatizer is None:
        lemmatizer = WordNetLemmatizer()
    txt = data.str.lower().str.cat(sep=' ')  # lower case
    words = tokenizer.tokenize(txt)  # tokenize
    words = [w for w in words if w not in stop_words]  # remove stop words
    words = [lemmatizer.lemmatize(w) for w in words]

    return words
