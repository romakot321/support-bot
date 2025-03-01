from setuptools import setup, find_packages


setup(
    name='app',
    version='0.0.1.dev1',
    description='API',
    platforms=['POSIX'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)

