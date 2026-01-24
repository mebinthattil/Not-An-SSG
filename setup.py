from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name='not_an_ssg',
    version='2.1.0',
    author='Mebin',
    author_email='mail@mebin.in',
    url='https://github.com/mebinthattil/Not-An-SSG',
    packages=find_packages(),
    package_data={
        'not_an_ssg': [
            'articles_css.css',
            'demo_comprehensive.md',
            'LICENSE',
            'templates/**/*'
        ]
    },
    include_package_data=True,
    install_requires=[
        "boto3>=1.37.10",
        "markdown>=3.7",
        "pygments>=2.18.0",
        "python-dotenv>=1.1.1",
        "PyYAML>=6.0",
        "importlib-resources>=1.3.0;python_version<'3.9'"],
    entry_points={
        'console_scripts': [
            'not_an_ssg = not_an_ssg:cli_main']},
    long_description=readme,
    long_description_content_type="text/markdown",
)

        