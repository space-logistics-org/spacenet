from setuptools import setup

setup(
    name='SpaceNet',
    version='3.0',
    packages=[
        'spacenet', 
        'app/database',
        'app/campaign'
    ],
    include_package_data=True,
    install_requires=[
        'fastapi',
        'uvicorn[standard]',
        'aiofiles',
        "pydantic"
    ]
)