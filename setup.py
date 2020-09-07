import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="evhelper-core",
    version="2020.08.29.0",
    author="Christopher Dilley",
    author_email="cgdilley@gmail.com",
    description="Core components of all EV Helper scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Cabuu/PythonModule-CabuuCore",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        "tree_format"
    ],
    python_requires=">=3.7"
)
