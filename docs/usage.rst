=====
Usage
=====

To use phototdt in a project::

    import phototdt
    session_folder = "path/to/block/folder"
    # Get tdt data
    photo_data = phototdt.get_tdt_data(session_folder)
    # Get camera timestamps
    from phototdt.phototdt import get_cam_timestamps
    cam_timestamps = get_cam_timestamps(folder=session_folder)
    # Convert photometry data from block to csv (interactive if folder is None)
    from phototdt.tdt_to_csv import tdt_to_csv 
    tdt_to_csv(session_folder)
:::

You can rename the block contents into BIDS format::
    from phototdt.rename_block import rename_block
    session_folder = "path/to/block/folder"
    rename_block(session_folder)
:::