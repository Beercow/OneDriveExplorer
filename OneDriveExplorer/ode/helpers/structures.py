def HEADER(data):
    return {
        "Version": hex(data.read(4)[0])[2:],
        "unknown": data.read(4),
        "unknown1": data.read(4),
        "syncTokenData": data.read(516),
        "syncTokenData_size": int.from_bytes(data.read(4), "little"),
        "unknown2": data.read(4)
    }


def DAT_BLOCK(data, BLOCK_CONSTANT):
    return {
        "data_block": data.read(BLOCK_CONSTANT)
    }


def DAT_FILE_v29(data):
    return {
        "header": data.read(4),  # 01 = File
        "entry_offset": data.read(4),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(8),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown5": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown6": data.read(1),
        "unknown7": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown8": data.read(4)
    }


def DAT_FILE_v2a(data):
    return {
        "header": data.read(4),  # 01 = File
        "entry_offset": data.read(4),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(8),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown5": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown6": data.read(1),
        "unknown7": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown8": data.read(36)
    }


def DAT_FILE_v2b(data):
    return {
        "header": data.read(4),  # 01 = File
        "entry_offset": data.read(4),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(8),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown5": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown6": data.read(1),
        "unknown7": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown8": data.read(36)
    }


def DAT_FILE_v2c(data):
    return {
        "header": data.read(4),  # 01 = File
        "entry_offset": data.read(4),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown9": data.read(44)
    }


def DAT_FILE_v2d(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown9": data.read(44)
    }


def DAT_FILE_v2e(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown9": data.read(68)
    }


def DAT_FILE_v2f(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown9": data.read(68)
    }


def DAT_FILE_v30(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown9": data.read(92)
    }


def DAT_FILE_v31(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown9": data.read(100)
    }


def DAT_FILE_v32(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown9": data.read(100)
    }


def DAT_FILE_v33(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown9": data.read(100)
    }


def DAT_FILE_v34(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(308),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown9": data.read(100)
    }


def DAT_FILE_v35(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(4),
        "serverSize": data.read(8),
        "serverLastChange": data.read(8),
        "serverHashDigest": data.read(20),
        "unknown9": data.read(8),
        "localWaterlineData": data.read(27),
        "unknown10": data.read(53),
        "localWriteValidationToken": data.read(20),
        "localCobaltHashDigest": data.read(20),
        "localSyncTokenData": data.read(24),
        "unknown11": data.read(116),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown12": data.read(92),
        "mediaDateTaken": int.from_bytes(data.read(4), "little"),
        "unknown13": data.read(8),
        "unknown14": data.read(4),
        "mediaWidth": int.from_bytes(data.read(4), "little"),
        "mediaHeight": int.from_bytes(data.read(4), "little")
    }


def DAT_FILE_v36(data):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "unknown6": data.read(1),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown7": data.read(1),
        "unknown8": data.read(4),
        "serverSize": data.read(8),
        "serverLastChange": data.read(8),
        "serverHashDigest": data.read(20),
        "unknown9": data.read(8),
        "localWaterlineData": data.read(27),
        "unknown10": data.read(53),
        "localWriteValidationToken": data.read(20),
        "localCobaltHashDigest": data.read(20),
        "localSyncTokenData": data.read(24),
        "unknown11": data.read(172),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown12": data.read(92),
        "mediaDateTaken": int.from_bytes(data.read(4), "little"),
        "unknown13": data.read(8),
        "unknown14": data.read(4),
        "mediaWidth": int.from_bytes(data.read(4), "little"),
        "mediaHeight": int.from_bytes(data.read(4), "little")
    }


def DAT_FILE(data, FILE_CONSTANT):
    return {
        "header": data.read(8),  # 01 = File
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(8),
        "localHashDigest": data.read(20),  # quickXor, SHA1
        "unknown4": data.read(4),
        "lastChange": int.from_bytes(data.read(4), "little"),
        "unknown5": data.read(4),
        "size": int.from_bytes(data.read(8), "little"),
        "fileName": data.read(520),
        "fileStatus": int.from_bytes(data.read(2), "little"),
        "unknown6": data.read(50),
        "localWaterlineData": data.read(27),
        "unknown7": data.read(49),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "localWriteValidationToken": data.read(20),
        "localCobaltHashDigest": data.read(20),
        "unknown8": data.read(FILE_CONSTANT)
    }


def DAT_FOLDER_v29_v2c(data, FOLDER_CONSTANT):
    return {
        "header": data.read(4),  # 02 = Folder
        "entry_offset": data.read(4),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "folderName": data.read(520),
        "jumpLinkType": data.read(4),
        "parentScopeID": data.read(40),
        "folderStatus": int.from_bytes(data.read(1), "little"),
        "unknown4": data.read(1),
        "syncChildrenFiles": data.read(1),
        "unknown5": data.read(1),
        "spoPermissions": int.from_bytes(data.read(1), "little"),
        "unknown6": data.read(1),
        "unknown7": data.read(1),
        "unknown8": data.read(1),
        "unknown9": data.read(1),
        "unknown10": data.read(FOLDER_CONSTANT)
    }


def DAT_FOLDER_v2d_v36(data, FOLDER_CONSTANT):
    return {
        "header": data.read(8),  # 02 = Folder
        "entry_offset": data.read(8),
        "unknown1": data.read(8),
        "resourceID": data.read(39),
        "parentResourceID": data.read(39),
        "eTag": data.read(56),
        "unknown2": data.read(2),
        "volumeID": int.from_bytes(data.read(8), "little"),
        "itemIndex": int.from_bytes(data.read(8), "little"),
        "unknown3": data.read(4),
        "bitMask": data.read(4),
        "folderName": data.read(520),
        "jumpLinkType": data.read(4),
        "parentScopeID": data.read(40),
        "folderStatus": int.from_bytes(data.read(1), "little"),
        "unknown4": data.read(1),
        "syncChildrenFiles": data.read(1),
        "unknown5": data.read(1),
        "spoPermissions": int.from_bytes(data.read(1), "little"),
        "unknown6": data.read(1),
        "unknown7": data.read(1),
        "unknown8": data.read(1),
        "unknown9": data.read(1),
        "unknown10": data.read(FOLDER_CONSTANT)
    }


def DAT_DELETED(data, DELETE_CONSTANT):
    return {
        "header": data.read(8),  # 03 = Deleted
        "entry_offset": data.read(8),
        "unknown": data.read(DELETE_CONSTANT)
    }


def DAT_LIBRARY_SCOPE(data, LSCOPE_CONSTANT):
    return {
        "header": data.read(8),  # 09 = LibraryScope
        "entry_offset": data.read(8),
        "unknown1": data.read(4),
        "unknown2": data.read(4),
        "scopeID": data.read(39),
        "unknown3": data.read(117),
        "flags": data.read(4),
        "siteID": data.read(39),  # The SiteId is the unique GUID for the site collection.
        "webID": data.read(39),  # The WebId is the ID for a site (or subsite) in a site collection.
        "listID": data.read(39),  # Document library
        "unknown4": data.read(3),
        "libraryType": data.read(4),
        "unknown5": data.read(4),
        "unknown6": data.read(4),
        "syncTokenData": data.read(516),
        "syncTokenData_size": data.read(4),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown7": data.read(LSCOPE_CONSTANT)
    }


def DAT_LIBRARY_FOLDER(data, LFOLDER_CONSTANT):
    return {
        "header": data.read(8),  # 0A = libraryFolder
        "entry_offset": data.read(8),
        "unknown1": data.read(4),
        "unknown2": data.read(4),
        "scopeID": data.read(39),
        "unknown4": data.read(121),
        "listID": data.read(39),  # Document library
        "unknown5": data.read(LFOLDER_CONSTANT)
    }


def DAT_VAULT(data, VAULT_CONSTANT):
    return {
        "header": data.read(8),  # 0B = Unknown
        "entry_offset": data.read(8),
        "unknown1": data.read(4),
        "unknown2": data.read(4),
        "scopeID": data.read(39),
        "unknown3": data.read(649),
        "shortcutVolumeID": data.read(8),
        "shortcutItemIndex": data.read(8),
        "unknown5": data.read(VAULT_CONSTANT)
    }


def DAT_ADDED_SCOPE(data, ASCOPE_CONSTANT):
    return {
        "header": data.read(8),  # 0C = LibraryScope
        "entry_offset": data.read(8),
        "unknown1": data.read(4),
        "unknown2": data.read(4),
        "scopeID": data.read(39),
        "unknown3": data.read(117),
        "flags": data.read(4),
        "siteID": data.read(39),  # The SiteId is the unique GUID for the site collection.
        "webID": data.read(39),  # The WebId is the ID for a site (or subsite) in a site collection.
        "listID": data.read(39),  # Document library
        "sourceResourceID": data.read(39),  # Document library
        "libraryType": data.read(4),
        "unknown5": data.read(4),
        "syncTokenData": data.read(516),
        "syncTokenData_size": data.read(4),
        "spoPermissions": int.from_bytes(data.read(4), "little"),
        "unknown6": data.read(ASCOPE_CONSTANT)
    }
