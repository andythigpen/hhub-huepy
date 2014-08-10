from setuptools import setup, find_packages

setup(
    name='hhub-huepy',
    version="0.1",
    description="Plugin for hhub that controls Philips Hue",
    author="Andrew Thigpen",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "hhub>=0.1",
        "flask",
    ],
    entry_points="""
        [hhub.plugin]
        huepy=huepy.plugin:HuepyPlugin
    """,
)

