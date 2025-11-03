from setuptools import setup, find_packages

setup(
    name="fiber_autocad_optimizer",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pyautocad>=0.2.0",
        "PyYAML>=6.0",
    ],
    python_requires=">=3.7",
)
