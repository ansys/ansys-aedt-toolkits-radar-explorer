.. _contributing-main:

==========
Contribute
==========

Overall guidance on contributing to a PyAnsys repository appears in
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyAEDT or its toolkits.

The following contribution information is specific to PyAEDT toolkits.

You can be up and running with four lines of code:

.. code:: bash

   git clone https://github.com/ansys/ansys-aedt-toolkits-radar-explorer
   cd ansys-aedt-toolkits-radar-explorer
   pip install -e .

Run it with this code:

.. code:: bash

   run_toolkit

Developer installation
----------------------

#. Clone the repository:

   .. code:: bash

      git clone https://github.com/ansys/ansys-aedt-toolkits-radar-explorer

#. Create a fresh-clean Python environment and activate it as shown in
   the following code. If you require additional information, see the
   `venv`_ documentation in the Python documentation.

   .. code:: bash

      # Create a virtual environment
      python -m venv .venv
      # Activate it in a POSIX system
      source .venv/bin/activate
      # Activate it in Windows CMD environment
      .venv\Scripts\activate.bat
      # Activate it in Windows Powershell
      .venv\Scripts\Activate.ps1

#. Install the project in editable mode:

   .. code:: bash

      pip install -e .[tests,doc]

#. Verify your development installation:

   .. code:: bash

      pytest tests -v

Style and testing
-----------------
This project uses `pre-commit <https://pre-commit.com/>`_. Install it:

.. code::

   pip install pre-commit
   run pre-commit install

With each commit you make, ``pre-commit``runs to ensure that you have
followed project style guidelines. The output looks like this:

.. code::

   git commit -am 'fix style'
   isort....................................................................Passed
   black....................................................................Passed
   blacken-docs.............................................................Passed
   flake8...................................................................Passed
   codespell................................................................Passed
   pydocstyle...............................................................Passed
   check for merge conflicts................................................Passed
   debug statements (python)................................................Passed
   check yaml...............................................................Passed
   trim trailing whitespace.................................................Passed
   Validate GitHub Workflows................................................Passed

Run this command if you need to run  ``pre-commit`` again on all files and not just
staged files:

.. code::

   pre-commit run --all-files

Local build
-----------

You can deploy this application as a *frozen* application using `PyInstaller
<https://pypi.org/project/pyinstaller/>`__:

.. code::

   pip install -e .[freeze]
   run pyinstaller frozen.spec

This generates application files at ``dist/ansys_python_manager``. You can run the application locally by executing the ``Ansys Python Manager.exe`` file.

Documentation
-------------

For building documentation, you can run the usual rules provided in the
`Sphinx`_ Makefile:

.. code:: bash

    pip install -e .[doc]
    doc/make.bat html
    # subsequently open the documentation with:
    <your_browser_name> doc/html/index.html

.. LINKS AND REFERENCES
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _pip: https://pypi.org/project/pip/
.. _venv: https://docs.python.org/3/library/venv.html
