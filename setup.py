from setuptools import setup, find_packages

setup(
    name="cost-optimization-model",
    version="1.0.0",
    author="Soham Nageshkumar Dharne",
    author_email="s.dharne@essex.ac.uk",
    description="TCO Optimisation Model: Human vs AI vs Hybrid team composition decision support",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "scikit-learn>=1.3.0",
        "xgboost>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "plotly>=5.15.0",
        "streamlit>=1.28.0",
        "joblib>=1.3.0",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "dev": ["pytest>=7.4.0", "pytest-cov>=4.1.0", "jupyter>=1.0.0", "ipykernel>=6.25.0"],
    },
)
