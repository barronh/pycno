import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycno",
    version="0.0.1",
    author="Barron H. Henderson",
    author_email="barronh@gmail.com",
    description="Python map overlay software to read CNO and CNOB files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barronh/pycno",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "LICENSE :: OSI APPROVED :: GNU GENERAL PUBLIC LICENSE V3 (GPLV3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["numpy"],
    extras_require={
        "proj":  ["pyproj"],
    }
)
