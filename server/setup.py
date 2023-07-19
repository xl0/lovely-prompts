from setuptools import setup, find_packages

setup(
    name='lovely-prompts-server',
    version='0.0.1',
    url='https://github.com/xl0/lovely-prompts/',
    author='Alexey Zaytsev',
    author_email='alex@lovely-prompts.io',
    description='Lovely Prompts API server',
    packages=find_packages(),
    install_requires=['fastapi', 'uvicorn', 'pydantic', 'requests'], # Add other dependencies
)

