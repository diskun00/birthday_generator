from setuptools import setup

setup(
        name="birthday generator",
        version="0.1",
        author="Diskun",
        packages=["birthday_generator"],
        install_requires=["icalendar", "LunarSolarConverter"]
)
