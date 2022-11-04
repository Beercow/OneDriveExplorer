# OneDriveExplorer GUI

![](.\manual\ode.png)

Revision history  
date Rev. 1 - Initial Release

## OneDriveExplorer GUI Introduction
OneDriveExplorer GUI is used to view the contents of \<UserCid>.dat files. It can load multiple settings, logs, and $Recycle.bin files at once. Search across all settings files, view OneDrive logs and much more.
## Getting Started
After starting OneDriveExplorer, the main interface is displayed.

![](.\manual\startup.png)

Settings for themes, fonts, logs, output to csv, json, html are saved and reloaded between program executions. You can reset these options by deleting the ode.settings file.

### Interface sections
There are four sections to the main interface.

#### OneDrive Folders
On the left-hand side of the window is the OneDrive Folders tab. This tab displays the \<UserCid>.dat files that have been loaded and the folder structure of OneDrive. Once a \<UserCid>.dat file has been loaded and a folder/file has been selected, a context menu is available by right clicking on the folder/file. Context menu options will be discussed later.

#### Details
The Details pane shows detailed information about the folder/file selected. Information includes name, type, path, parentid, driveitemid, etag, and number of children.

#### Log Entries
The Log Entries pane shows related logs to the folder/file selected. This will only be populated if the OneDrive logs are parsed along with the \<UserCid>.dat file. This will be discussed in more detail.

#### Status bar
Across the bottom of the interface is a status bar as seen below.

![](.\manual\status.png)

The status bar contains a progress bar for the current running job and the total number of messages available on the Message form.  
Double clicking on the Total messages counter will show the Messages form. I there are any errors in the Messages form, the background will be yellow. If there are any errors, the background will be red. When the Messages form is viewed, the background will change back to the default color.

### Main Menu
The main menu contains options for loading \<UserCid>.dat files, preferences, themes, etc. Many of the menu items have shortcut keys. Pressing the keys shown by a menu item will activate the menu item.  
The next sections below will detail the submenus.

#### File
The File menu contains options for loading \<UserCid>.dat files and exporting.

![](.\manual\file_menu.png)

* Live system: Preforms a scan of the live system and loads any OneDrive information found. *Must be run as Administrator.
* OneDrive settings: Allows for loading/unloading OneDrive settings files. OneDrive settings will be discussed below.
* OneDrive logs: Allows for loading/unloading OneDrive ODL logs.
* Project: Allows for loading/saving of projects. Projects will be discussed below.
* Export 'OneDrive Folders': Exports what is shown in the OneDrive Folders tab.  
As an example, if the OneDrive Folders tab looks like this:

![](.\manual\onedrive_folders.png)

Exporting to PDF would generate a PDF file that contains the following:

![](.\manual\onedrive_folders2.png)

This can be useful for adding to reports or other documentation.

#### Options
The Options menu contains items for the look and feel and preferences of OneDriveExplorer.

![](.\manual\options_menu.png)

* Font: Change the font type, style and size. Applies to the Details, Log entries, and Log tabs.
* Skins: Change the overall look of OneDriveExplorer.
* Preferences: Program options such as auto save, disabling the user hive dialog, and ODL settings.  

The Preferences dialog allows you to change various OneDriveExplorer settings as seen below.

![](.\manual\preferences.png)

#### View
The View menu contains one option, Messages.

Messages toggles the visibility of the Messages window. The messages window displays status messages on the parsing process. The total number of messages is also shown on the main window's bottom status bar to the far right. Double clicking the message count will also show the Messages window.

![](.\manual\messages.png)

As mentioned above, the background of the messages count will be yellow if a warning message exists and red if an error message exists. The background will return to default when the Messages window is shown.  
The Messages window contains two options. One for clearing the messages and the other to export the messages. Exporting the messages can be useful for troubleshooting the application.

![](.\manual\messages_number.png)

#### Help
The help menu contains two options: Quick help and About.

## Using OneDriveExplorer
### Loading data
Loading data in OneDriveExplorer can happen in multiple ways. This includes Live system, \<UserCid>.dat files, ODL logs, output from command line runs, projects, etc. The following sections will walk through loading data in OneDriveExplorer.

#### Live system
*Note: OneDriveExplorer must be run as an administrator of this option to be enabled.  
Live system scans the current system looking for \<UserCid>.dat, NTUSER.dat, $Recycle.Bin, and OneDrive logs (if log parsing is enabled). Information will be parsed and loaded into OneDriveExplorer.

![](.\manual\live.png)

#### OneDrive settings
OneDrive settings contains three options for loading \<UserCid>.dat data: Load \<UserCid>.dat, Import JSON, and Import CSV.

![](.\manual\odsettings.png)

##### Load \<UserCid>.dat
Use this option to load a \<UserCid>.dat file. Default location is *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\settings\\<Personal\Business>*. Once a file is selected, OneDriveExplorer will prompt to load a User Hive and the $Recycle.Bin folder.

![](.\manual\userhive.png)

![](.\manual\recbin.png)

You can bypass these dialogs in one of two ways:
* Holding down SHIFT when loading \<UserCid>.dat
* In the Preferences dialog

![](.\manual\preferences1.png)

##### Import JSON
Import JSON allows for loading a previously saved JSON file from the command line or GUI application.

##### Import CSV
Import CSV allows for loading a previously saved CSV file from the command line or GUI application.

#### OneDrive logs
*Note: This option is only available if enabled in the Preferences dialog.  
Use this option to load OneDrive log files. The default location is *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\logs\\<Personal\Business>*. If the *ObfuscationStringMap.txt* file is found, it will be used to automatically deobfuscate the logs. There is another form of obfuscation that uses *general.keystor* but this has not been implemented yet. OneDrive logs will be discussed later.

#### Projects
Projects allow you to load one or more \<UserCid>.dat and log files; save the currently loaded \<UserCid>.dat and log files. This allows for quickly loading the same \<UserCid>.dat and log files for a particular case versus loading the files individually. Projects are saved with a *.ode_proj* extension.

### Selecting Folders/Files
Selecting Folders/Files in OneDriveExplorer works much the same as it does in Windows Explorer. Clicking the small arrow to the left of the folder or double clicking the folder will expand that folder.

### Finding Folders/Files
The top of the OneDrive Folders tab contains a simple entry box to enter text to find. If the text is found, the Folders/Files will be highlighted in yellow.

![](.\manual\find.png)

### Folders/Files context menu
The context menu changes dynamically depending on what you right click on. Most common functions are copy Name, Path, or Details. Folder entries allow for expanding and collapsing the tree structure. Top level entries have the option to unload the entire OneDrive folder structure.

![](.\manual\context.png)

### Details
When a Folder/File is selected, the Details pane is populated with various data about the selection.

![](.\manual\details.png)

* Name: Name of the Folder/File
* Type: What type of object is it. These can include:
  * Root Drive
  * Root Default
  * Root Shared
  * Folder
  * File
* Path: Full path to Folder/File
* Size: Size of file
* Hash: Hash of file
  * SHA1 for personal
  * quickXor for business
* ParentId: Specifies the identifier of the parent item
* DriveItemId: Represents a file/folder stored in OneDrive
* eTag: ETag for the entire item (metadata + content)
* Children: Number of files/folders below selected item

### OneDrive Logs
OneDrive logs are stored as binary files with extensions .odl, .odlgz, .odlsent and .aold usually found in the following location: *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\logs\\<Personal\Business>*. When loaded, new tabs will be populated with the logs for each user next to the OneDrive Folders tab.

![](.\manual\logs.png)

Selecting one of these tabs will bring up the logs for that user. From the log tab, you can sort columns and pop out individual cells.  
From the OneDrive Folders tab, selecting a file/folder will populate the Log Entries tab with some, not all, of the logs associated with the file/folder. This can be useful to see what activities have taken place on the file/folder.

![](.\manual\logs2.png)

# OneDriveExplorer
## OneDriveExplorer Introduction
OneDriveExplorer is a tool used to parse \<UserCid\>.dat files and reconstruct the folder structure of OneDrive. \<UserCid\>.dat files are commonly found at %USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\settings\\<Personal\Business>

## OneDriveExplorer Switches

In a command prompt, running OneDriveExplorer.exe will provide the following options:

```
usage: OneDriveExplorer.py [-h] [-f FILE] [-d DIR] [-r REGHIVE] [-rb RECYCLE_BIN] [--csv CSV] [--csvf CSVF]
                           [--html HTML] [--json JSON] [--pretty] [--debug] [-l [LOGS]]

options:  
  -h, --help            show this help message and exit  
  -f FILE, --file FILE  <UserCid>.dat file to be parsed  
  -d DIR, --dir DIR     Directory to recursively process, looking for <UserCid>.dat, NTUSER hive, $Recycle.Bin, and  
                        ODL logs. This mode is primarily used with KAPE.  
  -r REGHIVE, --REG_HIVE REGHIVE  
                        If a registry hive is provided, then the mount points of the SyncEngines will be resolved.  
  -rb RECYCLE_BIN, --RECYCLE_BIN RECYCLE_BIN  
                        $Recycle.Bin  
  --csv CSV             Directory to save CSV formatted results to. Be sure to include the full path in double quotes.  
  --csvf CSVF           File name to save CSV formatted results to. When present, overrides default name.  
  --html HTML           Directory to save html formatted results to. Be sure to include the full path in double  
                        quotes.  
  --json JSON           Directory to save json representation to. Use --pretty for a more human readable layout.  
  --pretty              When exporting to json, use a more human readable layout. Default is FALSE  
  --debug               Show debug information during processing.  
  -l [LOGS], --logs [LOGS]  
                        Directory to recursively process for ODL logs. Experimental.  
  ```
  
### Switch Descriptions
  
**-r**  
This switch will instruct OneDriveExplorer to use the registry hive supplied to resolve OneDrive mount points.  
Example: 
>OneDriveExplorer.exe -f \<file> -r NTUSER.dat  

**-rb**  
This switch will instruct OneDriveExplorer to use the $Recycle.Bin supplied to look for deleted files. This switch can only be used when a registry hive is supplied.  
Example:
>OneDriveExplorer.exe -f \<file> -r NTUSER.dat -rb c:\\$Recycle.Bin

## OneDriveExplorer Command Examples
### Example OneDriveExplorer Commands

## OneDriveExplorer Output
### Analyzing OneDriveExplorer Output - CSV

# OneDriveExplorer cstruct "mapping" files
