# OneDriveExplorer
# Copyright (C) 2022
#
# This file is part of OneDriveExplorer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

ODL_DEF = """

typedef struct _Data_block{
    uint64     signature;
    uint64     timestamp;
    uint32     unk1;
    uint32     unk2;
    char       unk3_guid[16];
    uint32     unk4;
    uint32     unk5;
    uint32     data_len;
    uint32     unk6;
} Data_block;

typedef struct _Data{
    uint32    code_file_name_len;
    char      code_file_name[code_file_name_len];
    uint32    unknown;
    uint32    code_function_name_len;
    char      code_function_name[code_function_name_len];
} Data;

// function parameters

typedef struct _absconn_onreceive{
    int64 unk1;
    int64 unk2;
    int32 size;
    char data[size];
} absconn_onreceive;

typedef struct _absconn_senddata{
    int64 unk1;
    int32 unk2;
    int32 size;
    char data[size];
} absconn_senddata;

typedef struct _aclhelper_getacl{
    int32 size;
    char data[size];
    int32 unk;
} aclhelper_getacl;

typedef struct _aclhelper_readonlyguard{
    int32 size;
    char data[size];
} aclhelper_readonlyguard;

typedef struct _aclhelper_recordcalltimetaken{
    int32 unk1;
    int64 unk2;
} aclhelper_recordcalltimetaken;

typedef struct _aclhelper_removedenydeletechildrenimpl{
    int32 size;
    char data[size];
} aclhelper_removedenydeletechildrenimpl;

typedef struct _aclhelper_setdenydeletechildrenimpl{
    int32 size;
    char data[size];
} aclhelper_setdenydeletechildrenimpl;

typedef struct _actionmanager_openlocalfolder{
} actionmanager_openlocalfolder;

typedef struct _activitycentererrorsmodel_onerrorschanged{
} activitycentererrorsmodel_onerrorschanged;

typedef struct _activitycenterheadermodel_updatesyncstatustext{
} activitycenterheadermodel_updatesyncstatustext;

typedef struct _activitycentermessagemodel_performaction{
} activitycentermessagemodel_performaction;

typedef struct _activitycentermessagemodel_setmessagedata{
} activitycentermessagemodel_setmessagedata;

typedef struct _activitycenterview_getwindowsize{
} activitycenterview_getwindowsize;

typedef struct _activitycenterview_onqmlenginewarnings{
} activitycenterview_onqmlenginewarnings;

typedef struct _activitycenterview_recordloadertelemetryqos{
} activitycenterview_recordloadertelemetryqos;

typedef struct _activitycenterview_recordtelemetry{
} activitycenterview_recordtelemetry;

typedef struct _addmountcontroller_onaddmountedfolderdone{
} addmountcontroller_onaddmountedfolderdone;

typedef struct _addmountfoldermodel_onaddmountedfolderdone{
} addmountfoldermodel_onaddmountedfolderdone;

typedef struct _adalauth_clearcredentials{
} adalauth_clearcredentials;

typedef struct _adalauth_clearcredentialsandmaybegetnewtokens{
} adalauth_clearcredentialsandmaybegetnewtokens;

typedef struct _adalauth_signin{
} adalauth_signin;

typedef struct _adalauth_signout{
} adalauth_signout;

typedef struct _adalauth_signoutbaseoneauthmsaluserauthentication_issignedin{
} adalauth_signoutbaseoneauthmsaluserauthentication_issignedin;

typedef struct _adalauthenticationcontext_acquiretoken{
} adalauthenticationcontext_acquiretoken;

typedef struct _adallogger_getadalloglevel{
} adallogger_getadalloglevel;

typedef struct _adallogger_initialize{
} adallogger_initialize;

typedef struct _adallogger_log{
} adallogger_log;

typedef struct _adallogger__adallogger{
} adallogger__adallogger;

typedef struct _adallogger__adalloggerbaseoneauthmsaluserauthentication_issignedin{
} adallogger__adalloggerbaseoneauthmsaluserauthentication_issignedin;

typedef struct _adalwrapper_geterrordescription{
} adalwrapper_geterrordescription;

typedef struct _adalwrapper_outstringhelper{
} adalwrapper_outstringhelper;

typedef struct _activehydrationscenario_report{
} activehydrationscenario_report;

typedef struct _activityitemsmodel_additemtohistory{
} activityitemsmodel_additemtohistory;

typedef struct _activityitemsmodel_updateprogressmap{
} activityitemsmodel_updateprogressmap;

typedef struct _activityitemsmodel_validatefriendlyprocessname{
} activityitemsmodel_validatefriendlyprocessname;

typedef struct _activityitemsmodel_validatefriendlyprocessnamebaseoneauthmsaluserauthentication_issignedin{
} activityitemsmodel_validatefriendlyprocessnamebaseoneauthmsaluserauthentication_issignedin;

typedef struct _apiloop_getselectivesyncinformationhandler{
} apiloop_getselectivesyncinformationhandler;

typedef struct _apiloop_ismappingvalideventhandler{
} apiloop_ismappingvalideventhandler;

typedef struct _apiloop_libraryerroreventhandler{
} apiloop_libraryerroreventhandler;

typedef struct _apiloop_loginhandler{
} apiloop_loginhandler;

typedef struct _apiloop_loginstatechangedeventhandler{
} apiloop_loginstatechangedeventhandler;

typedef struct _apiloop_maplibraryhandler{
} apiloop_maplibraryhandler;

typedef struct _apiloop_syncprogresshandler{
} apiloop_syncprogresshandler;

typedef struct _apiloop_uimessageeventhandler{
} apiloop_uimessageeventhandler;

typedef struct _appnpsofficialcampaign_deserializeextradata{
} appnpsofficialcampaign_deserializeextradata;

typedef struct _ariaconfig_geteventcollectorurifromgpo{
} ariaconfig_geteventcollectorurifromgpo;

typedef struct _ariadebugtracer_register{
    int32 unk;
} ariadebugtracer_register;

typedef struct _assignidstodrivechangetypedciworkitem_assignidstodrivechange{
} assignidstodrivechangetypedciworkitem_assignidstodrivechange;

typedef struct _asynctask_dotask{
} asynctask_dotask;

typedef struct _authevents_addlistener{
} authevents_addlistener;

typedef struct _authevents_fireevent{
} authevents_fireevent;

typedef struct _authhelpercomponent_initializecomponent{
} authhelpercomponent_initializecomponent;

typedef struct _authhelpercomponent_postinitialize{
} authhelpercomponent_postinitialize;

typedef struct _authinternalhelpers_getclaimsvaluefromstring{
} authinternalhelpers_getclaimsvaluefromstring;

typedef struct _authplatformhttprequest_create{
} authplatformhttprequest_create;

typedef struct _authplatformhttprequest_onrequestcomplete{
} authplatformhttprequest_onrequestcomplete;

typedef struct _authplatformhttprequest_wait{
} authplatformhttprequest_wait;

typedef struct _authplatform_isadalenabled{
} authplatform_isadalenabled;

typedef struct _authplatform_isfilemodificationtimeolderthan{
} authplatform_isfilemodificationtimeolderthan;

typedef struct _authproducthelper_defaultcachedcredentialnameandcomment{
} authproducthelper_defaultcachedcredentialnameandcomment;

typedef struct _authsigninmodel_launchauthuxloginscreen{
} authsigninmodel_launchauthuxloginscreen;

typedef struct _authsigninoperation_execute{
} authsigninoperation_execute;

typedef struct _authtelemetrydata_authreportadalnthsilentsigninwithwam{
} authtelemetrydata_authreportadalnthsilentsigninwithwam;

typedef struct _authtelemetrydata_authreportclearcredentials{
} authtelemetrydata_authreportclearcredentials;

typedef struct _authtelemetrydata_authreportexpresssigninoutcome{
} authtelemetrydata_authreportexpresssigninoutcome;

typedef struct _authtelemetrydata_authreportsilentsigninretryfailure{
} authtelemetrydata_authreportsilentsigninretryfailure;

typedef struct _authtelemetrydata_authreportspodiscover{
} authtelemetrydata_authreportspodiscover;

typedef struct _authtelemetrydata_authreportspodiscovergraph{
} authtelemetrydata_authreportspodiscovergraph;

typedef struct _authtelemetrydata_authtelemetryreportfirstrunorigintousagesync{
} authtelemetrydata_authtelemetryreportfirstrunorigintousagesync;

typedef struct _authtelemetrydata_authtelemetryreportpromptoutcome{
} authtelemetrydata_authtelemetryreportpromptoutcome;

typedef struct _authtelemetrydata_authtelemetryreportresult{
} authtelemetrydata_authtelemetryreportresult;

typedef struct _authtelemetrydata_authtelemetryupdatedata{
} authtelemetrydata_authtelemetryupdatedata;

typedef struct _authtelemetrydata_authtelemetryupdatepromptscenario{
} authtelemetrydata_authtelemetryupdatepromptscenario;

typedef struct _authtelemetrydata_calculatedeltaforaccounttimestamp{
} authtelemetrydata_calculatedeltaforaccounttimestamp;

typedef struct _authtelemetrydata_completesigninerrorstatetelemetryifapplicable{
} authtelemetrydata_completesigninerrorstatetelemetryifapplicable;

typedef struct _authtelemetrydata_endtelemetryscenario{
} authtelemetrydata_endtelemetryscenario;

typedef struct _authtelemetrydata_generatescenarioname{
} authtelemetrydata_generatescenarioname;

typedef struct _authtelemetrydata_recordtelemetrypoint{
} authtelemetrydata_recordtelemetrypoint;

typedef struct _authtelemetrydata_sendsilentbusinessconfigtelemetryresult{
} authtelemetrydata_sendsilentbusinessconfigtelemetryresult;

typedef struct _authtelemetrydata_starttelemetryscenario{
} authtelemetrydata_starttelemetryscenario;

typedef struct _authtelemetrydata_submitoneauthmsaltelemetry{
} authtelemetrydata_submitoneauthmsaltelemetry;

typedef struct _authtelemetrydata_operator_{
} authtelemetrydata_operator_;

typedef struct _authticket_getvalue{
} authticket_getvalue;

typedef struct _authticket_markexpired{
} authticket_markexpired;

typedef struct _autofixrenamemessagesource_getmessagedata{
} autofixrenamemessagesource_getmessagedata;

typedef struct _auth_discoverandverifytenant{
} auth_discoverandverifytenant;

typedef struct _auth_doofflinebackoffifnecessary{
} auth_doofflinebackoffifnecessary;

typedef struct _auth_doofflinebackoffifnecessarybaseoneauthmsaluserauthentication_issignedin{
} auth_doofflinebackoffifnecessarybaseoneauthmsaluserauthentication_issignedin;

typedef struct _auth_gettenantnameid{
} auth_gettenantnameid;

typedef struct _auth_initializewithinstanceid{
} auth_initializewithinstanceid;

typedef struct _auth_settenanttelemetryinfo{
} auth_settenanttelemetryinfo;

typedef struct _auth_signinsilently{
} auth_signinsilently;

typedef struct _auth_signout{
} auth_signout;

typedef struct _auth_signoutbaseoneauthmsaluserauthentication_issignedin{
} auth_signoutbaseoneauthmsaluserauthentication_issignedin;

typedef struct _auth_trytouseoneauthmsal{
} auth_trytouseoneauthmsal;

typedef struct _authenticationprovider_acquiretokeninternalworker{
} authenticationprovider_acquiretokeninternalworker;

typedef struct _authenticationprovider_checkifresourceblockedduetoexternalsharing{
} authenticationprovider_checkifresourceblockedduetoexternalsharing;

typedef struct _authenticationprovider_ensuresignincontextisvalid{
} authenticationprovider_ensuresignincontextisvalid;

typedef struct _authenticationprovider_processauthenticatorresult{
} authenticationprovider_processauthenticatorresult;

typedef struct _authenticationscenariotelemetry_report{
} authenticationscenariotelemetry_report;

typedef struct _automountmanager_executeautomountinternal{
} automountmanager_executeautomountinternal;

typedef struct _autoredirecthttprequest_processredirection{
} autoredirecthttprequest_processredirection;

typedef struct _bannermanager_migratebannerstore{
} bannermanager_migratebannerstore;

typedef struct _basecampaign_reportdeserializecampaignresult{
} basecampaign_reportdeserializecampaignresult;

typedef struct _basehost_coinitializeworkitem{
} basehost_coinitializeworkitem;

typedef struct _basehost_initialize{
} basehost_initialize;

typedef struct _basehost_isinstancerunning{
} basehost_isinstancerunning;

typedef struct _basehost_uninitializeinternal{
} basehost_uninitializeinternal;

typedef struct _basehost_waitforrefrundown{
} basehost_waitforrefrundown;

typedef struct _basehost_waitforrefrundownbaseoneauthmsaluserauthentication_issignedin{
} basehost_waitforrefrundownbaseoneauthmsaluserauthentication_issignedin;

typedef struct _baseoneauthmsaluserauthentication_firefirstrunwizardclosedevent{
} baseoneauthmsaluserauthentication_firefirstrunwizardclosedevent;

typedef struct _baseoneauthmsaluserauthentication_handleoneautherror{
} baseoneauthmsaluserauthentication_handleoneautherror;

typedef struct _baseoneauthmsaluserauthentication_initialize{
} baseoneauthmsaluserauthentication_initialize;

typedef struct _baseoneauthmsaluserauthentication_issignedin{
} baseoneauthmsaluserauthentication_issignedin;

typedef struct _basesettingsmanager_getcachedprivacysetting{
} basesettingsmanager_getcachedprivacysetting;

typedef struct _basesettingsmanager_onrequestcomplete{
} basesettingsmanager_onrequestcomplete;

typedef struct _basicclientinfoprovider_isuserfeedbackenabled{
} basicclientinfoprovider_isuserfeedbackenabled;

typedef struct _basicclientinfoprovider_isvalidsyncrequest{
} basicclientinfoprovider_isvalidsyncrequest;

typedef struct _batterystatusmanager_ispauseonbatterysaverenabledinternal{
} batterystatusmanager_ispauseonbatterysaverenabledinternal;

typedef struct _batterystatusmanager_onpowersettingchange{
} batterystatusmanager_onpowersettingchange;

typedef struct _batterystatusmanager_registerpowersettingnotification{
} batterystatusmanager_registerpowersettingnotification;

typedef struct _batterystatusmanager_unregisterpowersettingnotification{
} batterystatusmanager_unregisterpowersettingnotification;

typedef struct _beasthttptransport_starthttpserver{
} beasthttptransport_starthttpserver;

typedef struct _binaryloggingsession_startloggingsession{
    int8 unk;
} binaryloggingsession_startloggingsession;

typedef struct _browserview_ondestroy{
} browserview_ondestroy;

typedef struct _businessprivacysettingsmanager_handlegetsettingresponse{
} businessprivacysettingsmanager_handlegetsettingresponse;

typedef struct _businessprivacysettingsmanager_shouldusecachedsetting{
} businessprivacysettingsmanager_shouldusecachedsetting;

typedef struct _comservicemanager_coregisterclassobjectssta{
} comservicemanager_coregisterclassobjectssta;

typedef struct _comservicemanager_corevokeclassobjectssta{
} comservicemanager_corevokeclassobjectssta;

typedef struct _comservicemanager_preteardown{
} comservicemanager_preteardown;

typedef struct _comservicemanager_preteardownbaseoneauthmsaluserauthentication_issignedin{
} comservicemanager_preteardownbaseoneauthmsaluserauthentication_issignedin;

typedef struct _comservicemanager_teardowncomponent{
} comservicemanager_teardowncomponent;

typedef struct _comservicemodule_registerclasses{
} comservicemodule_registerclasses;

typedef struct _comservicemodule_unregisterclasses{
} comservicemodule_unregisterclasses;

typedef struct _cschannelcontext_processblob{
} cschannelcontext_processblob;

typedef struct _cwinhttp_addheader{
} cwinhttp_addheader;

typedef struct _cwinhttp_asyncdetectproxiescallback{
} cwinhttp_asyncdetectproxiescallback;

typedef struct _cwinhttp_asyncdetectproxiescallbackbaseoneauthmsaluserauthentication_issignedin{
} cwinhttp_asyncdetectproxiescallbackbaseoneauthmsaluserauthentication_issignedin;

typedef struct _cwinhttp_autodetectproxies{
} cwinhttp_autodetectproxies;

typedef struct _cwinhttp_createrequest{
} cwinhttp_createrequest;

typedef struct _cwinhttp_detectproxies{
} cwinhttp_detectproxies;

typedef struct _cwinhttp_doproxyfailover{
} cwinhttp_doproxyfailover;

typedef struct _cwinhttp_initializesession{
} cwinhttp_initializesession;

typedef struct _cwinhttp_oncallback{
} cwinhttp_oncallback;

typedef struct _cwinhttp_onrequestcomplete{
} cwinhttp_onrequestcomplete;

typedef struct _cwinhttp_sendnextchunk{
} cwinhttp_sendnextchunk;

typedef struct _cwinhttp_sendnextchunkbaseoneauthmsaluserauthentication_issignedin{
} cwinhttp_sendnextchunkbaseoneauthmsaluserauthentication_issignedin;

typedef struct _cwinhttp_shutdown{
} cwinhttp_shutdown;

typedef struct _cachemanager_determinerootfoldermappinglocation{
} cachemanager_determinerootfoldermappinglocation;

typedef struct _cachemanager_finalizediskspacecheck{
} cachemanager_finalizediskspacecheck;

typedef struct _cachemanager_finalizeonedriverootfoldersetup{
} cachemanager_finalizeonedriverootfoldersetup;

typedef struct _cachemanager_getcurrentuserupgradingfrom8point1state{
} cachemanager_getcurrentuserupgradingfrom8point1state;

typedef struct _cachemanager_handlesyncenginequotanotification{
} cachemanager_handlesyncenginequotanotification;

typedef struct _cachemanager_ongetlibrariescomplete{
} cachemanager_ongetlibrariescomplete;

typedef struct _cachemanager_onmaplibrarycomplete{
} cachemanager_onmaplibrarycomplete;

typedef struct _cachemanager_onsignedin{
} cachemanager_onsignedin;

typedef struct _cachemanager_populatecache{
} cachemanager_populatecache;

typedef struct _cachemanager_registersyncrootwithshellbyaccountinfo{
} cachemanager_registersyncrootwithshellbyaccountinfo;

typedef struct _cachemanager_reportprocessingchangesdurationifnecessary{
} cachemanager_reportprocessingchangesdurationifnecessary;

typedef struct _cachemanager_setuponedriverootfolder{
} cachemanager_setuponedriverootfolder;

typedef struct _cachemanager_updatechangedtenantvalues{
} cachemanager_updatechangedtenantvalues;

typedef struct _cachemanager_operator_{
} cachemanager_operator_;

typedef struct _certverifier_verifymicrosofttrustbaseoneauthmsaluserauthentication_issignedin{
} certverifier_verifymicrosofttrustbaseoneauthmsaluserauthentication_issignedin;

typedef struct _changefile_getpathforinsyncbitupdate{
} changefile_getpathforinsyncbitupdate;

typedef struct _changefile_loginfo{
} changefile_loginfo;

typedef struct _changefile_process{
} changefile_process;

typedef struct _changenotificationmanager_additemtolongpoll{
} changenotificationmanager_additemtolongpoll;

typedef struct _changenotificationmanager_operator_{
} changenotificationmanager_operator_;

typedef struct _clientpolicysettingsmanager_getsettingsmapforscope{
} clientpolicysettingsmanager_getsettingsmapforscope;

typedef struct _clientpolicysettings_loadpoliciesfromdisk{
} clientpolicysettings_loadpoliciesfromdisk;

typedef struct _clientpolicysettings_prerefreshifadvised{
} clientpolicysettings_prerefreshifadvised;

typedef struct _clientpolicysettings_prerefreshifadvisedbaseoneauthmsaluserauthentication_issignedin{
} clientpolicysettings_prerefreshifadvisedbaseoneauthmsaluserauthentication_issignedin;

typedef struct _clientpolicysettings_refreshallpoliciesifneeded{
} clientpolicysettings_refreshallpoliciesifneeded;

typedef struct _clientpolicysettings_refreshinternal{
} clientpolicysettings_refreshinternal;

typedef struct _clientpolicysettings_registerocsiclptentnatflagsinregistryformountpoint{
} clientpolicysettings_registerocsiclptentnatflagsinregistryformountpoint;

typedef struct _clientpolicysettings_updatesyncengineproviderurlnamespace{
} clientpolicysettings_updatesyncengineproviderurlnamespace;

typedef struct _clientpolicystate_getint{
} clientpolicystate_getint;

typedef struct _clientpolicystate_getint64{
} clientpolicystate_getint64;

typedef struct _clientpolicystate_getstringwithoutvalidsettingscheck{
} clientpolicystate_getstringwithoutvalidsettingscheck;

typedef struct _clientpolicystate_isrefreshneeded{
} clientpolicystate_isrefreshneeded;

typedef struct _clientpolicystate_isrefreshneededbaseoneauthmsaluserauthentication_issignedin{
} clientpolicystate_isrefreshneededbaseoneauthmsaluserauthentication_issignedin;

typedef struct _clientpolicystate_loadfromconfig{
} clientpolicystate_loadfromconfig;

typedef struct _clientpolicystate_loadfromxml{
} clientpolicystate_loadfromxml;

typedef struct _clientpolicystate_persisttofile{
} clientpolicystate_persisttofile;

typedef struct _clientpolicystate_readarray{
} clientpolicystate_readarray;

typedef struct _clientpolicystate_readrampsfromconfig{
} clientpolicystate_readrampsfromconfig;

typedef struct _clientpolicystate_readrule{
} clientpolicystate_readrule;

typedef struct _clientpolicystate_readxmlrange{
} clientpolicystate_readxmlrange;

typedef struct _clientpolicystate_refreshcachedexclusionlist{
} clientpolicystate_refreshcachedexclusionlist;

typedef struct _clientpolicystate_tryreadrampsettings{
} clientpolicystate_tryreadrampsettings;

typedef struct _clientsetupmanager_initializepackagethreadpool{
} clientsetupmanager_initializepackagethreadpool;

typedef struct _clientsetupmanager_installsparsepackage{
} clientsetupmanager_installsparsepackage;

typedef struct _clientsetupmanager_ongetmountedfoldercomplete{
} clientsetupmanager_ongetmountedfoldercomplete;

typedef struct _clientsetupmanager_operator_{
} clientsetupmanager_operator_;

typedef struct _cloudfetcher_cancelfilefetch{
} cloudfetcher_cancelfilefetch;

typedef struct _cloudfetcher_docoreloopwork{
} cloudfetcher_docoreloopwork;

typedef struct _cloudfetcher_docoreloopworkbaseoneauthmsaluserauthentication_issignedin{
} cloudfetcher_docoreloopworkbaseoneauthmsaluserauthentication_issignedin;

typedef struct _cloudfetcher_populatecloudtransferdownload{
} cloudfetcher_populatecloudtransferdownload;

typedef struct _coauthitempropertyhandler_getitemproperties{
} coauthitempropertyhandler_getitemproperties;

typedef struct _coauthitempropertyhandler_getpropertiesfromclientfile{
} coauthitempropertyhandler_getpropertiesfromclientfile;

typedef struct _coauthitempropertyhandler_getpropertiesfromrootfolder{
} coauthitempropertyhandler_getpropertiesfromrootfolder;

typedef struct _coauthitempropertyhandler_getpropertiesfromrootfolderbaseoneauthmsaluserauthentication_issignedin{
} coauthitempropertyhandler_getpropertiesfromrootfolderbaseoneauthmsaluserauthentication_issignedin;

typedef struct _coauthitempropertyhandler_populateitempropertiesforuri{
} coauthitempropertyhandler_populateitempropertiesforuri;

typedef struct _coauthitempropertyhandler_populateitempropertiesforuribaseoneauthmsaluserauthentication_issignedin{
} coauthitempropertyhandler_populateitempropertiesforuribaseoneauthmsaluserauthentication_issignedin;

typedef struct _coauthitempropertyhandler_populateviewonlineuri{
} coauthitempropertyhandler_populateviewonlineuri;

typedef struct _coauthitempropertyhandler_populateviewonlineuriforbusiness{
} coauthitempropertyhandler_populateviewonlineuriforbusiness;

typedef struct _coauthsupportutils_canusecollaborativemetadata{
} coauthsupportutils_canusecollaborativemetadata;

typedef struct _coauthsupportutils_recordcoauthsettingtelemetry{
} coauthsupportutils_recordcoauthsettingtelemetry;

typedef struct _configurationsettingsmanager_deletesetting{
} configurationsettingsmanager_deletesetting;

typedef struct _configurationsettingsmanager_deletesettingperinstance{
} configurationsettingsmanager_deletesettingperinstance;

typedef struct _configurationsettingsmanager_getbool{
} configurationsettingsmanager_getbool;

typedef struct _configurationsettingsmanager_getboolperinstance{
} configurationsettingsmanager_getboolperinstance;

typedef struct _configurationsettingsmanager_getint{
} configurationsettingsmanager_getint;

typedef struct _configurationsettingsmanager_getintbaseoneauthmsaluserauthentication_issignedin{
} configurationsettingsmanager_getintbaseoneauthmsaluserauthentication_issignedin;

typedef struct _configurationsettingsmanager_getintperinstance{
} configurationsettingsmanager_getintperinstance;

typedef struct _configurationsettingsmanager_getstringperinstance{
} configurationsettingsmanager_getstringperinstance;

typedef struct _configurationsettingsmanager_getulonglongperinstance{
} configurationsettingsmanager_getulonglongperinstance;

typedef struct _configurationsettingsmanager_setboolperinstance{
} configurationsettingsmanager_setboolperinstance;

typedef struct _configurationsettingsmanager_setint{
} configurationsettingsmanager_setint;

typedef struct _configurationsettingsmanager_setintperinstance{
} configurationsettingsmanager_setintperinstance;

typedef struct _configurationsettingsmanager_setstringperinstance{
} configurationsettingsmanager_setstringperinstance;

typedef struct _configurationsettingsmanager_setulonglongperinstance{
} configurationsettingsmanager_setulonglongperinstance;

typedef struct _consumerprivacysettingsmanager_getknowledge{
} consumerprivacysettingsmanager_getknowledge;

typedef struct _consumerprivacysettingsmanager_handlegetsettingresponse{
} consumerprivacysettingsmanager_handlegetsettingresponse;

typedef struct _contentcomparator_registercomparator{
} contentcomparator_registercomparator;

typedef struct _coreapi_beginconnectmountedfolder{
} coreapi_beginconnectmountedfolder;

typedef struct _coreapi_begingetmountedfolders{
} coreapi_begingetmountedfolders;

typedef struct _coreapi_begingetselectivesyncfolderinformation{
} coreapi_begingetselectivesyncfolderinformation;

typedef struct _coreapi_begingetselectivesyncrootfolderinformation{
} coreapi_begingetselectivesyncrootfolderinformation;

typedef struct _coreapi_getcoauthsettingstatus{
} coreapi_getcoauthsettingstatus;

typedef struct _coreapi_getselectivesyncfolderinformationinternal{
} coreapi_getselectivesyncfolderinformationinternal;

typedef struct _coreapi_isplaceholderson{
} coreapi_isplaceholderson;

typedef struct _coreloopworkitemqueuer_stop{
} coreloopworkitemqueuer_stop;

typedef struct _corestatemachine_handleidlestate{
} corestatemachine_handleidlestate;

typedef struct _corestatemachine_handleidlestatebaseoneauthmsaluserauthentication_issignedin{
} corestatemachine_handleidlestatebaseoneauthmsaluserauthentication_issignedin;

typedef struct _corestatemachine_handlescanningstate{
} corestatemachine_handlescanningstate;

typedef struct _corestatemachine_handlescanningstatebaseoneauthmsaluserauthentication_issignedin{
} corestatemachine_handlescanningstatebaseoneauthmsaluserauthentication_issignedin;

typedef struct _createfile_addfiletodrivewithstatus{
} createfile_addfiletodrivewithstatus;

typedef struct _createfile_handlelocalcreatefileremotelyadded{
} createfile_handlelocalcreatefileremotelyadded;

typedef struct _createfile_handlelocalcreatefileweadded{
} createfile_handlelocalcreatefileweadded;

typedef struct _createfile_loginfo{
} createfile_loginfo;

typedef struct _createfolder_finalizefoldercreation{
} createfolder_finalizefoldercreation;

typedef struct _createfolder_loginfo{
} createfolder_loginfo;

typedef struct _createfolder_trygetfullpathonfolder{
} createfolder_trygetfullpathonfolder;

typedef struct _createvaultfolder_handlecreatefolderfilesystemoperation{
} createvaultfolder_handlecreatefolderfilesystemoperation;

typedef struct _createvaultlinks_loginfo{
} createvaultlinks_loginfo;

typedef struct _createvaultlinks_process{
} createvaultlinks_process;

typedef struct _createvaultlinks_processbaseoneauthmsaluserauthentication_issignedin{
} createvaultlinks_processbaseoneauthmsaluserauthentication_issignedin;

typedef struct _dciutils_dropitemsandtheirdependents{
} dciutils_dropitemsandtheirdependents;

typedef struct _dciutils_getparentfolderid{
} dciutils_getparentfolderid;

typedef struct _dciutils_getparentfolderidbaseoneauthmsaluserauthentication_issignedin{
} dciutils_getparentfolderidbaseoneauthmsaluserauthentication_issignedin;

typedef struct _databasemanager_loaddefaultdb{
} databasemanager_loaddefaultdb;

typedef struct _datetakenmismatchresolver_resolvedatetakenmismatches{
} datetakenmismatchresolver_resolvedatetakenmismatches;

typedef struct _dbfunction_preparebindexecute{
} dbfunction_preparebindexecute;

typedef struct _dbfunction_preparestatement{
} dbfunction_preparestatement;

typedef struct _deletefolder_completeremovefolder{
} deletefolder_completeremovefolder;

typedef struct _deletefolder_completeremovefolderbaseoneauthmsaluserauthentication_issignedin{
} deletefolder_completeremovefolderbaseoneauthmsaluserauthentication_issignedin;

typedef struct _deletefolder_loginfo{
} deletefolder_loginfo;

typedef struct _deletefolder_process{
} deletefolder_process;

typedef struct _deletevalidator_sendtelemetryifnecessary{
} deletevalidator_sendtelemetryifnecessary;

typedef struct _deletevalidator_validatedelete{
} deletevalidator_validatedelete;

typedef struct _deltaproviderfactory_createorvalidatedeltaproviderforupload{
} deltaproviderfactory_createorvalidatedeltaproviderforupload;

typedef struct _deltaproviderfactory_createorvalidatedeltaproviderforuploadbaseoneauthmsaluserauthentication_issignedin{
} deltaproviderfactory_createorvalidatedeltaproviderforuploadbaseoneauthmsaluserauthentication_issignedin;

typedef struct _deprecateddevicehealthtracker_handlehealthsummarybyversion{
} deprecateddevicehealthtracker_handlehealthsummarybyversion;

typedef struct _desktophost_desktophost{
    int64 unk;
} desktophost_desktophost;

typedef struct _desktophost_displayapplicationinitializationerrordialog{
} desktophost_displayapplicationinitializationerrordialog;

typedef struct _desktophost_onaftercomponentinitialization{
} desktophost_onaftercomponentinitialization;

typedef struct _desktophost_ontransition{
    int32 unk;
} desktophost_ontransition;

typedef struct _desktophost_updatepersonallinks{
} desktophost_updatepersonallinks;

typedef struct _desktophost_operator_{
} desktophost_operator_;

typedef struct _desktopiconhandler_setdesktopiconpositions{
} desktopiconhandler_setdesktopiconpositions;

typedef struct _desktopiconhandler_shouldpreservedesktopicon{
} desktopiconhandler_shouldpreservedesktopicon;

typedef struct _deviceid_getcachedrampvalue{
} deviceid_getcachedrampvalue;

typedef struct _deviceid_getrampvaluefordeviceidchangefeature{
} deviceid_getrampvaluefordeviceidchangefeature;

typedef struct _deviceid_getusernameimpl{
} deviceid_getusernameimpl;

typedef struct _diagnostics_collectfileandfolderusageinfo{
} diagnostics_collectfileandfolderusageinfo;

typedef struct _diagnostics_collectnonvolatilewindowsshelldata{
} diagnostics_collectnonvolatilewindowsshelldata;

typedef struct _diagnostics_collectvolatilewindowsshelldata{
} diagnostics_collectvolatilewindowsshelldata;

typedef struct _diagnostics_collectvolatilewindowsshelldatabaseoneauthmsaluserauthentication_issignedin{
} diagnostics_collectvolatilewindowsshelldatabaseoneauthmsaluserauthentication_issignedin;

typedef struct _diagnostics_completeoperation{
} diagnostics_completeoperation;

typedef struct _diagnostics_completesyncdiagnostic{
} diagnostics_completesyncdiagnostic;

typedef struct _diagnostics_flattensyncproblems{
} diagnostics_flattensyncproblems;

typedef struct _diagnostics_recordbandwidthlimitsettingsfordevice{
} diagnostics_recordbandwidthlimitsettingsfordevice;

typedef struct _diagnostics_reportdiagnosticinfofinished{
} diagnostics_reportdiagnosticinfofinished;

typedef struct _diagnostics_reportdiagnosticinfoworker{
} diagnostics_reportdiagnosticinfoworker;

typedef struct _diagnostics_rundiagnostics{
} diagnostics_rundiagnostics;

typedef struct _diagnostics_startreportdiagnosticinfo{
} diagnostics_startreportdiagnosticinfo;

typedef struct _diagnostics_startsyncprogressaudit{
} diagnostics_startsyncprogressaudit;

typedef struct _dimemanager_handlesigninoperationdone{
} dimemanager_handlesigninoperationdone;

typedef struct _dimemanager_isaccountconfigsupported{
} dimemanager_isaccountconfigsupported;

typedef struct _downloadpersister_downloadpersister{
} downloadpersister_downloadpersister;

typedef struct _downloaderutil_comparefilehash{
} downloaderutil_comparefilehash;

typedef struct _downloaderutil_copyfiledatafromstream{
} downloaderutil_copyfiledatafromstream;

typedef struct _downloaderutil_copylocalfile{
} downloaderutil_copylocalfile;

typedef struct _downloaderutil_copylocalfilebaseoneauthmsaluserauthentication_issignedin{
} downloaderutil_copylocalfilebaseoneauthmsaluserauthentication_issignedin;

typedef struct _downloaderutil_downloadandverifyfile{
} downloaderutil_downloadandverifyfile;

typedef struct _downloaderutil_downloadandverifyfilewithofficeconfig{
} downloaderutil_downloadandverifyfilewithofficeconfig;

typedef struct _downloaderutil_downloadandverifyfilewithoutofficeconfig{
} downloaderutil_downloadandverifyfilewithoutofficeconfig;

typedef struct _downloaderutil_downloadfile{
} downloaderutil_downloadfile;

typedef struct _downloaderutil_downloadfilewithadditionalheaders{
} downloaderutil_downloadfilewithadditionalheaders;

typedef struct _downloaderutil_downloadorloadfile{
} downloaderutil_downloadorloadfile;

typedef struct _downloaderutil_downloadorloadfilewithadditionalheaders{
} downloaderutil_downloadorloadfilewithadditionalheaders;

typedef struct _downloaderutil_downloadwithoutverifyingfile{
} downloaderutil_downloadwithoutverifyingfile;

typedef struct _downloaderutil_getfileurl{
} downloaderutil_getfileurl;

typedef struct _downloaderutil_hastimeelapsed{
} downloaderutil_hastimeelapsed;

typedef struct _downloaderutil_reporttelemetry{
} downloaderutil_reporttelemetry;

typedef struct _downloaderutil_setfilehash{
} downloaderutil_setfilehash;

typedef struct _downloaderutil_verifyfile{
} downloaderutil_verifyfile;

typedef struct _drivechangeinterpreter_assignidstodrivechange{
} drivechangeinterpreter_assignidstodrivechange;

typedef struct _drivechangeinterpreter_dropitemsandtheirdependents{
} drivechangeinterpreter_dropitemsandtheirdependents;

typedef struct _drivechangeinterpreter_getparentfolderid{
} drivechangeinterpreter_getparentfolderid;

typedef struct _drivechangeinterpreter_handleexcludeddrivechange{
} drivechangeinterpreter_handleexcludeddrivechange;

typedef struct _drivechangeinterpreter_interpretchanges{
} drivechangeinterpreter_interpretchanges;

typedef struct _drivechangeinterpreter_old_assignidstodrivechange{
} drivechangeinterpreter_old_assignidstodrivechange;

typedef struct _drivechangeinterpreter_old_dropitemsandtheirdependents{
} drivechangeinterpreter_old_dropitemsandtheirdependents;

typedef struct _drivechangeinterpreter_old_filteroutchangeswhichareexpectedtofail{
} drivechangeinterpreter_old_filteroutchangeswhichareexpectedtofail;

typedef struct _drivechangeinterpreter_old_findfilemoves{
} drivechangeinterpreter_old_findfilemoves;

typedef struct _drivechangeinterpreter_old_findfilemovesbaseoneauthmsaluserauthentication_issignedin{
} drivechangeinterpreter_old_findfilemovesbaseoneauthmsaluserauthentication_issignedin;

typedef struct _drivechangeinterpreter_old_getparentfolderid{
} drivechangeinterpreter_old_getparentfolderid;

typedef struct _drivechangeinterpreter_old_getparentfolderidbaseoneauthmsaluserauthentication_issignedin{
} drivechangeinterpreter_old_getparentfolderidbaseoneauthmsaluserauthentication_issignedin;

typedef struct _drivechangeinterpreter_old_handleexcludeddrivechange{
} drivechangeinterpreter_old_handleexcludeddrivechange;

typedef struct _drivechangeinterpreter_old_handlepotentialfsidorparentchanges{
} drivechangeinterpreter_old_handlepotentialfsidorparentchanges;

typedef struct _drivechangeinterpreter_old_interpretchanges{
} drivechangeinterpreter_old_interpretchanges;

typedef struct _drivechangeinterpreter_old_performfsidlookupfordeletions{
} drivechangeinterpreter_old_performfsidlookupfordeletions;

typedef struct _drivechangeinterpreter_old_persistdeletesinchangestosendtodb{
} drivechangeinterpreter_old_persistdeletesinchangestosendtodb;

typedef struct _drivechangeinterpreter_old_postprocessfiledrivechanges{
} drivechangeinterpreter_old_postprocessfiledrivechanges;

typedef struct _drivechangeinterpreter_old_postprocessfolderdrivechanges{
} drivechangeinterpreter_old_postprocessfolderdrivechanges;

typedef struct _drivechangeinterpreter_old_processlocaldrivechanges{
} drivechangeinterpreter_old_processlocaldrivechanges;

typedef struct _drivechangeinterpreter_persistdeletesinchangestosendtodb{
} drivechangeinterpreter_persistdeletesinchangestosendtodb;

typedef struct _drivechangeinterpreter_postprocessfiledrivechanges{
} drivechangeinterpreter_postprocessfiledrivechanges;

typedef struct _drivechangeinterpreter_postprocessfolderdrivechanges{
} drivechangeinterpreter_postprocessfolderdrivechanges;

typedef struct _drivechangeinterpreter_prepareforinterpretchanges{
} drivechangeinterpreter_prepareforinterpretchanges;

typedef struct _drivechangeinterpreter_processlocaldrivechanges{
} drivechangeinterpreter_processlocaldrivechanges;

typedef struct _drivechangeinterpreter_runinterpretchanges{
} drivechangeinterpreter_runinterpretchanges;

typedef struct _drivechangeinterpreter_runinterpretchangesbaseoneauthmsaluserauthentication_issignedin{
} drivechangeinterpreter_runinterpretchangesbaseoneauthmsaluserauthentication_issignedin;

typedef struct _drivechangeinterpreter_setexcludedstateonunsyncedfileifnecessary{
} drivechangeinterpreter_setexcludedstateonunsyncedfileifnecessary;

typedef struct _drivechangeinterpreter_operator_{
} drivechangeinterpreter_operator_;

typedef struct _driveinfoconsumer_initrootscopewithdbheaderstatusesifrequired{
} driveinfoconsumer_initrootscopewithdbheaderstatusesifrequired;

typedef struct _driveinfoconsumer_loadsyncscopes{
} driveinfoconsumer_loadsyncscopes;

typedef struct _driveinfoconsumer_mountvaultscope{
} driveinfoconsumer_mountvaultscope;

typedef struct _driveinfoconsumer_setlocalmaxpathvalue{
} driveinfoconsumer_setlocalmaxpathvalue;

typedef struct _dropexcludedorignoreditemsandtheirdependentsdciworkitem_handleexcludeddrivechange{
} dropexcludedorignoreditemsandtheirdependentsdciworkitem_handleexcludeddrivechange;

typedef struct _ecsconfigurationmanager_isecsenabled{
} ecsconfigurationmanager_isecsenabled;

typedef struct _ecsconfigurationmanager_sendupdatetelemetrybaseoneauthmsaluserauthentication_issignedin{
} ecsconfigurationmanager_sendupdatetelemetrybaseoneauthmsaluserauthentication_issignedin;

typedef struct _ecsconfigurationupdater_onnotification{
} ecsconfigurationupdater_onnotification;

typedef struct _ecsconfigurationupdater_startupdatetimer{
} ecsconfigurationupdater_startupdatetimer;

typedef struct _ecsconfigurationupdater_startupdatetimerbaseoneauthmsaluserauthentication_issignedin{
} ecsconfigurationupdater_startupdatetimerbaseoneauthmsaluserauthentication_issignedin;

typedef struct _edpwrapper_initbyuserlogin{
} edpwrapper_initbyuserlogin;

typedef struct _edpwrapper_initedpmanagedforcurrententerpriseidentity{
} edpwrapper_initedpmanagedforcurrententerpriseidentity;

typedef struct _emailhrdcontroller_handleemailhrdresultsilentbusinessconfig{
} emailhrdcontroller_handleemailhrdresultsilentbusinessconfig;

typedef struct _emailhrdmodel_persistemailhrdinfo{
} emailhrdmodel_persistemailhrdinfo;

typedef struct _emailhrdrequest_parseofficeconfigresponse{
} emailhrdrequest_parseofficeconfigresponse;

typedef struct _emailhrdrequest_sendandwait{
} emailhrdrequest_sendandwait;

typedef struct _emailhrdrequest_sendemailhrdrequest{
} emailhrdrequest_sendemailhrdrequest;

typedef struct _emailhrdrequest_sendfederationrequest{
} emailhrdrequest_sendfederationrequest;

typedef struct _emailhrdrequest_sendidentityrequest{
} emailhrdrequest_sendidentityrequest;

typedef struct _enclosuredownloader_blockdownloadcompleted{
} enclosuredownloader_blockdownloadcompleted;

typedef struct _enclosuredownloader_completedownload{
} enclosuredownloader_completedownload;

typedef struct _enclosuredownloader_executenextdownloadstep{
} enclosuredownloader_executenextdownloadstep;

typedef struct _enclosuredownloader_getlengthoffilefromresponseheaders{
} enclosuredownloader_getlengthoffilefromresponseheaders;

typedef struct _enclosuredownloader_getmindiskspacelimitinbytes{
} enclosuredownloader_getmindiskspacelimitinbytes;

typedef struct _enclosuredownloader_initializefromplaceholder{
} enclosuredownloader_initializefromplaceholder;

typedef struct _enclosuredownloader_startdownload{
} enclosuredownloader_startdownload;

typedef struct _enclosuredownloader_startnextblockdownload{
} enclosuredownloader_startnextblockdownload;

typedef struct _enclosuredownloader_startnextblockdownloadbaseoneauthmsaluserauthentication_issignedin{
} enclosuredownloader_startnextblockdownloadbaseoneauthmsaluserauthentication_issignedin;

typedef struct _enclosureuploader_completeupload{
} enclosureuploader_completeupload;

typedef struct _enclosureuploader_doesfileadditionneedtobeuploaded{
} enclosureuploader_doesfileadditionneedtobeuploaded;

typedef struct _enclosureuploader_initializefileforread{
} enclosureuploader_initializefileforread;

typedef struct _enclosureuploader_logcurrentupload{
} enclosureuploader_logcurrentupload;

typedef struct _enclosureuploader_startupload{
} enclosureuploader_startupload;

typedef struct _enclosureuploader_transferinline{
} enclosureuploader_transferinline;

typedef struct _enumchanges_synclist{
} enumchanges_synclist;

typedef struct _enumchanges_triggerlistunsync{
} enumchanges_triggerlistunsync;

typedef struct _enumlistshomechangesv1_addorupdateliststosyncifneeded{
} enumlistshomechangesv1_addorupdateliststosyncifneeded;

typedef struct _enumlistshomechangesv1_addorupdateliststosyncifneededbaseoneauthmsaluserauthentication_issignedin{
} enumlistshomechangesv1_addorupdateliststosyncifneededbaseoneauthmsaluserauthentication_issignedin;

typedef struct _enumlistshomechanges_addorupdateliststosyncifneeded{
} enumlistshomechanges_addorupdateliststosyncifneeded;

typedef struct _errorhandler_addlibraryerrortoprimaryerrorstates{
} errorhandler_addlibraryerrortoprimaryerrorstates;

typedef struct _errorhandler_processlibraryerror{
} errorhandler_processlibraryerror;

typedef struct _errorhandler_showtoastforaddederror{
} errorhandler_showtoastforaddederror;

typedef struct _errorhandler_showtoastforaddederrorbaseoneauthmsaluserauthentication_issignedin{
} errorhandler_showtoastforaddederrorbaseoneauthmsaluserauthentication_issignedin;

typedef struct _errortelemetry_sendtelemetry{
} errortelemetry_sendtelemetry;

typedef struct _errortransforms_loadformattedactionparameter{
} errortransforms_loadformattedactionparameter;

typedef struct _eventaggregator_sendbackofftelemetry{
} eventaggregator_sendbackofftelemetry;

typedef struct _eventmachineasynctask_dowork{
} eventmachineasynctask_dowork;

typedef struct _eventmachinescheduler_attachthreadpool{
    int32 size;
    char data[size];
    int8 unk;
} eventmachinescheduler_attachthreadpool;

typedef struct _eventmachinescheduler_createasynctaskimpl{
} eventmachinescheduler_createasynctaskimpl;

typedef struct _eventmachinescheduler_detachthreadpool{
} eventmachinescheduler_detachthreadpool;

typedef struct _eventmachinetimer_eventmachinetimer{
} eventmachinetimer_eventmachinetimer;

typedef struct _eventmachinetimer_operator_{
} eventmachinetimer_operator_;

typedef struct _eventmachine_attachthread{
    int32 size;
    char data[size];
} eventmachine_attachthread;

typedef struct _eventmachine_createtimer{
} eventmachine_createtimer;

typedef struct _eventmachine_delivereventtodispatcher{
} eventmachine_delivereventtodispatcher;

typedef struct _eventmachine_detachthread{
} eventmachine_detachthread;

typedef struct _eventmachine_fireevent{
} eventmachine_fireevent;

typedef struct _featuresupport_evaluateconfiguration{
} featuresupport_evaluateconfiguration;

typedef struct _featuresupport_loadconfiguration{
} featuresupport_loadconfiguration;

typedef struct _fileneededeventlistener_notifyactivehydrationneeded{
} fileneededeventlistener_notifyactivehydrationneeded;

typedef struct _fileneededeventlistener_notifyactivehydrationnotneeded{
} fileneededeventlistener_notifyactivehydrationnotneeded;

typedef struct _fileneededeventlistener_notifyfilenotneeded{
} fileneededeventlistener_notifyfilenotneeded;

typedef struct _fileneededeventlistener_notifyfiletransfercomplete{
} fileneededeventlistener_notifyfiletransfercomplete;

typedef struct _filerealpath_disklookup{
} filerealpath_disklookup;

typedef struct _filesavepatternresolver_parsesetting{
} filesavepatternresolver_parsesetting;

typedef struct _filestatusnotifier_adddriveerror{
} filestatusnotifier_adddriveerror;

typedef struct _filestatusnotifier_additemtowarningstate{
} filestatusnotifier_additemtowarningstate;

typedef struct _filestatusnotifier_logitemstatusnotification{
} filestatusnotifier_logitemstatusnotification;

typedef struct _filestatusnotifier_sweepallwarnings{
} filestatusnotifier_sweepallwarnings;

typedef struct _filestatusnotifier_sweepallwarningsbaseoneauthmsaluserauthentication_issignedin{
} filestatusnotifier_sweepallwarningsbaseoneauthmsaluserauthentication_issignedin;

typedef struct _filesystemdeletenotifications_operator_{
} filesystemdeletenotifications_operator_;

typedef struct _filesystemid_getcurrentpath{
} filesystemid_getcurrentpath;

typedef struct _filetransfercoordinator_activehydrationneeded{
} filetransfercoordinator_activehydrationneeded;

typedef struct _filetransfercoordinator_filefetchnotneeded{
} filetransfercoordinator_filefetchnotneeded;

typedef struct _filetransfercoordinator_filefetchnotneededbaseoneauthmsaluserauthentication_issignedin{
} filetransfercoordinator_filefetchnotneededbaseoneauthmsaluserauthentication_issignedin;

typedef struct _filetransfercoordinator_filefetched{
} filetransfercoordinator_filefetched;

typedef struct _filetransfercoordinator_loadinitialneededfiles{
} filetransfercoordinator_loadinitialneededfiles;

typedef struct _filteroutchangeswhichareexpectedtofaildciworkitem_process{
} filteroutchangeswhichareexpectedtofaildciworkitem_process;

typedef struct _firstdeletemanager_initializecomponent{
} firstdeletemanager_initializecomponent;

typedef struct _firstdeletemanager_postinitialize{
} firstdeletemanager_postinitialize;

typedef struct _firstrunwizardoperations_sendwizardendedtelemetry{
} firstrunwizardoperations_sendwizardendedtelemetry;

typedef struct _fixupdrivechanges_marksentchangesafterfailure{
} fixupdrivechanges_marksentchangesafterfailure;

typedef struct _folderconfigurationhelpers_getdefaultrootfoldername{
} folderconfigurationhelpers_getdefaultrootfoldername;

typedef struct _folderconfigurationhelpers_getuservisiblerootfolder{
} folderconfigurationhelpers_getuservisiblerootfolder;

typedef struct _genericstartupsocket_detachsocket{
} genericstartupsocket_detachsocket;

typedef struct _genericstartupsocket_handleonconnected{
} genericstartupsocket_handleonconnected;

typedef struct _genericstartupsocket_metamorphose{
} genericstartupsocket_metamorphose;

typedef struct _getselectivesyncinformationcallbackhandler_endgetselectivesyncinformation{
    int 32 size1;
    char data1[size1];
    int32 size2;
    char data2[size2];
    int32 unk1;
    int32 size3;
    char data3[size3];
    int32 unk2;
    int32 unk3;
    int64 unk4;
    int64 unk5;
} getselectivesyncinformationcallbackhandler_endgetselectivesyncinformation;

typedef struct _graphrequestor_makegraphrequest{
} graphrequestor_makegraphrequest;

typedef struct _groovetakeoverhelper_handlerampsupdated{
} groovetakeoverhelper_handlerampsupdated;

typedef struct _httphandlermap_addhttphandler{
} httphandlermap_addhttphandler;

typedef struct _handlepotentialfsidorparentchangesdciworkitem_process{
} handlepotentialfsidorparentchangesdciworkitem_process;

typedef struct _healingpersister_loadhealingstatefromdisk{
} healingpersister_loadhealingstatefromdisk;

typedef struct _healing_canrunhealingfordivergence{
} healing_canrunhealingfordivergence;

typedef struct _healing_getcurrenthealingstate{
} healing_getcurrenthealingstate;

typedef struct _healing_ishealingcurrentlybackedoff{
} healing_ishealingcurrentlybackedoff;

typedef struct _httpapitelemetryscenario_reportnow{
} httpapitelemetryscenario_reportnow;

typedef struct _httpapi_backoff{
} httpapi_backoff;

typedef struct _httpapi_logresponse{
} httpapi_logresponse;

typedef struct _httpapi_sendrequest{
} httpapi_sendrequest;

typedef struct _httpapi_sendrequestbaseoneauthmsaluserauthentication_issignedin{
} httpapi_sendrequestbaseoneauthmsaluserauthentication_issignedin;

typedef struct _hydrateplaceholder_doasyncwork{
} hydrateplaceholder_doasyncwork;

typedef struct _hydrateplaceholder_process{
} hydrateplaceholder_process;

typedef struct _hydrateplaceholder_validateplaceholderdata{
} hydrateplaceholder_validateplaceholderdata;

typedef struct _iothread_threadmain{
} iothread_threadmain;

typedef struct _idlejobmanager_execute{
} idlejobmanager_execute;

typedef struct _idlejobmanager_idlejobfactory{
} idlejobmanager_idlejobfactory;

typedef struct _idlejobmanager_idlejobfactorybaseoneauthmsaluserauthentication_issignedin{
} idlejobmanager_idlejobfactorybaseoneauthmsaluserauthentication_issignedin;

typedef struct _importmanager_enablecontroller{
} importmanager_enablecontroller;

typedef struct _importmanager_onnotification{
} importmanager_onnotification;

typedef struct _importscreenshot_hotkeywndproc{
} importscreenshot_hotkeywndproc;

typedef struct _instrumentation_endqosexperience{
} instrumentation_endqosexperience;

typedef struct _instrumentation_endqospoint{
} instrumentation_endqospoint;

typedef struct _instrumentation_startqospoint{
} instrumentation_startqospoint;

typedef struct _invokable_error{
} invokable_error;

typedef struct _irismanager_isallowedtorun{
} irismanager_isallowedtorun;

typedef struct _irismanager_isirisrampenabled{
} irismanager_isirisrampenabled;

typedef struct _irismanager_onloginevent{
} irismanager_onloginevent;

typedef struct _irismanager_readnextexpectedupdatetime{
} irismanager_readnextexpectedupdatetime;

typedef struct _irismanager_stopperiodictimer{
} irismanager_stopperiodictimer;

typedef struct _irismanager_trystart{
} irismanager_trystart;

typedef struct _irisparser_getexpectedchildnode{
} irisparser_getexpectedchildnode;

typedef struct _irisparser_interpreterrorcode{
} irisparser_interpreterrorcode;

typedef struct _irisparser_parseerrorsnode{
} irisparser_parseerrorsnode;

typedef struct _irisparser_parseitemsnode{
} irisparser_parseitemsnode;

typedef struct _irisrequestprocessor_checkifrequestsucceeded{
} irisrequestprocessor_checkifrequestsucceeded;

typedef struct _itemstatusmanager_addwarnings{
} itemstatusmanager_addwarnings;

typedef struct _itemstatusmanager_logallwarningstelemetry{
} itemstatusmanager_logallwarningstelemetry;

typedef struct _itemstatusmanager_updatefolderentries{
} itemstatusmanager_updatefolderentries;

typedef struct _itemstatusmanager_updatefolderentriesbaseoneauthmsaluserauthentication_issignedin{
} itemstatusmanager_updatefolderentriesbaseoneauthmsaluserauthentication_issignedin;

typedef struct _kfmeventhandler_startmigrationoperation{
} kfmeventhandler_startmigrationoperation;

typedef struct _kfmlockedfilehandler_attemptlockedfileretry{
} kfmlockedfilehandler_attemptlockedfileretry;

typedef struct _kfmlockedfilehandler_getcachedsourcepaths{
} kfmlockedfilehandler_getcachedsourcepaths;

typedef struct _kfmlockedfilehandler_handlemigrationnotification{
} kfmlockedfilehandler_handlemigrationnotification;

typedef struct _kfmmanager_processkfmmigrationdoneevent{
} kfmmanager_processkfmmigrationdoneevent;

typedef struct _kfmmanager_processkfmmigrationinitiatedevent{
} kfmmanager_processkfmmigrationinitiatedevent;

typedef struct _kfmmanager_processscannedkfmdestinationpaths{
} kfmmanager_processscannedkfmdestinationpaths;

typedef struct _kfmredirectcheckhelper_isrootfolderpathset{
} kfmredirectcheckhelper_isrootfolderpathset;

typedef struct _kfmredirectcheckhelper_setrootfolderpath{
} kfmredirectcheckhelper_setrootfolderpath;

typedef struct _kfmsilentflowlauncher_firegpotelemetry{
} kfmsilentflowlauncher_firegpotelemetry;

typedef struct _kfmsilentflowlauncher_getcurrentonedriveoobekeystate{
} kfmsilentflowlauncher_getcurrentonedriveoobekeystate;

typedef struct _kfmsilentflowlauncher_getcurrentonedriveoobekeyvalue{
} kfmsilentflowlauncher_getcurrentonedriveoobekeyvalue;

typedef struct _kfmsilentflowlauncher_iskfmgpoapplied{
} kfmsilentflowlauncher_iskfmgpoapplied;

typedef struct _kfmsilentflowlauncher_launchkfmonwcosifneeded{
} kfmsilentflowlauncher_launchkfmonwcosifneeded;

typedef struct _kfmsilentflowlauncher_launchkfmpostoobeifneeded{
} kfmsilentflowlauncher_launchkfmpostoobeifneeded;

typedef struct _kfmsilentflowlauncher_launchkfmpostscoobeifneeded{
} kfmsilentflowlauncher_launchkfmpostscoobeifneeded;

typedef struct _kfmsilentflowlauncher_launchkfmrepairifneeded{
} kfmsilentflowlauncher_launchkfmrepairifneeded;

typedef struct _kfmsilentflowlauncher_loadsavedmigrationstate{
} kfmsilentflowlauncher_loadsavedmigrationstate;

typedef struct _kfmsilentflowlauncher_performgpoactionifneeded{
} kfmsilentflowlauncher_performgpoactionifneeded;

typedef struct _kfmsilentflowlauncher_removefolderfromsavedmigrationstate{
} kfmsilentflowlauncher_removefolderfromsavedmigrationstate;

typedef struct _kfmsilentflowlauncher_savemigrationstatetoregistry{
} kfmsilentflowlauncher_savemigrationstatetoregistry;

typedef struct _kfmsilentflowlauncher_savemigrationstatetoregistryinternal{
} kfmsilentflowlauncher_savemigrationstatetoregistryinternal;

typedef struct _kfmsilentflowlauncher_setcurrentonedriveoobekey{
} kfmsilentflowlauncher_setcurrentonedriveoobekey;

typedef struct _kfmsilentflowlauncher_operator_{
} kfmsilentflowlauncher_operator_;

typedef struct _kfmfpscampaign_iscampaignenabled{
} kfmfpscampaign_iscampaignenabled;

typedef struct _knownfoldermigrate_findknownfoldersnestedunderpath{
} knownfoldermigrate_findknownfoldersnestedunderpath;

typedef struct _knownfoldermigrate_firekfmovefoldercontentstelemetry{
} knownfoldermigrate_firekfmovefoldercontentstelemetry;

typedef struct _knownfoldermigrate_migratekfinternal{
} knownfoldermigrate_migratekfinternal;

typedef struct _knownfoldermigrate_operator_{
} knownfoldermigrate_operator_;

typedef struct _knownfolderredirect_init{
} knownfolderredirect_init;

typedef struct _knownfolderredirect_maponedriveknownfolder{
} knownfolderredirect_maponedriveknownfolder;

typedef struct _knownfolderredirect_updateknownfolderinternal{
} knownfolderredirect_updateknownfolderinternal;

typedef struct _knownfolderredirect_updateosknownfolder{
} knownfolderredirect_updateosknownfolder;

typedef struct _knownfolderredirect_updatewindowsandonedriveknownfolder{
} knownfolderredirect_updatewindowsandonedriveknownfolder;

typedef struct _knownfolderredirect_updatewindowsknownfolder{
} knownfolderredirect_updatewindowsknownfolder;

typedef struct _knownfolderredirect_operator_{
} knownfolderredirect_operator_;

typedef struct _listsyncengine_changelistsyncstateifpossible{
} listsyncengine_changelistsyncstateifpossible;

typedef struct _listsyncengine_changesyncstateandrunstatemachineasyncifpossible{
} listsyncengine_changesyncstateandrunstatemachineasyncifpossible;

typedef struct _listsyncengine_recordlistunsyncscenario{
} listsyncengine_recordlistunsyncscenario;

typedef struct _localmassdeletemanager_getdeletedfilecountindeletecandidates{
} localmassdeletemanager_getdeletedfilecountindeletecandidates;

typedef struct _localmassdeletemanager_localmassdeletemanager{
} localmassdeletemanager_localmassdeletemanager;

typedef struct _localmassdeletemanager_oninterpretchanges{
} localmassdeletemanager_oninterpretchanges;

typedef struct _localmassdeletemanager_processchangesinmassdeletestate{
} localmassdeletemanager_processchangesinmassdeletestate;

typedef struct _localmassdeletemanager_updatesettings{
} localmassdeletemanager_updatesettings;

typedef struct _lockfilemanager_createlockfile{
} lockfilemanager_createlockfile;

typedef struct _lockfilemanager_readlockfile{
} lockfilemanager_readlockfile;

typedef struct _lockfilemanager_takelockonlockfile{
} lockfilemanager_takelockonlockfile;

typedef struct _lockfilemanager_validatemountpointconsistency{
} lockfilemanager_validatemountpointconsistency;

typedef struct _logdevicefailuredatagram_recordqostelemetryfailure{
} logdevicefailuredatagram_recordqostelemetryfailure;

typedef struct _loguploader2_buildlogbatchqueue{
} loguploader2_buildlogbatchqueue;

typedef struct _loguploader2_clearuploadqueue{
} loguploader2_clearuploadqueue;

typedef struct _loguploader2_executelogcompression{
} loguploader2_executelogcompression;

typedef struct _loguploader2_executeloguploadbatch{
} loguploader2_executeloguploadbatch;

typedef struct _loguploader2_getfilehash{
} loguploader2_getfilehash;

typedef struct _loguploader2_getlastactiveloginformation{
} loguploader2_getlastactiveloginformation;

typedef struct _loguploader2_getloguploaderqueuedfile{
} loguploader2_getloguploaderqueuedfile;

typedef struct _loguploader2_logbatchisready{
} loguploader2_logbatchisready;

typedef struct _loguploader2_mainloopworker{
} loguploader2_mainloopworker;

typedef struct _loguploader2_reportstateifneeded{
} loguploader2_reportstateifneeded;

typedef struct _loguploader2_scanforunuploadedlogs{
} loguploader2_scanforunuploadedlogs;

typedef struct _loguploader2_scanforunuploadedlogshelper{
} loguploader2_scanforunuploadedlogshelper;

typedef struct _loguploader2_startnextloguploadbatchifable{
} loguploader2_startnextloguploadbatchifable;

typedef struct _loguploaderserviceapi_backoff{
} loguploaderserviceapi_backoff;

typedef struct _loguploaderserviceapi_getauthheader{
} loguploaderserviceapi_getauthheader;

typedef struct _loguploaderserviceapi_getlogbatchuploadlocation{
} loguploaderserviceapi_getlogbatchuploadlocation;

typedef struct _loguploaderserviceapi_isauthenticated{
} loguploaderserviceapi_isauthenticated;

typedef struct _loguploaderserviceapi_logresponse{
} loguploaderserviceapi_logresponse;

typedef struct _loguploader_clearuploadqueue{
} loguploader_clearuploadqueue;

typedef struct _loguploader_getpolicyint{
} loguploader_getpolicyint;

typedef struct _loguploader_getpolicystring{
} loguploader_getpolicystring;

typedef struct _loguploader_schedulelogupload{
} loguploader_schedulelogupload;

typedef struct _loguploader_updateallcachedvalues{
} loguploader_updateallcachedvalues;

typedef struct _loggingapi_loggingaddtomultivaluecommondatapoint{
} loggingapi_loggingaddtomultivaluecommondatapoint;

typedef struct _loggingapi_loggingfinalizebasiccommondatapoints{
} loggingapi_loggingfinalizebasiccommondatapoints;

typedef struct _loggingapi_loggingreconfigure{
} loggingapi_loggingreconfigure;

typedef struct _loggingapi_loggingremovefrommultivaluecommondatapoint{
} loggingapi_loggingremovefrommultivaluecommondatapoint;

typedef struct _loggingapi_loggingsetcommondatapoint{
    int32 size;
    char data[size];
    int32 size2;
    char data2[size2];
} loggingapi_loggingsetcommondatapoint;

typedef struct _loggingapi_loggingsetcommondatapointuserid{
} loggingapi_loggingsetcommondatapointuserid;

typedef struct _loggingapi_updateobfuscationencryptionkey{
} loggingapi_updateobfuscationencryptionkey;

typedef struct _loggingapi_updateobfuscationencryptionkeybaseoneauthmsaluserauthentication_issignedin{
} loggingapi_updateobfuscationencryptionkeybaseoneauthmsaluserauthentication_issignedin;

typedef struct _loggingtelemetrysession_updatetelemetrytransmissionprofile{
} loggingtelemetrysession_updatetelemetrytransmissionprofile;

typedef struct _logincallbackhandler_endlogin{
} logincallbackhandler_endlogin;

typedef struct _loginstatemanager_beginauthsignin{
} loginstatemanager_beginauthsignin;

typedef struct _loginstatemanager_deferredprocesscoreapisigninresult{
} loginstatemanager_deferredprocesscoreapisigninresult;

typedef struct _loginstatemanager_handlerequestsignoutonwizardclosed{
} loginstatemanager_handlerequestsignoutonwizardclosed;

typedef struct _loginstatemanager_handlewizardconnectrequest{
} loginstatemanager_handlewizardconnectrequest;

typedef struct _loginstatemanager_initializecomponent{
} loginstatemanager_initializecomponent;

typedef struct _loginstatemanager_isexpresssigninallowedforcurrentuser{
} loginstatemanager_isexpresssigninallowedforcurrentuser;

typedef struct _loginstatemanager_isexpresssigninallowedwithconnectedidcookie{
} loginstatemanager_isexpresssigninallowedwithconnectedidcookie;

typedef struct _loginstatemanager_issigninneeded{
} loginstatemanager_issigninneeded;

typedef struct _loginstatemanager_oninitialupdatecheckcomplete{
} loginstatemanager_oninitialupdatecheckcomplete;

typedef struct _loginstatemanager_onsyncenginesignincompleted{
} loginstatemanager_onsyncenginesignincompleted;

typedef struct _loginstatemanager_postinitialize{
} loginstatemanager_postinitialize;

typedef struct _loginstatemanager_signinwithui{
} loginstatemanager_signinwithui;

typedef struct _loginstatemanager_operator_{
} loginstatemanager_operator_;

typedef struct _moifootprint_invoke{
} moifootprint_invoke;

typedef struct _memoryusage_updateprocess{
} memoryusage_updateprocess;

typedef struct _migrationmanager_canperformbackgroundscan{
} migrationmanager_canperformbackgroundscan;

typedef struct _migrationmanager_checkforfolderaccessoperation{
} migrationmanager_checkforfolderaccessoperation;

typedef struct _migrationmanager_determinemoveorredirect{
} migrationmanager_determinemoveorredirect;

typedef struct _migrationmanager_executemigrate{
} migrationmanager_executemigrate;

typedef struct _migrationmanager_fireknownfolderstatetelemetry{
} migrationmanager_fireknownfolderstatetelemetry;

typedef struct _migrationmanager_fireoperationtelemetry{
} migrationmanager_fireoperationtelemetry;

typedef struct _migrationmanager_getlocalenameforprovisioning{
} migrationmanager_getlocalenameforprovisioning;

typedef struct _migrationmanager_handleallbackgroundscanscomplete{
} migrationmanager_handleallbackgroundscanscomplete;

typedef struct _migrationmanager_handleallbackgroundscanscompletebaseoneauthmsaluserauthentication_issignedin{
} migrationmanager_handleallbackgroundscanscompletebaseoneauthmsaluserauthentication_issignedin;

typedef struct _migrationmanager_handlegetspecialfolderinfonotification{
} migrationmanager_handlegetspecialfolderinfonotification;

typedef struct _migrationmanager_handlemigrationoperation{
} migrationmanager_handlemigrationoperation;

typedef struct _migrationmanager_handlescanoperation{
} migrationmanager_handlescanoperation;

typedef struct _migrationmanager_ismoveenabled{
} migrationmanager_ismoveenabled;

typedef struct _migrationmanager_setbackgroundscantimer{
} migrationmanager_setbackgroundscantimer;

typedef struct _migrationmanager_startbackgroundscan{
} migrationmanager_startbackgroundscan;

typedef struct _migrationmanager_startmigrationoperation{
} migrationmanager_startmigrationoperation;

typedef struct _migrationmanager_startoverquotacheckoperation{
} migrationmanager_startoverquotacheckoperation;

typedef struct _migrationmanager_startprovisionhelper{
} migrationmanager_startprovisionhelper;

typedef struct _migrationmanager_startscanoperation{
} migrationmanager_startscanoperation;

typedef struct _migrationmanager_updateoptedinfolderscache{
} migrationmanager_updateoptedinfolderscache;

typedef struct _migrationoperation_execute{
} migrationoperation_execute;

typedef struct _migrationscan_firecrossvolumetelemetry{
} migrationscan_firecrossvolumetelemetry;

typedef struct _migrationscan_firescantelemetry{
} migrationscan_firescantelemetry;

typedef struct _migrationscan_intersectcollections{
} migrationscan_intersectcollections;

typedef struct _migrationscan_redirectioncapabilitiescheck{
} migrationscan_redirectioncapabilitiescheck;

typedef struct _migrationscan_shouldscanexit{
} migrationscan_shouldscanexit;

typedef struct _migrationscan_sizecheck{
} migrationscan_sizecheck;

typedef struct _migrationscan_startscan{
} migrationscan_startscan;

typedef struct _minversionsupporthelper_getcurrentminsupportedversion{
} minversionsupporthelper_getcurrentminsupportedversion;

typedef struct _minversionsupporthelper_getfutureminsupportedversion{
} minversionsupporthelper_getfutureminsupportedversion;

typedef struct _minversionsupporthelper_iscurrentversionsupportedandsendtelemetry{
} minversionsupporthelper_iscurrentversionsupportedandsendtelemetry;

typedef struct _missingfile_computerates{
} missingfile_computerates;

typedef struct _missingfile_logdownloadtelemetry{
} missingfile_logdownloadtelemetry;

typedef struct _missingfile_loghydrationtelemetry{
} missingfile_loghydrationtelemetry;

typedef struct _modifiedattributes_adddependenciesforfilecrossusercopyclusteringbyscope{
} modifiedattributes_adddependenciesforfilecrossusercopyclusteringbyscope;

typedef struct _mountscenarios_report{
} mountscenarios_report;

typedef struct _mountedfolderapihandler_handleconnectmountedfolder{
} mountedfolderapihandler_handleconnectmountedfolder;

typedef struct _mountedfolderapihandler_prepareforconnectall{
} mountedfolderapihandler_prepareforconnectall;

typedef struct _mountedfoldercallbackhandler_endconnectmountedfolder{
} mountedfoldercallbackhandler_endconnectmountedfolder;

typedef struct _mountedfoldercallbackhandler_endgetlibraries{
} mountedfoldercallbackhandler_endgetlibraries;

typedef struct _mountedfoldercallbackhandler_endgetmountedfolders{
} mountedfoldercallbackhandler_endgetmountedfolders;

typedef struct _mountedfoldercallbackhandler_endmaplibrary{
} mountedfoldercallbackhandler_endmaplibrary;

typedef struct _mountedfoldermanager_addfolderinfotomountedfoldertree{
} mountedfoldermanager_addfolderinfotomountedfoldertree;

typedef struct _mountedfoldermanager_addmountedfoldertoitemstatusmanager{
} mountedfoldermanager_addmountedfoldertoitemstatusmanager;

typedef struct _mountedfoldermanager_onconnectmountedfoldercomplete{
} mountedfoldermanager_onconnectmountedfoldercomplete;

typedef struct _mountedfoldermanager_ongetmountedfolderscomplete{
} mountedfoldermanager_ongetmountedfolderscomplete;

typedef struct _mountedfoldermanager_registersyncengineprovider{
} mountedfoldermanager_registersyncengineprovider;

typedef struct _mountedfoldermanager_operator_{
} mountedfoldermanager_operator_;

typedef struct _movefile_loginfo{
} movefile_loginfo;

typedef struct _movefile_process{
} movefile_process;

typedef struct _movefile_updateandcommit{
} movefile_updateandcommit;

typedef struct _movefile_updateandcommitbaseoneauthmsaluserauthentication_issignedin{
} movefile_updateandcommitbaseoneauthmsaluserauthentication_issignedin;

typedef struct _movefoldercontentsprogresssink_postmoveitem{
} movefoldercontentsprogresssink_postmoveitem;

typedef struct _movefoldercontents_createdirandrecordresult{
} movefoldercontents_createdirandrecordresult;

typedef struct _movefoldercontents_deleteemptyfoldersfromtree{
} movefoldercontents_deleteemptyfoldersfromtree;

typedef struct _movefoldercontents_easymovefiles{
} movefoldercontents_easymovefiles;

typedef struct _movefoldercontents_hardmove{
} movefoldercontents_hardmove;

typedef struct _movefoldercontents_removedirectorywrapper{
} movefoldercontents_removedirectorywrapper;

typedef struct _movefoldercontents_tryeasymove{
} movefoldercontents_tryeasymove;

typedef struct _movefolder_loginfo{
} movefolder_loginfo;

typedef struct _movefolder_process{
} movefolder_process;

typedef struct _movefolder_processbaseoneauthmsaluserauthentication_issignedin{
} movefolder_processbaseoneauthmsaluserauthentication_issignedin;

typedef struct _noestartscenariotelemetry_recordscenario{
} noestartscenariotelemetry_recordscenario;

typedef struct _noestartscenariotelemetry_recordscenariobaseoneauthmsaluserauthentication_issignedin{
} noestartscenariotelemetry_recordscenariobaseoneauthmsaluserauthentication_issignedin;

typedef struct _namedmutexwrapper_release{
} namedmutexwrapper_release;

typedef struct _namedmutexwrapper_tryacquireandwait{  // needs work
    int32 size;
    char data[size];
} namedmutexwrapper_tryacquireandwait;

typedef struct _namedsemaphorewrapper_release{
} namedsemaphorewrapper_release;

typedef struct _namedsemaphorewrapper_tryacquireandwait{
} namedsemaphorewrapper_tryacquireandwait;

typedef struct _namespacevalidator_validate{
} namespacevalidator_validate;

typedef struct _networkawarenessmanager_onnetworkstatuschanged{
} networkawarenessmanager_onnetworkstatuschanged;

typedef struct _networkawarenessmanager_onnetworkstatuschangedbaseoneauthmsaluserauthentication_issignedin{
} networkawarenessmanager_onnetworkstatuschangedbaseoneauthmsaluserauthentication_issignedin;

typedef struct _networkchangedetector_oncomplete{
} networkchangedetector_oncomplete;

typedef struct _networkchangedetector_onerror{
} networkchangedetector_onerror;

typedef struct _networkchangedetector_startaddressprobes{
} networkchangedetector_startaddressprobes;

typedef struct _networkchangedetector_stopaddressprobes{
} networkchangedetector_stopaddressprobes;

typedef struct _networklistener_connectivitychanged{
} networklistener_connectivitychanged;

typedef struct _networkpal_initialize{
} networkpal_initialize;

typedef struct _networkpal_uninitialize{
} networkpal_uninitialize;

typedef struct _networkstatuschangedeventhandler_getconnectioncosttype{
} networkstatuschangedeventhandler_getconnectioncosttype;

typedef struct _networkutils_closesocket{
} networkutils_closesocket;

typedef struct _networkutils_getaddress{
} networkutils_getaddress;

typedef struct _networkutils_initialize{
} networkutils_initialize;

typedef struct _networkutils_newsocket{
} networkutils_newsocket;

typedef struct _networkutils_uninitialize{
} networkutils_uninitialize;

typedef struct _notificationlatencyscenario_report{
} notificationlatencyscenario_report;

typedef struct _notificationlatencyscenario_setresult{
} notificationlatencyscenario_setresult;

typedef struct _notificationserviceimpl_acknotification{
} notificationserviceimpl_acknotification;

typedef struct _notificationserviceimpl_disconnect{
} notificationserviceimpl_disconnect;

typedef struct _notificationserviceimpl_internalconnect{
} notificationserviceimpl_internalconnect;

typedef struct _notificationserviceimpl_onconnected{
} notificationserviceimpl_onconnected;

typedef struct _notificationserviceimpl_onreconnecting{
} notificationserviceimpl_onreconnecting;

typedef struct _notificationserviceimpl_requestchannel{
} notificationserviceimpl_requestchannel;

typedef struct _nucleusdllmain_startnucleusclient{
} nucleusdllmain_startnucleusclient;

typedef struct _nucleuseligibilitymanager_checkiseligibleandsetflagsifneeded{
} nucleuseligibilitymanager_checkiseligibleandsetflagsifneeded;

typedef struct _nucleuseligibilitymanager_reporteligibilitytelemetry{
} nucleuseligibilitymanager_reporteligibilitytelemetry;

typedef struct _nucleusoperatingenvironment_checkiflastshutdownwasclean{
} nucleusoperatingenvironment_checkiflastshutdownwasclean;

typedef struct _nucleusoperatingenvironment_run{
} nucleusoperatingenvironment_run;

typedef struct _nucleusoperatingenvironment_operator_{
} nucleusoperatingenvironment_operator_;

typedef struct _nucleusupdateringsettingsupdater_schedulenextupdate{
} nucleusupdateringsettingsupdater_schedulenextupdate;

typedef struct _nucleusupdateringsettingsupdater_validatecontent{
} nucleusupdateringsettingsupdater_validatecontent;

typedef struct _oauthconnectedid_getconnectedid{
} oauthconnectedid_getconnectedid;

typedef struct _oauthconnectedid_setsignincookies{
} oauthconnectedid_setsignincookies;

typedef struct _oauthcredstorewin_findcredential{
} oauthcredstorewin_findcredential;

typedef struct _oauthcredstorewin_loadcachedcredential{
} oauthcredstorewin_loadcachedcredential;

typedef struct _oauthcredstorewin_storecachedcredential{
} oauthcredstorewin_storecachedcredential;

typedef struct _oauthcredentialacquirer_refreshcredential{
} oauthcredentialacquirer_refreshcredential;

typedef struct _oauthcredentialacquirer_retrievecredential{
} oauthcredentialacquirer_retrievecredential;

typedef struct _oauthcredentialacquirer_storecredential{
} oauthcredentialacquirer_storecredential;

typedef struct _oauthcredentialcache_getcredential{
} oauthcredentialcache_getcredential;

typedef struct _oauthcredentialcache_setcredential{
} oauthcredentialcache_setcredential;

typedef struct _oauthprofile_setprofilevaluesfromresponse{
} oauthprofile_setprofilevaluesfromresponse;

typedef struct _oauthurlhelper_getinitialweburl{
} oauthurlhelper_getinitialweburl;

typedef struct _oauthurlhelper_getsignouturl{
} oauthurlhelper_getsignouturl;

typedef struct _oauth_clearcredentials{
} oauth_clearcredentials;

typedef struct _oauth_getsigninurl{
} oauth_getsigninurl;

typedef struct _oauth_isdogfooduser{
} oauth_isdogfooduser;

typedef struct _oauth_signin{
} oauth_signin;

typedef struct _oauth_signinwithmsawamsilently{
} oauth_signinwithmsawamsilently;

typedef struct _odignorehelper_isodignoregrouppolicyenabled{
} odignorehelper_isodignoregrouppolicyenabled;

typedef struct _odignorehelper_loadodignoreentries{
} odignorehelper_loadodignoreentries;

typedef struct _odignorehelper_readandstoreodignorefile{
} odignorehelper_readandstoreodignorefile;

typedef struct _odignorehelper_readandstoreodignoregpoentries{
} odignorehelper_readandstoreodignoregpoentries;

typedef struct _ooberequesthandler_getkfmupsellstate{
} ooberequesthandler_getkfmupsellstate;

typedef struct _ooberequesthandler_getkfmupsellstatebaseoneauthmsaluserauthentication_issignedin{
} ooberequesthandler_getkfmupsellstatebaseoneauthmsaluserauthentication_issignedin;

typedef struct _ooberequesthandler_getonedrivesigninstate{
} ooberequesthandler_getonedrivesigninstate;

typedef struct _ooberequesthandler_syncclientinvokeinternal{
} ooberequesthandler_syncclientinvokeinternal;

typedef struct _officeconfigutil_getcachetimestamp{
} officeconfigutil_getcachetimestamp;

typedef struct _officeconfigutil_useofficeconfigupdatevalues{
} officeconfigutil_useofficeconfigupdatevalues;

typedef struct _officeopccontentcomparator_iscomparatorsupported{
} officeopccontentcomparator_iscomparatorsupported;

typedef struct _officeprivacysettingsmanager_finishinit{
} officeprivacysettingsmanager_finishinit;

typedef struct _oneauthapi_operator_{
} oneauthapi_operator_;

typedef struct _oneauthauthenticator_getaccountfromaccounthint{
} oneauthauthenticator_getaccountfromaccounthint;

typedef struct _oneauthauthenticator_getauthparameters{
} oneauthauthenticator_getauthparameters;

typedef struct _oneauthauthenticator_processoneauthresponse{
} oneauthauthenticator_processoneauthresponse;

typedef struct _oneauthmsaluserauthentication_acquirecredsilently{
} oneauthmsaluserauthentication_acquirecredsilently;

typedef struct _oneauthmsaluserauthentication_authenticatetoservice{
} oneauthmsaluserauthentication_authenticatetoservice;

typedef struct _oneauthmsaluserauthentication_createauthenticationparameter{
} oneauthmsaluserauthentication_createauthenticationparameter;

typedef struct _oneauthmsaluserauthentication_handleoneautherror{
} oneauthmsaluserauthentication_handleoneautherror;

typedef struct _oneauthmsaluserauthentication_initialize{
} oneauthmsaluserauthentication_initialize;

typedef struct _oneauthmsaluserauthentication_invalidatecredential{
} oneauthmsaluserauthentication_invalidatecredential;

typedef struct _oneauthmsaluserauthentication_iscrosstenantcall{
} oneauthmsaluserauthentication_iscrosstenantcall;

typedef struct _oneauthmsaluserauthentication_oneauthacquireaccesstoken{
} oneauthmsaluserauthentication_oneauthacquireaccesstoken;

typedef struct _oneauthmsaluserauthentication_savecredentialforaccount{
} oneauthmsaluserauthentication_savecredentialforaccount;

typedef struct _oneauthmsaluserauthentication_setauthenticationauthority{
} oneauthmsaluserauthentication_setauthenticationauthority;

typedef struct _oneauthmsaluserauthentication_signin{
} oneauthmsaluserauthentication_signin;

typedef struct _oneauthmsalwrapper_initialize{
} oneauthmsalwrapper_initialize;

typedef struct _oneauthmsalwrapper_isuseruppercaseclientidforaadenabled{
} oneauthmsalwrapper_isuseruppercaseclientidforaadenabled;

typedef struct _oneauthmsalwrapper_operator_{
} oneauthmsalwrapper_operator_;

typedef struct _onermcommon_getusercid{
} onermcommon_getusercid;

typedef struct _onermdatarequest_sendonermdatarequest{
} onermdatarequest_sendonermdatarequest;

typedef struct _onermmanager_isirisrampenabled{
} onermmanager_isirisrampenabled;

typedef struct _onermmanager_onnotification{
} onermmanager_onnotification;

typedef struct _onermmanager_startperiodictimer{
} onermmanager_startperiodictimer;

typedef struct _onermmanager_trystart{
} onermmanager_trystart;

typedef struct _onermmanager_operator_{
} onermmanager_operator_;

typedef struct _onermprovider_sendonermdatarequesttelemetry{
} onermprovider_sendonermdatarequesttelemetry;

typedef struct _operationscheduler_asynccallcomplete{
} operationscheduler_asynccallcomplete;

typedef struct _operationscheduler_completeoperation{
} operationscheduler_completeoperation;

typedef struct _operationscheduler_createasyncrequest{
} operationscheduler_createasyncrequest;

typedef struct _operationscheduler_firenotification{
} operationscheduler_firenotification;

typedef struct _operationscheduler_initializethreads{
} operationscheduler_initializethreads;

typedef struct _operationscheduler_onmarshalcallback{
} operationscheduler_onmarshalcallback;

typedef struct _operationscheduler_onmarshalnotification{
} operationscheduler_onmarshalnotification;

typedef struct _operationscheduler_onmarshaloperation{
} operationscheduler_onmarshaloperation;

typedef struct _operationscheduler_registernotificationsink{
} operationscheduler_registernotificationsink;

typedef struct _operationscheduler_schedule{
} operationscheduler_schedule;

typedef struct _operationscheduler_sendasynctaskcompletetoui{
} operationscheduler_sendasynctaskcompletetoui;

typedef struct _operationscheduler_uninitialize{
} operationscheduler_uninitialize;

typedef struct _operationscheduler_uninitializethreads{
} operationscheduler_uninitializethreads;

typedef struct _operationscheduler_unregisternotificationsink{
} operationscheduler_unregisternotificationsink;

typedef struct _orderedchangesex_handlecycles{
} orderedchangesex_handlecycles;

typedef struct _orderedchangesex_insertchangeintofinallist{
} orderedchangesex_insertchangeintofinallist;

typedef struct _orderedchangesex_logdependencies{
} orderedchangesex_logdependencies;

typedef struct _orderedchangesex_logorderedchanges{
} orderedchangesex_logorderedchanges;

typedef struct _originatoridex_originatoridex{
} originatoridex_originatoridex;

typedef struct _originatoridex_originatoridexbaseoneauthmsaluserauthentication_issignedin{
} originatoridex_originatoridexbaseoneauthmsaluserauthentication_issignedin;

typedef struct _originatoridprovider_loadoriginatoridexfromconfig{
} originatoridprovider_loadoriginatoridexfromconfig;

typedef struct _originatoridprovider_logger{
} originatoridprovider_logger;

typedef struct _originatoridprovider_updateislocalchangeflagonmeshdataentries{
} originatoridprovider_updateislocalchangeflagonmeshdataentries;

typedef struct _pausemanager_startresume{
} pausemanager_startresume;

typedef struct _pendinguploadslist_sendstarvationtelemetryifnecessary{
} pendinguploadslist_sendstarvationtelemetryifnecessary;

typedef struct _perfauditor_stopcollect{
} perfauditor_stopcollect;

typedef struct _performfsidlookupfordeletionsdciworkitem_process{
} performfsidlookupfordeletionsdciworkitem_process;

typedef struct _periodicretrylist_addtoperiodicretrylist{
} periodicretrylist_addtoperiodicretrylist;

typedef struct _periodicretrylist_addtoperiodicretrylistbaseoneauthmsaluserauthentication_issignedin{
} periodicretrylist_addtoperiodicretrylistbaseoneauthmsaluserauthentication_issignedin;

typedef struct _periodicretrylist_checkiffileisunlocked{
} periodicretrylist_checkiffileisunlocked;

typedef struct _periodicretrylist_handleperiodicretrychanges{
} periodicretrylist_handleperiodicretrychanges;

typedef struct _persistdeletesinchangestosendtodbdciworkitem_process{
} persistdeletesinchangestosendtodbdciworkitem_process;

typedef struct _persistsynctoken_process{
} persistsynctoken_process;

typedef struct _persistenttimer_stop{
} persistenttimer_stop;

typedef struct _pinstatehelpers_changefiletriggerhydrationordehydration{
} pinstatehelpers_changefiletriggerhydrationordehydration;

typedef struct _pinstatehelpers_gethydrationanddehydrationactions{
} pinstatehelpers_gethydrationanddehydrationactions;

typedef struct _pinstatehelpers_triggerhydrationordehydration{
} pinstatehelpers_triggerhydrationordehydration;

typedef struct _pinstatehelpers_triggerhydrationordehydrationbaseoneauthmsaluserauthentication_issignedin{
} pinstatehelpers_triggerhydrationordehydrationbaseoneauthmsaluserauthentication_issignedin;

typedef struct _placeholderhelpers_updateinsyncstateandidentity{
} placeholderhelpers_updateinsyncstateandidentity;

typedef struct _placeholdermanager_changeplaceholdersenabled{
} placeholdermanager_changeplaceholdersenabled;

typedef struct _placeholdersmessagesource_getplaceholderstatus{
} placeholdersmessagesource_getplaceholderstatus;

typedef struct _postponedchanges_postponedchangessettings{
} postponedchanges_postponedchangessettings;

typedef struct _processenvironmentmanager_onrampsupdated{
} processenvironmentmanager_onrampsupdated;

typedef struct _processlocaldrivechangesdciworkitem_process{
} processlocaldrivechangesdciworkitem_process;

typedef struct _protocolhandlermanager_fireprotocolhandlertelemetry{
} protocolhandlermanager_fireprotocolhandlertelemetry;

typedef struct _proxyordirectsocket_detachsocket{
} proxyordirectsocket_detachsocket;

typedef struct _proxyordirectsocket_internalconnect{
} proxyordirectsocket_internalconnect;

typedef struct _publicresourceid_fromresourceid{
} publicresourceid_fromresourceid;

typedef struct _publicresourceid_toresourceid{
} publicresourceid_toresourceid;

typedef struct _qtlocalization_initialize{
} qtlocalization_initialize;

typedef struct _qtstartup_configurerenderer{
} qtstartup_configurerenderer;

typedef struct _qtstartup_configurescalefactor{
} qtstartup_configurescalefactor;

typedef struct _qtstartup_start{
} qtstartup_start;

typedef struct _ratelimiter_ratelimiter{
} ratelimiter_ratelimiter;

typedef struct _ratelimiter_refreshcountersifnecessary{
} ratelimiter_refreshcountersifnecessary;

typedef struct _readdirectorychanges_readchanges{
} readdirectorychanges_readchanges;

typedef struct _realizerchangeinterpreter_createchangefilerealizerworkitem{
} realizerchangeinterpreter_createchangefilerealizerworkitem;

typedef struct _realizerchangeinterpreter_createdeletefilerealizerworkitem{
} realizerchangeinterpreter_createdeletefilerealizerworkitem;

typedef struct _realizerchangeinterpreter_createdeletefolderrealizerworkitem{
} realizerchangeinterpreter_createdeletefolderrealizerworkitem;

typedef struct _realizerchangeinterpreter_createmovefilerealizerworkitem{
} realizerchangeinterpreter_createmovefilerealizerworkitem;

typedef struct _realizerchangeinterpreter_createmovefolderrealizerworkitem{
} realizerchangeinterpreter_createmovefolderrealizerworkitem;

typedef struct _realizerchangeinterpreter_createnewfilerealizerworkitem{
} realizerchangeinterpreter_createnewfilerealizerworkitem;

typedef struct _realizerchangeinterpreter_createnewfilerealizerworkitembaseoneauthmsaluserauthentication_issignedin{
} realizerchangeinterpreter_createnewfilerealizerworkitembaseoneauthmsaluserauthentication_issignedin;

typedef struct _realizerchangeinterpreter_createnewfolderrealizerworkitem{
} realizerchangeinterpreter_createnewfolderrealizerworkitem;

typedef struct _realizerchangeinterpreter_createpersistsynctokenrealizerworkitem{
} realizerchangeinterpreter_createpersistsynctokenrealizerworkitem;

typedef struct _realizerchangeinterpreter_filteroutprocessedentry{
} realizerchangeinterpreter_filteroutprocessedentry;

typedef struct _realizerchangeinterpreter_processdownloadedentries{
} realizerchangeinterpreter_processdownloadedentries;

typedef struct _realizerchangeinterpreter_processdownloadedfileentry{
} realizerchangeinterpreter_processdownloadedfileentry;

typedef struct _realizerchangeinterpreter_processdownloadedfolderentry{
} realizerchangeinterpreter_processdownloadedfolderentry;

typedef struct _realizerchangeinterpreter_processnewsynctoken{
} realizerchangeinterpreter_processnewsynctoken;

typedef struct _realizerchangeinterpreter_operator_{
} realizerchangeinterpreter_operator_;

typedef struct _realizerchangeinterpreter_operator_baseoneauthmsaluserauthentication_issignedin{
} realizerchangeinterpreter_operator_baseoneauthmsaluserauthentication_issignedin;

typedef struct _realizer_addprioritychange{
} realizer_addprioritychange;

typedef struct _realizer_processchanges{
} realizer_processchanges;

typedef struct _reindexsynciconsmanager_isperiodicreindexenabled{
} reindexsynciconsmanager_isperiodicreindexenabled;

typedef struct _reindexsynciconsmanager_isreindexsynciconsenabled{
} reindexsynciconsmanager_isreindexsynciconsenabled;

typedef struct _reindexsynciconsmanager_shouldruncommandlinereindex{
} reindexsynciconsmanager_shouldruncommandlinereindex;

typedef struct _removefile_loginfo{
} removefile_loginfo;

typedef struct _removefile_process{
} removefile_process;

typedef struct _reportmanager_fetchtakfromsyncadminreportsgrouppolicy{
} reportmanager_fetchtakfromsyncadminreportsgrouppolicy;

typedef struct _reportmanager_isfeatureenabled{
} reportmanager_isfeatureenabled;

typedef struct _resetcommandline_saveresetenabledstate{
} resetcommandline_saveresetenabledstate;

typedef struct _resourcelibrary_initialize{
    int32 unk;
} resourcelibrary_initialize;

typedef struct _resourcelibrary_initializeimpl{
} resourcelibrary_initializeimpl;

typedef struct _router_registerroute{
} router_registerroute;

typedef struct _rpcclientutil_createservicebinding{
} rpcclientutil_createservicebinding;

typedef struct _rpcclientutil_dorpccall{
} rpcclientutil_dorpccall;

typedef struct _rpcclientutil_getserviceconfig{
} rpcclientutil_getserviceconfig;

typedef struct _rpcclientutil_isserviceinstalled{
} rpcclientutil_isserviceinstalled;

typedef struct _rpcserverutil_getcallerprocessid{
} rpcserverutil_getcallerprocessid;

typedef struct _rpcserverutil_registerrpcserver{
} rpcserverutil_registerrpcserver;

typedef struct _rpcserverutil_setservicestatus{
} rpcserverutil_setservicestatus;

typedef struct _runningobjecttablehelper_addobject{
} runningobjecttablehelper_addobject;

typedef struct _runningobjecttablehelper_removeobject{
} runningobjecttablehelper_removeobject;

typedef struct _runtime_getproxyname{
} runtime_getproxyname;

typedef struct _runtime_isretriableerror{
} runtime_isretriableerror;

typedef struct _runtime_isretriableerrorbaseoneauthmsaluserauthentication_issignedin{
} runtime_isretriableerrorbaseoneauthmsaluserauthentication_issignedin;

typedef struct _spoapi_spodiscover{
} spoapi_spodiscover;

typedef struct _spoapi_spodiscoverandverifytenant{
} spoapi_spodiscoverandverifytenant;

typedef struct _spoapi_spogetcookieforresource{
} spoapi_spogetcookieforresource;

typedef struct _spodiscoverygraph_interpretstatuscode{
} spodiscoverygraph_interpretstatuscode;

typedef struct _spodiscoverygraph_makedecisions{
} spodiscoverygraph_makedecisions;

typedef struct _spodiscoverygraph_processbody{
} spodiscoverygraph_processbody;

typedef struct _spodiscoverygraph_processresponse{
} spodiscoverygraph_processresponse;

typedef struct _spodiscoveryoperation_execute{
} spodiscoveryoperation_execute;

typedef struct _spoiddiscovery_cacheexpired{
} spoiddiscovery_cacheexpired;

typedef struct _spoiddiscovery_discover{
} spoiddiscovery_discover;

typedef struct _spoiddiscovery_discoverfromserver{
} spoiddiscovery_discoverfromserver;

typedef struct _spoofficediscovery_discover{
} spoofficediscovery_discover;

typedef struct _spoofficediscovery_discoverfromserver{
} spoofficediscovery_discoverfromserver;

typedef struct _spoofficediscovery_parseodbnode{
} spoofficediscovery_parseodbnode;

typedef struct _spoofficediscovery_setspovaluesfromresponse{
} spoofficediscovery_setspovaluesfromresponse;

typedef struct _spoofficediscoveryv2_discover{
} spoofficediscoveryv2_discover;

typedef struct _spoofficediscoveryv2_discoverfromcache{
} spoofficediscoveryv2_discoverfromcache;

typedef struct _spoofficediscoveryv2_operator_{
} spoofficediscoveryv2_operator_;

typedef struct _spoticket_getticketvalue{
} spoticket_getticketvalue;

typedef struct _spouser_forcesignin{
} spouser_forcesignin;

typedef struct _spouser_getoauthticket{
} spouser_getoauthticket;

typedef struct _spouser_getodspticket{
} spouser_getodspticket;

typedef struct _sqliteexception_sqliteexception{
} sqliteexception_sqliteexception;

typedef struct _scannertelemetry_logperftelemetry{
} scannertelemetry_logperftelemetry;

typedef struct _scannertelemetry_logperftelemetrybaseoneauthmsaluserauthentication_issignedin{
} scannertelemetry_logperftelemetrybaseoneauthmsaluserauthentication_issignedin;

typedef struct _scannertelemetry_logtelemetry{
} scannertelemetry_logtelemetry;

typedef struct _scannertelemetry_recordsample{
} scannertelemetry_recordsample;

typedef struct _scannertelemetry_reporttelemetryfordroppedexcludeditemspertype{
} scannertelemetry_reporttelemetryfordroppedexcludeditemspertype;

typedef struct _scenarioqossyncperfwrapper_recordqostelemetry{
} scenarioqossyncperfwrapper_recordqostelemetry;

typedef struct _scenarioqossyncwrapper_recordqostelemetry{
} scenarioqossyncwrapper_recordqostelemetry;

typedef struct _scenarioqoswrapper_recordqostelemetry{
} scenarioqoswrapper_recordqostelemetry;

typedef struct _scenariotracking_lognewtracecreated{
} scenariotracking_lognewtracecreated;

typedef struct _scenariotracking_logupdatedscenariotrace{
} scenariotracking_logupdatedscenariotrace;

typedef struct _scenariotracking_reportunrecordedscenario{
} scenariotracking_reportunrecordedscenario;

typedef struct _scenariotracking__scenariobase{
} scenariotracking__scenariobase;

typedef struct _scopeinfo_deletesubscriptions{
} scopeinfo_deletesubscriptions;

typedef struct _scopeinfo_getquotastatepollinterval{
} scopeinfo_getquotastatepollinterval;

typedef struct _scopeinfo_settransitiontolockedcompleted{
} scopeinfo_settransitiontolockedcompleted;

typedef struct _scopeinfo_settransitioningtolocked{
} scopeinfo_settransitioningtolocked;

typedef struct _scopeinfo_writesettingstoregistry{
} scopeinfo_writesettingstoregistry;

typedef struct _scopeinitializer_startsyncscopeinitialization{
} scopeinitializer_startsyncscopeinitialization;

typedef struct _securityintegration_createcbpbroker{
} securityintegration_createcbpbroker;

typedef struct _securityintegration_isregistrationinfodifferent{
} securityintegration_isregistrationinfodifferent;

typedef struct _securityintegration_logregistrationwithfailuretelemetry{
} securityintegration_logregistrationwithfailuretelemetry;

typedef struct _securityintegration_onpremiumstatechanged{
} securityintegration_onpremiumstatechanged;

typedef struct _securityintegration_onwscstatechanged{
} securityintegration_onwscstatechanged;

typedef struct _securityintegration_registerwithdefender{
} securityintegration_registerwithdefender;

typedef struct _serverrefreshstate_setrefreshneeded{
} serverrefreshstate_setrefreshneeded;

typedef struct _servicecapabilities_specifydefaultcapabilities{
} servicecapabilities_specifydefaultcapabilities;

typedef struct _servicediscoverymanager_handlelistusercheckexception{
} servicediscoverymanager_handlelistusercheckexception;

typedef struct _servicediscoverymanager_handleusercheckexception{
} servicediscoverymanager_handleusercheckexception;

typedef struct _servicediscoverymanager_handleusercheckexceptionbaseoneauthmsaluserauthentication_issignedin{
} servicediscoverymanager_handleusercheckexceptionbaseoneauthmsaluserauthentication_issignedin;

typedef struct _servicediscoverymanager_recordscenario{
} servicediscoverymanager_recordscenario;

typedef struct _sessionmanager_beginsession{
} sessionmanager_beginsession;

typedef struct _setdatetakenonfilesystemjob_execute{
} setdatetakenonfilesystemjob_execute;

typedef struct _setexcludedfile_loginfo{
} setexcludedfile_loginfo;

typedef struct _setexcludedfile_process{
} setexcludedfile_process;

typedef struct _settingsfilemanager_loadassertsettings{
} settingsfilemanager_loadassertsettings;

typedef struct _settingsfilemanager_loaddeviceandoriginatorids{
} settingsfilemanager_loaddeviceandoriginatorids;

typedef struct _settingsfilemanager_loadglobalsettings{
} settingsfilemanager_loadglobalsettings;

typedef struct _settingsfilemanager_loaduserconfigfile{
} settingsfilemanager_loaduserconfigfile;

typedef struct _settingsfilemanager_logtheusersettingsloadedfromuserconfigfile{
} settingsfilemanager_logtheusersettingsloadedfromuserconfigfile;

typedef struct _settingsfilemanager_savedrivesettingsconsumer{
} settingsfilemanager_savedrivesettingsconsumer;

typedef struct _settingsfilemanager_savedrivesettingsforsharepointdatamodel{
} settingsfilemanager_savedrivesettingsforsharepointdatamodel;

typedef struct _settingsfilemanager_savegeneralsettings{
} settingsfilemanager_savegeneralsettings;

typedef struct _settingsfilemanager_savesettings{
} settingsfilemanager_savesettings;

typedef struct _settingsfilemanager_savesubscriptions{
} settingsfilemanager_savesubscriptions;

typedef struct _settingsfilemanager_writeglobalclientsettingtofile{
} settingsfilemanager_writeglobalclientsettingtofile;

typedef struct _settingspersistence_clearintegersettingstable{
} settingspersistence_clearintegersettingstable;

typedef struct _settingspersistence_clearstringsettingstable{
} settingspersistence_clearstringsettingstable;

typedef struct _settings_setsignedinusercidstring{
} settings_setsignedinusercidstring;

typedef struct _setuputilities_enabledplforwcos{
} setuputilities_enabledplforwcos;

typedef struct _setuputilities_onedriveusersetup{
} setuputilities_onedriveusersetup;

typedef struct _setuputilities_operator_{
} setuputilities_operator_;

typedef struct _setuputils_getonedriveupdatexmldownloadattemptregistry{
} setuputils_getonedriveupdatexmldownloadattemptregistry;

typedef struct _shellmanager_updateallpendingitems{
} shellmanager_updateallpendingitems;

typedef struct _shellmanager_updateallpendingitemsbaseoneauthmsaluserauthentication_issignedin{
} shellmanager_updateallpendingitemsbaseoneauthmsaluserauthentication_issignedin;

typedef struct _shellsyncstateverifier_drivefilecountexceedslimit{
} shellsyncstateverifier_drivefilecountexceedslimit;

typedef struct _shellsyncstateverifier_reportsummary{
} shellsyncstateverifier_reportsummary;

typedef struct _shellsyncstateverifier_sendtelemetry{
} shellsyncstateverifier_sendtelemetry;

typedef struct _shellsyncstateverifier_sendtelemetrybaseoneauthmsaluserauthentication_issignedin{
} shellsyncstateverifier_sendtelemetrybaseoneauthmsaluserauthentication_issignedin;

typedef struct _shellsyncstateverifier_shouldrun{
} shellsyncstateverifier_shouldrun;

typedef struct _shellsyncstateverifier_verifyshellsyncstateforfolder{
} shellsyncstateverifier_verifyshellsyncstateforfolder;

typedef struct _signinbrowsernavigator_onbeforenavigate{
} signinbrowsernavigator_onbeforenavigate;

typedef struct _silentmovecontroller_handlemigrationnotification{
} silentmovecontroller_handlemigrationnotification;

typedef struct _silentmovecontroller_handlescancomplete{
} silentmovecontroller_handlescancomplete;

typedef struct _silentmovecontroller_releaselockandnotify{
} silentmovecontroller_releaselockandnotify;

typedef struct _silentmovecontroller_startsilentexecution{
} silentmovecontroller_startsilentexecution;

typedef struct _simplebuffer_onerror{
} simplebuffer_onerror;

typedef struct _simplebuffer_prepareforposting{
} simplebuffer_prepareforposting;

typedef struct _sizedwritestreams_writetoplaceholder{
} sizedwritestreams_writetoplaceholder;

typedef struct _skydriveclient_getcommandstring{
} skydriveclient_getcommandstring;

typedef struct _skydriveclient_getcommandstringbaseoneauthmsaluserauthentication_issignedin{
} skydriveclient_getcommandstringbaseoneauthmsaluserauthentication_issignedin;

typedef struct _skydriveclient_getdetaileditemstatusex{
} skydriveclient_getdetaileditemstatusex;

typedef struct _skydriveclient_getdetaileditemstatusexbaseoneauthmsaluserauthentication_issignedin{
} skydriveclient_getdetaileditemstatusexbaseoneauthmsaluserauthentication_issignedin;

typedef struct _skydriveclient_getfilesyncclientcapabilities{
} skydriveclient_getfilesyncclientcapabilities;

typedef struct _skydriveurlhelper_generateskydriveurl{
} skydriveurlhelper_generateskydriveurl;

typedef struct _standaloneupdatercontroller_applyupdate{
} standaloneupdatercontroller_applyupdate;

typedef struct _standaloneupdatercontroller_downloadupdate{
} standaloneupdatercontroller_downloadupdate;

typedef struct _standaloneupdatercontroller_getupdatedescriptions{
} standaloneupdatercontroller_getupdatedescriptions;

typedef struct _standaloneupdatercontroller_ismachinethrottled{
} standaloneupdatercontroller_ismachinethrottled;

typedef struct _standaloneupdatercontroller_launchonedrivesetup{
} standaloneupdatercontroller_launchonedrivesetup;

typedef struct _standaloneupdatercontroller_selectappropriateupdate{
} standaloneupdatercontroller_selectappropriateupdate;

typedef struct _standaloneupdatercontroller_shouldapplyupdate{
} standaloneupdatercontroller_shouldapplyupdate;

typedef struct _standaloneupdatercontroller_trygetonedriveagupdatexmlurl{
} standaloneupdatercontroller_trygetonedriveagupdatexmlurl;

typedef struct _standaloneupdaterinstallationrepair_getdefaultsetupcomponents{
} standaloneupdaterinstallationrepair_getdefaultsetupcomponents;

typedef struct _standaloneupdaterinstallationrepair_isofficeintegrationkeyinvalidstate{
} standaloneupdaterinstallationrepair_isofficeintegrationkeyinvalidstate;

typedef struct _standaloneupdaterinstallationrepair_isofficeintegrationkeyinvalidstatebaseoneauthmsaluserauthentication_issignedin{
} standaloneupdaterinstallationrepair_isofficeintegrationkeyinvalidstatebaseoneauthmsaluserauthentication_issignedin;

typedef struct _standaloneupdaterinstrumentation_setcommondatapoints{
} standaloneupdaterinstrumentation_setcommondatapoints;

typedef struct _standaloneupdaterinstrumentation_operator_{
} standaloneupdaterinstrumentation_operator_;

typedef struct _standaloneupdatershellabstraction_launchprocess{
} standaloneupdatershellabstraction_launchprocess;

typedef struct _standaloneupdater_downloadandapplyupdateringsettings{
} standaloneupdater_downloadandapplyupdateringsettings;

typedef struct _standaloneupdater_downloadsetupandperformupdate{
} standaloneupdater_downloadsetupandperformupdate;

typedef struct _standaloneupdater_getsettingsdir{
} standaloneupdater_getsettingsdir;

typedef struct _standaloneupdater_grabupdatemutex{
} standaloneupdater_grabupdatemutex;

typedef struct _standaloneupdater_initializewithdefaultimplementations{
} standaloneupdater_initializewithdefaultimplementations;

typedef struct _standaloneupdater_launchnucleussilentconfig{
} standaloneupdater_launchnucleussilentconfig;

typedef struct _standaloneupdater_performupdate{
} standaloneupdater_performupdate;

typedef struct _standaloneupdater_run{
} standaloneupdater_run;

typedef struct _standaloneupdater_runbaseoneauthmsaluserauthentication_issignedin{
} standaloneupdater_runbaseoneauthmsaluserauthentication_issignedin;

typedef struct _standaloneupdater_runupdatermode{
} standaloneupdater_runupdatermode;

typedef struct _standaloneupdater_sendwofcompressionsuitabletelemetry{
} standaloneupdater_sendwofcompressionsuitabletelemetry;

typedef struct _standaloneupdater_sendwofcompressionsuitabletelemetrybaseoneauthmsaluserauthentication_issignedin{
} standaloneupdater_sendwofcompressionsuitabletelemetrybaseoneauthmsaluserauthentication_issignedin;

typedef struct _standaloneupdater_operator_{
} standaloneupdater_operator_;

typedef struct _statemachine_transition{
} statemachine_transition;

typedef struct _storageproviderfinderimplrot_getstorageprovider{
} storageproviderfinderimplrot_getstorageprovider;

typedef struct _storageproviderfinderimplrot_getstorageproviderbaseoneauthmsaluserauthentication_issignedin{
} storageproviderfinderimplrot_getstorageproviderbaseoneauthmsaluserauthentication_issignedin;

typedef struct _storageproviderfinder_getaccountinstancebypath{
} storageproviderfinder_getaccountinstancebypath;

typedef struct _storageproviderfinder_retrievepropertyhandlerbycheckingallaccounts{
} storageproviderfinder_retrievepropertyhandlerbycheckingallaccounts;

typedef struct _storageproviderfinder_retrievepropertyhandlerbyqueryingaccount{
} storageproviderfinder_retrievepropertyhandlerbyqueryingaccount;

typedef struct _storageproviderhandler_endlogin{
} storageproviderhandler_endlogin;

typedef struct _storageproviderhandler_getpropertyhandlerfrompath{
} storageproviderhandler_getpropertyhandlerfrompath;

typedef struct _storageproviderhandler_getpropertyhandlerfromuri{
} storageproviderhandler_getpropertyhandlerfromuri;

typedef struct _storageproviderhandler_initializewithsyncengineocsi{
} storageproviderhandler_initializewithsyncengineocsi;

typedef struct _storageproviderhandler_recordstorageproviderhandlerapitelemetry{
} storageproviderhandler_recordstorageproviderhandlerapitelemetry;

typedef struct _storageproviderhandler_recordstorageproviderhandlerapitelemetrybaseoneauthmsaluserauthentication_issignedin{
} storageproviderhandler_recordstorageproviderhandlerapitelemetrybaseoneauthmsaluserauthentication_issignedin;

typedef struct _storageproviderhandler_signinsyncengine{
} storageproviderhandler_signinsyncengine;

typedef struct _storageproviderhandler_waitonevent{
} storageproviderhandler_waitonevent;

typedef struct _storageproviderpropertyhandler_endgetitempropertiesex{
} storageproviderpropertyhandler_endgetitempropertiesex;

typedef struct _storageproviderpropertyhandler_initializewithpath{
} storageproviderpropertyhandler_initializewithpath;

typedef struct _storageproviderpropertyhandler_initializewithuri{
} storageproviderpropertyhandler_initializewithuri;

typedef struct _storageproviderpropertyhandler_retrieveproperties{
} storageproviderpropertyhandler_retrieveproperties;

typedef struct _storageproviderpropertyhandler_waitonevent{
} storageproviderpropertyhandler_waitonevent;

typedef struct _storageproviderstatusuisourcecomponent_initializecomponent{
} storageproviderstatusuisourcecomponent_initializecomponent;

typedef struct _storageproviderstatusuisourcecomponent_postinitialize{
} storageproviderstatusuisourcecomponent_postinitialize;

typedef struct _storageproviderstatusuisource_onvisualstatechanged{
} storageproviderstatusuisource_onvisualstatechanged;

typedef struct _storageproviderstatusuisource_operator_{
} storageproviderstatusuisource_operator_;

typedef struct _storageproviderurisource_getcontentinfoforpath{
} storageproviderurisource_getcontentinfoforpath;

typedef struct _storageproviderurisource_getcontentinfoforpathinternal{
} storageproviderurisource_getcontentinfoforpathinternal;

typedef struct _storageproviderurisource_getpathforcontenturi{
} storageproviderurisource_getpathforcontenturi;

typedef struct _storageproviderurisource_getpathforcontenturibaseoneauthmsaluserauthentication_issignedin{
} storageproviderurisource_getpathforcontenturibaseoneauthmsaluserauthentication_issignedin;

typedef struct _storageproviderurisource_getpathforcontenturiinternal{
} storageproviderurisource_getpathforcontenturiinternal;

typedef struct _storageproviderurisource_storageproviderurisource{
} storageproviderurisource_storageproviderurisource;

typedef struct _storageserializer_deserializegetcanonicalfolderpath{
} storageserializer_deserializegetcanonicalfolderpath;

typedef struct _storageserviceapi_addfeaturessupportedheader{
} storageserviceapi_addfeaturessupportedheader;

typedef struct _storageserviceapi_backoff{
} storageserviceapi_backoff;

typedef struct _storageserviceapi_cancelallrequests{
} storageserviceapi_cancelallrequests;

typedef struct _storageserviceapi_canceldownloadblock{
} storageserviceapi_canceldownloadblock;

typedef struct _storageserviceapi_enumchanges{
} storageserviceapi_enumchanges;

typedef struct _storageserviceapi_enumchangesbaseoneauthmsaluserauthentication_issignedin{
} storageserviceapi_enumchangesbaseoneauthmsaluserauthentication_issignedin;

typedef struct _storageserviceapi_enumselectivesyncentries{
} storageserviceapi_enumselectivesyncentries;

typedef struct _storageserviceapi_getcanonicalfolderpath{
} storageserviceapi_getcanonicalfolderpath;

typedef struct _storageserviceapi_getquotastatus{
} storageserviceapi_getquotastatus;

typedef struct _storageserviceapi_handleticketfailure{
} storageserviceapi_handleticketfailure;

typedef struct _storageserviceapi_logresponse{
} storageserviceapi_logresponse;

typedef struct _storageserviceapi_sendrequest{
} storageserviceapi_sendrequest;

typedef struct _storageserviceapi_sendrequestbaseoneauthmsaluserauthentication_issignedin{
} storageserviceapi_sendrequestbaseoneauthmsaluserauthentication_issignedin;

typedef struct _storageserviceapi_storageserviceapi{
} storageserviceapi_storageserviceapi;

typedef struct _streamsocket_beginconnect{
} streamsocket_beginconnect;

typedef struct _streamsocket_beginreceive{
} streamsocket_beginreceive;

typedef struct _streamsocket_beginsend{
} streamsocket_beginsend;

typedef struct _streamsocket_bindtosink{
} streamsocket_bindtosink;

typedef struct _streamsocket_close{
} streamsocket_close;

typedef struct _streamsocket_internalclose{
} streamsocket_internalclose;

typedef struct _streamsocket_onclosecomplete{
} streamsocket_onclosecomplete;

typedef struct _streamsocket_run{
} streamsocket_run;

typedef struct _streamsocket_streamsocket{
} streamsocket_streamsocket;

typedef struct _surveymanager_deserializestate{
} surveymanager_deserializestate;

typedef struct _surveymanager_getstatefilepath{
} surveymanager_getstatefilepath;

typedef struct _surveymanager_initializecomponent{
} surveymanager_initializecomponent;

typedef struct _surveymanager_loadstatefromdisk{
} surveymanager_loadstatefromdisk;

typedef struct _surveymanager_loadstatefromdiskbaseoneauthmsaluserauthentication_issignedin{
} surveymanager_loadstatefromdiskbaseoneauthmsaluserauthentication_issignedin;

typedef struct _surveymanager_postinitialize{
} surveymanager_postinitialize;

typedef struct _surveymanager_processcampaigns{
} surveymanager_processcampaigns;

typedef struct _surveymanager_reportdeserializestateresult{
} surveymanager_reportdeserializestateresult;

typedef struct _surveymanager_serializestate{
} surveymanager_serializestate;

typedef struct _surveymanager_serializestatebaseoneauthmsaluserauthentication_issignedin{
} surveymanager_serializestatebaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncactivitytracker_reportsyncactivity{
} syncactivitytracker_reportsyncactivity;

typedef struct _syncactivitytracker_setsyncactivitytype{
} syncactivitytracker_setsyncactivitytype;

typedef struct _syncactivitytracker_stopsubsequentsync{
} syncactivitytracker_stopsubsequentsync;

typedef struct _synccomplete_process{
} synccomplete_process;

typedef struct _syncengineclient_begingetitempropertiesex{
} syncengineclient_begingetitempropertiesex;

typedef struct _syncengineclient_begingetlibraries{
} syncengineclient_begingetlibraries;

typedef struct _syncengineclient_begingetselectivesyncinformation{
} syncengineclient_begingetselectivesyncinformation;

typedef struct _syncengineclient_beginlogin{
} syncengineclient_beginlogin;

typedef struct _syncengineclient_beginmaplibrary{
} syncengineclient_beginmaplibrary;

typedef struct _syncengineclient_beginvolumechangenotification{
} syncengineclient_beginvolumechangenotification;

typedef struct _syncengineclient_cleanuplogin{
} syncengineclient_cleanuplogin;

typedef struct _syncengineclient_completegetselectivesyncinformation{
} syncengineclient_completegetselectivesyncinformation;

typedef struct _syncengineclient_deletesettingsforcacheduser{
} syncengineclient_deletesettingsforcacheduser;

typedef struct _syncengineclient_finalrelease{
} syncengineclient_finalrelease;

typedef struct _syncengineclient_getcoauthsettingstatus{
} syncengineclient_getcoauthsettingstatus;

typedef struct _syncengineclient_getpartnerintegrationstatus{
} syncengineclient_getpartnerintegrationstatus;

typedef struct _syncengineclient_getplaceholdersstatus{
} syncengineclient_getplaceholdersstatus;

typedef struct _syncengineclient_onconnectmountedfolder{
} syncengineclient_onconnectmountedfolder;

typedef struct _syncengineclient_ongetaccountinformation{
} syncengineclient_ongetaccountinformation;

typedef struct _syncengineclient_ongetlibraries{
} syncengineclient_ongetlibraries;

typedef struct _syncengineclient_ongetmountedfolders{
} syncengineclient_ongetmountedfolders;

typedef struct _syncengineclient_onmaplibrary{
} syncengineclient_onmaplibrary;

typedef struct _syncengineclient_onsignin{
} syncengineclient_onsignin;

typedef struct _syncengineclient_startsignin{
} syncengineclient_startsignin;

typedef struct _syncengineclient_startsyncengineruntime{
} syncengineclient_startsyncengineruntime;

typedef struct _syncengineclient_stopsyncengineruntime{
} syncengineclient_stopsyncengineruntime;

typedef struct _syncengineeventhandler_libraryerror{
} syncengineeventhandler_libraryerror;

typedef struct _syncengineeventhandler_loginstatechanged{
} syncengineeventhandler_loginstatechanged;

typedef struct _syncengineeventhandler_syncengineerror{
} syncengineeventhandler_syncengineerror;

typedef struct _syncengineeventhandler_uidisplayrequested{
} syncengineeventhandler_uidisplayrequested;

typedef struct _syncenginefileinfoprovider_getaccountinfoforpartner{
} syncenginefileinfoprovider_getaccountinfoforpartner;

typedef struct _syncenginefileinfoprovider_getaccountinfoforpartnerbaseoneauthmsaluserauthentication_issignedin{
} syncenginefileinfoprovider_getaccountinfoforpartnerbaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncenginefileinfoprovider_getpropertyhandlerfrompath{
} syncenginefileinfoprovider_getpropertyhandlerfrompath;

typedef struct _syncenginefileinfoprovider_getpropertyhandlerfromuri{
} syncenginefileinfoprovider_getpropertyhandlerfromuri;

typedef struct _syncengineruntimemanager_dispatchruntimethreads{
} syncengineruntimemanager_dispatchruntimethreads;

typedef struct _syncenginesubscriptionstoragesubscription_cancelrequest{
} syncenginesubscriptionstoragesubscription_cancelrequest;

typedef struct _syncenginesubscriptionstoragesubscription_createsubscription{
} syncenginesubscriptionstoragesubscription_createsubscription;

typedef struct _syncenginesubscriptionstoragesubscription_createvroomactivitysubscription{
} syncenginesubscriptionstoragesubscription_createvroomactivitysubscription;

typedef struct _syncenginesubscriptionstoragesubscription_deletesubscription{
} syncenginesubscriptionstoragesubscription_deletesubscription;

typedef struct _syncenginesubscriptionstoragesubscription_handlefailureifneeded{
} syncenginesubscriptionstoragesubscription_handlefailureifneeded;

typedef struct _syncenginesubscriptionstoragesubscription_handlefailureifneededbaseoneauthmsaluserauthentication_issignedin{
} syncenginesubscriptionstoragesubscription_handlefailureifneededbaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncenginesubscriptionstoragesubscription_logandrecordqos{
} syncenginesubscriptionstoragesubscription_logandrecordqos;

typedef struct _syncenginesubscriptionstoragesubscription_onhandlecreate{
} syncenginesubscriptionstoragesubscription_onhandlecreate;

typedef struct _syncenginesubscriptionstoragesubscription_onrequestcomplete{
} syncenginesubscriptionstoragesubscription_onrequestcomplete;

typedef struct _syncenginesubscriptionstoragesubscription_sendrequest{
} syncenginesubscriptionstoragesubscription_sendrequest;

typedef struct _syncenginesubscriptionstore_delete{
} syncenginesubscriptionstore_delete;

typedef struct _syncenginesubscriptionwnschannelcallbackproxy_close{
} syncenginesubscriptionwnschannelcallbackproxy_close;

typedef struct _syncenginesubscriptionwnschannelcallbackproxy_corelooponnetworkchange{
} syncenginesubscriptionwnschannelcallbackproxy_corelooponnetworkchange;

typedef struct _syncenginesubscriptionwnschannelcallbackproxy_corelooponnetworkchangebaseoneauthmsaluserauthentication_issignedin{
} syncenginesubscriptionwnschannelcallbackproxy_corelooponnetworkchangebaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncenginesubscriptionwnschannelcallbackproxy_corelooponnotificationreceived{
} syncenginesubscriptionwnschannelcallbackproxy_corelooponnotificationreceived;

typedef struct _syncenginesubscriptionwnschannelcallbackproxy_lognotification{
} syncenginesubscriptionwnschannelcallbackproxy_lognotification;

typedef struct _syncenginesubscriptionwnschannelcallbackproxy_onbackonline{
} syncenginesubscriptionwnschannelcallbackproxy_onbackonline;

typedef struct _syncenginesubscriptionwnschannelcallbackproxy_onchannelclosed{
} syncenginesubscriptionwnschannelcallbackproxy_onchannelclosed;

typedef struct _syncenginesubscriptionwnschannelcallbackproxy_onoffline{
} syncenginesubscriptionwnschannelcallbackproxy_onoffline;

typedef struct _syncenginesubscriptionwnschannel_createchannel{
} syncenginesubscriptionwnschannel_createchannel;

typedef struct _syncenginesubscriptionwnschannel_deletechannelifneeded{
} syncenginesubscriptionwnschannel_deletechannelifneeded;

typedef struct _syncenginesubscriptionwnschannel_deletechannelrequest{
} syncenginesubscriptionwnschannel_deletechannelrequest;

typedef struct _syncenginesubscriptionwnschannel_getwnsvaluefromregistry{
} syncenginesubscriptionwnschannel_getwnsvaluefromregistry;

typedef struct _syncenginesubscriptionwnschannel_oncreatedwnschannel{
} syncenginesubscriptionwnschannel_oncreatedwnschannel;

typedef struct _syncenginesubscriptionwnschannel_onnotificationreceived{
} syncenginesubscriptionwnschannel_onnotificationreceived;

typedef struct _syncenginesubscriptionwnschannel_teardown{
} syncenginesubscriptionwnschannel_teardown;

typedef struct _syncenginesubscription_addworkitem{
} syncenginesubscription_addworkitem;

typedef struct _syncenginesubscription_close{
} syncenginesubscription_close;

typedef struct _syncenginesubscription_corelooponcreatedstoragesubscription{
} syncenginesubscription_corelooponcreatedstoragesubscription;

typedef struct _syncenginesubscription_createsubscriptionifneeded{
} syncenginesubscription_createsubscriptionifneeded;

typedef struct _syncenginesubscription_createsubscriptionwithauthticket{
} syncenginesubscription_createsubscriptionwithauthticket;

typedef struct _syncenginesubscription_deletesubscriptionifneeded{
} syncenginesubscription_deletesubscriptionifneeded;

typedef struct _syncenginesubscription_loadsubscriptionid{
} syncenginesubscription_loadsubscriptionid;

typedef struct _syncenginesubscription_oncreatedstoragesubscription{
} syncenginesubscription_oncreatedstoragesubscription;

typedef struct _syncenginesubscription_onnotificationreceived{
} syncenginesubscription_onnotificationreceived;

typedef struct _syncenginesubscription_onnotificationreceivedbaseoneauthmsaluserauthentication_issignedin{
} syncenginesubscription_onnotificationreceivedbaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncenginesubscription_onsubscriptionlost{
} syncenginesubscription_onsubscriptionlost;

typedef struct _syncenginesubscription_prepare{
} syncenginesubscription_prepare;

typedef struct _syncenginesubscription_restorepersistedsubscriptionid{
} syncenginesubscription_restorepersistedsubscriptionid;

typedef struct _syncenginesubscription_setserverrefreshneeded{
} syncenginesubscription_setserverrefreshneeded;

typedef struct _syncenginesubscription_setserverrefreshneededbaseoneauthmsaluserauthentication_issignedin{
} syncenginesubscription_setserverrefreshneededbaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncenginesubscription_teardowncomplete{
} syncenginesubscription_teardowncomplete;

typedef struct _syncenginesubscription_teardownsubscriptionifexpired{
} syncenginesubscription_teardownsubscriptionifexpired;

typedef struct _syncenginesubscription_transitiontostate{
} syncenginesubscription_transitiontostate;

typedef struct _syncenginesubscription_updatefromclientpolicy{
} syncenginesubscription_updatefromclientpolicy;

typedef struct _syncenginesubscription_updatepollingmode{
} syncenginesubscription_updatepollingmode;

typedef struct _synchelpers_adjustupdatetimeifneeded{
} synchelpers_adjustupdatetimeifneeded;

typedef struct _synchelpers_adjustupdatetimeifneededbaseoneauthmsaluserauthentication_issignedin{
} synchelpers_adjustupdatetimeifneededbaseoneauthmsaluserauthentication_issignedin;

typedef struct _synchelpers_calctransferratesfortelemetry{
} synchelpers_calctransferratesfortelemetry;

typedef struct _synchelpers_calctransferratesfortelemetrybaseoneauthmsaluserauthentication_issignedin{
} synchelpers_calctransferratesfortelemetrybaseoneauthmsaluserauthentication_issignedin;

typedef struct _synchelpers_deleteifmarked{
} synchelpers_deleteifmarked;

typedef struct _synchelpers_finalizesuccessfultransfer{
} synchelpers_finalizesuccessfultransfer;

typedef struct _synchelpers_generatepathfromurlwithscope{
} synchelpers_generatepathfromurlwithscope;

typedef struct _synchelpers_recordchangeenumerationresult{
} synchelpers_recordchangeenumerationresult;

typedef struct _synchelpers_recordlocalchanges{
} synchelpers_recordlocalchanges;

typedef struct _synchelpers_recorduploaddownload{
} synchelpers_recorduploaddownload;

typedef struct _synchelpers_setneedsplaceholderremoval{
} synchelpers_setneedsplaceholderremoval;

typedef struct _synchelpers_updatefileorfoldernamevalidationrampsandsettings{
} synchelpers_updatefileorfoldernamevalidationrampsandsettings;

typedef struct _syncobjectcontainer_completependingonenotefixups{
} syncobjectcontainer_completependingonenotefixups;

typedef struct _syncobjectcontainer_loadsyncscopes{
} syncobjectcontainer_loadsyncscopes;

typedef struct _syncobjectcontainer_setlocalmaxpathvalue{
} syncobjectcontainer_setlocalmaxpathvalue;

typedef struct _syncobjectcontainer_updatesyncengineproviderregistration{
} syncobjectcontainer_updatesyncengineproviderregistration;

typedef struct _syncperformanceaudit_loadsyncperformanceauditruninfo{
} syncperformanceaudit_loadsyncperformanceauditruninfo;

typedef struct _syncperformanceaudit_startsyncperformanceaudit{
} syncperformanceaudit_startsyncperformanceaudit;

typedef struct _syncperformanceaudit_startsyncperformanceauditbaseoneauthmsaluserauthentication_issignedin{
} syncperformanceaudit_startsyncperformanceauditbaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncperftrack_recordtelemetry{
} syncperftrack_recordtelemetry;

typedef struct _syncperftrack_startmeasure{
} syncperftrack_startmeasure;

typedef struct _syncperftrack_stopscenario{
} syncperftrack_stopscenario;

typedef struct _syncperftrack_stopscenarioandreport{
} syncperftrack_stopscenarioandreport;

typedef struct _syncperftrack_trackscope{
} syncperftrack_trackscope;

typedef struct _syncperftrack_untrackscope{
} syncperftrack_untrackscope;

typedef struct _syncprogressaudit_senddiagnosticinfo{
} syncprogressaudit_senddiagnosticinfo;

typedef struct _syncprogressaudit_sendsyncpulse{
} syncprogressaudit_sendsyncpulse;

typedef struct _syncprogressaudit_sendsyncpulsebaseoneauthmsaluserauthentication_issignedin{
} syncprogressaudit_sendsyncpulsebaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncprogressaudit_startsyncprogressaudit{
} syncprogressaudit_startsyncprogressaudit;

typedef struct _syncprogresssource_getfriendlynameofapplication{
} syncprogresssource_getfriendlynameofapplication;

typedef struct _syncprogresssource_populatemapwithexetofriendlyname{
} syncprogresssource_populatemapwithexetofriendlyname;

typedef struct _syncprogresssource_operator_{
} syncprogresssource_operator_;

typedef struct _syncrootregistrationverification_logsyncrootverificationinfo{
} syncrootregistrationverification_logsyncrootverificationinfo;

typedef struct _syncrootregistrationverification_reporttelemetryandresetcounts{
} syncrootregistrationverification_reporttelemetryandresetcounts;

typedef struct _syncrootregistrationverification_verifysyncrootregistration{
} syncrootregistrationverification_verifysyncrootregistration;

typedef struct _syncrootregistrationverification_verifysyncrootregistrationforallscopes{
} syncrootregistrationverification_verifysyncrootregistrationforallscopes;

typedef struct _syncserviceproxy_completechangeenumeration{
} syncserviceproxy_completechangeenumeration;

typedef struct _syncserviceproxy_completegetspecialfolderinfo{
} syncserviceproxy_completegetspecialfolderinfo;

typedef struct _syncserviceproxy_completeselectivesyncenumeration{
} syncserviceproxy_completeselectivesyncenumeration;

typedef struct _syncserviceproxy_createchangefilerealizerworkitem{
} syncserviceproxy_createchangefilerealizerworkitem;

typedef struct _syncserviceproxy_createchangefilerealizerworkitembaseoneauthmsaluserauthentication_issignedin{
} syncserviceproxy_createchangefilerealizerworkitembaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncserviceproxy_createnewfilerealizerworkitem{
} syncserviceproxy_createnewfilerealizerworkitem;

typedef struct _syncserviceproxy_createnewfolderrealizerworkitem{
} syncserviceproxy_createnewfolderrealizerworkitem;

typedef struct _syncserviceproxy_createpersistsynctokenrealizerworkitem{
} syncserviceproxy_createpersistsynctokenrealizerworkitem;

typedef struct _syncserviceproxy_endsyncscopeinitialization{
} syncserviceproxy_endsyncscopeinitialization;

typedef struct _syncserviceproxy_filteroutprocessedentry{
} syncserviceproxy_filteroutprocessedentry;

typedef struct _syncserviceproxy_getfindchangespagesize{
} syncserviceproxy_getfindchangespagesize;

typedef struct _syncserviceproxy_handlefaileduploadbatch{
} syncserviceproxy_handlefaileduploadbatch;

typedef struct _syncserviceproxy_loguploadbatchperitemtelemetry{
} syncserviceproxy_loguploadbatchperitemtelemetry;

typedef struct _syncserviceproxy_maplibrary{
} syncserviceproxy_maplibrary;

typedef struct _syncserviceproxy_ondownloadedclientpolicy{
} syncserviceproxy_ondownloadedclientpolicy;

typedef struct _syncserviceproxy_ondownloadedentries{
} syncserviceproxy_ondownloadedentries;

typedef struct _syncserviceproxy_ondownloadedselectivesyncentries{ // needs work
    int32 size1;
    char data1[size1];
    int32 size2;
    char data2[size2];
    int32 size3;
    char data3[size3];
    int32 size4;
    char data4[size4];
    int32 size5;
    char data5[size5];
} syncserviceproxy_ondownloadedselectivesyncentries;

typedef struct _syncserviceproxy_onretrievedquotastate{
} syncserviceproxy_onretrievedquotastate;

typedef struct _syncserviceproxy_onretrievedspaceused{
} syncserviceproxy_onretrievedspaceused;

typedef struct _syncserviceproxy_onretrievedspaceusedbaseoneauthmsaluserauthentication_issignedin{
} syncserviceproxy_onretrievedspaceusedbaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncserviceproxy_onuploadedentries{
} syncserviceproxy_onuploadedentries;

typedef struct _syncserviceproxy_processdownloadedentries{
} syncserviceproxy_processdownloadedentries;

typedef struct _syncserviceproxy_processnewsynctoken{
} syncserviceproxy_processnewsynctoken;

typedef struct _syncserviceproxy_processuploadedentries{
} syncserviceproxy_processuploadedentries;

typedef struct _syncserviceproxy_shouldstartchangeenumerationbetreatedasinitialsync{
} syncserviceproxy_shouldstartchangeenumerationbetreatedasinitialsync;

typedef struct _syncserviceproxy_startchangeenumeration{
} syncserviceproxy_startchangeenumeration;

typedef struct _syncserviceproxy_startquotarefresh{
} syncserviceproxy_startquotarefresh;

typedef struct _syncserviceproxy_startsendchangebatch{
} syncserviceproxy_startsendchangebatch;

typedef struct _syncserviceproxy_startspaceused{
} syncserviceproxy_startspaceused;

typedef struct _syncserviceproxy_startsyncscopeinitialization{
} syncserviceproxy_startsyncscopeinitialization;

typedef struct _syncserviceproxy_triggerstartupchangeenumerationonallscopes{
} syncserviceproxy_triggerstartupchangeenumerationonallscopes;

typedef struct _syncserviceproxy_triggerstartupchangeenumerationonallscopesbaseoneauthmsaluserauthentication_issignedin{
} syncserviceproxy_triggerstartupchangeenumerationonallscopesbaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncserviceproxy_uploadentries{
} syncserviceproxy_uploadentries;

typedef struct _syncstatus_logsyncstatusifnecessary{
} syncstatus_logsyncstatusifnecessary;

typedef struct _synctelemetry_checkforblockage{
} synctelemetry_checkforblockage;

typedef struct _synctelemetry_checkforblockagebaseoneauthmsaluserauthentication_issignedin{
} synctelemetry_checkforblockagebaseoneauthmsaluserauthentication_issignedin;

typedef struct _synctelemetry_logtelemetry{
} synctelemetry_logtelemetry;

typedef struct _synctelemetry_ondbloaded{
} synctelemetry_ondbloaded;

typedef struct _synctelemetry_recordgetmountedfolderscenario{
} synctelemetry_recordgetmountedfolderscenario;

typedef struct _synctelemetry_recordscenario{
} synctelemetry_recordscenario;

typedef struct _synctelemetry_reporttelemetry{
} synctelemetry_reporttelemetry;

typedef struct _synctelemetry_sendandresetchangesetuploadtelemetry{
} synctelemetry_sendandresetchangesetuploadtelemetry;

typedef struct _synctelemetry_startscenario{
} synctelemetry_startscenario;

typedef struct _synctelemetry_stopscenario{
} synctelemetry_stopscenario;

typedef struct _syncuploadtelemetry_computerates{
} syncuploadtelemetry_computerates;

typedef struct _syncuploadtelemetry_logfullfileuploadcomplete{
} syncuploadtelemetry_logfullfileuploadcomplete;

typedef struct _syncverification_addtoscopeverificationcollection{
} syncverification_addtoscopeverificationcollection;

typedef struct _syncverification_candospeedtestindiagnostics{
} syncverification_candospeedtestindiagnostics;

typedef struct _syncverification_completeverification{
} syncverification_completeverification;

typedef struct _syncverification_filteroutalreadyprocessedclouditems{
} syncverification_filteroutalreadyprocessedclouditems;

typedef struct _syncverification_loadsyncverificationruninfo{
} syncverification_loadsyncverificationruninfo;

typedef struct _syncverification_logdivergencepathcontent{
} syncverification_logdivergencepathcontent;

typedef struct _syncverification_ondownloadedentriesforsyncverification{
} syncverification_ondownloadedentriesforsyncverification;

typedef struct _syncverification_ondownloadedentriesrunnextstageforperfindchangespageverification{
} syncverification_ondownloadedentriesrunnextstageforperfindchangespageverification;

typedef struct _syncverification_ondownloadedentriesrunnextstageforperfindchangespageverificationbaseoneauthmsaluserauthentication_issignedin{
} syncverification_ondownloadedentriesrunnextstageforperfindchangespageverificationbaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncverification_populateitemsbypathmap{
} syncverification_populateitemsbypathmap;

typedef struct _syncverification_populateitemsbypathmapbaseoneauthmsaluserauthentication_issignedin{
} syncverification_populateitemsbypathmapbaseoneauthmsaluserauthentication_issignedin;

typedef struct _syncverification_reportcloudfilespecificsyncproblem{
} syncverification_reportcloudfilespecificsyncproblem;

typedef struct _syncverification_runscopeverificationforlockedvault{
} syncverification_runscopeverificationforlockedvault;

typedef struct _syncverification_scanfilesystem{
} syncverification_scanfilesystem;

typedef struct _syncverification_senddiagnosticinfo{
} syncverification_senddiagnosticinfo;

typedef struct _syncverification_sendsubscriptioninfo{
} syncverification_sendsubscriptioninfo;

typedef struct _syncverification_sendsyncinfocategories{
} syncverification_sendsyncinfocategories;

typedef struct _syncverification_sendsyncinfocategorieskpi{
} syncverification_sendsyncinfocategorieskpi;

typedef struct _syncverification_startsyncverification{
} syncverification_startsyncverification;

typedef struct _syncverification_updatehealingitemscollection{
} syncverification_updatehealingitemscollection;

typedef struct _syncwebsocketmanager_processsyncstatuschange{
} syncwebsocketmanager_processsyncstatuschange;

typedef struct _syncedignoredfilecloudcleanupjob_refreshcleanuprulesfromsettings{
} syncedignoredfilecloudcleanupjob_refreshcleanuprulesfromsettings;

typedef struct _systraymanager_changestate{
} systraymanager_changestate;

typedef struct _systraymanager_onlibrarystatus{
} systraymanager_onlibrarystatus;

typedef struct _systraymanager_ontoasthandled{
} systraymanager_ontoasthandled;

typedef struct _systraymanager_reportcloudfilesnamespacecreationifneeded{
} systraymanager_reportcloudfilesnamespacecreationifneeded;

typedef struct _systraymanager_reportcloudfilesnamespacecreationifneededbaseoneauthmsaluserauthentication_issignedin{
} systraymanager_reportcloudfilesnamespacecreationifneededbaseoneauthmsaluserauthentication_issignedin;

typedef struct _systraymanager_updatesystrayprogressorerrorstate{
} systraymanager_updatesystrayprogressorerrorstate;

typedef struct _systray_onrampsupdated{
} systray_onrampsupdated;

typedef struct _systray_show{
} systray_show;

typedef struct _systray_showbaseoneauthmsaluserauthentication_issignedin{
} systray_showbaseoneauthmsaluserauthentication_issignedin;

typedef struct _systray_trypromotesystrayicon{
} systray_trypromotesystrayicon;

typedef struct _systray_operator_{
} systray_operator_;

typedef struct _telemetryconfiguration_operator_{
    int32 size;
    char data[size];
} telemetryconfiguration_operator_;

typedef struct _telemetryhelper_sendtelemetryevent{
} telemetryhelper_sendtelemetryevent;

typedef struct _telemetryproxyconfigurationfile_initialize{
    int32 size;
    char data[size + 2];
} telemetryproxyconfigurationfile_initialize;

typedef struct _telemetryproxyconfigurationfile_updatelocalvariablefromfile{
} telemetryproxyconfigurationfile_updatelocalvariablefromfile;

typedef struct _thread_setwaithandle{
} thread_setwaithandle;

typedef struct _thread_start{
} thread_start;

typedef struct _thread_stop{
} thread_stop;

typedef struct _thread_thread{
} thread_thread;

typedef struct _thread_threadproc{
} thread_threadproc;

typedef struct _thread__thread{
} thread__thread;

typedef struct _throttledtransfers_processretryafterheader{
} throttledtransfers_processretryafterheader;

typedef struct _throttledtransfers_removeexpiredentries{
} throttledtransfers_removeexpiredentries;

typedef struct _throttledtransfers_removeexpiredentriesbaseoneauthmsaluserauthentication_issignedin{
} throttledtransfers_removeexpiredentriesbaseoneauthmsaluserauthentication_issignedin;

typedef struct _throttledtransfers_reportandclearthrottleinfo{
} throttledtransfers_reportandclearthrottleinfo;

typedef struct _throttledtransfers_reportthrottledtransfer{
} throttledtransfers_reportthrottledtransfer;

typedef struct _throttledtransfers_throttleresourceid{
} throttledtransfers_throttleresourceid;

typedef struct _thumbnailauthprovider_fetchticketfromauth{
} thumbnailauthprovider_fetchticketfromauth;

typedef struct _thumbnailproviderservice_addrequesttoqueue{
} thumbnailproviderservice_addrequesttoqueue;

typedef struct _thumbnailproviderservice_initialize{
} thumbnailproviderservice_initialize;

typedef struct _thumbnailproviderservice_onthumbnailrequestcompleted{
} thumbnailproviderservice_onthumbnailrequestcompleted;

typedef struct _thumbnailproviderservice_requestthumbnail{
} thumbnailproviderservice_requestthumbnail;

typedef struct _thumbnailtelemetry_logalltelemetry{
} thumbnailtelemetry_logalltelemetry;

typedef struct _thumbnailtelemetry_logduration{
} thumbnailtelemetry_logduration;

typedef struct _timerqueue_insertwithtimeout{
} timerqueue_insertwithtimeout;

typedef struct _timerqueue_stop{
} timerqueue_stop;

typedef struct _timer_initialize{
} timer_initialize;

typedef struct _tlssocket_close{
} tlssocket_close;

typedef struct _tlssocket_closebaseoneauthmsaluserauthentication_issignedin{
} tlssocket_closebaseoneauthmsaluserauthentication_issignedin;

typedef struct _tlssocket_onsendcomplete{
} tlssocket_onsendcomplete;

typedef struct _tlssocket_sendgoodbye{
} tlssocket_sendgoodbye;

typedef struct _tlssocket_setsocket{
} tlssocket_setsocket;

typedef struct _toastdisplayer_createtoast{
} toastdisplayer_createtoast;

typedef struct _toastdisplayer_createtoastxml{
} toastdisplayer_createtoastxml;

typedef struct _toastdisplayer_displaytoast{
} toastdisplayer_displaytoast;

typedef struct _toastdisplayer_sendtoasthandlednotification{
} toastdisplayer_sendtoasthandlednotification;

typedef struct _unsynclist_unsynclistimpl{
} unsynclist_unsynclistimpl;

typedef struct _unsynclist_operator_{
} unsynclist_operator_;

typedef struct _updatedownloader_checkforapplicableupdates{
} updatedownloader_checkforapplicableupdates;

typedef struct _updatedownloader_downloadlatestupdates{
} updatedownloader_downloadlatestupdates;

typedef struct _updatedownloader_initialize{
} updatedownloader_initialize;

typedef struct _updatedownloader_loadandparsecachedupdatexml{
} updatedownloader_loadandparsecachedupdatexml;

typedef struct _updatemanager_deleteoldsetupbinaries{
} updatemanager_deleteoldsetupbinaries;

typedef struct _updatemanager_downloadandlaunchupdate{
} updatemanager_downloadandlaunchupdate;

typedef struct _updatemanager_downloadandlaunchupdatewithtimer{
} updatemanager_downloadandlaunchupdatewithtimer;

typedef struct _updatemanager_launchsetupexe{
} updatemanager_launchsetupexe;

typedef struct _updatemanager_launchsetupexebaseoneauthmsaluserauthentication_issignedin{
} updatemanager_launchsetupexebaseoneauthmsaluserauthentication_issignedin;

typedef struct _updatemanager_sendpermachineupdaterregisteredtelemetry{
} updatemanager_sendpermachineupdaterregisteredtelemetry;

typedef struct _updatemanager_sendtelemetryformissingistorageprovidercomkeys{
} updatemanager_sendtelemetryformissingistorageprovidercomkeys;

typedef struct _updatephstaterc_loginfo{
} updatephstaterc_loginfo;

typedef struct _updatephstaterc_process{
} updatephstaterc_process;

typedef struct _updatephstaterc_processbaseoneauthmsaluserauthentication_issignedin{
} updatephstaterc_processbaseoneauthmsaluserauthentication_issignedin;

typedef struct _updateringsettingsdownloader_downloadandapplysettings{
} updateringsettingsdownloader_downloadandapplysettings;

typedef struct _updateringsettingsloader_getfilestreamfromcache{
} updateringsettingsloader_getfilestreamfromcache;

typedef struct _updateringsettingsloader_loadfromcache{
} updateringsettingsloader_loadfromcache;

typedef struct _updateringsettingsmanager_applyrampoverrides{
} updateringsettingsmanager_applyrampoverrides;

typedef struct _updateringsettingsmanager_createkillswitchset{
} updateringsettingsmanager_createkillswitchset;

typedef struct _updateringsettingsmanager_propagaterampstotelemetry{
} updateringsettingsmanager_propagaterampstotelemetry;

typedef struct _updateringsettingsmanager_sendtelemetryonupdateringsource{
} updateringsettingsmanager_sendtelemetryonupdateringsource;

typedef struct _updateringsettingsmanager_sendupdatetelemetry{
} updateringsettingsmanager_sendupdatetelemetry;

typedef struct _updateringsettingsmanager_tryupdate{
} updateringsettingsmanager_tryupdate;

typedef struct _updateringsettingsparser_parse{
} updateringsettingsparser_parse;

typedef struct _updateringsettingsupdater_tryupdatesettings{
} updateringsettingsupdater_tryupdatesettings;

typedef struct _updateringsettingsupdater_tryupdatesettingswithcachedconfig{
} updateringsettingsupdater_tryupdatesettingswithcachedconfig;

typedef struct _updateringsettingsupdater_tryupdatesettingswithnewconfig{
} updateringsettingsupdater_tryupdatesettingswithnewconfig;

typedef struct _updateringsettingsupdater_validatecontent{
} updateringsettingsupdater_validatecontent;

typedef struct _updatexmlparser_getxmlstream{
} updatexmlparser_getxmlstream;

typedef struct _updatexmlparser_parseupdatenodexml{
} updatexmlparser_parseupdatenodexml;

typedef struct _updatexmlparser_parseupdatexml{
} updatexmlparser_parseupdatexml;

typedef struct _updaterclient_performupdate{
} updaterclient_performupdate;

typedef struct _updaterinstrumentation_logandsetdatapoint{
} updaterinstrumentation_logandsetdatapoint;

typedef struct _updaterinstrumentation_setcid{
} updaterinstrumentation_setcid;

typedef struct _updaterinstrumentation_operator_{
} updaterinstrumentation_operator_;

typedef struct _updaterservice_downloadandapplyecsconfiguration{
} updaterservice_downloadandapplyecsconfiguration;

typedef struct _updaterservice_downloadandapplyupdateringsettings{
} updaterservice_downloadandapplyupdateringsettings;

typedef struct _updaterservice_initializelogging{
} updaterservice_initializelogging;

typedef struct _updaterservice_performupdate{
} updaterservice_performupdate;

typedef struct _updaterservice_performupdatewithretry{
} updaterservice_performupdatewithretry;

typedef struct _updaterservice_sendoverallresult{
} updaterservice_sendoverallresult;

typedef struct _updaterservice_sendoverallresultbaseoneauthmsaluserauthentication_issignedin{
} updaterservice_sendoverallresultbaseoneauthmsaluserauthentication_issignedin;

typedef struct _updaterutil_ismachinethrottled{
} updaterutil_ismachinethrottled;

typedef struct _updaterutil_isupdatedescriptionvalid{
} updaterutil_isupdatedescriptionvalid;

typedef struct _updaterutil_parseupdatexmlstream{
} updaterutil_parseupdatexmlstream;

typedef struct _updaterutil_selectupdate{
} updaterutil_selectupdate;

typedef struct _uploadgate_addfiletoqueue{
} uploadgate_addfiletoqueue;

typedef struct _uploadgate_duplicateuploadexists{
} uploadgate_duplicateuploadexists;

typedef struct _uploadgate_duplicateuploadexistsbaseoneauthmsaluserauthentication_issignedin{
} uploadgate_duplicateuploadexistsbaseoneauthmsaluserauthentication_issignedin;

typedef struct _uploadgate_invokesynccompleteifapplicable{
} uploadgate_invokesynccompleteifapplicable;

typedef struct _uploadgate_logupdateddrivechange{
} uploadgate_logupdateddrivechange;

typedef struct _uploadgate_logupdateddrivechangebaseoneauthmsaluserauthentication_issignedin{
} uploadgate_logupdateddrivechangebaseoneauthmsaluserauthentication_issignedin;

typedef struct _uploadgate_notifyuploadremoved{
} uploadgate_notifyuploadremoved;

typedef struct _uploadgate_queuefilestoupload{
} uploadgate_queuefilestoupload;

typedef struct _uploadgate_removecompleteduploads{
} uploadgate_removecompleteduploads;

typedef struct _uploadgate_stopnotificationcoalesceifnecessary{
} uploadgate_stopnotificationcoalesceifnecessary;

typedef struct _uploadmetadatascenario_add{
} uploadmetadatascenario_add;

typedef struct _uploadmetadatascenario_get{
} uploadmetadatascenario_get;

typedef struct _uploadmetadatascenario_remove{
} uploadmetadatascenario_remove;

typedef struct _uploadmetadatascenario_report{
} uploadmetadatascenario_report;

typedef struct _uploadmetadatascenario_reportbatch{
} uploadmetadatascenario_reportbatch;

typedef struct _uploadmetadatascenario_uploadmetadatascenario{
} uploadmetadatascenario_uploadmetadatascenario;

typedef struct _uploadmetadatascenario__uploadmetadatascenario{
} uploadmetadatascenario__uploadmetadatascenario;

typedef struct _uploadmetadatascenario__uploadmetadatascenariobaseoneauthmsaluserauthentication_issignedin{
} uploadmetadatascenario__uploadmetadatascenariobaseoneauthmsaluserauthentication_issignedin;

typedef struct _uploadscenario_add{
} uploadscenario_add;

typedef struct _uploadscenario_changeresourceid{
} uploadscenario_changeresourceid;

typedef struct _uploadscenario_get{
} uploadscenario_get;

typedef struct _uploadscenario_remove{
} uploadscenario_remove;

typedef struct _uploadscenario_report{
} uploadscenario_report;

typedef struct _uploadscenario_setresult{
} uploadscenario_setresult;

typedef struct _uploadscenario_uploadscenario{
} uploadscenario_uploadscenario;

typedef struct _uploadscenario__uploadscenario{
} uploadscenario__uploadscenario;

typedef struct _upsellsmanager_finishinit{
} upsellsmanager_finishinit;

typedef struct _uriprovider_updateuricache{
} uriprovider_updateuricache;

typedef struct _usagedatagatherer_operator_{
} usagedatagatherer_operator_;

typedef struct _usagedatagatherer_operator_baseoneauthmsaluserauthentication_issignedin{
} usagedatagatherer_operator_baseoneauthmsaluserauthentication_issignedin;

typedef struct _usercookie_getcookie{
} usercookie_getcookie;

typedef struct _usercookie_getcookiefromuri{
} usercookie_getcookiefromuri;

typedef struct _usercookie_getcookiefromuribaseoneauthmsaluserauthentication_issignedin{
} usercookie_getcookiefromuribaseoneauthmsaluserauthentication_issignedin;

typedef struct _user_clone{
} user_clone;

typedef struct _user_handleauthevent{
} user_handleauthevent;

typedef struct _user_initialize{
} user_initialize;

typedef struct _utilities_deleteperaccountregkeys{
} utilities_deleteperaccountregkeys;

typedef struct _utilities_deleteperaccountsettings{
} utilities_deleteperaccountsettings;

typedef struct _utilities_deleteperaccountsettingsbaseoneauthmsaluserauthentication_issignedin{
} utilities_deleteperaccountsettingsbaseoneauthmsaluserauthentication_issignedin;

typedef struct _utilities_deleteusedsaveddiskspacecheckfromregistry{
} utilities_deleteusedsaveddiskspacecheckfromregistry;

typedef struct _utilities_getbusinessinstancenameinternal{
} utilities_getbusinessinstancenameinternal;

typedef struct _utilities_getfirstconfiguredrunningaccount{
} utilities_getfirstconfiguredrunningaccount;

typedef struct _utilities_getinstancename{
} utilities_getinstancename;

typedef struct _utilities_getusersaveddiskspacecheckstatefromregistry{
} utilities_getusersaveddiskspacecheckstatefromregistry;

typedef struct _utilities_iswinrtcontractsupported{
} utilities_iswinrtcontractsupported;

typedef struct _utilities_setaccountpropertiesregistrykeys{
} utilities_setaccountpropertiesregistrykeys;

typedef struct _utilities_setaccountregvaluedwordforinstance{
} utilities_setaccountregvaluedwordforinstance;

typedef struct _utilities_setaccountregvaluewstrforinstance{
} utilities_setaccountregvaluewstrforinstance;

typedef struct _utilities_setaccountregistryvaluedwordforinstance{
} utilities_setaccountregistryvaluedwordforinstance;

typedef struct _utilities_setfirstrunregkey{
} utilities_setfirstrunregkey;

typedef struct _utilities_operator_{
} utilities_operator_;

typedef struct _utilitymanager_updatetelemetrystate{
} utilitymanager_updatetelemetrystate;

typedef struct _validatepostprocessingdciworkitem_process{
} validatepostprocessingdciworkitem_process;

typedef struct _vaultcontroller_handlesignout{
} vaultcontroller_handlesignout;

typedef struct _vaultcontroller_loadvhdinfo{
} vaultcontroller_loadvhdinfo;

typedef struct _vaultcontroller_parsevhdinfo{
} vaultcontroller_parsevhdinfo;

typedef struct _vaultcontroller_updatevaultstate{
} vaultcontroller_updatevaultstate;

typedef struct _vaulthelper_setupvaultshortcut{
} vaulthelper_setupvaultshortcut;

typedef struct _vaultmanager_handlevaultstatechanged{
} vaultmanager_handlevaultstatechanged;

typedef struct _vaultmanager_updatevaultshortcuticon{
} vaultmanager_updatevaultshortcuticon;

typedef struct _vaultmanager_updatevaultshortcutsyncstatus{
} vaultmanager_updatevaultshortcutsyncstatus;

typedef struct _visualstatecontroller_changestate{
} visualstatecontroller_changestate;

typedef struct _visualstatecontroller_handleerrorstatechangedevent{
} visualstatecontroller_handleerrorstatechangedevent;

typedef struct _visualstatecontroller_handlenotificationwhileonline{
} visualstatecontroller_handlenotificationwhileonline;

typedef struct _visualstatecontroller_handleupdatecheckcomplete{
} visualstatecontroller_handleupdatecheckcomplete;

typedef struct _visualstatecontroller_handleupdatecheckstarting{
} visualstatecontroller_handleupdatecheckstarting;

typedef struct _watcherwin_addmountpoint{
} watcherwin_addmountpoint;

typedef struct _watcherwin_addpossiblechangeifnotalreadyadded{
} watcherwin_addpossiblechangeifnotalreadyadded;

typedef struct _watcherwin_examinechange{
} watcherwin_examinechange;

typedef struct _watcherwin_monitor{
} watcherwin_monitor;

typedef struct _watcherwin_triggerwatchermonitorawake{
} watcherwin_triggerwatchermonitorawake;

typedef struct _watcher_addmountpoint{
} watcher_addmountpoint;

typedef struct _watcher_addpossiblechangeifnotalreadyadded{
} watcher_addpossiblechangeifnotalreadyadded;

typedef struct _watcher_clearrequestfullscan{
} watcher_clearrequestfullscan;

typedef struct _watcher_examinechange{
} watcher_examinechange;

typedef struct _watcher_monitor{
} watcher_monitor;

typedef struct _watcher_requestdelayedscan{
} watcher_requestdelayedscan;

typedef struct _watcher_requestdelayedscanbaseoneauthmsaluserauthentication_issignedin{
} watcher_requestdelayedscanbaseoneauthmsaluserauthentication_issignedin;

typedef struct _watcher_requestfullscan{
} watcher_requestfullscan;

typedef struct _watcher_resetignorelist{
} watcher_resetignorelist;

typedef struct _watcher_resetignorelistbaseoneauthmsaluserauthentication_issignedin{
} watcher_resetignorelistbaseoneauthmsaluserauthentication_issignedin;

typedef struct _watcher_setrequestfullscan{
} watcher_setrequestfullscan;

typedef struct _watcher_shutdownallwatchers{
} watcher_shutdownallwatchers;

typedef struct _watcher_shutdownallwatchersbaseoneauthmsaluserauthentication_issignedin{
} watcher_shutdownallwatchersbaseoneauthmsaluserauthentication_issignedin;

typedef struct _webclientupdatedownloader_copyoverdownloadeddata{
} webclientupdatedownloader_copyoverdownloadeddata;

typedef struct _webclientupdatedownloader_copyoverdownloadeddatawithstream{
} webclientupdatedownloader_copyoverdownloadeddatawithstream;

typedef struct _webclientupdatedownloader_downloadupdatefile{
} webclientupdatedownloader_downloadupdatefile;

typedef struct _webrequest_onrequestcomplete{
} webrequest_onrequestcomplete;

typedef struct _webrequest_sendwebrequest{
} webrequest_sendwebrequest;

typedef struct _webserver_getnextendpointrestarttime{
} webserver_getnextendpointrestarttime;

typedef struct _webserver_schedulenextendpointrestart{
} webserver_schedulenextendpointrestart;

typedef struct _webserver_start{
} webserver_start;

typedef struct _webview2manager_initializecomponent{
} webview2manager_initializecomponent;

typedef struct _webview2manager_postinitialize{
} webview2manager_postinitialize;

typedef struct _win32nativefilehandlewrapper_win32nativefilehandlewrapper{
} win32nativefilehandlewrapper_win32nativefilehandlewrapper;

typedef struct _win32nativefilehandlewrapper__win32nativefilehandlewrapper{
} win32nativefilehandlewrapper__win32nativefilehandlewrapper;

typedef struct _wincoauthsupportutils_getdeclaredprotocolversionforapp{
} wincoauthsupportutils_getdeclaredprotocolversionforapp;

typedef struct _wincoauthsupportutils_getdeclaredprotocolversionforextension{
} wincoauthsupportutils_getdeclaredprotocolversionforextension;

typedef struct _wincoauthsupportutils_isassociatedappsupportedbyhold{
} wincoauthsupportutils_isassociatedappsupportedbyhold;

typedef struct _wincoauthsupportutils_traversesyncengineproviderscopesandunregister{
} wincoauthsupportutils_traversesyncengineproviderscopesandunregister;

typedef struct _wincoauthsupportutils_unregistersyncengineproviderifunmountedscope{
} wincoauthsupportutils_unregistersyncengineproviderifunmountedscope;

typedef struct _wintelemetrydllhandler_hasgrouppolicyconfiguringtelemetryuploadlocation{
} wintelemetrydllhandler_hasgrouppolicyconfiguringtelemetryuploadlocation;

typedef struct _wintelemetrydllhandler_shoulduseexperimentaldll{
    int16 unk1;
    int8  unk2;
} wintelemetrydllhandler_shoulduseexperimentaldll;

typedef struct _winboxfiltercommunicationsport_connect{
} winboxfiltercommunicationsport_connect;

typedef struct _winboxfiltercommunicationsport_connecttosyncroot{
} winboxfiltercommunicationsport_connecttosyncroot;

typedef struct _winboxfiltercommunicationsport_disconnect{
} winboxfiltercommunicationsport_disconnect;

typedef struct _winboxfiltercommunicationsport_disconnectfromsyncroot{
} winboxfiltercommunicationsport_disconnectfromsyncroot;

typedef struct _winboxfiltercommunicationsport_oncancelfetchdata{
} winboxfiltercommunicationsport_oncancelfetchdata;

typedef struct _winboxfiltercommunicationsport_ondeletecompletion{
} winboxfiltercommunicationsport_ondeletecompletion;

typedef struct _winboxfiltercommunicationsport_onfetchdata{
} winboxfiltercommunicationsport_onfetchdata;

typedef struct _winboxfiltercommunicationsport_onrenamecompletion{
} winboxfiltercommunicationsport_onrenamecompletion;

typedef struct _winboxfiltercommunicationsport_placeholdergetdatasize{
} winboxfiltercommunicationsport_placeholdergetdatasize;

typedef struct _winboxfiltercommunicationsport_placeholderreaddata{
} winboxfiltercommunicationsport_placeholderreaddata;

typedef struct _winboxfiltercommunicationsport_placeholderwritedata{
} winboxfiltercommunicationsport_placeholderwritedata;

typedef struct _winboxfiltercommunicationsport_reporthydrationtelemetry{
} winboxfiltercommunicationsport_reporthydrationtelemetry;

typedef struct _winboxfiltercommunicationsport_reportticketprogress{
} winboxfiltercommunicationsport_reportticketprogress;

typedef struct _winboxfiltercommunicationsport_startloggingfilterevents{
} winboxfiltercommunicationsport_startloggingfilterevents;

typedef struct _winboxfiltercommunicationsport_stoploggingfilterevents{
} winboxfiltercommunicationsport_stoploggingfilterevents;

typedef struct _winboxplaceholderutil_changefileinsyncstate{
} winboxplaceholderutil_changefileinsyncstate;

typedef struct _winboxplaceholderutil_changeplaceholderpinstate{
} winboxplaceholderutil_changeplaceholderpinstate;

typedef struct _winboxplaceholderutil_clearerrorstate{
} winboxplaceholderutil_clearerrorstate;

typedef struct _winboxplaceholderutil_closenativehandle{
} winboxplaceholderutil_closenativehandle;

typedef struct _winboxplaceholderutil_createplaceholder{
} winboxplaceholderutil_createplaceholder;

typedef struct _winboxplaceholderutil_getfileextendedstate{
} winboxplaceholderutil_getfileextendedstate;

typedef struct _winboxplaceholderutil_getnativehandlebypath{
} winboxplaceholderutil_getnativehandlebypath;

typedef struct _winboxplaceholderutil_getplaceholder{
} winboxplaceholderutil_getplaceholder;

typedef struct _winboxplaceholderutil_getplaceholderbaseoneauthmsaluserauthentication_issignedin{
} winboxplaceholderutil_getplaceholderbaseoneauthmsaluserauthentication_issignedin;

typedef struct _winboxplaceholderutil_getplaceholderbypath{
} winboxplaceholderutil_getplaceholderbypath;

typedef struct _winboxplaceholderutil_reportpassiveprogress{
} winboxplaceholderutil_reportpassiveprogress;

typedef struct _winboxplaceholderutil_reportpassiveprogressinternal{
} winboxplaceholderutil_reportpassiveprogressinternal;

typedef struct _winboxplaceholderutil_setpropertystorevalue{
} winboxplaceholderutil_setpropertystorevalue;

typedef struct _winboxplatformimpl_available_cfgetplaceholderrangeinfoforhydration{
} winboxplatformimpl_available_cfgetplaceholderrangeinfoforhydration;

typedef struct _winboxplatformimpl_available_cfgetplaceholderrangeinfoforhydrationbaseoneauthmsaluserauthentication_issignedin{
} winboxplatformimpl_available_cfgetplaceholderrangeinfoforhydrationbaseoneauthmsaluserauthentication_issignedin;

typedef struct _winboxplatformimpl_rtlsetprocessplaceholdercompatibilitymode{
} winboxplatformimpl_rtlsetprocessplaceholdercompatibilitymode;

typedef struct _winboxsyncrootmanager_registersyncrootusingcfapi{
} winboxsyncrootmanager_registersyncrootusingcfapi;

typedef struct _winboxsyncrootmanager_reportprovidersyncstatusforsyncroot{
} winboxsyncrootmanager_reportprovidersyncstatusforsyncroot;

typedef struct _winboxticketmanager_respondtoticket{
} winboxticketmanager_respondtoticket;

typedef struct _windowmanager_handlequeryendsessionmessage{
} windowmanager_handlequeryendsessionmessage;

typedef struct _windowmanager_handlequeryendsessionmessagebaseoneauthmsaluserauthentication_issignedin{
} windowmanager_handlequeryendsessionmessagebaseoneauthmsaluserauthentication_issignedin;

typedef struct _windowmanager_launchwizard{
} windowmanager_launchwizard;

typedef struct _windowmanager_notifyactivitycentermessageupdated{
} windowmanager_notifyactivitycentermessageupdated;

typedef struct _windowmanager_onnotification{
} windowmanager_onnotification;

typedef struct _windowmanager_sendbasicclienttelemetry{
} windowmanager_sendbasicclienttelemetry;

typedef struct _windowmanager_setdisablequitmenuitem{
} windowmanager_setdisablequitmenuitem;

typedef struct _windowmanager_setdisablequitmenuitembaseoneauthmsaluserauthentication_issignedin{
} windowmanager_setdisablequitmenuitembaseoneauthmsaluserauthentication_issignedin;

typedef struct _windowmanager_setresourcemanagertelemetry{
} windowmanager_setresourcemanagertelemetry;

typedef struct _windowmanager_signalsetuptogo{
} windowmanager_signalsetuptogo;

typedef struct _windowmanager_signalsetuptogobaseoneauthmsaluserauthentication_issignedin{
} windowmanager_signalsetuptogobaseoneauthmsaluserauthentication_issignedin;

typedef struct _windowmanager_uninitialize{
} windowmanager_uninitialize;

typedef struct _windowmanager_uninitializebaseoneauthmsaluserauthentication_issignedin{
} windowmanager_uninitializebaseoneauthmsaluserauthentication_issignedin;

typedef struct _windowsthumbnailupdater_updatethumbnailcache{
} windowsthumbnailupdater_updatethumbnailcache;

typedef struct _windowsthumbnailupdater_updatethumbnailcachebaseoneauthmsaluserauthentication_issignedin{
} windowsthumbnailupdater_updatethumbnailcachebaseoneauthmsaluserauthentication_issignedin;

typedef struct _wizardmodel_setadditioninfo{
} wizardmodel_setadditioninfo;

typedef struct _wizardmodel__wizardmodel{
} wizardmodel__wizardmodel;

typedef struct _wizardnavigator_dooperation{
} wizardnavigator_dooperation;

typedef struct _wizardnavigator_onoperationdone{
} wizardnavigator_onoperationdone;

typedef struct _wizardnavigator_onwizardclosed{
} wizardnavigator_onwizardclosed;

typedef struct _wizardnavigator_undooperations{
} wizardnavigator_undooperations;

typedef struct _wizardproxy_launchauthuxloginscreen{
} wizardproxy_launchauthuxloginscreen;

typedef struct _wizardproxy_onauthuxcallback{
} wizardproxy_onauthuxcallback;

typedef struct _wnpconnmanager_asyncgetproxy{
} wnpconnmanager_asyncgetproxy;

typedef struct _wnpconnmanager_connect{
} wnpconnmanager_connect;

typedef struct _wnpconnmanager_disconnect{
} wnpconnmanager_disconnect;

typedef struct _wnpconnmanager_onconnected{
} wnpconnmanager_onconnected;

typedef struct _wnpconnmanager_ondisconnected{
} wnpconnmanager_ondisconnected;

typedef struct _wnpconnmanager_onerror{
} wnpconnmanager_onerror;

typedef struct _wnpconnmanager_ongetproxycomplete{
} wnpconnmanager_ongetproxycomplete;

typedef struct _wnpconnmanager_send{
} wnpconnmanager_send;

typedef struct _wnpsimplebuffer_onerror{
} wnpsimplebuffer_onerror;

typedef struct _wnptransimpl_connect{
} wnptransimpl_connect;

typedef struct _wnptransimpl_connecttownpnet{
} wnptransimpl_connecttownpnet;

typedef struct _wnptransimpl_disconnect{
} wnptransimpl_disconnect;

typedef struct _wnptransimpl_disconnectinternal{
} wnptransimpl_disconnectinternal;

typedef struct _wnptransimpl_handleconnectionfailure{
} wnptransimpl_handleconnectionfailure;

typedef struct _wnptransimpl_killautoreconnect{
} wnptransimpl_killautoreconnect;

typedef struct _wnptransimpl_onconnectdetected{
} wnptransimpl_onconnectdetected;

typedef struct _wnptransimpl_onconnectedtointernet{
} wnptransimpl_onconnectedtointernet;

typedef struct _wnptransimpl_onconnectedtointernetbaseoneauthmsaluserauthentication_issignedin{
} wnptransimpl_onconnectedtointernetbaseoneauthmsaluserauthentication_issignedin;

typedef struct _wnptransimpl_ondisconnectedfrominternet{
} wnptransimpl_ondisconnectedfrominternet;

typedef struct _wnptransimpl_onwnpcommandresponse{
} wnptransimpl_onwnpcommandresponse;

typedef struct _wnptransimpl_onwnpconnected{
} wnptransimpl_onwnpconnected;

typedef struct _wnptransimpl_onwnpdisconnected{
} wnptransimpl_onwnpdisconnected;

typedef struct _wnptransimpl_onwnpnotification{
} wnptransimpl_onwnpnotification;

typedef struct _wnptransimpl_resetautoreconnecttimer{
} wnptransimpl_resetautoreconnecttimer;

typedef struct _wnptransimpl_sendcommand{
} wnptransimpl_sendcommand;

typedef struct _wnptransimpl_startautoreconnect{
} wnptransimpl_startautoreconnect;

typedef struct _wnsclient_onchannelrequestcomplete{
} wnsclient_onchannelrequestcomplete;

typedef struct _wnsclient_onconnectcomplete{
} wnsclient_onconnectcomplete;

typedef struct _wnsclient_onconnectionchanged{
} wnsclient_onconnectionchanged;

typedef struct _wnsclient_onnotificationreceived{
} wnsclient_onnotificationreceived;

typedef struct _wnsclient_requestchanneloniothread{
} wnsclient_requestchanneloniothread;

typedef struct _workpool_enqueuework{
} workpool_enqueuework;

typedef struct _workpool_hardstop{
} workpool_hardstop;

typedef struct _workpool_ontimerfired{
} workpool_ontimerfired;

typedef struct _workpool_start{
} workpool_start;

typedef struct _workpool_stop{
} workpool_stop;

typedef struct _workerthreadpool_addthread{
} workerthreadpool_addthread;

typedef struct _workerthreadpool_onthreadexiting{
} workerthreadpool_onthreadexiting;

typedef struct _workerthreadpool_removethread{
} workerthreadpool_removethread;

typedef struct _workerthreadpool_workermainloop{
} workerthreadpool_workermainloop;

typedef struct _workerthreadpool__workerthreadpool{
} workerthreadpool__workerthreadpool;

typedef struct _workerthreadpool__workerthreadpool_deprecated{
} workerthreadpool__workerthreadpool_deprecated;

typedef struct _activitycenterview_startqtappobject{
} activitycenterview_startqtappobject;

typedef struct _apiloop_apiloopthreadproc{
} apiloop_apiloopthreadproc;

typedef struct _apiloop_start{
} apiloop_start;

typedef struct _apiloop_stop{
} apiloop_stop;

typedef struct _application_baseapplication{
} application_baseapplication;

typedef struct _application_initialize{
} application_initialize;

typedef struct _application_ontransition{
} application_ontransition;

typedef struct _application_shutdown{
} application_shutdown;

typedef struct _authplatform_getlanguage{
} authplatform_getlanguage;

typedef struct _authproducthelper_defaultlanguage{
} authproducthelper_defaultlanguage;

typedef struct _authproducthelper_shoulduseintenvironment{
} authproducthelper_shoulduseintenvironment;

typedef struct _badlibpaths_buildstandardbadpathlist{
} badlibpaths_buildstandardbadpathlist;

typedef struct _badlibpaths_getexclusiontype{
} badlibpaths_getexclusiontype;

typedef struct _bannercontentnotification_bannercontentnotification{
} bannercontentnotification_bannercontentnotification;

typedef struct _bannercontentoperation_execute{
} bannercontentoperation_execute;

typedef struct _bannercontentoperation_getbuttonuri{
} bannercontentoperation_getbuttonuri;

typedef struct _bannermanager_handlecontentupdated{
} bannermanager_handlecontentupdated;

typedef struct _bannermanager_ongetcontent{
} bannermanager_ongetcontent;

typedef struct _bannermanager_ongetsubscription{
} bannermanager_ongetsubscription;

typedef struct _bannermanager_onrampsupdated{
} bannermanager_onrampsupdated;

typedef struct _bannersubscriptionnotification_bannersubscriptionnotification{
} bannersubscriptionnotification_bannersubscriptionnotification;

typedef struct _bannersubscriptionoperation_execute{
} bannersubscriptionoperation_execute;

typedef struct _batterystatusmanager_loadusersetting{
} batterystatusmanager_loadusersetting;

typedef struct _cache_add{
} cache_add;

typedef struct _cache_find{
} cache_find;

typedef struct _cache_remove{
} cache_remove;

typedef struct _cachemanager_onnotification{
} cachemanager_onnotification;

typedef struct _centennialofficeutils_initialize{
} centennialofficeutils_initialize;

typedef struct _centennialofficeutils_loadpackagemanager{
} centennialofficeutils_loadpackagemanager;

typedef struct _certverifier_verifymicrosofttrust{
} certverifier_verifymicrosofttrust;

typedef struct _clientstructs_checkifshouldignorewnsnetworknotifications{
} clientstructs_checkifshouldignorewnsnetworknotifications;

typedef struct _clientstructs_loadinitialmountpointpath{
} clientstructs_loadinitialmountpointpath;

typedef struct _clientstructs_reportholddurationtelemetry{
} clientstructs_reportholddurationtelemetry;

typedef struct _clientstructs_setdeleteusersettings{
} clientstructs_setdeleteusersettings;

typedef struct _clientstructs_setlockfileguid{
} clientstructs_setlockfileguid;

typedef struct _clientconfigurationtelemetryoperation_sendtelemetry{
} clientconfigurationtelemetryoperation_sendtelemetry;

typedef struct _clientsetupmanager_writeinfo{
    int32 size;
    char data[size];
} clientsetupmanager_writeinfo;

typedef struct _clientstructs_goidle{
} clientstructs_goidle;

typedef struct _clientstructs_initialize{
} clientstructs_initialize;

typedef struct _clientstructs_logidledebugstats{
} clientstructs_logidledebugstats;

typedef struct _configfile_getstrarrayconfigval{
} configfile_getstrarrayconfigval;

typedef struct _configfile_getstrconfigval{
} configfile_getstrconfigval;

typedef struct _configfile_readconfigfile{
} configfile_readconfigfile;

typedef struct _coreapi_beginvolumechangenotification{
} coreapi_beginvolumechangenotification;

typedef struct _coreapi_getaccountinformation{
} coreapi_getaccountinformation;

typedef struct _coreapi_getlibraries{
} coreapi_getlibraries;

typedef struct _coreapi_maplibrary{
} coreapi_maplibrary;

typedef struct _coreapi_signin{
} coreapi_signin;

typedef struct _corecommon_enableordisableplaceholders{
} corecommon_enableordisableplaceholders;

typedef struct _corecommon_handleplaceholdersenabledtransition{
} corecommon_handleplaceholdersenabledtransition;

typedef struct _corecommon_setcoauthappprotocolversions{
} corecommon_setcoauthappprotocolversions;

typedef struct _corecommon_shouldplaceholdersbeenabled{
} corecommon_shouldplaceholdersbeenabled;

typedef struct _corecommon_setlocalmassdeletedetectedtime{
} corecommon_setlocalmassdeletedetectedtime;

typedef struct _corecommon_setlocalmassdeletedetectionfeaturestate{
} corecommon_setlocalmassdeletedetectionfeaturestate;

typedef struct _corecommon_setpartnerresetneeded{
} corecommon_setpartnerresetneeded;

typedef struct _core_cleanupcore{
} core_cleanupcore;

typedef struct _core_loadusersettingsforbandwidth{
} core_loadusersettingsforbandwidth;

typedef struct _core_coreloop{
} core_coreloop;

typedef struct _core_fireaccountstatuscallback{
} core_fireaccountstatuscallback;

typedef struct _core_firesignincallback{
} core_firesignincallback;

typedef struct _core_getselectivesyncinformation{
} core_getselectivesyncinformation;

typedef struct _core_getselectivesyncinformationfromlocaldatabase{
} core_getselectivesyncinformationfromlocaldatabase;

typedef struct _core_getselectivesyncinformationfromstorageservice{
} core_getselectivesyncinformationfromstorageservice;

typedef struct _core_handlecancelhydration{
} core_handlecancelhydration;

typedef struct _core_handlecoremessage{
} core_handlecoremessage;

typedef struct _core_handlehydratefile{
} core_handlehydratefile;

typedef struct _core_handlescanstate{
} core_handlescanstate;

typedef struct _core_handlevolumechangenotification{
} core_handlevolumechangenotification;

typedef struct _core_handlevolumechangenotificationbaseoneauthmsaluserauthentication_issignedin{
} core_handlevolumechangenotificationbaseoneauthmsaluserauthentication_issignedin;

typedef struct _core_initpaths{
} core_initpaths;

typedef struct _core_initusersettings{
} core_initusersettings;

typedef struct _core_loadassertsettings{
} core_loadassertsettings;

typedef struct _core_loaddrivecontents{
} core_loaddrivecontents;

typedef struct _core_loadglobalsettings{
} core_loadglobalsettings;

typedef struct _core_logoutcurrentuser{
} core_logoutcurrentuser;

typedef struct _core_updatecachedrampsfromclientpolicy{
} core_updatecachedrampsfromclientpolicy;

typedef struct _coreapiutilities_mapsyncengineresulttosyncclientresult{
} coreapiutilities_mapsyncengineresulttosyncclientresult;

typedef struct _corecommon_coauthappprotocolversionstostring{
} corecommon_coauthappprotocolversionstostring;

typedef struct _corecommon_uninitializeplaceholdermanager{
} corecommon_uninitializeplaceholdermanager;

typedef struct _corecommon_logclientsettings{
} corecommon_logclientsettings;

typedef struct _corecommon_writeglobalclientsettingtofile{
} corecommon_writeglobalclientsettingtofile;

typedef struct _deviceid_gethostname{
    int32 unk;
} deviceid_gethostname;

typedef struct _deviceid_getmachineguid{
    int32 unk;
} deviceid_getmachineguid;

typedef struct _deviceid_getuserdomain{
    int32 unk;
} deviceid_getuserdomain;

typedef struct _deviceid_getusernamew{
    int32 unk;
} deviceid_getusernamew;

typedef struct _downloader_comparefilehash{
} downloader_comparefilehash;

typedef struct _downloader_copyfiledatafromstream{
} downloader_copyfiledatafromstream;

typedef struct _downloader_downloadandverifyfile{
} downloader_downloadandverifyfile;

typedef struct _downloader_downloadfile{
} downloader_downloadfile;

typedef struct _downloader_downloadfilewithadditionalheaders{
} downloader_downloadfilewithadditionalheaders;

typedef struct _downloader_downloadorloadfile{
} downloader_downloadorloadfile;

typedef struct _downloader_downloadorloadfilewithadditionalheaders{
} downloader_downloadorloadfilewithadditionalheaders;

typedef struct _downloader_downloadwithoutverifyingfile{
} downloader_downloadwithoutverifyingfile;

typedef struct _downloader_getfileurl{
} downloader_getfileurl;

typedef struct _downloader_hastimeelapsed{
} downloader_hastimeelapsed;

typedef struct _downloader_reporttelemetry{
} downloader_reporttelemetry;

typedef struct _downloader_setfilehash{
} downloader_setfilehash;

typedef struct _downloader_verifyfile{
} downloader_verifyfile;

typedef struct _downloader_operator_{
} downloader_operator_;

typedef struct _drivechange_computerates{
} drivechange_computerates;

typedef struct _drivechange_logfullfileuploadcomplete{
} drivechange_logfullfileuploadcomplete;

typedef struct _drivechange_markdeleted{
} drivechange_markdeleted;

typedef struct _drive_addinitialdrivecontents{
} drive_addinitialdrivecontents;

typedef struct _drive_cleanupmountpoint{
} drive_cleanupmountpoint;

typedef struct _drive_cleanupmountpointsyncroot{
} drive_cleanupmountpointsyncroot;

typedef struct _drive_clearrequestedscan{
} drive_clearrequestedscan;

typedef struct _drive_handrdcwchangestocore{
} drive_handrdcwchangestocore;

typedef struct _drive_preparemountpoint{
} drive_preparemountpoint;

typedef struct _drive_preparemountpointsyncroot{
} drive_preparemountpointsyncroot;

typedef struct _drive_removefile{
} drive_removefile;

typedef struct _drive_removefolder{
} drive_removefolder;

typedef struct _drive_removeunrealizedfile{
} drive_removeunrealizedfile;

typedef struct _drive_requestscan{
} drive_requestscan;

typedef struct _drive_setconnected{
} drive_setconnected;

typedef struct _drive_addpendingchanges{
} drive_addpendingchanges;

typedef struct _drive_deletefilesbyext{
} drive_deletefilesbyext;

typedef struct _drive_detectmovefromdb{
} drive_detectmovefromdb;

typedef struct _drive_getfolderbyrelativepathfromdb{
} drive_getfolderbyrelativepathfromdb;

typedef struct _drive_getfoldercurrentfullpath{
} drive_getfoldercurrentfullpath;

typedef struct _drive_haspathconflict{
} drive_haspathconflict;

typedef struct _drive_initdrivemonitor{
} drive_initdrivemonitor;

typedef struct _drive_isvalidtempdir{
} drive_isvalidtempdir;

typedef struct _drive_sendeventtoui{
} drive_sendeventtoui;

typedef struct _drive_testfolderemptiness{
} drive_testfolderemptiness;

typedef struct _drive_updatefsidforfile{
} drive_updatefsidforfile;

typedef struct _drive_updatefsidforfolder{
} drive_updatefsidforfolder;

typedef struct _drive_updatefsidforfolderbaseoneauthmsaluserauthentication_issignedin{
} drive_updatefsidforfolderbaseoneauthmsaluserauthentication_issignedin;

typedef struct _ecsconfigurationmanager_applycachedexpirationinfo{
} ecsconfigurationmanager_applycachedexpirationinfo;

typedef struct _ecsconfigurationmanager_loadconfigurationfromcache{
} ecsconfigurationmanager_loadconfigurationfromcache;

typedef struct _ecsconfigurationmanager_recordenabledramps{
} ecsconfigurationmanager_recordenabledramps;

typedef struct _ecsconfigurationmanager_sendupdatetelemetry{
} ecsconfigurationmanager_sendupdatetelemetry;

typedef struct _ecsconfigurationmanager_setetag{
} ecsconfigurationmanager_setetag;

typedef struct _ecsconfigurationmanager_setexpires{
} ecsconfigurationmanager_setexpires;

typedef struct _ecsconfigurationparser_parseecsconfiguration{
} ecsconfigurationparser_parseecsconfiguration;

typedef struct _ecsconfigurationparser_parseecsconfigurationbaseoneauthmsaluserauthentication_issignedin{
} ecsconfigurationparser_parseecsconfigurationbaseoneauthmsaluserauthentication_issignedin;

typedef struct _ecsconfigurationupdater_applycontent{
} ecsconfigurationupdater_applycontent;

typedef struct _ecsconfigurationupdater_getadditionalheaders{
} ecsconfigurationupdater_getadditionalheaders;

typedef struct _ecsconfigurationupdater_isecsenabled{
} ecsconfigurationupdater_isecsenabled;

typedef struct _ecsconfigurationupdater_tryupdatesettings{
} ecsconfigurationupdater_tryupdatesettings;

typedef struct _ecsconfigurationupdater_tryupdatesettingswithcachedconfig{
} ecsconfigurationupdater_tryupdatesettingswithcachedconfig;

typedef struct _ecsconfigurationupdater_tryupdatesettingswithnewconfig{
} ecsconfigurationupdater_tryupdatesettingswithnewconfig;

typedef struct _eventaggregator_setconfigurationparameters{
} eventaggregator_setconfigurationparameters;

typedef struct _filedb_close{
} filedb_close;

typedef struct _filedb_getheaderhelper{
} filedb_getheaderhelper;

typedef struct _filedb_getnewdbentrypos{
} filedb_getnewdbentrypos;

typedef struct _filedb_getstreamsize{
} filedb_getstreamsize;

typedef struct _filedb_initialize{
} filedb_initialize;

typedef struct _filedb_load{
} filedb_load;

typedef struct _filedb_loadselectivesyncinformationfromdisk{
} filedb_loadselectivesyncinformationfromdisk;

typedef struct _filedb_logfreediskspace{
} filedb_logfreediskspace;

typedef struct _filedb_recorditem{
} filedb_recorditem;

typedef struct _filedb_removeitem{
} filedb_removeitem;

typedef struct _filedb_sanitycheckfreeslotlist{
} filedb_sanitycheckfreeslotlist;

typedef struct _filescanner_addscopetovaultfolderscache{
} filescanner_addscopetovaultfolderscache;

typedef struct _filescanner_cachelistfrompolicy{
} filescanner_cachelistfrompolicy;

typedef struct _filescanner_checkerrorstatemismatch{
} filescanner_checkerrorstatemismatch;

typedef struct _filescanner_checkhashneededforpotentialfilechange{
} filescanner_checkhashneededforpotentialfilechange;

typedef struct _filescanner_createdrivechangeformodifiedfile{
} filescanner_createdrivechangeformodifiedfile;

typedef struct _filescanner_detectandhandletruncatedfile{
} filescanner_detectandhandletruncatedfile;

typedef struct _filescanner_detectandhandletruncatedfilebaseoneauthmsaluserauthentication_issignedin{
} filescanner_detectandhandletruncatedfilebaseoneauthmsaluserauthentication_issignedin;

typedef struct _filescanner_findfilebynameandrepairfsidcacheifrequired{
} filescanner_findfilebynameandrepairfsidcacheifrequired;

typedef struct _filescanner_getupdatephstate{
} filescanner_getupdatephstate;

typedef struct _filescanner_getupdatephstatebaseoneauthmsaluserauthentication_issignedin{
} filescanner_getupdatephstatebaseoneauthmsaluserauthentication_issignedin;

typedef struct _filescanner_handlescannedfolder{
} filescanner_handlescannedfolder;

typedef struct _filescanner_handlescannedfullfile{
} filescanner_handlescannedfullfile;

typedef struct _filescanner_initializecache{
} filescanner_initializecache;

typedef struct _filescanner_queueupdateexcludedstate{
} filescanner_queueupdateexcludedstate;

typedef struct _filescanner_startscannertelemetry{
} filescanner_startscannertelemetry;

typedef struct _filescanner_stopscannerperfauditor{
} filescanner_stopscannerperfauditor;

typedef struct _filescanner_stopscannerperfauditorforfullscanifapplicable{
} filescanner_stopscannerperfauditorforfullscanifapplicable;

typedef struct _filescanner_validateexcludedorignoredfile{
} filescanner_validateexcludedorignoredfile;

typedef struct _filescanner_dofullscanwork{
} filescanner_dofullscanwork;

typedef struct _filescanner_doprecisescanwork{
} filescanner_doprecisescanwork;

typedef struct _filescanner_finalizescan{
} filescanner_finalizescan;

typedef struct _filescanner_initdrivescan{
} filescanner_initdrivescan;

typedef struct _filescanner_sendpendingchangestoserver{
} filescanner_sendpendingchangestoserver;

typedef struct _filescanner_sweepdrivecontents{
} filescanner_sweepdrivecontents;

typedef struct _filescanner_sweepdrivecontentsbaseoneauthmsaluserauthentication_issignedin{
} filescanner_sweepdrivecontentsbaseoneauthmsaluserauthentication_issignedin;

typedef struct _filesystem_createshortcut{
} filesystem_createshortcut;

typedef struct _filesystem_determinemountpointfilesysteminformation{
} filesystem_determinemountpointfilesysteminformation;

typedef struct _filesystem_filesystemutil{
    int64 unk1;
    int64 unk2;
    int64 unk3;
    int64 unk4;
    int32 unk5;
} filesystem_filesystemutil;

typedef struct _filesystem_getfileinformationinternal{
} filesystem_getfileinformationinternal;

typedef struct _filesystem_getvolumetype{
} filesystem_getvolumetype;

typedef struct _filesystem_onoplocknotificationreceived{
} filesystem_onoplocknotificationreceived;

typedef struct _filesystem_openoplockforread{
} filesystem_openoplockforread;

typedef struct _filesystem_tstat{
} filesystem_tstat;

typedef struct _filesystem_unlink{
} filesystem_unlink;

typedef struct _filesystem_createdirectoryfull{
} filesystem_createdirectoryfull;

typedef struct _filesystem_createfolder{
} filesystem_createfolder;

typedef struct _filesystem_deletefile{
} filesystem_deletefile;

typedef struct _filesystem_deletefolder{
} filesystem_deletefolder;

typedef struct _filesystem_hidefolder{
} filesystem_hidefolder;

typedef struct _filesystem_openfileread{
} filesystem_openfileread;

typedef struct _filesystem_openfilewrite{
} filesystem_openfilewrite;

typedef struct _filesystem_s_addoplock{
} filesystem_s_addoplock;

typedef struct _hasher_allocatehashbufferifneeded{
} hasher_allocatehashbufferifneeded;

typedef struct _instrumentation_telemetryrecordoverallresults{
} instrumentation_telemetryrecordoverallresults;

typedef struct _kfmsilentflowlauncher_getwindowsoobekeyvalue{
} kfmsilentflowlauncher_getwindowsoobekeyvalue;

typedef struct _kfmsilentflowlauncher_wasoobecompletedrecently{
} kfmsilentflowlauncher_wasoobecompletedrecently;

typedef struct _localchange_handlecreatefolderfilesystemoperation{
} localchange_handlecreatefolderfilesystemoperation;

typedef struct _localchange_handlecreatefolderondisk{
} localchange_handlecreatefolderondisk;

typedef struct _localchange_sendprocessresulttelemetry{
} localchange_sendprocessresulttelemetry;

typedef struct _localchanges_disklookup{
} localchanges_disklookup;

typedef struct _localchanges_getfolderrealpathhelper{
} localchanges_getfolderrealpathhelper;

typedef struct _localchanges_readmodtime{
} localchanges_readmodtime;

typedef struct _localchanges_setfilestubonlyandtriggerredownloadorrecreate{
} localchanges_setfilestubonlyandtriggerredownloadorrecreate;

typedef struct _localchanges_updatesyncstates{
} localchanges_updatesyncstates;

typedef struct _localchanges_handlefileifreadonly{
} localchanges_handlefileifreadonly;

typedef struct _loginstatemanager_initialize{
} loginstatemanager_initialize;

typedef struct _loginstatemanager_onnotification{
} loginstatemanager_onnotification;

typedef struct _loginstatemanager_persistuserandexit{
} loginstatemanager_persistuserandexit;

typedef struct _loguploader2_logshouldbeuploaded{
} loguploader2_logshouldbeuploaded;

typedef struct _migrationmanager_arekfmrampsenabled{
} migrationmanager_arekfmrampsenabled;

typedef struct _networkawarenessmanager_loadusersetting{
} networkawarenessmanager_loadusersetting;

typedef struct _operationscheduler_deletetimer{
} operationscheduler_deletetimer;

typedef struct _operationscheduler_scheduleontimer{
} operationscheduler_scheduleontimer;

typedef struct _remoteaccessmanager_setstate{
} remoteaccessmanager_setstate;

typedef struct _resourcemanager_initialize{
} resourcemanager_initialize;

typedef struct _serverconn_connecttoliveid{
} serverconn_connecttoliveid;

typedef struct _serverconn_handlentcsynccomplete{
} serverconn_handlentcsynccomplete;

typedef struct _serverconn_initserverconn{
} serverconn_initserverconn;

typedef struct _serverconn_setupserverconfig{
} serverconn_setupserverconfig;

typedef struct _setupcontroller_deleteupdateerrorcount{
} setupcontroller_deleteupdateerrorcount;

typedef struct _setupcontroller_deleteupdateerrorcountandsendfinalresulttelemetry{
} setupcontroller_deleteupdateerrorcountandsendfinalresulttelemetry;

typedef struct _setupcontroller_deleteupdateerrorcountandsendfinalresulttelemetrybaseoneauthmsaluserauthentication_issignedin{
} setupcontroller_deleteupdateerrorcountandsendfinalresulttelemetrybaseoneauthmsaluserauthentication_issignedin;

typedef struct _setupengine_workitemproc{
} setupengine_workitemproc;

typedef struct _setupengine_workitemprocbaseoneauthmsaluserauthentication_issignedin{
} setupengine_workitemprocbaseoneauthmsaluserauthentication_issignedin;

typedef struct _singleusersetupcontroller_ispermachineworkneeded{
} singleusersetupcontroller_ispermachineworkneeded;

typedef struct _skydriveclient_operator_{
} skydriveclient_operator_;

typedef struct _syncengineclient_finalreleasebaseoneauthmsaluserauthentication_issignedin{
} syncengineclient_finalreleasebaseoneauthmsaluserauthentication_issignedin;

typedef struct _utilities_updaterootfolderenvvariableforunlink{
} utilities_updaterootfolderenvvariableforunlink;

typedef struct _utils_wpndebugtrace{
} utils_wpndebugtrace;

typedef struct _winmain_wwinmain{
} winmain_wwinmain;

typedef struct _winmain_wwinmainbaseoneauthmsaluserauthentication_issignedin{
} winmain_wwinmainbaseoneauthmsaluserauthentication_issignedin;

typedef struct _wnpconn_checkfornetmsgs{
} wnpconn_checkfornetmsgs;

typedef struct _wnpconn_onbufferfull{
} wnpconn_onbufferfull;

typedef struct _wnpnet_asynctransfercallback{
} wnpnet_asynctransfercallback;

typedef struct _wnpnet_asynctransfercallbackbaseoneauthmsaluserauthentication_issignedin{
} wnpnet_asynctransfercallbackbaseoneauthmsaluserauthentication_issignedin;

typedef struct _wnpnet_changestatemachinestate{
} wnpnet_changestatemachinestate;

typedef struct _wnpnet_connect{
} wnpnet_connect;

typedef struct _wnpnet_connectbaseoneauthmsaluserauthentication_issignedin{
} wnpnet_connectbaseoneauthmsaluserauthentication_issignedin;

typedef struct _wnpnet_disconnectinternal{
} wnpnet_disconnectinternal;

typedef struct _wnpnet_dispatchnetmsgqueue{
} wnpnet_dispatchnetmsgqueue;

typedef struct _wnpnet_onnetdisconnected{
} wnpnet_onnetdisconnected;

typedef struct _wnpnet_onpngresponsewaittimer{
} wnpnet_onpngresponsewaittimer;

typedef struct _wnpnet_onserverxfr{
} wnpnet_onserverxfr;

typedef struct _wnputil_error{
} wnputil_error;

typedef struct _basesettingsmanager_setofficeprivacylevelonloggingsession{
} basesettingsmanager_setofficeprivacylevelonloggingsession;

typedef struct _baseuserauthenticationinternal_gettenantidforsporesource{
} baseuserauthenticationinternal_gettenantidforsporesource;

typedef struct _basicclientinfoprovider_isoutstandingrequestvalidandforteamsite{
} basicclientinfoprovider_isoutstandingrequestvalidandforteamsite;

typedef struct _batterystatusmanager_checkbatterysaveron{
} batterystatusmanager_checkbatterysaveron;

typedef struct _browserexternalshare_copytoclipboard{
} browserexternalshare_copytoclipboard;

typedef struct _browserexternalshare_getsharingcontextinformation{
} browserexternalshare_getsharingcontextinformation;

typedef struct _browserexternalshare_ismoreappsenabled{
} browserexternalshare_ismoreappsenabled;

typedef struct _browserexternalshare_onnotification{
} browserexternalshare_onnotification;

typedef struct _browserexternalshare_resize{
} browserexternalshare_resize;

typedef struct _browserexternalshare_sendlinkviamoreapps{
} browserexternalshare_sendlinkviamoreapps;

typedef struct _browserexternalshare_verifyurlisallowed{
} browserexternalshare_verifyurlisallowed;

typedef struct _browserview_setsuppressdialogs{
} browserview_setsuppressdialogs;

typedef struct _cachemanager_getfolderentriesfromnotification{
} cachemanager_getfolderentriesfromnotification;

typedef struct _changefolder_loginfo{
} changefolder_loginfo;

typedef struct _chooserootfoldermodel_getinitialchoosefolderstate{
} chooserootfoldermodel_getinitialchoosefolderstate;

typedef struct _chooserootfoldermodel_onpathvalidationdone{
} chooserootfoldermodel_onpathvalidationdone;

typedef struct _chooserootfoldermodel_operator_{
} chooserootfoldermodel_operator_;

typedef struct _clientconfigurationtelemetryoperation_sendofficecredentialtelemetry{
} clientconfigurationtelemetryoperation_sendofficecredentialtelemetry;

typedef struct _clientitem_setmounted{
} clientitem_setmounted;

typedef struct _clientitem_transitionfromunrealizedfile{
} clientitem_transitionfromunrealizedfile;

typedef struct _clientpolicysettings_refreshifneeded{
} clientpolicysettings_refreshifneeded;

typedef struct _clientpolicystate_deletepersistedpolicy{
} clientpolicystate_deletepersistedpolicy;

typedef struct _clientpolicystate_getdefaultshareurltemplatevalue{
} clientpolicystate_getdefaultshareurltemplatevalue;

typedef struct _clientsetupmanager_iselevatedupdaterequired{
} clientsetupmanager_iselevatedupdaterequired;

typedef struct _clientstructs_recordocsiapitelemetry{
} clientstructs_recordocsiapitelemetry;

typedef struct _coauthitempropertyhandler_getpropertiesfromclientfolder{
} coauthitempropertyhandler_getpropertiesfromclientfolder;

typedef struct _coauthitempropertyhandler_populateitempropertiesforpath{
} coauthitempropertyhandler_populateitempropertiesforpath;

typedef struct _coauthitempropertyhandler_populateitempropertiesforresourceid{
} coauthitempropertyhandler_populateitempropertiesforresourceid;

typedef struct _coauthitempropertyhandler_recordocsiapitelemetry{
} coauthitempropertyhandler_recordocsiapitelemetry;

typedef struct _coauthitempropertyhandler_setitemproperties{
} coauthitempropertyhandler_setitemproperties;

typedef struct _coauthitempropertyhandler_setitempropertiesforclientfile{
} coauthitempropertyhandler_setitempropertiesforclientfile;

typedef struct _coauthitempropertyhandler_setitempropertiesforunrealizedfile{
} coauthitempropertyhandler_setitempropertiesforunrealizedfile;

typedef struct _coauthitempropertyhandler_setsize{
} coauthitempropertyhandler_setsize;

typedef struct _coauthitempropertyhandler_trysetvalidlocalocsimovedestinationflag{
} coauthitempropertyhandler_trysetvalidlocalocsimovedestinationflag;

typedef struct _coauthitempropertyhandler_updateknownocsiclientsifneeded{
} coauthitempropertyhandler_updateknownocsiclientsifneeded;

typedef struct _coauthsupportutils_generatecoauthextendedversioninfo{
} coauthsupportutils_generatecoauthextendedversioninfo;

typedef struct _coauthsupportutils_splitandstoreappversion{
} coauthsupportutils_splitandstoreappversion;

typedef struct _consumerprivacysettingsmanager_markprivacydisclosureseen{
} consumerprivacysettingsmanager_markprivacydisclosureseen;

typedef struct _core_handleaddmountedfolderrequest{
} core_handleaddmountedfolderrequest;

typedef struct _core_performquotacheckifneeded{
} core_performquotacheckifneeded;

typedef struct _core_uploadsyncenginestateduringactivehydrationtimeouttotelemetry{
} core_uploadsyncenginestateduringactivehydrationtimeouttotelemetry;

typedef struct _coreapi_beginaddmountedfolder{
} coreapi_beginaddmountedfolder;

typedef struct _coreapi_beginremovemountedfolder{
} coreapi_beginremovemountedfolder;

typedef struct _coreapi_getlocalmassdeletefeaturestate{
} coreapi_getlocalmassdeletefeaturestate;

typedef struct _coreapi_signout{
} coreapi_signout;

typedef struct _corecommon_disableofficeintegrationifneeded{
} corecommon_disableofficeintegrationifneeded;

typedef struct _createfile_addfileifexists{
} createfile_addfileifexists;

typedef struct _createfile_operator_{
} createfile_operator_;

typedef struct _createfile_process{
} createfile_process;

typedef struct _createfile_processmatchingunrealizedfile{
} createfile_processmatchingunrealizedfile;

typedef struct _createfile_shoulddelete0bytepreseedfile{
} createfile_shoulddelete0bytepreseedfile;

typedef struct _createfolder_process{
} createfolder_process;

typedef struct _crossscopemovedetectorlegacy_findcrossscopemovesinchildren{
} crossscopemovedetectorlegacy_findcrossscopemovesinchildren;

typedef struct _cwinhttp_checkforrequesttimeout{
} cwinhttp_checkforrequesttimeout;

typedef struct _cwinhttp_createrequestwithbuffersize{
} cwinhttp_createrequestwithbuffersize;

typedef struct _dehydratefile_loginfo{
} dehydratefile_loginfo;

typedef struct _dehydratefile_process{
} dehydratefile_process;

typedef struct _dehydratefile_recordtelemetry{
} dehydratefile_recordtelemetry;

typedef struct _deltaproviderfactory_createorvalidatedeltaproviderfordownload{
} deltaproviderfactory_createorvalidatedeltaproviderfordownload;

typedef struct _deltaproviderfactory_createorvalidatedeltaproviderifmatchingrulefound{
} deltaproviderfactory_createorvalidatedeltaproviderifmatchingrulefound;

typedef struct _deltaproviderfactory_instantiatedeltaprovider{
} deltaproviderfactory_instantiatedeltaprovider;

typedef struct _desktophost_sendwebrequesttoinstance{
} desktophost_sendwebrequesttoinstance;

typedef struct _desktophost_startallinstancesexceptcurrentinstance{
} desktophost_startallinstancesexceptcurrentinstance;

typedef struct _desktophost_startinstance{
} desktophost_startinstance;

typedef struct _desktophost_startinstances{
} desktophost_startinstances;

typedef struct _diagnostics_uploadassertinfo{
} diagnostics_uploadassertinfo;

typedef struct _drive_beginresync{
} drive_beginresync;

typedef struct _drive_markscopeasresynccompleted{
} drive_markscopeasresynccompleted;

typedef struct _drive_processdeleteditemsfromdifferentialresync{
} drive_processdeleteditemsfromdifferentialresync;

typedef struct _drive_resynccomplete{
} drive_resynccomplete;

typedef struct _drive_schedulescan{
} drive_schedulescan;

typedef struct _drive_unregisterscopesyncroot{
} drive_unregisterscopesyncroot;

typedef struct _drivechangeinterpreter_filtermatchingdrivechanges{
} drivechangeinterpreter_filtermatchingdrivechanges;

typedef struct _drivechangeinterpreter_filteroutchangeswhichareexpectedtofail{
} drivechangeinterpreter_filteroutchangeswhichareexpectedtofail;

typedef struct _drivechangeinterpreter_handledeferredfilemoves{
} drivechangeinterpreter_handledeferredfilemoves;

typedef struct _drivechangeinterpreter_handledeferredfoldermoves{
} drivechangeinterpreter_handledeferredfoldermoves;

typedef struct _drivechangeinterpreter_handlehardlinks{
} drivechangeinterpreter_handlehardlinks;

typedef struct _drivechangeinterpreter_reportdeletetelemetry{
} drivechangeinterpreter_reportdeletetelemetry;

typedef struct _drivechangeinterpreter_updatemountedrootscopestodeletesmap{
} drivechangeinterpreter_updatemountedrootscopestodeletesmap;

typedef struct _drivechangeinterpreter_validateplaceholderdeletes{
} drivechangeinterpreter_validateplaceholderdeletes;

typedef struct _driveinfobusiness_completependingonenotefixups{
} driveinfobusiness_completependingonenotefixups;

typedef struct _driveinfobusiness_loadsyncscopes{
} driveinfobusiness_loadsyncscopes;

typedef struct _driveinfobusiness_setlocalmaxpathvalue{
} driveinfobusiness_setlocalmaxpathvalue;

typedef struct _driveinfobusiness_setupmountedfolderroot{
} driveinfobusiness_setupmountedfolderroot;

typedef struct _driveinfobusiness_unmountsyncscope{
} driveinfobusiness_unmountsyncscope;

typedef struct _driveinfobusiness_updatesyncengineproviderregistration{
} driveinfobusiness_updatesyncengineproviderregistration;

typedef struct _emailhrdcontroller_handleemailhrdresultwithpage{
} emailhrdcontroller_handleemailhrdresultwithpage;

typedef struct _enclosuredownloader_initializedeltaprovider{
} enclosuredownloader_initializedeltaprovider;

typedef struct _enclosuredownloader_isdownloadstillvalid{
} enclosuredownloader_isdownloadstillvalid;

typedef struct _enclosureuploader_blockuploadcompleted{
} enclosureuploader_blockuploadcompleted;

typedef struct _enclosureuploader_calculateuploadrates{
} enclosureuploader_calculateuploadrates;

typedef struct _enclosureuploader_setrescanonfailedserverresponseifnecessary{
} enclosureuploader_setrescanonfailedserverresponseifnecessary;

typedef struct _enclosureuploader_startnextblockupload{
} enclosureuploader_startnextblockupload;

typedef struct _enclosureuploader_writesessionidtodc{
} enclosureuploader_writesessionidtodc;

typedef struct _filedb_changescopeheaderhelper{
} filedb_changescopeheaderhelper;

typedef struct _filedb_shrink{
} filedb_shrink;

typedef struct _fileneededeventlistener_notifyfileneeded{
} fileneededeventlistener_notifyfileneeded;

typedef struct _filescanner_detectduplicateitembyfsidinternal{
} filescanner_detectduplicateitembyfsidinternal;

typedef struct _filescanner_handlefullfilepathonscanforpossibleofficetempfiles{
} filescanner_handlefullfilepathonscanforpossibleofficetempfiles;

typedef struct _filescanner_handlescannedplaceholderfile{
} filescanner_handlescannedplaceholderfile;

typedef struct _filescanner_isfullscanneeded{
} filescanner_isfullscanneeded;

typedef struct _filescanner_queueupdatephstatedc{
} filescanner_queueupdatephstatedc;

typedef struct _filestatusnotifier_clearitemwarning{
} filestatusnotifier_clearitemwarning;

typedef struct _filesystem_getdisksize{
} filesystem_getdisksize;

typedef struct _filesystem_getfileforreadaccesswithoplocksemantics{
} filesystem_getfileforreadaccesswithoplocksemantics;

typedef struct _filesystem_gethardlinksatpath{
} filesystem_gethardlinksatpath;

typedef struct _filesystem_openfilereadwithcoauthsharingmodes{
} filesystem_openfilereadwithcoauthsharingmodes;

typedef struct _filesystem_pathisfolder{
} filesystem_pathisfolder;

typedef struct _filetransfercoordinator_activehydrationfailed{
} filetransfercoordinator_activehydrationfailed;

typedef struct _filetransfercoordinator_filefetchfailed{
} filetransfercoordinator_filefetchfailed;

typedef struct _filetransfercoordinator_filefetchneeded{
} filetransfercoordinator_filefetchneeded;

typedef struct _filetransfercoordinator_getdownloadstatus{
} filetransfercoordinator_getdownloadstatus;

typedef struct _filetransfercoordinator_retrydownloads{
} filetransfercoordinator_retrydownloads;

typedef struct _firstrunwizardoperations_sendexperimenttelemetry{
} firstrunwizardoperations_sendexperimenttelemetry;

typedef struct _fixupdrivechanges_handlefaileddrivechangeex{
} fixupdrivechanges_handlefaileddrivechangeex;

typedef struct _floodgateprovider_startfloodgate{
} floodgateprovider_startfloodgate;

typedef struct _fspaths_appenddirdivider_logged{
} fspaths_appenddirdivider_logged;

typedef struct _fspaths_hasdirdivider_logged{
} fspaths_hasdirdivider_logged;

typedef struct _genericstartupsocket_handleerror{
} genericstartupsocket_handleerror;

typedef struct _genericstartupsocket_handleondisconnected{
} genericstartupsocket_handleondisconnected;

typedef struct _hasher_dohashwork{
} hasher_dohashwork;

typedef struct _healing_executehealingactions{
} healing_executehealingactions;

typedef struct _healing_performloggingforeachhealingitem{
} healing_performloggingforeachhealingitem;

typedef struct _healingpersister_detokenizehealingstring{
} healingpersister_detokenizehealingstring;

typedef struct _importcontroller_setsyncinfo{
} importcontroller_setsyncinfo;

typedef struct _itemstatusmanager_removeunusedentries{
} itemstatusmanager_removeunusedentries;

typedef struct _itemstatusmanager_removewarnings{
} itemstatusmanager_removewarnings;

typedef struct _kfmlockedfilemessagesource_getmessagedata{
} kfmlockedfilemessagesource_getmessagedata;

typedef struct _kfmscancontroller_onpagefinished{
} kfmscancontroller_onpagefinished;

typedef struct _localchange_dowork{
} localchange_dowork;

typedef struct _localchanges_startlocalchangehash{
} localchanges_startlocalchangehash;

typedef struct _localchanges_transitionfile{
} localchanges_transitionfile;

typedef struct _localchanges_transitionfolder{
} localchanges_transitionfolder;

typedef struct _loggingapi_loggingrecordassert{
} loggingapi_loggingrecordassert;

typedef struct _loginstatemanager_attemptsilentsignin{
} loginstatemanager_attemptsilentsignin;

typedef struct _loginstatemanager_beginusersignout{
} loginstatemanager_beginusersignout;

typedef struct _loginstatemanager_handlesilentsigninretryfailure{
} loginstatemanager_handlesilentsigninretryfailure;

typedef struct _loginstatemanager_oncoreapisignedout{
} loginstatemanager_oncoreapisignedout;

typedef struct _loginstatemanager_recordsignouttelemetry{
} loginstatemanager_recordsignouttelemetry;

typedef struct _migrationscan_folderredirectioncheck{
} migrationscan_folderredirectioncheck;

typedef struct _mountedfoldercallbackhandler_endaddmountedfolder{
} mountedfoldercallbackhandler_endaddmountedfolder;

typedef struct _mountedfoldercallbackhandler_endremovemountedfolder{
} mountedfoldercallbackhandler_endremovemountedfolder;

typedef struct _mountfolder_process{
} mountfolder_process;

typedef struct _movefile_updateplaceholderstate{
} movefile_updateplaceholderstate;

typedef struct _movewindowmodel_canshowmigrationpage{
} movewindowmodel_canshowmigrationpage;

typedef struct _notificationserviceimpl_ondisconnected{
} notificationserviceimpl_ondisconnected;

typedef struct _oauth_authenticatetoservice{
} oauth_authenticatetoservice;

typedef struct _oauthaad_authenticatetoservice{
} oauthaad_authenticatetoservice;

typedef struct _oauthaad_clearcredentials{
} oauthaad_clearcredentials;

typedef struct _oauthaadcredentialacquirer_getcredentialfromcache{
} oauthaadcredentialacquirer_getcredentialfromcache;

typedef struct _oauthaadcredentialacquirer_getcredentialswithauthcode{
} oauthaadcredentialacquirer_getcredentialswithauthcode;

typedef struct _oauthaadcredentialacquirer_loadcredential{
} oauthaadcredentialacquirer_loadcredential;

typedef struct _oauthaadcredentialacquirer_refreshcredential{
} oauthaadcredentialacquirer_refreshcredential;

typedef struct _oauthaadcredentialacquirer_retrievecredential{
} oauthaadcredentialacquirer_retrievecredential;

typedef struct _oauthaadcredentialacquirer_storecredential{
} oauthaadcredentialacquirer_storecredential;

typedef struct _oauthcredentialacquirer_parserefreshresponse{
} oauthcredentialacquirer_parserefreshresponse;

typedef struct _onermcommon_getaadauthtokenforheader{
} onermcommon_getaadauthtokenforheader;

typedef struct _onermcommon_getauthtokenforheader{
} onermcommon_getauthtokenforheader;

typedef struct _onermparser_isvalidonermdata{
} onermparser_isvalidonermdata;

typedef struct _onermparser_isvalidonermdataforacm{
} onermparser_isvalidonermdataforacm;

typedef struct _onermparser_isvalidonermdatafortoast{
} onermparser_isvalidonermdatafortoast;

typedef struct _onermprovider_sendonermtelemetry{
} onermprovider_sendonermtelemetry;

typedef struct _onermtelemetryrequest_onrequestcomplete{
} onermtelemetryrequest_onrequestcomplete;

typedef struct _onermtelemetryrequest_sendonermtelemetryrequest{
} onermtelemetryrequest_sendonermtelemetryrequest;

typedef struct _ooberequesthandler_getscanresults{
} ooberequesthandler_getscanresults;

typedef struct _ooberequesthandler_isdevicekfmeligibleinternal{
} ooberequesthandler_isdevicekfmeligibleinternal;

typedef struct _ooberequesthandler_setonedrivekfmoptin{
} ooberequesthandler_setonedrivekfmoptin;

typedef struct _oobescanwrapper_onscancomplete{
} oobescanwrapper_onscancomplete;

typedef struct _oobescanwrapper_startscan{
} oobescanwrapper_startscan;

typedef struct _orderedchangesex_filteroutchangeifitshouldbeskipped{
} orderedchangesex_filteroutchangeifitshouldbeskipped;

typedef struct _periodicretrylist_tryremovefromperiodicretrylist{
} periodicretrylist_tryremovefromperiodicretrylist;

typedef struct _postponedchanges_postponechange{
} postponedchanges_postponechange;

typedef struct _postponedchanges_postponedretrycomplete{
} postponedchanges_postponedretrycomplete;

typedef struct _postponedchanges_retrypostponedchanges{
} postponedchanges_retrypostponedchanges;

typedef struct _postponedchanges_setpostponedstatus{
} postponedchanges_setpostponedstatus;

typedef struct _protocolhandlermanager_executewebbasedrequest{
} protocolhandlermanager_executewebbasedrequest;

typedef struct _protocolhandlermanager_executewebrequestsignedinforsyncorlaunchcommand{
} protocolhandlermanager_executewebrequestsignedinforsyncorlaunchcommand;

typedef struct _protocolhandlermanager_startwebbasedrequest{
} protocolhandlermanager_startwebbasedrequest;

typedef struct _proxyordirectsocket_handleerror{
} proxyordirectsocket_handleerror;

typedef struct _proxyordirectsocket_ondisconnected{
} proxyordirectsocket_ondisconnected;

typedef struct _proxyordirectsocket_ontimerfired{
} proxyordirectsocket_ontimerfired;

typedef struct _realizerhash_process{
} realizerhash_process;

typedef struct _removelib_process{
} removelib_process;

typedef struct _replacefile_comparediskfileagainstdb{
} replacefile_comparediskfileagainstdb;

typedef struct _replacefile_doreplacefile{
} replacefile_doreplacefile;

typedef struct _replacefile_processinternal{
} replacefile_processinternal;

typedef struct _scenariotracking_applyscenarioimplicitparameters{
} scenariotracking_applyscenarioimplicitparameters;

typedef struct _scenariotracking_markscenarioreported{
} scenariotracking_markscenarioreported;

typedef struct _scopeinfo_stopsyncactivity{
} scopeinfo_stopsyncactivity;

typedef struct _selectsyncfolderspage_loadbuystoragelink{
} selectsyncfolderspage_loadbuystoragelink;

typedef struct _selectsyncfolderspage_loadquotainfo{
} selectsyncfolderspage_loadquotainfo;

typedef struct _selectsyncfolderspage_updateteamsitelist{
} selectsyncfolderspage_updateteamsitelist;

typedef struct _serverconn_handleloginstatemachine{
} serverconn_handleloginstatemachine;

typedef struct _sessionmanager_endsession{
} sessionmanager_endsession;

typedef struct _sessionmanager_iscurrentsession{
} sessionmanager_iscurrentsession;

typedef struct _settingsdialogview_launch{
} settingsdialogview_launch;

typedef struct _settingsdialogviewmodel_areplaceholderssupported{
} settingsdialogviewmodel_areplaceholderssupported;

typedef struct _settingsdialogviewmodel_getautopausesettings{
} settingsdialogviewmodel_getautopausesettings;

typedef struct _settingsdialogviewmodel_getlocalmassdeletedetectionstate{
} settingsdialogviewmodel_getlocalmassdeletedetectionstate;

typedef struct _settingsdialogviewmodel_loadofficesettingsvalues{
} settingsdialogviewmodel_loadofficesettingsvalues;

typedef struct _settingsdialogviewmodel_loadsettingsvalues{
} settingsdialogviewmodel_loadsettingsvalues;

typedef struct _settingsfilemanager_savedrivesettingsbusiness{
} settingsfilemanager_savedrivesettingsbusiness;

typedef struct _setupengine_handleinstallationdowngrade{
} setupengine_handleinstallationdowngrade;

typedef struct _sharingstatusmismatchresolver_resolvesharingstatusmismatches{
} sharingstatusmismatchresolver_resolvesharingstatusmismatches;

typedef struct _shellsyncstateverifier_getfolderindexingcompletionstate{
} shellsyncstateverifier_getfolderindexingcompletionstate;

typedef struct _signinbrowsernavigator_ondocumentcomplete{
} signinbrowsernavigator_ondocumentcomplete;

typedef struct _signinbrowsernavigator_onnavigatecomplete{
    int32 size;
    char data[size];
} signinbrowsernavigator_onnavigatecomplete;

typedef struct _skydriveclient_invokecommandhelper{
} skydriveclient_invokecommandhelper;

typedef struct _spoclientpolicy_download{
} spoclientpolicy_download;

typedef struct _standardbrowsernavigator_navigatetopage{
} standardbrowsernavigator_navigatetopage;

typedef struct _standardbrowsernavigator_onauthenticationfinished{
} standardbrowsernavigator_onauthenticationfinished;

typedef struct _standardbrowsernavigator_operator_{
} standardbrowsernavigator_operator_;

typedef struct _standardbrowsernavigator_recordnavigationtelemetry{
} standardbrowsernavigator_recordnavigationtelemetry;

typedef struct _storageproviderhandlerproxy_setdirtyonfailure{
} storageproviderhandlerproxy_setdirtyonfailure;

typedef struct _storageproviderpropertyhandler_endsetitempropertiesex{
} storageproviderpropertyhandler_endsetitempropertiesex;

typedef struct _storageproviderpropertyhandler_saveproperties{
} storageproviderpropertyhandler_saveproperties;

typedef struct _storageproviderpropertyhandler_setstorageproviderfilelastchangetime{
} storageproviderpropertyhandler_setstorageproviderfilelastchangetime;

typedef struct _storageproviderpropertyhandler_setstorageproviderfilesize{
} storageproviderpropertyhandler_setstorageproviderfilesize;

typedef struct _storagerequest_onheadersavailable{
} storagerequest_onheadersavailable;

typedef struct _storageserviceapi_getclientpolicy{
} storageserviceapi_getclientpolicy;

typedef struct _storageserviceapi_getdownloadlink{
} storageserviceapi_getdownloadlink;

typedef struct _storageserviceapi_openuploadsession{
} storageserviceapi_openuploadsession;

typedef struct _storageserviceapi_processresponsecommon{
} storageserviceapi_processresponsecommon;

typedef struct _streamsocket_onerror{
} streamsocket_onerror;

typedef struct _streamsocket_oneventfired{
} streamsocket_oneventfired;

typedef struct _syncactivitytracker_stopinitialsync{
} syncactivitytracker_stopinitialsync;

typedef struct _syncactivitytracker_stopstartupsync{
} syncactivitytracker_stopstartupsync;

typedef struct _syncengineclient_beginismappingvalid{
} syncengineclient_beginismappingvalid;

typedef struct _syncengineclient_beginlogout{
} syncengineclient_beginlogout;

typedef struct _syncengineclient_beginsetitempropertiesex{
} syncengineclient_beginsetitempropertiesex;

typedef struct _syncengineclient_getholdfilestatus{
} syncengineclient_getholdfilestatus;

typedef struct _syncengineclient_getlocalmassdeletefeaturestate{
} syncengineclient_getlocalmassdeletefeaturestate;

typedef struct _syncengineclient_onaddmountedfolder{
} syncengineclient_onaddmountedfolder;

typedef struct _syncengineclient_onismappingvalid{
} syncengineclient_onismappingvalid;

typedef struct _syncengineclient_onremovemountedfolder{
} syncengineclient_onremovemountedfolder;

typedef struct _syncengineclient_onsetitemproperties{
} syncengineclient_onsetitemproperties;

typedef struct _synchelpers_finalizefailedtransfer{
} synchelpers_finalizefailedtransfer;

typedef struct _synchelpers_generateskydriveurlfrompathwithscope{
} synchelpers_generateskydriveurlfrompathwithscope;

typedef struct _synchelpers_queryvaluefromexecutablepath{
} synchelpers_queryvaluefromexecutablepath;

typedef struct _synchelpers_recordchangeenumerationwithfiltereditemstats{
} synchelpers_recordchangeenumerationwithfiltereditemstats;

typedef struct _synchelpers_recordfilesyncerror{
} synchelpers_recordfilesyncerror;

typedef struct _synchelpers_recordrootpermissions{
} synchelpers_recordrootpermissions;

typedef struct _synchelpers_schedulestubonlyfilerealization{
} synchelpers_schedulestubonlyfilerealization;

typedef struct _syncperftrack_checkscenariosucceeded{
} syncperftrack_checkscenariosucceeded;

typedef struct _syncserviceproxy_checkscopesforpendingdifferentialresync{
} syncserviceproxy_checkscopesforpendingdifferentialresync;

typedef struct _syncserviceproxy_createchangefolderrealizerworkitem{
} syncserviceproxy_createchangefolderrealizerworkitem;

typedef struct _syncserviceproxy_createdeletefilerealizerworkitem{
} syncserviceproxy_createdeletefilerealizerworkitem;

typedef struct _syncserviceproxy_createmovefilerealizerworkitem{
} syncserviceproxy_createmovefilerealizerworkitem;

typedef struct _syncserviceproxy_createmovefolderrealizerworkitem{
} syncserviceproxy_createmovefolderrealizerworkitem;

typedef struct _syncserviceproxy_firesignincallbackifallscopesinitialized{
} syncserviceproxy_firesignincallbackifallscopesinitialized;

typedef struct _syncserviceproxy_handleuploadbatchnonsuccesshttpstatus{
} syncserviceproxy_handleuploadbatchnonsuccesshttpstatus;

typedef struct _syncserviceproxy_operator_{
} syncserviceproxy_operator_;

typedef struct _syncserviceproxy_prepareforconnectall{
} syncserviceproxy_prepareforconnectall;

typedef struct _syncserviceproxy_processdownloadedfileentry{
} syncserviceproxy_processdownloadedfileentry;

typedef struct _syncserviceproxy_processdownloadedfolderentry{
} syncserviceproxy_processdownloadedfolderentry;

typedef struct _syncserviceproxy_resync{
} syncserviceproxy_resync;

typedef struct _syncserviceproxy_updatefilemetadataworkitem{
} syncserviceproxy_updatefilemetadataworkitem;

typedef struct _syncserviceproxy_updatefoldermetadataworkitem{
} syncserviceproxy_updatefoldermetadataworkitem;

typedef struct _synctelemetry_clearexpiredasserts{
} synctelemetry_clearexpiredasserts;

typedef struct _synctelemetry_recordstartresynctelemetry{
} synctelemetry_recordstartresynctelemetry;

typedef struct _synctelemetry_reportcompleteresynctelemetry{
} synctelemetry_reportcompleteresynctelemetry;

typedef struct _synctelemetry_updateassertinfo{
} synctelemetry_updateassertinfo;

typedef struct _syncverification_addsyncproblemwithdetailsandupdatehealingitems{
} syncverification_addsyncproblemwithdetailsandupdatehealingitems;

typedef struct _syncverification_comparecloudtofilesystem{
} syncverification_comparecloudtofilesystem;

typedef struct _syncverification_comparedattofilesystem{
} syncverification_comparedattofilesystem;

typedef struct _systray_loadballoontip{
} systray_loadballoontip;

typedef struct _takeovergroovesyncoperation_finishtakeoveroperation{
} takeovergroovesyncoperation_finishtakeoveroperation;

typedef struct _throttledtransfers_clearthrottleditemwarning{
} throttledtransfers_clearthrottleditemwarning;

typedef struct _throttledtransfers_getthrottledscopeinfo{
} throttledtransfers_getthrottledscopeinfo;

typedef struct _throttledtransfers_removethrottledinfoforresourceid{
} throttledtransfers_removethrottledinfoforresourceid;

typedef struct _throttledtransfers_setthrottleditemwarning{
} throttledtransfers_setthrottleditemwarning;

typedef struct _thumbnailrequestlimiter_isvalidservicerequestrate{
} thumbnailrequestlimiter_isvalidservicerequestrate;

typedef struct _tlssocket_beginsend{
} tlssocket_beginsend;

typedef struct _toastmessageconfigurationsforerrors_firetoastnotificationforteamsitepermissionserrortype{
} toastmessageconfigurationsforerrors_firetoastnotificationforteamsitepermissionserrortype;

typedef struct _tutorialpage_navigateforward{
} tutorialpage_navigateforward;

typedef struct _tutorialpagemodel_openfolder{
} tutorialpagemodel_openfolder;

typedef struct _updatephstate_loginfo{
} updatephstate_loginfo;

typedef struct _updatephstate_process{
} updatephstate_process;

typedef struct _uploadgate_fixuprelativepathifnecessary{
} uploadgate_fixuprelativepathifnecessary;

typedef struct _uploadgate_removeuploads{
} uploadgate_removeuploads;

typedef struct _user_forcesignin{
} user_forcesignin;

typedef struct _utilities_migrateregistrytree{
} utilities_migrateregistrytree;

typedef struct _utilities_qosuiaction{
} utilities_qosuiaction;

typedef struct _vaultmanager_shouldintroducevault{
} vaultmanager_shouldintroducevault;

typedef struct _versionwindow_onclicktryagain{
} versionwindow_onclicktryagain;

typedef struct _versionwindow_onclosing{
} versionwindow_onclosing;

typedef struct _versionwindow_show{
} versionwindow_show;

typedef struct _versionwindowcontroller_operator_{
} versionwindowcontroller_operator_;

typedef struct _versionwindowcontroller_webquerycallback{
} versionwindowcontroller_webquerycallback;

typedef struct _watcher_removeandreleasewatchermountpoint{
} watcher_removeandreleasewatchermountpoint;

typedef struct _watcher_stoptrackingchangeid{
} watcher_stoptrackingchangeid;

typedef struct _webrequest_addauthheader{
} webrequest_addauthheader;

typedef struct _webrequest_getvroomroot{
} webrequest_getvroomroot;

typedef struct _winboxfiltercommunicationsport_placeholderrestartdatatransfer{
} winboxfiltercommunicationsport_placeholderrestartdatatransfer;

typedef struct _winboxplaceholderutil_dehydrateplaceholder{
} winboxplaceholderutil_dehydrateplaceholder;

typedef struct _winboxplaceholderutil_getshellitemforpathandupdateshellitemsmapifneeded{
} winboxplaceholderutil_getshellitemforpathandupdateshellitemsmapifneeded;

typedef struct _winboxsyncrootmanager_unregistersyncroot{
} winboxsyncrootmanager_unregistersyncroot;

typedef struct _windowmanager_calculatewindowposition{
} windowmanager_calculatewindowposition;

typedef struct _windowmanager_oncopydata{
} windowmanager_oncopydata;

typedef struct _windowmanager_registermodelessdialog{
} windowmanager_registermodelessdialog;

typedef struct _windowmanager_setactivemodelessdialog{
} windowmanager_setactivemodelessdialog;

typedef struct _windowmanager_setmodaldialogvisible{
} windowmanager_setmodaldialogvisible;

typedef struct _windowmanager_unregistermodelessdialog{
} windowmanager_unregistermodelessdialog;

typedef struct _winutils_getqscreenfromwindowscoordinate{
} winutils_getqscreenfromwindowscoordinate;

typedef struct _winutils_monitorcallback{
} winutils_monitorcallback;

typedef struct _wizardproxy_beginvalidatepathwithsyncengine{
} wizardproxy_beginvalidatepathwithsyncengine;

typedef struct _wizardproxy_onaddmountedfolderdone{
} wizardproxy_onaddmountedfolderdone;

typedef struct _wizardproxy_onismappingvalidresult{
} wizardproxy_onismappingvalidresult;

typedef struct _wizardwindow_setspinningtext{
} wizardwindow_setspinningtext;

typedef struct _wnpconnmanager_onreceivecomplete{
} wnpconnmanager_onreceivecomplete;

typedef struct _activitycenterview_showwindow{
} activitycenterview_showwindow;

typedef struct _activitycenterfootermodel_haspremiumupsell{
} activitycenterfootermodel_haspremiumupsell;

typedef struct _activitycenterheadermodel_checkusingactivitycenter2enabled{
} activitycenterheadermodel_checkusingactivitycenter2enabled;

typedef struct _activitycenterheadermodel_updateerrordisplay{
} activitycenterheadermodel_updateerrordisplay;

typedef struct _addtoonedrivemessagesource_getmessagedata{
} addtoonedrivemessagesource_getmessagedata;

typedef struct _awarenessexperimentmanager_getmessagedata{
} awarenessexperimentmanager_getmessagedata;

typedef struct _baseoneauthmsaluserauthentication_findoneauthaccountbyid{
} baseoneauthmsaluserauthentication_findoneauthaccountbyid;

typedef struct _basicclientinfoprovider_getdeviceid{
} basicclientinfoprovider_getdeviceid;

typedef struct _batterystatusmanager_isbatterysaveron{
} batterystatusmanager_isbatterysaveron;

typedef struct _convertonenote_addshortcuttodrive{
} convertonenote_addshortcuttodrive;

typedef struct _convertonenote_converttoanotherlctype{
} convertonenote_converttoanotherlctype;

typedef struct _convertonenote_createshortcutandaddtodrive{
} convertonenote_createshortcutandaddtodrive;

typedef struct _convertonenote_hasconversionbeenperformed{
} convertonenote_hasconversionbeenperformed;

typedef struct _convertonenote_loginfo{
} convertonenote_loginfo;

typedef struct _convertonenote_process{
} convertonenote_process;

typedef struct _convertonenote_recordconversioncompletetelemetry{
} convertonenote_recordconversioncompletetelemetry;

typedef struct _convertonenote_removeonenotefilesfromdiskanddb{
} convertonenote_removeonenotefilesfromdiskanddb;

typedef struct _convertonenote_removeonenotefoldersfromdiskanddb{
} convertonenote_removeonenotefoldersfromdiskanddb;

typedef struct _convertonenote_removeonenotehierarchyfromdiskanddb{
} convertonenote_removeonenotehierarchyfromdiskanddb;

typedef struct _core_performchangeenumerationifneeded{
} core_performchangeenumerationifneeded;

typedef struct _coreapieventhandler_handlegetlinkcallback{
} coreapieventhandler_handlegetlinkcallback;

typedef struct _corestatemachine_handlewaitingforserverstate{
} corestatemachine_handlewaitingforserverstate;

typedef struct _dataintegrity_logdebugsummary{
} dataintegrity_logdebugsummary;

typedef struct _dataintegrity_reportandclearissues{
} dataintegrity_reportandclearissues;

typedef struct _dbconnection_updateschemaifrequired{
} dbconnection_updateschemaifrequired;

typedef struct _dbresultset_movenext{
} dbresultset_movenext;

typedef struct _dciutils_setexcludedstateonunsyncedfileifnecessary{
} dciutils_setexcludedstateonunsyncedfileifnecessary;

typedef struct _deviceid_getcollectionstringvalue{
} deviceid_getcollectionstringvalue;

typedef struct _deviceid_reportpreferredcase{
} deviceid_reportpreferredcase;

typedef struct _deviceid_updatecachedrampvalue{
} deviceid_updatecachedrampvalue;

typedef struct _dimemanager_isdimeenabledforstoragetriggerandaction{
} dimemanager_isdimeenabledforstoragetriggerandaction;

typedef struct _drivechangegenerator_checkerrorstatemismatch{
} drivechangegenerator_checkerrorstatemismatch;

typedef struct _drivechangegenerator_checkhashneededforpotentialfilechange{
} drivechangegenerator_checkhashneededforpotentialfilechange;

typedef struct _drivechangegenerator_createdrivechangeformodifiedfile{
} drivechangegenerator_createdrivechangeformodifiedfile;

typedef struct _drivechangegenerator_handlescannedfullfile{
} drivechangegenerator_handlescannedfullfile;

typedef struct _drivechangegenerator_sweepdrivecontents{
} drivechangegenerator_sweepdrivecontents;

typedef struct _engineinitializer_cleanupcore{
} engineinitializer_cleanupcore;

typedef struct _engineinitializer_connecttoliveid{
} engineinitializer_connecttoliveid;

typedef struct _engineinitializer_fireaccountstatuscallback{
} engineinitializer_fireaccountstatuscallback;

typedef struct _engineinitializer_firesignincallback{
} engineinitializer_firesignincallback;

typedef struct _engineinitializer_initusersettings{
} engineinitializer_initusersettings;

typedef struct _engineinitializer_logoutcurrentuser{
} engineinitializer_logoutcurrentuser;

typedef struct _engineinitializer_oncoremessagesigninaccount{
} engineinitializer_oncoremessagesigninaccount;

typedef struct _filedb_createdbfileversionhelper{
} filedb_createdbfileversionhelper;

typedef struct _filedb_handlelegacyversion{
} filedb_handlelegacyversion;

typedef struct _filedb_recordfiledbmigrationtelemetry{
} filedb_recordfiledbmigrationtelemetry;

typedef struct _firstdeletemanager_firetaskdialog{
} firstdeletemanager_firetaskdialog;

typedef struct _firstdeletemanager_handletaskdialogaction{
} firstdeletemanager_handletaskdialogaction;

typedef struct _genericstartupsocket_handleonreceivecomplete{
} genericstartupsocket_handleonreceivecomplete;

typedef struct _knownfolderutilwin_redirectknownfolder{
} knownfolderutilwin_redirectknownfolder;

typedef struct _localchange_handleexistingfolderondisk{
} localchange_handleexistingfolderondisk;

typedef struct _menubuilder_addpauseresume{
} menubuilder_addpauseresume;

typedef struct _menubuilder_getsupportmenustate{
} menubuilder_getsupportmenustate;

typedef struct _menuhandler_handlemenuaction{
} menuhandler_handlemenuaction;

typedef struct _mountedfolderapihandler_handleaddmountedfolderrequest{
} mountedfolderapihandler_handleaddmountedfolderrequest;

typedef struct _mountedfoldermanager_connectwizardmountpoints{
} mountedfoldermanager_connectwizardmountpoints;

typedef struct _mountedfoldermanager_handlefinishedbusinesswizard{
} mountedfoldermanager_handlefinishedbusinesswizard;

typedef struct _mountedfoldermanager_ongetspaceusedcomplete{
} mountedfoldermanager_ongetspaceusedcomplete;

typedef struct _mountedfoldermanager_onsetselectivesynccomplete{
} mountedfoldermanager_onsetselectivesynccomplete;

typedef struct _oneauthmsaluserauthentication_handlesignincallback{
} oneauthmsaluserauthentication_handlesignincallback;

typedef struct _oneauthmsaluserauthentication_operator_{
} oneauthmsaluserauthentication_operator_;

typedef struct _originatoridprovider_loadsettings{
} originatoridprovider_loadsettings;

typedef struct _processunvalidateddeletesdciworkitem_isosupgrade{
} processunvalidateddeletesdciworkitem_isosupgrade;

typedef struct _proxyordirectsocket_onconnected{
} proxyordirectsocket_onconnected;

typedef struct _realizer_convertlcinplace{
} realizer_convertlcinplace;

typedef struct _realizerchangeinterpreter_createonenoterealizerworkitem{
} realizerchangeinterpreter_createonenoterealizerworkitem;

typedef struct _scopeinitializer_endsyncscopeinitialization{
} scopeinitializer_endsyncscopeinitialization;

typedef struct _setfilemetadataworkslicerjob_execute{
} setfilemetadataworkslicerjob_execute;

typedef struct _settingsdatabase_createdatabaseparentdirectory{
} settingsdatabase_createdatabaseparentdirectory;

typedef struct _settingsmodelwin_getautostartenabled{
} settingsmodelwin_getautostartenabled;

typedef struct _settingsmodelwin_getcoauthintegrationstatus{
} settingsmodelwin_getcoauthintegrationstatus;

typedef struct _settingsmodelwin_getlocalmassdeletedetectionenabled{
} settingsmodelwin_getlocalmassdeletedetectionenabled;

typedef struct _settingsmodelwin_getplaceholdersenabled{
} settingsmodelwin_getplaceholdersenabled;

typedef struct _settingsmodelwin_getplaceholderssupported{
} settingsmodelwin_getplaceholderssupported;

typedef struct _setuputilities_updatefoldericon{
} setuputilities_updatefoldericon;

typedef struct _shellmanager_handlegetlinkcomplete{
} shellmanager_handlegetlinkcomplete;

typedef struct _streamsocket__streamsocket{
} streamsocket__streamsocket;

typedef struct _synccomplete_clearfullenumerationinprogressscopeflagandpersistscopeinfo{
} synccomplete_clearfullenumerationinprogressscopeflagandpersistscopeinfo;

typedef struct _syncenginefileinfoprovider_setcid{
} syncenginefileinfoprovider_setcid;

typedef struct _syncenginefileinfoprovider_setcommondatapoints{
} syncenginefileinfoprovider_setcommondatapoints;

typedef struct _syncenginesubscriptionstore_readdatafromfile{
} syncenginesubscriptionstore_readdatafromfile;

typedef struct _syncenginesubscriptionstore_writedatatofile{
} syncenginesubscriptionstore_writedatatofile;

typedef struct _syncverification_abortsyncverificationandresetdrivestate{
} syncverification_abortsyncverificationandresetdrivestate;

typedef struct _taskdialogview_onbuttonclicked{
} taskdialogview_onbuttonclicked;

typedef struct _throttledtransfers_setthrottlinginfoforlibrary{
} throttledtransfers_setthrottlinginfoforlibrary;

typedef struct _uploadabledrivecontentchange_backoffupload{
} uploadabledrivecontentchange_backoffupload;

typedef struct _versionwindow_recorduiactioncompletedtelemetry{
} versionwindow_recorduiactioncompletedtelemetry;

typedef struct _visualstatecontroller_onsignedin{
} visualstatecontroller_onsignedin;

typedef struct _weblinkutils_writeweblink{
} weblinkutils_writeweblink;

typedef struct _winboxplaceholderutil_updateplaceholder{
} winboxplaceholderutil_updateplaceholder;

typedef struct _winboxplaceholderutil_updateplaceholderbypath{
} winboxplaceholderutil_updateplaceholderbypath;

typedef struct _windowmanager_launchqttaskdialog{
} windowmanager_launchqttaskdialog;

typedef struct _windowmanager_onqttaskdialogclosed{
} windowmanager_onqttaskdialogclosed;

typedef struct _wnpnet_processtridmsg{
} wnpnet_processtridmsg;

"""
