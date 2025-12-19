.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.5.0 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.5.0>`_ - December 19, 2025
==============================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Initial commit.
          - `#1 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/1>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/download-artifact from 5.0.0 to 6.0.0
          - `#213 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/213>`_

        * - Bump actions/upload-artifact from 4.6.2 to 5.0.0
          - `#215 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/215>`_

        * - Bump actions/checkout from 5.0.0 to 6.0.1
          - `#219 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/219>`_

        * - Bump softprops/action-gh-release from 2.3.3 to 2.5.0
          - `#220 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/220>`_

        * - Bump ansys/actions from 10.1.4 to 10.2.3
          - `#221 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/221>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix vale warning
          - `#210 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/210>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Restore pypi release step
          - `#4 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/4>`_

        * - Update CHANGELOG for v0.4.0
          - `#207 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/207>`_

        * - Fix permissions for doc deploy
          - `#208 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/208>`_

        * - Bump 0.5.dev0
          - `#209 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/209>`_

        * - Add action security checking
          - `#211 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/211>`_

        * - Update license to Apache-2.0
          - `#216 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/216>`_

        * - Fix condition in \`\`block-dependabot\`\` check
          - `#222 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/222>`_

        * - Review permissions for jobs in workflows and provide comments where needed
          - `#223 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/223>`_


`0.4.0 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.4.0>`_ - October 09, 2025
======================================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add materials to UI
          - `#189 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/189>`_

        * - Allow IE simulations
          - `#190 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/190>`_

        * - Hide model units when RCS is loaded
          - `#197 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/197>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump softprops/action-gh-release from 2.3.2 to 2.3.3
          - `#174 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/174>`_

        * - Bump ansys/actions from 10.0.20 to 10.1.1
          - `#175 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/175>`_

        * - Bump ansys/actions from 10.1.1 to 10.1.2
          - `#196 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/196>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improve custom object usage
          - `#173 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/173>`_

        * - Update installer for matplotlib
          - `#188 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/188>`_

        * - Add binaries to frozen.spec
          - `#202 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/202>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.3.0
          - `#171 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/171>`_

        * - Bump v0.4.dev0
          - `#172 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/172>`_

        * - Update CHANGELOG for v0.3.1
          - `#201 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/201>`_

        * - Add extra changes for open sourcing the project
          - `#206 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/206>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Extend UI testing of home menu
          - `#166 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/166>`_

        * - Introducing tests for covering \`\`common_windows_utils.py\`\`
          - `#193 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/193>`_

        * - Update tests for \`\`common_windows_utils\`\`
          - `#195 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/195>`_


`0.3.1 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.3.1>`_ - October 07, 2025
=========================================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.1.2 to 10.1.4
          - `#199 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/199>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Overall review
          - `#191 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/191>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Increase coverage
          - `#194 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/194>`_


`0.3.1 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.3.1>`_ - October 01, 2025
=========================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add materials to UI
          - `#189 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/189>`_

        * - Allow IE simulations
          - `#190 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/190>`_

        * - Hide model units when RCS is loaded
          - `#197 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/197>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump softprops/action-gh-release from 2.3.2 to 2.3.3
          - `#174 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/174>`_

        * - Bump ansys/actions from 10.0.20 to 10.1.1
          - `#175 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/175>`_

        * - Bump ansys/actions from 10.1.1 to 10.1.2
          - `#196 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/196>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improve custom object usage
          - `#173 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/173>`_

        * - Update installer for matplotlib
          - `#188 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/188>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.3.0
          - `#171 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/171>`_

        * - Bump v0.4.dev0
          - `#172 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/172>`_

        * - Increase cov
          - `#194 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/194>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Extend UI testing of home menu
          - `#166 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/166>`_

        * - Introducing tests for covering \`\`common_windows_utils.py\`\`
          - `#193 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/193>`_

        * - Update tests for \`\`common_windows_utils\`\`
          - `#195 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/195>`_


`0.3.0 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.3.0>`_ - September 19, 2025
===========================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add model units in UI
          - `#167 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/167>`_

        * - Add expiration date
          - `#168 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/168>`_

        * - Change incident angle names
          - `#169 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/169>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/download-artifact from 4.3.0 to 5.0.0
          - `#146 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/146>`_

        * - Bump actions/checkout from 4.2.2 to 5.0.0
          - `#149 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/149>`_

        * - Bump ansys/actions into v10.0.14 and update dependabot / code owners
          - `#154 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/154>`_

        * - Bump ansys-sphinx-theme from 1.5.3 to 1.6.0
          - `#155 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/155>`_

        * - Bump ansys/actions into v10.0.15
          - `#157 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/157>`_

        * - Bump actions/setup-python from 5.6.0 to 6.0.0
          - `#164 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/164>`_

        * - Bump actions/labeler from 5.0.0 to 6.0.1
          - `#165 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/165>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Rendering of plots using ``pyvista`` in documentation
          - `#141 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/141>`_

        * - Interactive ``pyvista`` plots in documentation
          - `#143 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/143>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Documentation API
          - `#147 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/147>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update changelog for v0.2.1
          - `#140 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/140>`_

        * - Update workflow to use dedicated runner
          - `#145 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/145>`_

        * - Avoid running job with dependabot's PR unless accepted
          - `#156 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/156>`_

        * - Increase coverage
          - `#163 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/163>`_

        * - Increase actions coverage
          - `#170 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/170>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Replace ``black`` badge with ``ruff`` badge in ``README.rst``
          - `#142 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/142>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Introduce UI tests for the help menu
          - `#148 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/148>`_

        * - Gracefully handle VTK when closing UI multiple times
          - `#152 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/152>`_

        * - Extend menu testing and refactor code base
          - `#153 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/153>`_


`0.2.1 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.2.1>`_ - July 08, 2025
======================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add interpolation customizations for 2D and 3D ISAR
          - `#117 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/117>`_

        * - Plot lower from higher data with rotation in 3d view
          - `#125 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/125>`_

        * - Projection mode for 2D ISAR
          - `#127 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/127>`_

        * - Add projection plots for 3D ISAR plots
          - `#133 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/133>`_

        * - Edit 3D plot name and min and max values
          - `#137 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/137>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 9 to 10
          - `#123 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/123>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update documentation
          - `#122 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/122>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Orthographic label shows up as default, but it should be perspective
          - `#120 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/120>`_

        * - Correct 2d isar cuts
          - `#129 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/129>`_

        * - Update vtk osmesa
          - `#139 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/139>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.2.0
          - `#115 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/115>`_

        * - Update dev version 0.3.dev0
          - `#118 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/118>`_

        * - Setting up ``ruff``
          - `#136 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/136>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improve repository settings
          - `#135 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/135>`_


`0.2.0 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.2.0>`_ - May 30, 2025
=====================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Implement 3D ISAR
          - `#96 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/96>`_

        * - Switch to fast regular-grid 3D complex interpolator for 3D ISAR
          - `#98 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/98>`_

        * - Add a colormap choice for results
          - `#104 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/104>`_

        * - Run simulation in non graphical by default
          - `#106 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/106>`_

        * - Use uniform linear interpolator for 2D ISAR
          - `#108 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/108>`_

        * - 3D plot computation in a separated thread
          - `#109 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/109>`_

        * - Point cloud rendering mode for ISAR 3D
          - `#111 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/111>`_

        * - Improve 3D Settings column
          - `#114 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/114>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Delete 2D plots
          - `#97 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/97>`_

        * - Not rotation of imported geometry
          - `#103 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/103>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.1.4
          - `#90 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/90>`_


`0.1.4 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.1.4>`_ - May 27, 2025
=====================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - UI improvements
          - `#88 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/88>`_

        * - Add on/off in toggle
          - `#89 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/89>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.1.3
          - `#72 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/72>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - New toolkit name
          - `#73 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/73>`_


`0.1.3 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.1.3>`_ - May 20, 2025
=====================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add UI enhancements
          - `#68 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/68>`_

        * - UI clean-up, remove RCS and waterfall solve modes
          - `#70 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/70>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/download-artifact from 4.1.9 to 4.3.0
          - `#67 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/67>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Apply correct CAD model translation
          - `#69 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/69>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.1.2
          - `#66 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/66>`_

        * - Fix Linux version in CICD
          - `#71 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/71>`_


`0.1.2 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.1.2>`_ - May 16, 2025
=====================================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - UI improvements and save configuration file
          - `#59 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/59>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Documentation
          - `#63 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/63>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - ISAR 2D range extents
          - `#61 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/61>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.1.1
          - `#60 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/60>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Move RCS visualization
          - `#64 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/64>`_


`0.1.1 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.1.1>`_ - May 14, 2025
=====================================================================================================

.. tab-set::


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.1.0
          - `#57 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/57>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update Python 3.12
          - `#58 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/58>`_


`0.1.0 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v0.1.0>`_ - May 08, 2025
=====================================================================================================

.. tab-set::


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add CHANGELOG
          - `#53 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/53>`_

        * - Updates to release
          - `#55 <https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/pull/55>`_


.. vale on