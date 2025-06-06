# OneDriveExplorer

![](.\manual\ode.png)

**Revision history**  
2022-11-08 Rev. 1 - Initial Release  
2022-12-07 Rev. 2 - Updated for v2022.12.08  
2023-03-10 Rev. 3 - Updated for v2023.03.10  
2023-05-05 Rev. 4 - Updated for v2023.05.05  
2023-09-07 Rev. 5 - Updated for v2023.09.07  
2023-12-13 Rev. 6 - Updated for v2023.12.13  
2024-10-31 Rev. 7 - Updated for v2024.11.01
2025-05-13 Rev. 8 - Updated for v2025.05.13

## OneDriveExplorer GUI Introduction
OneDriveExplorer GUI is used to view the contents of \<UserCid>.dat files. It can load multiple settings, logs, and $Recycle.bin files at once. Search across all settings files, view OneDrive logs and much more.
## Getting Started
After starting OneDriveExplorer, the OneDrive data view is displayed.

![](.\manual\startup.png)

Settings for themes, fonts, logs, output to csv, json, html are saved and reloaded between program executions. You can reset these options by deleting the ode.settings file.

### OneDrive Data View sections
There are five sections to the main interface.

#### Navigation Pane
On the left-hand side of the window is the navigation pane. This pane displays the \<UserCid>.dat and SQLite files that have been loaded and the folder structure of OneDrive. Once a \<UserCid>.dat and/or SQLite file has been loaded and a folder has been selected, a context menu is available by right clicking on the folder. Context menu options will be discussed later.

#### File/Folder Pane
The file/folder pane shows the contents of the folder selected in the navigation pane along with it's OneDrive status. Once a file/folder has been loaded and a folder has been selected, a context menu is available by right clicking on the file/folder. Context menu options will be discussed later.

##### Status
File folder status is a s follows:  
![](.\Manual\blog2.png)

<span style="color:red">*Note: Not Synced and Not Linked do not exist on the endpoint. These are artifacts of syncing and linking libraries.</span>

#### Details
The Details pane shows detailed information about the folder/file selected. Information includes name, type, path, parentid, driveitemid, etag, and number of children.

#### Log Entries
The Log Entries pane shows related logs to the folder/file selected. This will only be populated if the OneDrive logs are parsed along with the \<UserCid>.dat/SQLite file. This will be discussed in more detail.

#### Status bar
Across the bottom of the interface is a status bar as seen below.

![](.\manual\status.png)

The status bar contains a progress bar for the current running job and the total number of messages available on the Message form.  
Double clicking on the Total messages counter will show the Messages form. I there are any errors in the Messages form, the background will be yellow. If there are any errors, the background will be red. When the Messages form is viewed, the background will change back to the default color.

### Main Menu
The main menu contains options for loading \<UserCid>.dat files, preferences, themes, etc. Many of the menu items have shortcut keys. Pressing the keys shown by a menu item will activate the menu item.  
The next sections below will detail the submenus.

#### File
The File menu contains options for loading OneDrive settings files and exporting.

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

* Font: Change the font type, style, and size. Applies to the Details, Log entries, and Log tabs.
* Skins: Change the overall look of OneDriveExplorer.
* Sync with Github: Downloads the latest Cstructs from https://github.com/Beercow/ODEFiles
* Preferences: Program options such as auto save, disabling the user hive dialog, and ODL settings.  

The Preferences dialog allows you to change various OneDriveExplorer settings as seen below.

![](.\manual\preferences.png)

#### View
The View menu contains two options: Messages and CStructs.

![](.\manual\view.png)

##### Messages
Messages toggles the visibility of the Messages window. The messages window displays status messages on the parsing process. The total number of messages is also shown on the main window's bottom status bar to the far right. Double clicking the message count will also show the Messages window.

![](.\manual\messages.png)

As mentioned above, the background of the messages count will be yellow if a warning message exists and red if an error message exists. The background will return to default when the Messages window is shown.  
The Messages window contains two options. One for clearing the messages and the other to export the messages. Exporting the messages can be useful for troubleshooting the application.

![](.\manual\messages_number.png)

##### CStructs
The CStructs option displays a list of available cstructs for a given code file. Details include author, functions, and description. CStructs will be discussed in more detail in a dedicated section of this manual.

#### Help
The help menu contains two options: Quick help and About.

## Using OneDriveExplorer
### Loading data
Loading data in OneDriveExplorer can happen in multiple ways. This includes Live system, \<UserCid>.dat files, ODL logs, output from command line runs, projects, etc. The following sections will walk through loading data in OneDriveExplorer.

#### Live system
*Note: OneDriveExplorer must be run as an administrator of this option to be enabled.  
Live system scans the current system looking for \<UserCid>.dat/SQLite, NTUSER.dat, $Recycle.Bin, and OneDrive logs (if log parsing is enabled). Information will be parsed and loaded into OneDriveExplorer.

![](.\manual\live.png)

#### OneDrive metadata
OneDrive metadat contains three options for loading a user's profile, individual files, or saved data from OneDriveExplorer.

![](.\manual\odsettings.png)

##### Profile
Use this option to load a user's OneDrive profile. Default location is *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\\*. Once the folder is selected, OneDriveExplorer will prompt to load a User Hive and the $Recycle.Bin folder.

![](.\manual\userhive.png)

![](.\manual\recbin.png)

You can bypass these dialogs in one of two ways:
* Holding down SHIFT when loading \<UserCid>.dat
* In the Preferences dialog

![](.\manual\preferences1.png)

##### Load Individual Files
Use this option to loose or individual OneDrive metadata files. When selected, OneDriveExplorer will present options for metadata files to load.

![](.\manual\loose.png)

Default location for metadata files:  
**\<userCid>.dat**: *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\settings\\<Personal\Business[1-9]>*  
**SyncEngineDatabase.db**: *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\settings\\<Personal\Business[1-2]>*  
**SafeDelete.db**: *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\settings\\<Personal\Business[1-9]>*  
**Microsoft.ListSync.db**: *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\ListSync\Business1[1-9]\settings\\<Personal\Business[1-9]>*  
**Microsoft.FileUsageSync.db**: *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\ListSync\Business1[1-9]\settings\\<Personal\Business[1-9]>*  
**NTUSER.DAT**: *%USERPROFILE%*  
**$Recycle.Bin**: *%SystemDrive%*

##### Import Saved data
Import Saved Data has two options. Import JSON and Import CSV.

![](.\manual\import_saved_data.png) 

###### Import JSON
Import JSON allows for loading a previously saved JSON file from the command line or GUI application.

###### Import CSV
Import CSV allows for loading a previously saved CSV file from the command line or GUI application.

![](.\manual\import_csv.png)

#### OneDrive logs
*Note: This option is only available if enabled in the Preferences dialog.  
OneDrive logs contains two options for loading ODL data: Load ODL logs and Import csv. OneDrive logs will be discussed later. 

![](.\manual\odlogs.png)

##### Load ODL logs
Use this option to load OneDrive log files. The default location is *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\logs\\<Personal\Business>*. If the *ObfuscationStringMap.txt* or *general.keystor* file is found, it will be used to automatically deobfuscate the logs.

##### Import CSV
Import CSV allows for loading a previously saved CSV file from the command line or GUI application.

#### Projects
Projects allow you to load one or more \<UserCid>.dat and log files; save the currently loaded \<UserCid>.dat and log files. This allows for quickly loading the same \<UserCid>.dat and log files for a particular case versus loading the files individually. Projects are saved with a *.ode_proj* extension.

### Selecting columns
Columns can be added or removed by right clicking the column header in the file/folder pane. Columns that can be selected include Date Created, Date Accessed, Date Modified, and Size. The version of ONeDrive determines if this data will be available.

![](.\manual\columns.png)

### Selecting Folders/Files
Selecting Folders/Files in OneDriveExplorer works much the same as it does in Windows Explorer. Clicking the small arrow to the left of the folder or double clicking the folder will expand that folder.

### Finding Folders/Files
The top of the OneDrive Folders tab contains a simple entry box to enter text to find. If the text is found, the Folders/Files will be populated in the middle pane.

![](.\manual\find.png)

### Folders/Files context menu
The context menu changes dynamically depending on what you right click on. Most common functions are copy Name, Path, Details, or Log Entries. Folder entries allow for expanding and collapsing the tree structure. Top level entries have the option to unload the entire OneDrive folder structure.

![](.\manual\context.png)

### File/Folder Details Pane
When a Folder/File is selected, the Details pane is populated with various data about the selection. There can be up to four tabs with different information about the file/folder.

![](.\manual\details.png)

**<u>These include:</u>**
* **Details**: Basic details for the file/folder
  * Name: Name of the Folder/File
  * Path: Full path to Folder/File
  * Size: Size of file
  * Hash: Hash of file
    * SHA1
    * quickXor
  * parentResourceID: Specifies the identifier of the parent item
  * resourceID: Represents a file/folder stored in OneDrive
  * eTag: ETag for the entire item (metadata + content)  
<br>
* **Metadata**: Additional metadata about the file if available
  * resourceID: Represents a file/folder stored in OneDrive
  * fileName: Name of file
  * spoCompositeID: A unique ID that is a composite of the following values:
    * siteID
    * webID
    * listID
  * createdBy: User that created the file
  * modified by: Last user to modify file
  * fileExtension: The extension of the file
  * lastWriteCount: Number indicating order files were written to  
<br>
* **MetadataJSON**: Contains information related to image, audio, and video files  
<br>
* **filePolicies**: Contains information about the policies applied to the file in OneDrive

### OneDrive Logs
OneDrive logs are stored as binary files with extensions .odl, .odlgz, .odlsent and .aold usually found in the following location: *%USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\logs\\<Personal\Business>*. When loaded, new tabs will be populated with the logs for each user next to the OneDrive Folders tab.

![](.\manual\logs.png)

Selecting one of these tabs will bring up the logs for that user. From the log tab, you can sort columns and pop out individual cells.  
From the OneDrive Folders tab, selecting a file/folder will populate the Log Entries tab with some, not all, of the logs associated with the file/folder. This can be useful to see what activities have taken place on the file/folder.

![](.\manual\logs2.png)

### Email Data View sections
There are three sections to the Email data view.

![](.\manual\email.png)

#### Email List
List of emails and dates that are contained in the OneDrive metadata.

#### Email Information
Information on the selected email such as: Subject, ConversationId, From, To, Date, and File Name.

#### File data
This section contains information on the file being shared in the email.

### Meeting Data View sections
There are four sections to the Meeting data view.

![](.\manual\meeting.png)

#### Meeting List
List of meetings that are contained in the OneDrive metadata.

#### Meeting Information
Information on the selected meeting such as: Title, ICalUid, ConversationId, MeetingStartTime, isRecurring, File Name, File Share Data.

#### File data
This section contains information on the file being shared in the meeting.

#### Participant List
List of participants in the meeting.

### Event Data View sections
There are four sections to the Event data view.

![](.\manual\event.png)

#### Event List
List of events that are contained in the OneDrive metadata.

#### Event Information
Information on the selected event such as: Title, ICalUid, ConversationId, MeetingStartTime, isRecurring, File Name, File Share Data.

#### File data
This section contains information on the file being shared in the event.

#### Participant List
List of participants in the event.

### Chat Data View sections
There are three sections to the Chat data view.

![](.\manual\chat.png)

#### Chat List
List of Teams chats that are contained in the OneDrive metadata.

#### File data
This section contains information on the file being shared in the Teams chat.

#### Participant List
List of participants in the Teams Chat.

### Note Data View sections
There are three sections to the Note data view. These are Teams chats that are with the user only.

![](.\manual\note.png)

#### Note List
List of Teams chats that are contained in the OneDrive metadata.

#### File data
This section contains information on the file being shared in the Teams chat.

#### Participant List
List of participants in the Teams Chat.

### SharePoint Data View sections
There are three sections to the SharePoint data view. These are Teams chats that are with the user only.

![](.\manual\sharepoint.png)

#### SharePoint List
List of SharePoint sites that are contained in the OneDrive metadata.

#### SharePoint Shared files
List of files shared with the user from SharePoint.

#### File data
This section contains information on the file being shared from SharePoint.

### CStructs
cstruct files provide a means to better parse ODL entries. The parameters of ODL entries consist of structured binary data and are parsed with a regex looking for ascii characters. cstruct files give us a means to define the structured data and extract it accordingly.

CStructs live under the main OneDriveExplorer directory in a subdirectory called 'cstructs'. If you would like to load cstruct files from a different directory, use the --cstructs switch when starting OneDriveExplorer

> OneDriveExplorer.exe --cstructs <folder_path>

When OneDriveExplorer is started, it looks for all files matching that pattern in the cstructs folder. It then verifies that each file found is a valid cstruct file. IF it is, the cstruct is made available to OneDriveExplorer.

To view all available cstructs, use the View | CStructs menu option. When this is selected the following dialog is displayed:

![](.\manual\cstructs.png)

To get additional details about the cstruct, click the Add'l Info button. The following dialog will be displayed:

![](.\manual\add_info.png)

# OneDriveExplorer
## OneDriveExplorer Introduction
OneDriveExplorer is a tool used to parse \<UserCid\>.dat files and reconstruct the folder structure of OneDrive. \<UserCid\>.dat files are commonly found at %USERPROFILE%\\%AppData%\Local\Microsoft\OneDrive\settings\\<Personal\Business>

## Getting started

Running OneDriveExplorer.exe without any arguments displays a list of command line options:

```
usage: OneDriveExplorer.py [-h] [--LIVE LIVE] [--PROFILE PROFILE] [--SETTINGS_DAT SETTINGS_DAT]
                           [--SYNC_ENGINE SYNC_ENGINE] [--SAFE_DEL SAFE_DEL] [--LIST_SYNC LIST_SYNC]
                           [--FILE_USAGE_SYNC FILE_USAGE_SYNC] [--REG_HIVE REG_HIVE] [--RECYCLE_BIN RECYCLE_BIN]
                           [--LOGS [LOGS]] [--output-dir OUTPUT_DIR] [--csv] [--html] [--json] [--pretty] [--clist]
                           [--cstructs CSTRUCTS] [--sync] [--debug] [--guids]

options:
  -h, --help            show this help message and exit
  --LIVE LIVE           Directory to recursively process, looking for <UserCid>.dat, NTUSER hive, $Recycle.Bin, and
                        ODL logs. This mode is primarily used with KAPE.
  --PROFILE PROFILE     Profile folder to process. Default location: %APPDATALOCAL%\Microsoft\OneDrive
  --SETTINGS_DAT SETTINGS_DAT
                        <UserCid>.dat file to be parsed
  --SYNC_ENGINE SYNC_ENGINE
                        SyncEngineDatabase.db file to load.
  --SAFE_DEL SAFE_DEL   SafeDelete.db file to load.
  --LIST_SYNC LIST_SYNC
                        Microsoft.ListSync.db file to load.
  --FILE_USAGE_SYNC FILE_USAGE_SYNC
                        Microsoft.FileUsageSync.db file to load.
  --REG_HIVE REG_HIVE   If a registry hive is provided then the mount points of the SyncEngines will be resolved.
  --RECYCLE_BIN RECYCLE_BIN
                        $Recycle.Bin folder to load.
  --LOGS [LOGS]         Directory to recursively process for ODL logs.
  --output-dir OUTPUT_DIR
                        Directory to save results to. Be sure to include the full path in double quotes.
  --csv                 Save CSV formatted results.
  --html                Save html formatted results.
  --json                Save json formatted results. Use --pretty for a more human readable layout.
  --pretty              When exporting to json, use a more human readable layout. Default is FALSE
  --clist               List available cstructs. Defaults to 'cstructs' folder where program was executed. Use
                        --cstructs for different cstruct folder.
  --cstructs CSTRUCTS   The path where ODL cstructs are located. Defaults to 'cstructs' folder where program was
                        executed.
  --sync                If true, OneDriveExplorer will download the latest Cstrucs from
                        https://github.com/Beercow/ODEFiles prior to running. Default is FALSE
  --debug               Show debug information during processing.
  --guids               OneDriveExplorer will generate 10 GUIDs and exit. Useful when creating new Cstructs. Default
                        is FALSE
  ```
  
There are several groups of command line options for OneDriveExplorer.

### Source
  
* **--LIVE**: Directory to recursively process, looking for <UserCid>.dat, NTUSER hive, $Recycle.Bin, and ODL logs. This mode is primarily used with KAPE.

* **--PROFILE**: Profile folder to process.

* **--SETTINGS_DAT**: Full path, including \<UserCid>.dat, of \<UserCid>.dat file to be parse

* **--SYNC_ENGINE**: Full path, including SyncEngineDatabase.db, of SyncEngineDatabase.db file to be parse

* **--SAFE_DEL**: Full path, including SafeDelete.db, of SafeDelete.db file to be parse

* **--LIST_SYNC**: Full path, including Microsoft.ListSync.db, of Microsoft.ListSync.db file to be parse

* **--FILE_USAGE_SYNC**: Full path, including Microsoft.FileUsageSync.db, of .db file to be parse

* **--REG_HIVE**: This switch will instruct OneDriveExplorer to use the registry hive supplied to resolve OneDrive mount points.  
 
* **--RECYCLE_BIN**: This switch will instruct OneDriveExplorer to use the $Recycle.Bin supplied to look for deleted files. This switch can only be used when a registry hive is supplied.  

* **--LOGS**: Directory to recursively process for ODL logs.

### Output

* **--csv**: Directory to save CSV formatted results to. Be sure to include the full path in double quotes.

* **--csvf**: File name to save CSV formatted results to. When present, overrides default name

* **--html**: Directory to save html formatted results to. Be sure to include the full path in double quotes.

* **--json**: Directory to save json representation to. Use --pretty for a more human readable layout.

* **--pretty**: When exporting to json, use a more human readable layout. Default is FALSE

### Other

* **--clist**: List available cstructs. Also used to check for errors in cstruct files.

* **--cstructs**: The path where ODL cstructs are located. Defaults to 'cstructs' folder where program was executed.

* **--sync**: Downloads the latest Cstructs from https://github.com/Beercow/ODEFiles

* **--debug**: Show debug information during processing.

* **--guids**: Generates 10 random GUIDs for use with cstruct files.

### Usage
To use OneDriveExplorer, simply provide the profile path to the `--PROFILE` argument

```bash
OneDriveExplorer.py --PROFILE %APPDATALOCAL%\Microsoft\OneDrive
```

Depending on the options, OneDriveExplorer can produce JSON, CSV, or HTML files of the parsed data. The `--pretty` option can be used to output the JSON into a more human readable layout.

A user registry hive can be supplied with the `--REG_HIVE` argument. This will resolve some of the mount points associated with OneDrive. Along with the registry hive, $Recycle.Bin can be added with the `--RECYCLE_BIN` option to look for deleted files.

# Version changes
## v2025.05.13
### Added
#### GUI
* Ability to add, parse, and individual files
* Data Views
  * OneDrive
  * Email
  * Meeting
  * Events
  * Teams Chat
  * Notes
  * SharePoint
#### GUI/commandline
* Microsoft.FileUsageSync.db (recent_files_formatted_spo)
* Profile option (no need to input individual files)
* Unmanaged exception handling
#### commandline
* command line options have changed (see -h) 
### Fixed
#### GUI
* Search not working properly

Code clean up  
ODL parsing speed improvement  
Bug fixes  
## v2025.02.14
### Added
#### GUI
* Indicates between OneDrive Personal/Business
#### GUI/commandline
* Offline mode data (OCR, SharedWith)
#### commandline
* --output-dir use to change the output directory
* --csv, --html, --json are now output types, no need to add a save path
* --csvf has been removed
### Fixed
#### GUI
* Metadata tabs not populating rare
## v2024.11.20
### Fixed
#### GUI
* please wait does not stay on top all of the time
* Long searches lock up gui
* Remove OneDrive Folder lock up gui
* Unload all files lock up gui
* Log crash issue
#### GUI/commandline
* Improved log naming
* Minor fixes
## v2024.11.12
### Added
#### GUI
* Colored folders to sync/link
#### GUI/commandline
* Better handling of v3 logs
* Profile, Key_Type, Log_Type, Context_Data to log files
### Fixed
#### GUI
* Missing image
#### commandline
* No indication of parsing SQLite
* No indication of file save
#### GUI/commandline
* Error with folder schema
## v2024.11.01
### Added
#### GUI
* Updated quick help
* Update preference page
* Project can only load at start
#### GUI/cmmandline
* Folder colors
* Profile and Log Type added to logs
### Fixed
#### GUI
* Quit window dissapear on drag
* Fix TypeError: can only concatenate str (not "float") to str in import csv
* Fix import csv indicator (missing building folder structure)
#### commandline
* not reading registry
#### GUI/commandline
* dtypes pulling from wrong dataframe
## v2024.10.16
### Added
#### GUI
* Sortable columns in the file manager
* Double click in search on file to file location
* Disable/enable log correlation
* Select columns in file pane
* folderStatus 12
* availability type based on hydration data
* availability type based on lastKnownPinState (v32)
#### GUI/commandline
* Folder sharedItem (dat file bitmask)
* diskLastAccessTime (v30)
* diskCreationTime (v32)
### Fixed 
#### GUI/commandline
* Some database versions were not parsing
## v2024.09.20
### Added
#### GUI/commandline
* od_ClientFolder_Records sharedItem
* ODL v1 logs
### Fixed 
#### GUI/commandline
* recycle bin hash logic
* Fixed logs corrolating off of parentResourceID
* Fixed CSV import not dropping deleted from df
## v2024.07.24
### Fixed 
#### GUI/commandline
* Fixed dtypes in syncEngineDatabase.db
* graphMetadata would cause crash in certain scenarios
## v2024.07.19
### Added
#### GUI/commandline
* hydration data updates
* shortcutVolumID and shortcutItemIndex added
### Fixed 
#### GUI/commandline
* Fixed deobfuscation of older ODL logs
* Hash functions are properly applied
## v2024.05.20
### Fixed 
#### GUI
* fixes for lock icon
#### GUI/commandline
* not enough values to unpack (expected 4, got 2)
* cannot insert level_0, already exists
## v2024.05.17
### Added
#### GUI
* add lock icon
### Fixed 
#### GUI/commandline
* fixed empty hash error
* fixed empty volumeID error
* fixed empty values in size, sharedItem, and Media
## v2024.03.22
### Added
#### GUI/commandline
* od_GraphMetadata_Records
* od_HydrationData
* filter_delete_info
* spoPermissions for scope
* Decode vault logs
#### GUI
* Double click folder in middle pane
* Breadcrumb viewer
* Export corolated logs
### Fixed 
#### GUI
* CStruct, clean up apperance
#### GUI/commandline
* Fix inRecycleBin 
* Combined recycle artifacts to eliminate multiples of same file/folder
## v2023.12.20
### Fixed 
#### GUI/commandline
* Added more error checking in ODL parser 
* spoPermissions wrong in v35 and v36 dat files
## v2023.12.13
### Added
#### GUI/commandline
* Media data
* spoPermissions
### Fixed 
#### GUI
* Increased sash size
* File/Folder status
#### GUI/commandline
* Proper nesting of files/folders 
* json format
* Code cleanup
## v2023.09.22
### Fixed 
#### GUI/commandline
* updated odl parser for version 3
## v2023.09.07
### Added
#### GUI/commandline
* New dat file parser
* File/Folder status
#### GUI
* Updates to interface
### Fixed 
#### GUI
* File count 0 on json import
* NTUSER.DAT search performance
* Double parsing dat file in live
* Space missing from eTag in Details
* Infinate loop when searching for logs in certain
* Search box and details higlighting not taking
* SQLite issues with live path variable messed up
* Live Sysem does not need to be on the same drive as profiles
#### GUI/commandline
* Error handling for unknown dat version
* cstruct warning clarified
* Inconsistent size format with recbin
* Convert SQLite timestamp to iso8601 format
## v2023.07.05
### Fixed 
#### GUI
* Help dialog
#### GUI/commandline
* SQL is now read-only (fixes errors and is more forensically sound)
* Code cleanup
## v2023.05.05
### Added
#### commandline/GUI
* Added parsing of new OneDrive SQLite databases
## v2023.03.10
### Fixed 
#### GUI
* Clear button visuals
* Updated Copyright in About pane
### Added
#### GUI
* Sync with Github
#### commandline
* --clist option to list ODL cstructs and check for errors
* --guids option  to generate GUIDs for Cstructs
* --sync command to sync cstructs
## v2023.03.06
### Added 
#### GUI
* Clear button in search box
#### commandline/GUI
* Progress bar for deleted items
### Fixed 
#### GUI
* Remove search term when disabled
* Clear search when adding OneDrive settings data
## v2022.12.09
### Fixed
#### commandline
* Fixed error when using -l with -f
* ODL saves to --csv path (default is .)
#### GUI
* ODL saves to Auto Save Path
## v2022.12.08
### Added
#### commandline/GUI
* Account for all business accounts (can be up to 9 total)
* Add switch to change cstruct directory
* Validate cstruct files
#### GUI
* Added tooltips
* Import ODL from csv
* Validates ode.settings file (no need to delete on new update)
### Fixed
#### commandline
* Fixed json error
#### GUI
* Fixed json import error
* Error handling for importing bad csv's
## v2022.11.08
### Added
#### commandline/GUI
* Support unobfuscation with `general.keystore` file
## v2022.11.04
### Added
#### commandline/GUI
* Use ObfuscationStringMap.txt if present
* ODL maps
#### GUI
* Indicator for saving log files 
* Cell pop out
* Log entries pane
* Export treeview to png, pdf
### Fixed
#### commandline/GUI
* Find all deleted files for business
#### GUI
* Fixed freezing in message window
* Better column sizing
## v2022.06.17
### Added
#### commandline/GUI
* Find deleted files
* SHA1 of deleted file for OneDrive personal
* quickxorhash of deleted file for OneDrive business
* ODL logs (experimental)
#### GUI
* Highlight on right click in treeview
* Removed empty values from Details pane
* Parse live system
* File/Folder count columns
* Projects
### Fixed
#### GUI
* Minimum width on slider left/right
* Bug fixes
## v2022.05.18
### Fixed
* Update to OneDrive broke parsing
## v2022.04.06
### Added
#### commandline/GUI
* New parsing method
* Unicode support for names
* quicXorHash/SHA1 of file
### Fixed
#### GUI
* Search not working properly if file is removed
* Unable to save a csv or html
## v2022.03.11-r1
### Added
#### commandline
* -d option for using with KAPE
## v2022.03.11
### Added
#### commandline/GUI
* Added path in JSON
#### GUI
* Unload all folders changed to Unload all files
* Enabled Details pane to allow for copy/paste of information
* Path in Details pane
* Disable collapse folders when there are no folders to collapse
* Files/Folders alphabetical order
* Indication if search term is not found
* Progress bar on exe splash screen
* file/folder count when parsing JSON
* Copy Menu
  * Copy Name
  * Copy Path
  * Copy Details
### Fixed
* Changed buffer to prevent names from getting cut off
* Fixed paths to be Windows paths \ vs /
## v2022.03.04
### Added
#### commandline
* --debug argument
#### GUI
* Debug messages
### Fixed
* Freezing on Import JSON/CSV
* Menus and Find were not disabled during Load JSON
* Handle error if Name is not found
## v2022.03.02
### Added
#### commandline/GUI
* Registry hive option
* File size information
#### GUI
* Disable hive dialog in Preferences
### Fixed
* Error in file/folder count that could cause the GUI to freeze
* Disabled Find unless something is loaded
* --pretty changed to check box in Preferences
* Set minimum size on GUI
## v2022.02.23
### Added
#### commandline/GUI
* Shared folders added to JSON
#### GUI
* Options menu
  * Save to JSON
  * Save to CSV
  * Save to HTML
  * Save to path
* Splash screen to executable
* More icons
## v2022.02.18
### Added
#### commandline
* Export to csv
* Export to html
#### GUI
* Import csv
* Horizontal scrollbar on treeview
* icons
* Requires Pillow
### Fixed
* Bug where one folder and its contents would get dropped
* File/folder count
## v2022.02.16
### Added
* Requires pandas
### Fixed
* Folder_UUID is now ParentId
* Object_UUID is now DriveItemId
* Names not resolving properly
* Huge performance increase to parser
## v2022.02.11
### Added
#### GUI
* Autosaves parsed data to JSON
* Load multiple dat/json
* Added load JSON
* Unload of individual or all files
* Better ordering of folder structure 
* Right click menu
  * Remove folder
  * Copy
  * Expand folder
  * Collapse folder
#### cmdline/GUI
* Top level object, Type changed to Root, Name changed to name of parsed file
* Default JSON file name changed from OneDrive.json to \<filename>_OneDrive.json
### Fixed
* Minor code cleanup
## v2022.02.09
### Added
* Added search to the GUI
### Fixed
* Can load new file in GUI without closing
* Improved personal file parsing
* Handle exception if object name cannot be found
## v2022.02.08
### Added
* Added support for OneDrive Personal dat files
### Fixed
* Missing files/folders
## v2022.02.03
### Initial Release
