"""
CliMaPan-Lab: Climate-Pandemic Economic Modeling Laboratory
Setup script for package installation
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="climapan-lab",
    version="0.0.1",
    author="CliMaPan-Lab Team",
    description="Climate-Pandemic Economic Modeling Laboratory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/climapan-lab",
    packages=find_packages(exclude=["tests*", "docs*", "results*"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "jaxabm>=0.1.0",
        "scikit-learn>=1.0.0",
        "scipy>=1.7.0",
        "joblib>=1.1.0",
        "salib>=1.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "climapan-run=climapan_lab.run_sim:main",
            "climapan-example=climapan_lab.examples.simple_example:run_simple_simulation",
        ],
    },
)
