from setuptools import setup, find_packages

version = "0.1"

setup(
    name="AfpyLogs",
    version=version,
    keywords="",
    author="Gael Pasgrimaud",
    author_email="gael@gawel.org",
    url="",
    license="GPL",
    packages=find_packages(exclude=["ez_setup"]),
    include_package_data=True,
    zip_safe=False,
    # uncomment this to be able to run tests with setup.py
    # test_suite = "gp.transcript.tests.test_transcriptdocs.test_suite",
    install_requires=["paste", "pyquery", "webob", "pastedeploy", "gunicorn"],
    entry_points="""
      [paste.app_factory]
      main = afpylogs.app:factory
      """,
)
