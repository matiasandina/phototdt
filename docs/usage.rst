=====
Usage
=====

To use phototdt in a project::

    # Get camera timestamps
    session_folder = "path/to/block/folder"
    from phototdt.phototdt import get_cam_timestamps
    cam_timestamps = get_cam_timestamps(folder=session_folder)
    # Convert data from block (interactive if folder is None)
    from phototdt.tdt_to_csv import tdt_to_csv 
    tdt_to_csv(session_folder)

