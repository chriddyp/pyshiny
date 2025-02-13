import io
import os
from setuptools import setup, find_packages

main_ns = {}
exec(open("dash/version.py", encoding="utf-8").read(), main_ns)  # pylint: disable=exec-used, consider-using-with


def read_req_file(req_type):
    with open(os.path.join("requirements", f"{req_type}.txt"), encoding="utf-8") as fp:
        requires = (line.strip() for line in fp)
        return [req for req in requires if req and not req.startswith("#")]


setup(
    name="dash",
    version=main_ns["__version__"],
    author="Chris Parmer",
    author_email="chris@plotly.com",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    license="MIT",
    description=(
        "A Python framework for building reactive web-apps. "
        "Developed by Plotly."
    ),
    long_description=io.open("README.md", encoding="utf-8").read(),  # pylint: disable=consider-using-with
    long_description_content_type="text/markdown",
    install_requires=read_req_file("install"),
    python_requires=">=3.8",
    extras_require={
        "async": read_req_file("async"),
        "ci": read_req_file("ci"),
        "dev": read_req_file("dev"),
        "testing": read_req_file("testing"),
        "celery": read_req_file("celery"),
        "diskcache": read_req_file("diskcache"),
        "compress": read_req_file("compress")
    },
    entry_points={
        "console_scripts": [
            "dash-generate-components = "
            "dash.development.component_generator:cli",
            "renderer = dash.development.build_process:renderer",
            "dash-update-components = dash.development.update_components:cli"
        ],
        "pytest11": ["dash = dash.testing.plugin"],
    },
    url="https://plotly.com/dash",
    project_urls={
        "Documentation": "https://dash.plotly.com",
        "Source": "https://github.com/plotly/dash",
        "Issue Tracker": "https://github.com/plotly/dash/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Dash",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database :: Front-Ends",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Widget Sets",
    ],
    data_files=[
        # like `jupyter nbextension install --sys-prefix`
        ("share/jupyter/nbextensions/dash", [
            "dash/nbextension/main.js",
        ]),
        # like `jupyter nbextension enable --sys-prefix`
        ("etc/jupyter/nbconfig/notebook.d", [
            "dash/nbextension/dash.json"
        ]),
        # Place jupyterlab extension in extension directory
        ("share/jupyter/lab/extensions", [
            "dash/labextension/dist/dash-jupyterlab.tgz"
        ]),
    ],
)
