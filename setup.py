import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='cppgen',
    version='2021.03.01',
    author='Космическое П.',
    author_email='kosmospredanie@yandex.ru',
    description='C/C++ definition generator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kosmospredanie/cppgen',
    license='MIT',
    project_urls={
        'Source': 'https://github.com/kosmospredanie/cppgen',
        'Bug Tracker': 'https://github.com/kosmospredanie/cppgen/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'cppgen=cppgen.cppgen:main',
            'hppgen=cppgen.hppgen:main',
        ],
    },
)
