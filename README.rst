omni:us image processing package
================================

The main objective is to bundle general image processing tools into a single package in order to make them reusable in other packages and applications. This may include functions for the following topics:

- Image arithmetic
- Point operations
- Geometric operations
- Image analysis
- Morphological operations
- Digital filters
- Feature detectors
- Images transforms
- Image synthesis
- Visualization

Project steering committee
--------------------------

- Lutz Goldmann <lutz@omnius.com> (Lead)
- Mauricio Villegas <mauricio@omnius.com>
- Waqas Tahir <waqas@omnius.com>

Contributing
------------

- The master branch in bitbucket is blocked for pushing. Thus to contribute it is required to create and push to a new branch and issue a pull request.
- A pull request will only be accepted if

  - All python files pass a pylint error check.
  - All unit tests run successfully.
  - The test coverage remains more or less the same or it increases.

- When developing after cloning be sure to run the githook-pre-commit to setup the pre-commit hook. This will help you by automatically running pylint before every commit and automatically update the package documentation.

Testing
-------

The setup.py includes commands to run the unit tests and to get a test coverage report::

    # Run unit tests
    python setup.py test

    # Run unit tests and print test coverage report
    python setup.py test_coverage