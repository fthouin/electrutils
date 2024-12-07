from setuptools import setup

setup(
    name='electrutils',
    version='0.1.0',    
    description='Python modules to acquire and analyse electronics data in my home lab',
    url='https://github.com/fthouin/electrutils',
    author='Felix Thouin',
    author_email='felix.thouin@gmail.com',
    license='GPL',
    packages=['electrutils'],
    install_requires=['numpy',
                      'matplotlib',
                      'scipy'                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)