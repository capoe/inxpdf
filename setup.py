from setuptools import setup, find_packages

def get_description():
    return "SVG to PDF slide converter"

def get_scripts():
    return [
        "./bin/jinxpdf",
    ]

if __name__ == "__main__":
    setup(
        name="inxpdf",
        version="0.1.1",
        url="https://github.com/capoe/inxpdf",
        description=get_description(),
        long_description=get_description(),
        packages=find_packages(),
        scripts=get_scripts(),
        setup_requires=[],
        install_requires=["numpy", "lxml"],
        include_package_data=True,
        ext_modules=[],
        license="Apache License 2.0",
        classifiers=[
        ],
        keywords="inkscape svg pdf",
        python_requires=">=3.7",
    )

