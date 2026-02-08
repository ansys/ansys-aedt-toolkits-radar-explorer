.. _installation:

Installation
############

You can install the Radar Explorer Toolkit using the latest installer from the repository's `Releases <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/latest>`_ page or install it from PyPI.

Install the toolkit using the installer
=======================================

Install the Radar Explorer Toolkit for your operating system using the latest installer:

.. tab-set::

  .. tab-item:: Windows

    To install the toolkit on Windows, follow these steps:

    #. Download the latest installer for Windows from the repository's `Releases <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/latest>`_ page.

       The file is named ``Radar-Explorer-Toolkit-Installer-windows.exe``.

    #. Run the installer.

    #. Search for ``Radar Explorer Toolkit`` and launch it.

    The **Radar Explorer Toolkit** window opens.

  .. tab-item:: Linux - Ubuntu

    .. tab-set::

      .. tab-item:: Ubuntu

        Supported Linux operating systems are Ubuntu 24.04 and 22.04. To install the toolkit on a supported Ubuntu version, follow these steps:

        #. Update the ``apt-get`` repository and install required packages with **sudo** privileges:

           .. code:: shell

             sudo apt-get update -y
             sudo apt-get install wget gnome libffi-dev libssl-dev libsqlite3-dev libxcb-xinerama0 build-essential -y

        #. Download and install the ``zlib`` library:

           .. code:: shell

             wget https://zlib.net/current/zlib.tar.gz
             tar xvzf zlib.tar.gz
             cd zlib-*
             make clean
             ./configure
             make
             sudo make install

        #. Download the latest Radar Explorer Toolkit installer for Ubuntu from the
           repository's `Releases <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/latest>`_ page.

           The file is named ``Radar-Explorer-Toolkit-Installer-ubuntu_*.zip``.

        #. Run this command in the terminal:

           .. code:: shell

             unzip Radar-Explorer-Toolkit-ubuntu_*.zip
             ./installer.sh

        #.  Search for ``Radar Explorer Toolkit`` and launch it.

        The **Radar Explorer Toolkit** window opens.

Uninstall the toolkit
=====================

To uninstall the Radar Explorer Toolkit, follow these steps:

#. From the toolkit's menu, select **File > Uninstall**.
#. Click **Uninstall**.

Install the toolkit with Python
===============================

Install the Radar Explorer Toolkit from PyPI like any other open source Python package. You can install both the backend (AI) and user interface (UI) methods or only the backend methods.

.. note::
    - If you have an existing virtual environment, skip step 1.
    - If you have already installed the toolkit in your virtual environment,
      skip step 2.

#. Create and activate a new Python virtual environment:

   .. code:: text

       # Create a virtual environment
       python -m venv .venv

       # Activate it in a POSIX system
       source .venv/bin/activate

       # Activate it in a Windows CMD environment
       .venv\Scripts\activate.bat

       # Activate it in Windows PowerShell
       .venv\Scripts\ActivateT.op si1

#. To install both the backend and UI methods from the GitHub repository:

   .. code:: bash

       python -m pip install ansys-aedt-toolkits-radar-explorer[all]

#. To install only the backend methods:

   .. code:: bash

       pip install ansys-aedt-toolkits-radar-explorer

#. If you installed both the backend and UI methods, launch the toolkit:

   .. code:: bash

       python .venv\Lib\site-packages\ansys\aedt\toolkits\radar_explorer\run_toolkit.py

   .. image:: ../_static/radar_settings.png
        :width: 800
        :alt: UI of the toolkit opened from the console, **Settings** tab

.. note::
   If you are a developer wanting to contribute to the Radar Explorer Toolkit, see :ref:`Contribute <contributing-main>`.
