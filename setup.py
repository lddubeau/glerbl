from setuptools import setup, find_packages

long_description = ""
found = False
with file("README.rst", 'r') as readme:
    captured = []
    for line in readme:
        if line == \
           ".. Everything above goes into setup.py's long_description.\n":
            found = True
            break
        captured.append(line)

    long_description = "".join(captured)

if not found:
    raise ValueError("can't find end of long description in README.rst")

setup(
    name="glerbl",
    version="0.0.2",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'glerbl = glerbl.__main__:main'
        ],
    },
    author="Louis-Dominique Dubeau",
    author_email="ldd@lddubeau.com",
    description="Glerbl manages git hooks.",
    license="GPLv3+",
    keywords=["git", "git hooks"],
    url="https://github.com/lddubeau/glerbl",
    setup_requires=[
        'nose>=1.3.0',
        'freshen>=0.2',
    ],
    #use_2to3=True,
    classifiers=[
        "Programming Language :: Python",
        #"Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Version Control",
        "Topic :: Software Development :: Quality Assurance"
    ],
    long_description=long_description
)