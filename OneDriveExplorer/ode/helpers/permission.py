def permissions(_):
    perstr = []
    # Lists and Documents
    if _ & 0x0:
        perstr.append("EmptyMask")
    if _ & 0x1:
        perstr.append("ViewListItems")
    if _ & 0x2:
        perstr.append("AddListItems")
    if _ & 0x4:
        perstr.append("EditListItems")
    if _ & 0x8:
        perstr.append("DeleteListItems")
    if _ & 0x10:
        perstr.append("ApproveItems")
    if _ & 0x20:
        perstr.append("OpenItems")
    if _ & 0x40:
        perstr.append("ViewVersions")
    if _ & 0x80:
        perstr.append("DeleteVersions")
    if _ & 0x100:
        perstr.append("OverrideListBehaviors")
    if _ & 0x200:
        perstr.append("ManagePersonalViews")
    if _ & 0x400:
        perstr.append("ManageLists")
    if _ & 0x800:
        perstr.append("ViewApplicationPages")
    # Web Level
    if _ & 0x1000:
        perstr.append("Open")
    if _ & 0x2000:
        perstr.append("ViewPages")
    if _ & 0x4000:
        perstr.append("AddAndCustomizePages")
    if _ & 0x8000:
        perstr.append("ApplyThemAndBorder")
    if _ & 0x10000:
        perstr.append("ApplyStyleSheets")
    if _ & 0x20000:
        perstr.append("ViewAnalyticsData")
    if _ & 0x40000:
        perstr.append("UseSSCSiteCreation")
    if _ & 0x80000:
        perstr.append("CreateSubsite")
    if _ & 0x100000:
        perstr.append("CreateGroups")
    if _ & 0x200000:
        perstr.append("ManagePermissions")
    if _ & 0x400000:
        perstr.append("BrowseDirectories")
    if _ & 0x800000:
        perstr.append("BrowseUserInfo")
    if _ & 0x1000000:
        perstr.append("AddDelPersonalWebParts")
    if _ & 0x2000000:
        perstr.append("UpdatePersonalWebParts")
    if _ & 0x4000000:
        perstr.append("ManageWeb")
    return perstr
