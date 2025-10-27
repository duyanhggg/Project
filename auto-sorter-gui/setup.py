from setuptools import setup, find_packages

setup(
    name="auto-sorter-gui",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A GUI application for automatically sorting files based on their extensions.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/auto-sorter-gui",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "watchdog",
        "plyer",
        "infi.systray",
        "tkinter",  # If using tkinter for GUI
        # Add other dependencies as needed
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)