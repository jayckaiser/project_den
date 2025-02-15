import os
import pathlib
import setuptools

# Retrieve the README and requirements into the setup.
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
 
with open(os.path.join(HERE, 'requirements.txt'), encoding='utf-8') as fp:
    all_reqs = fp.readlines()

setuptools.setup (
    name = 'project_den',
    description = 'Transforms Project DEN time-in and time-out data into a dashboard visualization.',
    version = '0.0.1',
    packages = setuptools.find_namespace_packages(include=['project_den', 'project_den.*']),
    include_package_data=True,
    install_requires = all_reqs,
    python_requires = '>=3',
    author = "Jay Kaiser",
    keyword = "data, transformation",
    long_description = README,
    long_description_content_type = "text/markdown",
    license = 'Apache 2.0',
    url = 'https://github.com/jayckaiser/project_den',
    dependency_links = all_reqs,
    author_email = 'jayckaiser@gmail.com',
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
    ]
)