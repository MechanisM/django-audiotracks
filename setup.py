from setuptools import setup, find_packages
 
setup(
    name='django-audiotracks',
    version='0.1',
    description='A pluggable Django app to publish audio tracks',
    long_description=open("README.rst").read(),
    keywords='django audio sound',
    author='Alex Marandon',
    license='MIT',
    author_email='contact@alexmarandon.com',
    url='https://github.com/alex-marandon/django-audiotracks',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires = [
        'mutagen==1.20',
        'PIL'
        ],
    include_package_data=True,
    zip_safe=False,
)
