try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup

setup(
    name="structure_threader",
    version="0.1.5",
    packages=["structure_threader",
              "structure_threader.evanno",
              "structure_threader.plotter",
              "structure_threader.sanity_checks"],
    install_requires=[
        "matplotlib",
        "numpy",
    ],
    description=("A program to parallelize runs of 'Structure' and "
    "'fastStructure'."),
    url="https://github.com/StuntsPT/Structure_threader",
    author="Francisco Pina-Martins",
    author_email="",
    license="GPL3",
    classifiers=["Intended Audience :: Science/Research",
                 "License :: OSI Approved :: GNU General Public License v3 ("
                 "GPLv3)",
                 "Natural Language :: English",
                 "Operating System:: POSIX:: Linux",
                 "Topic :: Scientific/Engineering :: Bio-Informatics"],
    entry_points={
        "console_scripts": [
            "structure_threader = structure_threader.structure_threader:main",
        ]
    },
)
