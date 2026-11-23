from setuptools import setup, find_packages

setup(
    name="foolgit",
    version="1.0.0",
    description="A minimalist, foolproof, and customizable Git assistant with CLI & PyQt6 Dark GUI.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "gui": ["PyQt6>=6.4.0"],
    },
    entry_points={
        "console_scripts": [
            "foolgit=foolgit_pkg.cli_entry:main",
            "foolgit-gui=foolgit_pkg.gui:launch_gui",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
        "Topic :: Software Development :: Version Control :: Git",
    ],
)
