import os
import re
import yaml
from datetime import datetime
import warnings

def rename_block(block_path):
    """Rename the files in a folder using a BIDS-compliant naming convention.

    This function renames the files in a given folder using a BIDS-compliant naming
    convention based on the file names, and saves a log of the renaming operation to a
    YAML file. The function also checks that the file names in the folder follow the
    expected pattern, and that the file extensions are proper. If any of these checks
    fail, the function raises an error.

    Parameters
    ----------
    block_path : str
        The path to the folder containing the files to be renamed.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If the file names in the folder do not follow the expected pattern, or if the
        file extensions are not proper.
    """
    # TODO: Use multiple helper functions to write the renaming as needed

    # Initialize an empty list to store the patterns and new names for the files
    patterns = []
    new_names = []
    files_in_dir = os.listdir(block_path)

    # Iterate over the files in the folder
    for file in files_in_dir:
        # Use a regular expression to match the desired pattern in the file name
        # experiment_name-YYMMDD-HHMMSS_ID-YYMMDD-HHMMSS-suffix
        pattern = r"^(.+?)-(\d{6})-(\d{6})_(.+?)-(\d{6})-(\d{6})(.*?)(\.\w+)$"
        match = re.match(pattern, file)

        # If the pattern is found in the file name
        if match:
            # Extract the groups from the regular expression match
            experiment_name = match.group(1)
            version_date = match.group(2)
            version_time = match.group(3)
            identifier = match.group(4)
            start_date = match.group(5)
            start_time = match.group(6)
            # this will be anything after the last pattern, except the file extension
            suffix = match.group(7).replace("_", "") # clean any underscores here
            # this will be the file extension
            file_extension = match.group(8)
            # Store the pattern in the list
            patterns.append(f"{experiment_name}-{version_date}-{version_time}_{identifier}-{start_date}-{start_time}")
            # Generate the new name for the file using the session timestamp
            if suffix=="":
                new_name = bids_format(identifier, start_date, start_time)
                new_name = f"{new_name}{file_extension}"
            else:
                new_name = bids_format(identifier, start_date, start_time, suffix=f"{suffix}{file_extension}")

            # Add the new name to the list
            new_names.append(new_name)
        else:
            if "identifier" not in locals():
                warnings.warn(f"cannot find identifier in {file}. File will not be renamed")
                new_name = file
            else:
                # If the exppattern is not found, use the original file name as the new name
                new_name = bids_format(identifier, start_date, start_time, suffix = file)

                # Add the new name to the list
            new_names.append(new_name)

    # Check that all the patterns in the list are identical
    if len(set(patterns)) > 1:
        raise ValueError("Error: The files in the folder have different patterns.")

    # Check that the file extensions are proper
    if not all(
        os.path.splitext(file1)[1] == os.path.splitext(file2)[1]
        for file1, file2 in zip(files_in_dir, new_names)
    ): 
        raise ValueError("Some of the file extensions do not match")

    # Create a dictionary to store the renaming operation
    renaming_dict = dict(zip(files_in_dir, new_names))

    # Print a verbose output of the renaming operation
    print("Renaming")
    for original_name, new_name in renaming_dict.items():
        print(f"Original name: {original_name} -> New name: {new_name}")
        os.rename(os.path.join(block_path, original_name), os.path.join(block_path, new_name))

    # Save a log of the renaming operation
    renaming_dict['experiment_name'] = experiment_name
    renaming_dict['experiment_version'] = f"{version_date}T{version_time}"

    # Write the dictionary to a YAML file and save it to the directory
    yaml_name = os.path.join(block_path, f"{bids_format(identifier, start_date, start_time, suffix='tdt_renaming')}.yaml")
    with open(yaml_name, "w") as file:
        yaml.dump(renaming_dict, file)

def bids_format(identifier, start_date, start_time=None, suffix=None):
    # Check if b can be coerced to a date
    try:
        datetime.strptime(start_date, "%Y%m%d")
    except ValueError:
        try:
            datetime.strptime(start_date, "%y%m%d")
        except ValueError:
            raise ValueError("start_date is not in the correct format. Expecting YYMMDD or YYYYMMDD, got {start_date}")
    
    if start_time is None and suffix is None:
        return f"sub-{identifier}_ses-{start_date}"
    elif suffix is None:
        try:
            datetime.strptime(start_time, "%H%M%S")
        except ValueError:
            raise ValueError("start_time is not in the correct format. Expecting HHMMSS, got {start_time}")
        return f"sub-{identifier}_ses-{start_date}T{start_time}"
    else:
        return f"sub-{identifier}_ses-{start_date}T{start_time}_desc-{suffix}"
