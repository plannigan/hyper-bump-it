# Development Guide

Welcome! Thanks for wanting to make the project better. This section provides an overview of
project structure and how to work with the code base.

Before diving into this, it is best to read:

* The whole Usage Guide
* The [Code of Conduct][code-of-conduct]

## How to Contribute

There are lots of ways to contribute to the project.

* [Report a bug][bug]
* [Request a new feature][feature]
* Create a pull request that updates the code
* Create a pull request that updates the documentation
* Sponsor development of the project
    <iframe
     src="https://github.com/sponsors/plannigan/button"
     title="Sponsor plannigan"
     height="32" width="114" style="border: 0; border-radius: 6px; margin-bottom: -11px;">
    </iframe>

### Creating a Pull Request

Before creating a pull request, please first discuss the intended change by creating a new issue or
commenting on an existing issue.

#### Code Contributions

Code contributions should include test for the change. For a bug fix, there should be a new test
case that demonstrates the issue that was reported (which the contribution addresses). For a new
feature, new test cases should cover the new code, while also and checking for edge cases.
Generally, the goal is that each change should increase the code coverage rather than decreasing
it. ([more details][testing])

Pull requests will need to pass all tests and linting checks that are part of the [CI pipeline][ci]
before they can be merged.

Significant changes should update the [documentation][documentation] with details about how to use
the provided functionality.

Changes that affect users of `hyper-bump-it` must include an entry the [CHANGELOG][changelog] under
the `[Unrelease]` header. Once a new release is ready to be published, a version number will be
assigned in place of this header ([more details][releasing]). If a logical change is broken into
multiple pull requests, each pull request does not need to add a new entry. For significant changes
that affect the development of the project, as apposed to users of `hyper-bump-it`, the `Internal`
section can be used.

## Continuous Integration Pipeline

The Continuous Integration (CI) Pipeline runs to confirm that the repository is in a good state. It
will run when:

* a pull request is created
* new commits are pushed to the branch for an existing pull request
* a maintainer merges a pull request to the default branch

Pull requests will need to pass all tests and linting checks that are part of the CI pipeline
before they can be merged.

### Lints

The first set of jobs that run as part of the CI pipline are linters that perform static analysis
on the code. This includes: [MyPy][mypy-docs], [Black][black-docs], [Isort][isort-docs],
[Flake8][flake8-docs], and [Bandit][bandit-docs].

### Tests

The next set of jobs run the unit tests ([more details][testing]). The pipeline runs the tests
cases across each supported version of Python to ensure compatibility.

For each run of the test cases, the job will record the test results and code coverage information.
The pipeline uploads the code coverage information to [CodeCov][codecov] to ensure that a pull
request doesn't significantly reduce the total code coverage percentage or introduce a large amount
of code that is untested.

### Distribution Verification

The next set of jobs perform a basic smoke test  to ensure that the library can be packaged
correctly and used. The sdist and wheel distributions are built and installs in into a virtual
environment. Then two checks are performed:

* Run Python and import the library version
* Run `hyper-bump-it --help`

This is done across each supported version of Python to ensure compatibility.

### Documentation Building

When running as part of a pull request, the documentation is build in strict mode so that it will
fail if there are any errors. The job bundles the generated files into an artifact so that the
documentation website can be viewed in its rendered form.

When the pipeline is running as a result of a maintainer merging a pull request to the default
branch, a job runs that publishes the current state of the documentation to as the `dev` version.
This will allow users to view the "in development" state of the documentation with any changed that
have been made since a maintainer published the `latest` version.

### Renovate Configuration Lint

[Renovate][renovate] is used to automate the process of keeping project dependencies up to date.
A small job that confirms that the configuration is valid.

## Local Development Environment

The project includes a Dockerfile in order to make it easy to have a consistent development
environment. The Docker documentation has details on how to [install docker][install-docker] on a
computer.

Starting the container can be done with:

```bash
docker-compose run --rm devbox
```

This will present a terminal environment that can be used to experiment with the code. The
[Python interpreter][python-interpreter] can be started to import `hyper-bump-it` or any
dependencies. The container also has [pdb++][pdbpp-docs] install that can be used as a debugger
when running code.

Contributors are welcome to set up a different development environment & debugger if they would
like. But, they will need to ensure it stays consistent with the project.

### Running Pipeline Locally

The containerized development environment makes it easy to run the most important checks from the
CI pipeline locally.

```bash
docker-compose run --rm test
```

This will run the same tests (with code coverage) and linting done by the CI pipeline. The only
difference is that, when run locally, `black` and `isort` are configured to automatically correct
issues they detect.

## Testing

The project use [pytest][pytest-docs] as a testing framework. Keeping test coverage high helps
confirm that the implementation works as expected and refactoring the code doesn't have unintended
side effects.

### Testing Fixtures

In addition to the fixtures provided by `pytest`, the project also utilizes two plugins that
provide fixtures that integrate other libraries into `pytest`.

* [pytest-mock][pytest-mock] - Exposes [unitest.mock][unittest-mock].
* [pytest-freezer][pytest-freezer] - Exposes [freezgun][freezgun] (`datetime` manipulation).

## Documentation

The project use [mkdocs][mkdocs] as static site generator. The [mkdocs-material][mkdocs-material]
theme is used to control the look and feel of the website. [mike][mike] is used to manage
documentation for each version of `hyper-bump-it`.

The documentation can be build locally. The following command will build the documentation and
start a local server to view the rendered documentation.

```bash
docker-compose up mkdocs
```

## Building the Library

`hyper-bump-it` is [PEP 517][pep-517] compliant. [build][build] is used as the frontend tool for
building the project. [setuptools][setuptools] is used as the build backend. `pyproject.toml`
contains the package metadata. A `setup.py` is also included to support an editable install while
developing the project.

### Dependencies

Other packages that the project directly depends on (`hyper-bump-it` imports the package or
development tool used by project) are listed in a few different places.

* **pyproject.toml** - List the supported version ranges of all direct dependencies needed to run
    `hyper-bump-it`.
* **requirements.txt** - Lists all direct dependencies for development and testing.
* **requirements-test.txt** - Lists all direct dependencies needed for development. This primarily
    covers dependencies needed to run the test suite & lints.
* **requirements-docs.txt** - Lists all direct dependencies needed for building this documentation
    content.

## Publishing a New Version

Once the package is ready to be released, there are a few things that need to be done:

1. Start with a local clone of the repo on the default branch with a clean working tree.
2. Run `hyper-bump-it` on itself with the appropriate part name (`major`, `minor`, or `patch`).
    Example: `python -m hyper_bump_it by minor`
    
    This wil create a new branch, updates all affected files with the new version, and commit the
    changes to the branch, & push it.

3. Create a new pull request for the pushed branch.
4. Get the pull request approved.
5. Merge the pull request to the default branch.

Merging the pull request will trigger a GitHub Action that will create a new release. The creation
of this new release will trigger a GitHub Action that will to build a wheel & a source
distributions of the package and push them to [PyPI][pypi].

!!! warning
    The action that uploads the files to PyPI will not run until a repository maintainer
    acknowledges that the job is ready to run. This is to keep the PyPI publishing token secure.
    Otherwise, any job would have access to the token.

In addition to uploading the files to PyPI, the documentation website will be updated to include
the new version and make it the new `latest` version.


[code-of-conduct]: https://github.com/plannigan/hyper-bump-it/blob/main/CODE_OF_CONDUCT.md
[bug]: https://github.com/plannigan/hyper-bump-it/issues/new?assignees=&labels=bug&template=bug_report.md&title=
[feature]: https://github.com/plannigan/hyper-bump-it/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=
[testing]: #testing
[ci]: #continuous-integration-pipeline
[documentation]: #documentation
[changelog]: changelog.md
[releasing]: #publishing-a-new-version
[mypy-docs]: https://mypy.readthedocs.io/en/stable/
[black-docs]: https://black.readthedocs.io/en/stable/
[isort-docs]: https://pycqa.github.io/isort/
[flake8-docs]: http://flake8.pycqa.org/en/stable/
[bandit-docs]: https://bandit.readthedocs.io/en/latest/
[codecov]: https://app.codecov.io/gh/plannigan/hyper-bump-it
[renovate]: https://docs.renovatebot.com/
[install-docker]: https://docs.docker.com/install/
[python-interpreter]: https://docs.python.org/3/tutorial/interpreter.html
[pdbpp-docs]: https://github.com/pdbpp/pdbpp#usage
[pytest-docs]: https://docs.pytest.org/en/latest/
[pytest-mock]: https://pytest-mock.readthedocs.io
[unittest-mock]: https://docs.python.org/3/library/unittest.mock.html
[pytest-freezer]: https://github.com/pytest-dev/pytest-freezer
[freezgun]: https://github.com/spulec/freezegun
[mkdocs]: https://www.mkdocs.org/
[mkdocs-material]: https://squidfunk.github.io/mkdocs-material/
[mike]: https://github.com/jimporter/mike
[pep-517]: https://www.python.org/dev/peps/pep-0517
[build]: https://pypa-build.readthedocs.io/
[setuptools]: https://setuptools.pypa.io/en/latest/
[pypi]: https://pypi.org/project/hyper-bump-it/