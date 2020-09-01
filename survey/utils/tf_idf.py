import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Union

from survey.attributes import SingleCategoryAttribute
from survey.custom_types import CategoricalQuestion
from survey.surveys.survey import Survey
from survey.utils.misc import listify
from survey.utils.nlp import top_words_in_doc, create_wordcloud_from_tf_idf


def plot_tf_idf_for_cat_text_question(
        survey: Survey,
        categorical_question: CategoricalQuestion,
        text_question: str
):
    """
    Plot TF IDF wordcloud for each group with the same answer for a categorical
    question on a text question.

    :param survey: Survey instance.
    :param categorical_question: CategoricalQuestion to be analyzed.
    :param text_question: FreeTextQuestion to be analyzed.
    """
    corpus = []
    for cat_value in categorical_question.categories:
        respondents = survey.find_respondents(
            question=categorical_question, answers=cat_value
        )
        responses = survey.question_responses(text_question, respondents)
        corpus.append(responses.str.cat(sep=' '))
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2),
                         min_df=0, max_df=1, stop_words='english')
    doc_term_frequency = tf.fit_transform(corpus)
    features = tf.get_feature_names()
    for i in range(len(categorical_question.categories)):
        top_words = top_words_in_doc(doc_term_frequency=doc_term_frequency,
                                     features=features, row_id=i)
        create_wordcloud_from_tf_idf(
            top_words=top_words,
            col_split=categorical_question.name,
            col_split_value=list(categorical_question.categories)[i]
        )
        plt.show()


def plot_tf_idf_for_control_experiment_groups(
        survey: Survey,
        cat_question: CategoricalQuestion, cat_answers: List[str],
        attribute: SingleCategoryAttribute,
        exp_attribute_values: Union[str, List[str]],
        ctl_attribute_values: Union[str, List[str]],
        text_question: str
):
    """
    Plot TF IDF wordcloud of answers to a FreeTextQuestion by the Experimental
    Group vs Control Group, where:
        - each Group answered one of `cat_answers` to `cat_question`
        - the Experimental Group all have one of `exp_attribute_values` for
          `attribute`
        - the Control Group all have one of `ctl_attribute_values` for
          `attribute`

    :param survey: Survey instance.
    :param cat_question: CategoricalQuestion to filter respondents by.
    :param cat_answers: Answers given by both groups to `cat_question`.
    :param attribute: Demographic attribute for which the Experimental and
                      Control Groups have different values.
    :param exp_attribute_values: Values of `attribute` for Experimental Group.
    :param ctl_attribute_values: Values of `attribute` for Control Group.
    :param text_question: FreeTextQuestion to extract answer text from.
    """
    # get respondents experimental and control group respondents
    exp_respondents = survey.find_respondents(cat_question, cat_answers,
                                              attribute, exp_attribute_values)
    ctl_respondents = survey.find_respondents(cat_question, cat_answers,
                                              attribute, ctl_attribute_values)
    # # create corpus of 2 documents, one for each group
    exp_responses = survey.question_responses(text_question, exp_respondents)
    ctl_responses = survey.question_responses(text_question, ctl_respondents)
    corpus = [exp_responses.str.cat(sep=' '), ctl_responses.str.cat(sep=' ')]
    # fit TF IDF vectorizer and get matrix and feature names
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2),
                         max_df=1, stop_words='english')
    doc_term_frequency = tf.fit_transform(corpus)
    features = tf.get_feature_names()
    # create wordcloud for each group
    attribute_values = [listify(exp_attribute_values),
                        listify(ctl_attribute_values)]
    for i in range(len(attribute_values)):
        top_words = top_words_in_doc(doc_term_frequency=doc_term_frequency,
                                     features=features, row_id=i)
        create_wordcloud_from_tf_idf(
            top_words=top_words,
            col_split=f'[{cat_question.name}:{cat_answers}]',
            col_split_value=f'[{", ".join(attribute_values[i])}]'
        )
        plt.show()


def plot_tf_idf_for_control_experiment_groups_attributes(
        survey: Survey,
        attribute: SingleCategoryAttribute,
        exp_attribute_values: Union[str, List[str]],
        ctl_attribute_values: Union[str, List[str]],
        text_question: str
):
    """
    Plot TF IDF wordcloud of answers to a FreeTextQuestion by the Experimental
    Group vs Control Group, where:
        - the Experimental Group all have one of `exp_attribute_values` for
          `attribute`
        - the Control Group all have one of `ctl_attribute_values` for
          `attribute`

    :param survey: Survey instance.
    :param attribute: Demographic attribute for which the Experimental and
                      Control Groups have different values.
    :param exp_attribute_values: Values of `attribute` for Experimental Group.
    :param ctl_attribute_values: Values of `attribute` for Control Group.
    :param text_question: FreeTextQuestion to extract answer text from.
    """
    # get respondents experimental and control group respondents
    exp_respondents = survey.find_respondents(
        filter_category=attribute, filter_values=exp_attribute_values
    )
    ctl_respondents = survey.find_respondents(
        filter_category=attribute, filter_values=ctl_attribute_values
    )
    # create corpus of 2 documents, one for each group
    exp_responses = survey.question_responses(text_question, exp_respondents)
    ctl_responses = survey.question_responses(text_question, ctl_respondents)
    corpus = [exp_responses.str.cat(sep=' '), ctl_responses.str.cat(sep=' ')]
    # fit TF IDF vectorizer and get matrix and feature names
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2),
                         max_df=1, stop_words='english')
    doc_term_frequency = tf.fit_transform(corpus)
    features = tf.get_feature_names()
    # create wordcloud for each group
    attribute_values = [listify(exp_attribute_values),
                        listify(ctl_attribute_values)]
    for i in range(len(attribute_values)):
        top_words = top_words_in_doc(doc_term_frequency=doc_term_frequency,
                                     features=features, row_id=i)
        create_wordcloud_from_tf_idf(
            top_words=top_words,
            col_split=text_question,
            col_split_value=f'[{", ".join(attribute_values[i])}]'
        )
        plt.show()


def plot_tf_idf_for_control_experiment_groups_diff_response(
        survey: Survey,
        cat_question: CategoricalQuestion,
        exp_cat_answers: List[str], ctl_cat_answers: List[str],
        attribute: SingleCategoryAttribute,
        exp_attribute_values: Union[str, List[str]],
        ctl_attribute_values: Union[str, List[str]],
        text_question: str
):
    """
    Plot TF IDF wordcloud of answers to a FreeTextQuestion by the Experimental
    Group vs Control Group, where:
        - each Group answered one of `cat_answers` to `cat_question`
        - the Experimental Group all have one of `exp_attribute_values` for
          `attribute`
        - the Control Group all have one of `ctl_attribute_values` for
          `attribute`

    :param survey: Survey instance.
    :param cat_question: CategoricalQuestion to filter responses by.
    :param exp_cat_answers: Answers given by experimental group to
                            `cat_question`.
    :param ctl_cat_answers: Answers given by control group to `cat_question`.
    :param attribute: Demographic attribute for which the experimental and
                      control Groups have different values.
    :param exp_attribute_values: Values of `attribute` for experimental group.
    :param ctl_attribute_values: Values of `attribute` for control group.
    :param text_question: FreeTextQuestion to extract answer text from.
    """
    # get respondents experimental and control group respondents
    exp_respondents = survey.find_respondents(cat_question, exp_cat_answers,
                                              attribute, exp_attribute_values)
    ctl_respondents = survey.find_respondents(cat_question, ctl_cat_answers,
                                              attribute, ctl_attribute_values)
    # create corpus of 2 documents, one for each group
    exp_responses = survey.question_responses(text_question, exp_respondents)
    ctl_responses = survey.question_responses(text_question, ctl_respondents)
    corpus = [exp_responses.str.cat(sep=' '), ctl_responses.str.cat(sep=' ')]
    # fit TF IDF vectorizer and get matrix and feature names
    tf = TfidfVectorizer(analyzer='word', max_df=1,
                         ngram_range=(1, 2), stop_words='english')
    doc_term_frequency = tf.fit_transform(corpus)
    features = tf.get_feature_names()
    # create wordcloud for each group
    attribute_values = [listify(exp_attribute_values),
                        listify(ctl_attribute_values)]
    cat_answers = [exp_cat_answers, ctl_cat_answers]
    for i in range(len(attribute_values)):
        top_words = top_words_in_doc(doc_term_frequency=doc_term_frequency,
                                     features=features, row_id=i)
        create_wordcloud_from_tf_idf(
            top_words=top_words,
            col_split=f'[{cat_question.name}:{cat_answers[i]}]',
            col_split_value=f'[{", ".join(attribute_values[i])}]'
        )
        plt.show()
