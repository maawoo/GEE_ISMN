import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GEE_ISMN-pkg-maawoo-PatFisch",
    version="0.0.1",
    author="Marco Wolsza & Patrick Fischer",
    author_email="author@example.com",
    description="A simple package to extract Sentinel-1 backscatter "
                "timeseries for ISMN station locations and compare those "
                "with soil moisture measurements.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maawoo/GEO419",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)