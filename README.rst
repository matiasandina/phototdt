========
phototdt
========


.. image:: https://img.shields.io/pypi/v/phototdt.svg
        :target: https://pypi.python.org/pypi/phototdt

.. image:: https://img.shields.io/travis/matiasandina/phototdt.svg
        :target: https://travis-ci.com/matiasandina/phototdt

.. image:: https://readthedocs.org/projects/phototdt/badge/?version=latest
        :target: https://phototdt.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/matiasandina/phototdt/shield.svg
     :target: https://pyup.io/repos/github/matiasandina/phototdt/
     :alt: Updates



This Python package contains functions to get photometry data from a Tucker-Davis Technology (TDT) photomerty system and calculate dFF using methods developed by Martianova and colleagues. For more information on the analysis method, you can visit `Martianova, E., Aronson, S., Proulx, C.D. Multi-Fiber Photometry to Record Neural Activity in Freely Moving Animal.. J. Vis. Exp. (152), e60278, doi: 10.3791/60278 (2019).`_. Implementation details and other language implementations (R, Matlab) are archived in `the publication's repository`_


* Free software: BSD license
* Documentation: https://phototdt.readthedocs.io.


Features
--------

This package reads TDT data from the directory of the block (e.g., ``photometry_dir``)

* Use ``photo_data = phototdt.get_tdt_data(photometry_dir)`` to read and obtain a DataFrame photometry data.
* Use ``phototdt.tdt_to_csv.tdt_to_csv(photometry_dir)`` to convert block to a csv file and calculate zdFF on the 465 channel.
* Use ``phototdt.get_cam_timestamps(photometry_dir)`` to read camera timestamps from block. 

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`Martianova, E., Aronson, S., Proulx, C.D. Multi-Fiber Photometry to Record Neural Activity in Freely Moving Animal.. J. Vis. Exp. (152), e60278, doi: 10.3791/60278 (2019).`: https://www.jove.com/t/60278/multi-fiber-photometry-to-record-neural-activity-freely-moving
.. _`the publication's repository`: https://github.com/katemartian/Photometry_data_processing
