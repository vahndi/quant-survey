from distutils.core import setup
from setuptools import find_packages

setup(
    name='quant-survey',
    packages=find_packages(),
    version='0.0.007',
    license='MIT',
    description='Library for quantitative survey analysis.',
    author='Vahndi Minah',
    url='https://github.com/vahndi/quant-survey',
    keywords=['quant', 'survey'],
    install_requires=[
        'matplotlib',
        'mpl-format',
        'nltk',
        'numpy',
        'pandas',
        'probability',
        'seaborn',
        'scikit-learn',
        'stringcase',
        'tqdm',
        'wordcloud'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
)
