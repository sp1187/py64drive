from setuptools import setup

setup(name='py64drive',
    version='0.1',
    description='Python script and library for USB communication with the 64drive',
    license='MIT',
    url='http://github.com/sp1187/py64drive',
    py_modules=["py64drive"],
    install_requires=["pylibftdi"],
    scripts=["scripts/py64drive"]
)


