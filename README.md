# OneDriveExplorer Summary:
OneDriveExplorer is a command line and GUI based application for reconstructing the folder structure of OneDrive from the `.\<UserCid>.dat` file.
# Usage:
## Command line
![](./Images/cmd_help.png)

To use OneDriveExporer, simply provide the `.\<UserCid>.dat` file to the `-f` argument
> OneDriveExplorer.py -f business1\d1a7c039-6175-4ddb-bcdb-a8de45cf1678.dat

OneDriveExplorer will produce a JSON file called OneDrive.json containing the folder structure. The `--pretty` option can be used to output the JSON into a more human readable layout.
![](./Images/json.png)
## GUI
The GUI consists of two panes: the folder structure on the left and details on the right. By clicking on one of the entries in the left pane, the details pane will populate with various data such as name, whether it is a file or folder, UUIDs and the number of children, if any.
![](./Images/gui.png)

# Todo
- [x] Add support for OneDrive personal
- [ ] GUI not populating correctly when opening different dat file