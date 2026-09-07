API reference
=============

The Radar Explorer Toolkit API contains the ``ToolkitBackend`` class, which provides methods for controlling the toolkit workflow. This API provides methods for synthesizing and creating an antenna. You use this toolkit's API at the toolkit level.

.. note::
    The `PyAEDT Common Toolkit <https://aedt.common.toolkit.docs.pyansys.com/>`_ provides the common methods for creating an AEDT session or connecting to an existing AEDT session.

You use the Radar Explorer Toolkit API to perform end-to-end workflows or directly postprocess radar results to display graphics objects and plot data.

Visualization
-------------

The Radar Explorer Toolkit API offers sophisticated tools for advanced monostatic RCS postprocessing. It contains two complementary classes: ``MonostaticRCSData`` and ``MonostaticRCSPlotter``.

- ``MonostaticRCSData``: Focuses on the direct access and processing of RCS solution data. It supports a comprehensive set of postprocessing operations, from visualizing radiation patterns to computing key performance metrics.

- ``MonostaticRCSPlotter``: Focuses on the postprocessing of RCS solution data.


.. currentmodule:: ansys.aedt.toolkits.radar_explorer.rcs_visualization

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   MonostaticRCSData
   MonostaticRCSPlotter


This code shows how to get RCS data and perform some postprocessing:

.. code:: python

    from ansys.aedt.core import Hfss
    from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter

    app = Hfss()
    rcs_object = app.get_rcs_data()
    rcs_plotter = MonostaticRCSPlotter(rcs_data=rcs_object.rcs_data)
    rcs_plotter.plot_rcs()

If you exported the RCS data previously, you can directly get this data:

.. code:: python

    from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter
    from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData

    input_file = r"path_to_data\pyaedt_rcs_metadata.json"
    rcs_data = MonostaticRCSData(input_file)
    rcs_plotter = MonostaticRCSPlotter(rcs_data)
    rcs_plotter.plot_cut()

The following diagram shows how both classes work. You can use them independently or from the ``get_rcs_data()`` method.

.. image:: ../_static/rcs_visualization_pyaedt.png
   :width: 800
   :alt: RCS Data
   :align: center

Workflow
--------

To perform an end-to-end workflow, use this class:

.. currentmodule:: ansys.aedt.toolkits.radar_explorer.backend.api

.. autosummary::
   :toctree: _autosummary

   ToolkitBackend

Here is an example of how you use it:

.. code:: python

    # Import required modules for the example
    import time
    from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData
    from ansys.aedt.toolkits.radar_explorer.rcs_visualization import (
        MonostaticRCSPlotter,
    )

    # Import backend
    from ansys.aedt.toolkits.template.backend.api import ToolkitBackend

    # Initialize generic service
    toolkit_api = ToolkitBackend()

    # Load default properties from a JSON file
    properties = toolkit_api.get_properties()

    # Set properties
    new_properties = {
        "num_phi": 101,
        "aspect_ang_phi": 80.0,
        "num_theta": 51,
        "aspect_ang_theta": 2.0,
    }
    flag4, msg4 = toolkit_api.set_properties(new_properties)
    properties = toolkit_api.get_properties()

    # Update RCS properties
    toolkit_api.update_rcs_properties(
        range_is_system=True, azimuth_is_system=True, elevation_is_system=True
    )

    # Launch AEDT
    thread_msg = toolkit_api.launch_thread(toolkit_api.launch_aedt)

    # Wait until thread is finished
    idle = toolkit_api.wait_to_be_idle()
    if not idle:
        print("AEDT not initialized.")
        sys.exit()

    # Create 3D component
    component_file = toolkit_api.generate_3d_component()

    # Insert SBR+ design
    _ = toolkit_api.insert_sbr_design(component_file, name="Trihedral_RCS")

    # Assign excitation
    v_plane_wave = toolkit_api.add_plane_wave(name="IncWaveVpol", polarization="Vertical")
    h_plane_wave = toolkit_api.add_plane_wave(name="IncWaveHpol", polarization="Horizontal")
    plane_wave_names = [v_plane_wave, h_plane_wave]

    # Create setup
    setup_name = toolkit_api.add_setup()

    # Analyze
    toolkit_api.analyze()
    toolkit_api.save_project()

    # Get RCS data

    rcs_metadata_vh = toolkit_api.export_rcs(
        h_plane_wave, "ComplexMonostaticRCSTheta", encode=False
    )
    rcs_metadata_hh = toolkit_api.export_rcs(
        h_plane_wave, "ComplexMonostaticRCSPhi", encode=False
    )

    # Load RCS data

    rcs_data_vv = MonostaticRCSData(metadata_file)
    rcs_data_vh = MonostaticRCSData(rcs_metadata_vh)

    # Load RCS Plotter

    rcs_data_vv_plotter = MonostaticRCSPlotter(rcs_data_vv)
    rcs_data_vh_plotter = MonostaticRCSPlotter(rcs_data_vh)

    # Select cut

    primary_sweep = "IWavePhi"
    secondary_sweep_value_vv = rcs_data_vv_plotter.rcs_data.incident_wave_theta
    secondary_sweep_value_vh = rcs_data_vh_plotter.rcs_data.incident_wave_theta

    # Plot RCS

    plot_vv = rcs_data_vv_plotter.plot_rcs(
        primary_sweep=primary_sweep, secondary_sweep_value=secondary_sweep_value_vv
    )
    plot_vh = rcs_data_vh_plotter.plot_rcs(
        primary_sweep=primary_sweep, secondary_sweep_value=secondary_sweep_value_vh
    )

    plot_vh_freq = rcs_data_vh_plotter.plot_rcs(
        primary_sweep="Freq", secondary_sweep="IWavePhi"
    )

    # Release AEDT
    toolkit_api.release_aedt()
