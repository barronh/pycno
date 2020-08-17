import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycno",
    version="0.0.2",
    author="Barron H. Henderson",
    author_email="barronh@gmail.com",
    description="Python map overlay software to read CNO and CNOB files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barronh/pycno",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["numpy"],
    extras_require={
        "proj":  ["pyproj"],
    }
)
