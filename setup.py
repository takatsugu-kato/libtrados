import setuptools

setuptools.setup(
    name="libtrados",
    version="1.0.0",
    author="tkato",
    author_email="kato@ideainstitute.co.jp",
    description="libtrados module handles memsource.",
    long_description="libtrados module handles memsource.",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'lxml'
    ]
)
