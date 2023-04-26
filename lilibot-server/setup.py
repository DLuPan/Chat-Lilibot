from setuptools import setup, find_packages

requirements = [
    "flask",
    "flask_cors",
    "flask_jwt_extended"
]


setup(
    name="lilibot-server",
    install_requires=requirements,
    packages=find_packages()
)
