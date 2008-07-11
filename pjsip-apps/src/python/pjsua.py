# $Id$
#
# Object oriented PJSUA wrapper.
#
# Copyright (C) 2003-2008 Benny Prijono <benny@prijono.org>
#

"""Multimedia communication client library based on SIP protocol.

This implements a fully featured multimedia communication client 
library based on PJSIP stack (http://www.pjsip.org)


FEATURES

  - Session Initiation Protocol (SIP:
     - Basic registration and call
     - Multiple accounts
     - Call hold, attended and unattended call transfer
     - Presence
     - Instant messaging
  - Media stack:
     - Audio
     - Conferencing
     - Narrowband and wideband
     - Codecs: PCMA, PCMU, GSM, iLBC, Speex, G.722, L16
     - RTP/RTCP
     - Secure RTP (SRTP
  - NAT traversal features
     - Symmetric RTP
     - STUN
     - TURN
     - ICE
 

"""
import _pjsua
import thread

class Error:
    """Error exception class.
    
    Member documentation:

    op_name  -- name of the operation that generated this error.
    obj      -- the object that generated this error.
    err_code -- the error code.

    """
    op_name = ""
    obj = None
    err_code = -1
    _err_msg = ""

    def __init__(self, op_name, obj, err_code, err_msg=""):
        self.op_name = op_name
        self.obj = obj
        self.err_code = err_code
        self._err_msg = err_msg

    def err_msg(self):
        "Retrieve the description of the error."
        if self._err_msg != "":
            return self._err_msg
        self._err_msg = Lib.strerror(self.err_code)
        return self._err_msg

    def __str__(self):
        return "Object: " + str(self.obj) + ", operation=" + self.op_name + \
               ", error=" + self.err_msg()

# 
# Constants
#

class TransportType:
    """SIP transport type constants.
    
    Member documentation:
    UNSPECIFIED -- transport type is unknown or unspecified
    UDP         -- UDP transport
    TCP         -- TCP transport
    TLS         -- TLS transport
    IPV6        -- this is not a transport type but rather a flag
                   to select the IPv6 version of a transport
    UDP_IPV6    -- IPv6 UDP transport
    TCP_IPV6    -- IPv6 TCP transport
    """
    UNSPECIFIED = 0
    UDP = 1
    TCP = 2
    TLS = 3
    IPV6 = 128
    UDP_IPV6 = UDP + IPV6
    TCP_IPV6 = TCP + IPV6

class TransportFlag:
    """Transport flags to indicate the characteristics of the transport.
    
    Member documentation:
    
    RELIABLE    -- transport is reliable.
    SECURE      -- transport is secure.
    DATAGRAM    -- transport is datagram based.
    
    """
    RELIABLE = 1
    SECURE = 2
    DATAGRAM = 4

class CallRole:
    """Call role constants.
    
    Member documentation:

    CALLER  -- role is caller
    CALLEE  -- role is callee

    """
    CALLER = 0
    CALLEE = 1

class CallState:
    """Call state constants.
    
    Member documentation:

    NULL            -- call is not initialized.
    CALLING         -- initial INVITE is sent.
    INCOMING        -- initial INVITE is received.
    EARLY           -- provisional response has been sent or received.
    CONNECTING      -- 200/OK response has been sent or received.
    CONFIRMED       -- ACK has been sent or received.
    DISCONNECTED    -- call is disconnected.
    """
    NULL = 0
    CALLING = 1
    INCOMING = 2
    EARLY = 3
    CONNECTING = 4
    CONFIRMED = 5
    DISCONNECTED = 6


class MediaState:
    """Call media state constants.
    
    Member documentation:

    NONE        -- media is not available.
    ACTIVE      -- media is active.
    LOCAL_HOLD  -- media is put on-hold by local party.
    REMOTE_HOLD -- media is put on-hold by remote party.
    ERROR       -- media error (e.g. ICE negotiation failure).
    """
    NONE = 0
    ACTIVE = 1
    LOCAL_HOLD = 2
    REMOTE_HOLD = 3
    ERROR = 4


class MediaDir:
    """Media direction constants.
    
    Member documentation:

    NONE              -- media is not active
    ENCODING          -- media is active in transmit/encoding direction only.
    DECODING          -- media is active in receive/decoding direction only
    ENCODING_DECODING -- media is active in both directions.
    """
    NONE = 0
    ENCODING = 1
    DECODING = 2
    ENCODING_DECODING = 3


class PresenceActivity:
    """Presence activities constants.
    
    Member documentation:

    UNKNOWN -- the person activity is unknown
    AWAY    -- the person is currently away
    BUSY    -- the person is currently engaging in other activity
    """
    UNKNOWN = 0
    AWAY = 1
    BUSY = 2

class TURNConnType:
    """These constants specifies the connection type to TURN server.
    
    Member documentation:
    UDP     -- use UDP transport.
    TCP     -- use TCP transport.
    TLS     -- use TLS transport.
    """
    UDP = 17
    TCP = 6
    TLS = 255


class UAConfig:
    """User agent configuration to be specified in Lib.init().
    
    Member documentation:

    max_calls   -- maximum number of calls to be supported.
    nameserver  -- array of nameserver hostnames or IP addresses. Nameserver
                   must be configured if DNS SRV resolution is desired.
    stun_domain -- if nameserver is configured, this can be used to query
                   the STUN server with DNS SRV.
    stun_host   -- the hostname or IP address of the STUN server. This will
                   also be used if DNS SRV resolution for stun_domain fails.
    user_agent  -- Optionally specify the user agent name.
    """
    max_calls = 4
    nameserver = []
    stun_domain = ""
    stun_host = ""
    user_agent = "pjsip python"
    
    def _cvt_from_pjsua(self, cfg):
        self.max_calls = cfg.max_calls
        self.thread_cnt = cfg.thread_cnt
        self.nameserver = cfg.nameserver
        self.stun_domain = cfg.stun_domain
        self.stun_host = cfg.stun_host
        self.user_agent = cfg.user_agent

    def _cvt_to_pjsua(self):
        cfg = _pjsua.config_default()
        cfg.max_calls = self.max_calls
        cfg.thread_cnt = 0
        cfg.nameserver = self.nameserver
        cfg.stun_domain = self.stun_domain
        cfg.stun_host = self.stun_host
        cfg.user_agent = self.user_agent
        return cfg


class LogConfig:
    """Logging configuration to be specified in Lib.init().
    
    Member documentation:

    msg_logging   -- specify if SIP messages should be logged. Set to
                     True.
    level         -- specify the input verbosity level.
    console_level -- specify the output verbosity level.
    decor         -- specify log decoration.
    filename      -- specify the log filename.
    callback      -- specify callback to be called to write the logging
                     messages. Sample function:

                     def log_cb(level, str, len):
                        print str,

    """
    msg_logging = True
    level = 5
    console_level = 5
    decor = 0
    filename = ""
    callback = None
    
    def __init__(self, level=-1, filename="", callback=None,
                 console_level=-1):
        self._cvt_from_pjsua(_pjsua.logging_config_default())
        if level != -1:
            self.level = level
        if filename != "":
            self.filename = filename
        if callback != None:
            self.callback = callback
        if console_level != -1:
            self.console_level = console_level

    def _cvt_from_pjsua(self, cfg):
        self.msg_logging = cfg.msg_logging
        self.level = cfg.level
        self.console_level = cfg.console_level
        self.decor = cfg.decor
        self.filename = cfg.log_filename
        self.callback = cfg.cb

    def _cvt_to_pjsua(self):
        cfg = _pjsua.logging_config_default()
        cfg.msg_logging = self.msg_logging
        cfg.level = self.level
        cfg.console_level = self.console_level
        cfg.decor = self.decor
        cfg.log_filename = self.filename
        cfg.cb = self.callback
        return cfg


class MediaConfig:
    """Media configuration to be specified in Lib.init().
    
    Member documentation:
    
    clock_rate          -- specify the core clock rate of the audio,
                           most notably the conference bridge.
    snd_clock_rate      -- optionally specify different clock rate for
                           the sound device.
    snd_auto_close_time -- specify the duration in seconds when the
                           sound device should be closed after inactivity
                           period.
    channel_count       -- specify the number of channels to open the sound
                           device and the conference bridge.
    audio_frame_ptime   -- specify the length of audio frames in millisecond.
    max_media_ports     -- specify maximum number of audio ports to be
                           supported by the conference bridge.
    quality             -- specify the audio quality setting (1-10)
    ptime               -- specify the audio packet length of transmitted
                           RTP packet.
    no_vad              -- disable Voice Activity Detector (VAD) or Silence
                           Detector (SD)
    ilbc_mode           -- specify iLBC codec mode (must be 30 for now)
    tx_drop_pct         -- randomly drop transmitted RTP packets (for
                           simulation). Number is in percent.
    rx_drop_pct         -- randomly drop received RTP packets (for
                           simulation). Number is in percent.
    ec_options          -- Echo Canceller option (specify zero).
    ec_tail_len         -- specify Echo Canceller tail length in milliseconds.
                           Value zero will disable the echo canceller.
    jb_min              -- specify the minimum jitter buffer size in
                           milliseconds. Put -1 for default.
    jb_max              -- specify the maximum jitter buffer size in
                           milliseconds. Put -1 for default.
    enable_ice          -- enable Interactive Connectivity Establishment (ICE)
    enable_turn         -- enable TURN relay. TURN server settings must also
                           be configured.
    turn_server         -- specify the domain or hostname or IP address of
                           the TURN server, in "host[:port]" format.
    turn_conn_type      -- specify connection type to the TURN server, from
                           the TURNConnType constant.
    turn_cred           -- specify AuthCred for the TURN credential.
    """
    clock_rate = 16000
    snd_clock_rate = 0
    snd_auto_close_time = 5
    channel_count = 1
    audio_frame_ptime = 20
    max_media_ports = 32
    quality = 6
    ptime = 0
    no_vad = False
    ilbc_mode = 30
    tx_drop_pct = 0
    rx_drop_pct = 0
    ec_options = 0
    ec_tail_len = 256
    jb_min = -1
    jb_max = -1
    enable_ice = True
    enable_turn = False
    turn_server = ""
    turn_conn_type = TURNConnType.UDP
    turn_cred = None
     
    def __init__(self):
        default = _pjsua.media_config_default()
        self._cvt_from_pjsua(default)

    def _cvt_from_pjsua(self, cfg):
        self.clock_rate = cfg.clock_rate
        self.snd_clock_rate = cfg.snd_clock_rate
        self.snd_auto_close_time = cfg.snd_auto_close_time
        self.channel_count = cfg.channel_count
        self.audio_frame_ptime = cfg.audio_frame_ptime
        self.max_media_ports = cfg.max_media_ports
        self.quality = cfg.quality
        self.ptime = cfg.ptime
        self.no_vad = cfg.no_vad
        self.ilbc_mode = cfg.ilbc_mode
        self.tx_drop_pct = cfg.tx_drop_pct
        self.rx_drop_pct = cfg.rx_drop_pct
        self.ec_options = cfg.ec_options
        self.ec_tail_len = cfg.ec_tail_len
        self.jb_min = cfg.jb_min
        self.jb_max = cfg.jb_max
        self.enable_ice = cfg.enable_ice
        self.enable_turn = cfg.enable_turn
        self.turn_server = cfg.turn_server
        self.turn_conn_type = cfg.turn_conn_type
        if cfg.turn_username:
            self.turn_cred = AuthCred(cfg.turn_realm, cfg.turn_username,
                                      cfg.turn_passwd, cfg.turn_passwd_type)
        else:
            self.turn_cred = None

    def _cvt_to_pjsua(self):
        cfg = _pjsua.media_config_default()
        cfg.clock_rate = self.clock_rate
        cfg.snd_clock_rate = self.snd_clock_rate
        cfg.snd_auto_close_time = self.snd_auto_close_time
        cfg.channel_count = self.channel_count
        cfg.audio_frame_ptime = self.audio_frame_ptime
        cfg.max_media_ports = self.max_media_ports
        cfg.quality = self.quality
        cfg.ptime = self.ptime
        cfg.no_vad = self.no_vad
        cfg.ilbc_mode = self.ilbc_mode
        cfg.tx_drop_pct = self.tx_drop_pct
        cfg.rx_drop_pct = self.rx_drop_pct
        cfg.ec_options = self.ec_options
        cfg.ec_tail_len = self.ec_tail_len
        cfg.jb_min = self.jb_min
        cfg.jb_max = self.jb_max
        cfg.enable_ice = self.enable_ice
        cfg.enable_turn = self.enable_turn
        cfg.turn_server = self.turn_server
        cfg.turn_conn_type = self.turn_conn_type
        if self.turn_cred:
            cfg.turn_realm = self.turn_cred.realm
            cfg.turn_username = self.turn_cred.username
            cfg.turn_passwd_type = self.turn_cred.passwd_type
            cfg.turn_passwd = self.turn_cred.passwd
        return cfg


class TransportConfig:
    """SIP transport configuration class.
    
    Member configuration:

    port        -- port number.
    bound_addr  -- optionally specify the address to bind the socket to.
                   Default is empty to bind to INADDR_ANY.
    public_addr -- optionally override the published address for this
                   transport. If empty, the default behavior is to get
                   the public address from STUN or from the selected
                   local interface. Format is "host:port".
    """
    port = 0
    bound_addr = ""
    public_addr = ""

    def __init__(self, port=5060, 
                 bound_addr="", public_addr=""):
        self.port = port
        self.bound_addr = bound_addr
        self.public_addr = public_addr

    def _cvt_to_pjsua(self):
        cfg = _pjsua.transport_config_default()
        cfg.port = self.port
        cfg.bound_addr = self.bound_addr
        cfg.public_addr = self.public_addr
        return cfg


class TransportInfo:
    """SIP transport info.
    
    Member documentation:

    type        -- transport type, from TransportType constants.
    description -- longer description for this transport.
    is_reliable -- True if transport is reliable.
    is_secure   -- True if transport is secure.
    is_datagram -- True if transport is datagram based.
    host        -- the IP address of this transport.
    port        -- the port number.
    ref_cnt     -- number of objects referencing this transport.
    """
    type = ""
    description = ""
    is_reliable = False
    is_secure = False
    is_datagram = False
    host = ""
    port = 0
    ref_cnt = 0
    
    def __init__(self, ti):
        self.type = ti.type_name
        self.description = ti.info
        self.is_reliable = (ti.flag & TransportFlag.RELIABLE)
        self.is_secure = (ti.flag & TransportFlag.SECURE)
        self.is_datagram = (ti.flag & TransportFlag.DATAGRAM)
        self.host = ti.addr
        self.port = ti.port
        self.ref_cnt = ti.usage_count
    
    
class Transport:
    "SIP transport class."
    _id = -1
    _lib = None
    _obj_name = ""

    def __init__(self, lib, id):
        self._lib = lib
        self._id = id
        self._obj_name = "Transport " + self.info().description

    def __str__(self):
        return self._obj_name

    def info(self):
        """Get TransportInfo.
        """
        ti = _pjsua.transport_get_info(self._id)
        if not ti:
            self._lib._err_check("info()", self, -1, "Invalid transport")
        return TransportInfo(ti)

    def enable(self):
        """Enable this transport."""
        err = _pjsua.transport_set_enable(self._id, True)
        self._lib._err_check("enable()", self, err)

    def disable(self):
        """Disable this transport."""
        err = _pjsua.transport_set_enable(self._id, 0)
        self._lib._err_check("disable()", self, err)

    def close(self, force=False):
        """Close and destroy this transport.

        Keyword argument:
        force   -- force deletion of this transport (not recommended).
        """
        err = _pjsua.transport_close(self._id, force)
        self._lib._err_check("close()", self, err)


class SIPUri:
    """Helper class to parse the most important components of SIP URI.

    Member documentation:

    scheme    -- URI scheme ("sip" or "sips")
    user      -- user part of the URI (may be empty)
    host      -- host name part
    port      -- optional port number (zero if port is not specified).
    transport -- transport parameter, or empty if transport is not
                 specified.

    """
    scheme = ""
    user = ""
    host = ""
    port = 0
    transport = ""

    def __init__(self, uri=None):
        if uri:
            self.decode(uri)

    def decode(self, uri):
        """Parse SIP URL.

        Keyword argument:
        uri -- the URI string.

        """
        self.scheme, self.user, self.host, self.port, self.transport = \
            _pjsua.parse_simple_uri(uri)

    def encode(self):
        """Encode this object into SIP URI string.

        Return:
            URI string.

        """
        output = self.scheme + ":"
        if self.user and len(self.user):
            output = output + self.user + "@"
        output = output + self.host
        if self.port:
            output = output + ":" + output(self.port)
        if self.transport:
            output = output + ";transport=" + self.transport
        return output


class AuthCred:
    """Authentication credential for SIP or TURN account.
    
    Member documentation:

    scheme      -- authentication scheme (default is "Digest")
    realm       -- realm
    username    -- username
    passwd_type -- password encoding (zero for plain-text)
    passwd      -- the password
    """
    scheme = "Digest"
    realm = "*"
    username = ""
    passwd_type = 0
    passwd = ""

    def __init__(self, realm, username, passwd, scheme="Digest", passwd_type=0):
        self.scheme = scheme
        self.realm = realm
        self.username = username
        self.passwd_type = passwd_type
        self.passwd = passwd


class AccountConfig:
    """ This describes account configuration to create an account.

    Member documentation:

    priority                -- account priority for matching incoming
                               messages.
    id                      -- SIP URI of this account. This setting is
                               mandatory.
    force_contact           -- force to use this URI as Contact URI. Setting
                               this value is generally not recommended.
    reg_uri                 -- specify the registrar URI. Mandatory if
                               registration is required.
    reg_timeout             -- specify the SIP registration refresh interval
                               in seconds.
    require_100rel          -- specify if reliable provisional response is
                               to be enforced (with Require header).
    publish_enabled         -- specify if PUBLISH should be used. When
                               enabled, the PUBLISH will be sent to the
                               registrar.
    pidf_tuple_id           -- optionally specify the tuple ID in outgoing
                               PIDF document.
    proxy                   -- list of proxy URI.
    auth_cred               -- list of AuthCred containing credentials to
                               authenticate against the registrars and
                               the proxies.
    auth_initial_send       -- specify if empty Authorization header should be
                               sent. May be needed for IMS.
    auth_initial_algorithm  -- when auth_initial_send is enabled, optionally
                               specify the authentication algorithm to use.
                               Valid values are "md5", "akav1-md5", or
                               "akav2-md5". 
    transport_id            -- optionally specify the transport ID to be used
                               by this account. Shouldn't be needed unless
                               for specific requirements (e.g. in multi-homed
                               scenario).
    allow_contact_rewrite   -- specify whether the account should learn its
                               Contact address from REGISTER response and 
                               update the registration accordingly. Default is
                               True.
    ka_interval             -- specify the interval to send NAT keep-alive 
                               packet.
    ka_data                 -- specify the NAT keep-alive packet contents.
    use_srtp                -- specify the SRTP usage policy. Valid values
                               are: 0=disable, 1=optional, 2=mandatory.
                               Default is 0.
    srtp_secure_signaling   -- specify the signaling security level required
                               by SRTP. Valid values are: 0=no secure 
                               transport is required, 1=hop-by-hop secure
                               transport such as TLS is required, 2=end-to-
                               end secure transport is required (i.e. "sips").
    """
    priority = 0
    id = ""
    force_contact = ""
    reg_uri = ""
    reg_timeout = 0
    require_100rel = False
    publish_enabled = False
    pidf_tuple_id = ""
    proxy = []
    auth_cred = []
    auth_initial_send = False
    auth_initial_algorithm = ""
    transport_id = -1
    allow_contact_rewrite = True
    ka_interval = 15
    ka_data = "\r\n"
    use_srtp = 0
    srtp_secure_signaling = 1

    def __init__(self, domain="", username="", password="", 
                 display="", registrar="", proxy=""):
        """
        Construct account config. If domain argument is specified, 
        a typical configuration will be built.

        Keyword arguments:
        domain    -- domain name of the server.
        username  -- user name.
        password  -- plain-text password.
        display   -- optional display name for the user name.
        registrar -- the registrar URI. If domain name is specified
                     and this argument is empty, the registrar URI
                     will be constructed from the domain name.
        proxy     -- the proxy URI. If domain name is specified
                     and this argument is empty, the proxy URI
                     will be constructed from the domain name.

        """
        default = _pjsua.acc_config_default()
        self._cvt_from_pjsua(default)
        if domain!="":
            self.build_config(domain, username, password,
                              display, registrar, proxy)

    def build_config(self, domain, username, password, display="",
                     registrar="", proxy=""):
        """
        Construct account config. If domain argument is specified, 
        a typical configuration will be built.

        Keyword arguments:
        domain    -- domain name of the server.
        username  -- user name.
        password  -- plain-text password.
        display   -- optional display name for the user name.
        registrar -- the registrar URI. If domain name is specified
                     and this argument is empty, the registrar URI
                     will be constructed from the domain name.
        proxy     -- the proxy URI. If domain name is specified
                     and this argument is empty, the proxy URI
                     will be constructed from the domain name.

        """
        if display != "":
            display = display + " "
        userpart = username
        if userpart != "":
            userpart = userpart + "@"
        self.id = display + "<sip:" + userpart + domain + ">"
        self.reg_uri = registrar
        if self.reg_uri == "":
            self.reg_uri = "sip:" + domain
        if proxy == "":
            proxy = "sip:" + domain + ";lr"
        if proxy.find(";lr") == -1:
            proxy = proxy + ";lr"
        self.proxy.append(proxy)
        if username != "":
            self.auth_cred.append(AuthCred("*", username, password))
    
    def _cvt_from_pjsua(self, cfg):
        self.priority = cfg.priority
        self.id = cfg.id
        self.force_contact = cfg.force_contact
        self.reg_uri = cfg.reg_uri
        self.reg_timeout = cfg.reg_timeout
        self.require_100rel = cfg.require_100rel
        self.publish_enabled = cfg.publish_enabled
        self.pidf_tuple_id = cfg.pidf_tuple_id
        self.proxy = cfg.proxy
        for cred in cfg.cred_info:
            self.auth_cred.append(AuthCred(cred.realm, cred.username, 
                                           cred.data, cred.scheme,
                                           cred.data_type))
        self.auth_initial_send = cfg.auth_initial_send
        self.auth_initial_algorithm = cfg.auth_initial_algorithm
        self.transport_id = cfg.transport_id
        self.allow_contact_rewrite = cfg.allow_contact_rewrite
        self.ka_interval = cfg.ka_interval
        self.ka_data = cfg.ka_data
        self.use_srtp = cfg.use_srtp
        self.srtp_secure_signaling = cfg.srtp_secure_signaling

    def _cvt_to_pjsua(self):
        cfg = _pjsua.acc_config_default()
        cfg.priority = self.priority
        cfg.id = self.id
        cfg.force_contact = self.force_contact
        cfg.reg_uri = self.reg_uri
        cfg.reg_timeout = self.reg_timeout
        cfg.require_100rel = self.require_100rel
        cfg.publish_enabled = self.publish_enabled
        cfg.pidf_tuple_id = self.pidf_tuple_id
        cfg.proxy = self.proxy
        for cred in self.auth_cred:
            c = _pjsua.Pjsip_Cred_Info()
            c.realm = cred.realm
            c.scheme = cred.scheme
            c.username = cred.username
            c.data_type = cred.passwd_type
            c.data = cred.passwd
            cfg.cred_info.append(c)
        cfg.auth_initial_send = self.auth_initial_send
        cfg.auth_initial_algorithm = self.auth_initial_algorithm
        cfg.transport_id = self.transport_id
        cfg.allow_contact_rewrite = self.allow_contact_rewrite
        cfg.ka_interval = self.ka_interval
        cfg.ka_data = self.ka_data
        cfg.use_srtp = self.use_srtp
        cfg.srtp_secure_signaling = self.srtp_secure_signaling
        return cfg
 
 
# Account information
class AccountInfo:
    """This describes Account info. Application retrives account info
    with Account.info().

    Member documentation:

    is_default      -- True if this is the default account.
    uri             -- the account URI.
    reg_active      -- True if registration is active for this account.
    reg_expires     -- contains the current registration expiration value,
                       in seconds.
    reg_status      -- the registration status. If the value is less than
                       700, it specifies SIP status code. Value greater than
                       this specifies the error code.
    reg_reason      -- contains the registration status text (e.g. the
                       error message).
    online_status   -- the account's presence online status, True if it's 
                       publishing itself as online.
    online_text     -- the account's presence status text.

    """
    is_default = False
    uri = ""
    reg_active = False
    reg_expires = -1
    reg_status = 0
    reg_reason = ""
    online_status = False
    online_text = ""

    def __init__(self, ai):
        self.is_default = ai.is_default
        self.uri = ai.acc_uri
        self.reg_active = ai.has_registration
        self.reg_expires = ai.expires
        self.reg_status = ai.status
        self.reg_reason = ai.status_text
        self.online_status = ai.online_status
        self.online_text = ai.online_status_text

# Account callback
class AccountCallback:
    """Class to receive notifications on account's events.

    Derive a class from this class and register it to the Account object
    using Account.set_callback() to start receiving events from the Account
    object.

    Member documentation:

    account     -- the Account object.

    """
    account = None

    def __init__(self, account):
        self.account = account

    def on_reg_state(self):
        """Notification that the registration status has changed.
        """
        pass

    def on_incoming_call(self, call):
        """Notification about incoming call.

        Unless this callback is implemented, the default behavior is to
        reject the call with default status code.

    Keyword arguments:
    call    -- the new incoming call
        """
        call.hangup()

    def on_pager(self, from_uri, contact, mime_type, body):
        """
        Notification that incoming instant message is received on
        this account.

        Keyword arguments:
        from_uri   -- sender's URI
        contact    -- sender's Contact URI
        mime_type  -- MIME type of the instant message body
        body       -- the instant message body

        """
        pass

    def on_pager_status(self, to_uri, body, im_id, code, reason):
        """
        Notification about the delivery status of previously sent
        instant message.

        Keyword arguments:
        to_uri  -- the destination URI of the message
        body    -- the message body
        im_id   -- message ID
        code    -- SIP status code
        reason  -- SIP reason phrase

        """
        pass

    def on_typing(self, from_uri, contact, is_typing):
        """
        Notification that remote is typing or stop typing.

        Keyword arguments:
        buddy     -- Buddy object for the sender, if found. Otherwise
                     this will be None
        from_uri  -- sender's URI of the indication
        contact   -- sender's contact URI
        is_typing -- boolean to indicate whether remote is currently
                     typing an instant message.

        """
        pass



class Account:
    """This describes SIP account class.

    PJSUA accounts provide identity (or identities) of the user who is 
    currently using the application. In SIP terms, the identity is used 
    as the From header in outgoing requests.

    Account may or may not have client registration associated with it. 
    An account is also associated with route set and some authentication 
    credentials, which are used when sending SIP request messages using 
    the account. An account also has presence's online status, which 
    will be reported to remote peer when they subscribe to the account's 
    presence, or which is published to a presence server if presence 
    publication is enabled for the account.

    Account is created with Lib.create_account(). At least one account 
    MUST be created. If no user association is required, application can 
    create a userless account by calling Lib.create_account_for_transport().
    A userless account identifies local endpoint instead of a particular 
    user, and it correspond with a particular transport instance.

    Also one account must be set as the default account, which is used as 
    the account to use when PJSUA fails to match a request with any other
    accounts.

    """
    _id = -1        
    _lib = None
    _cb = AccountCallback(None)
    _obj_name = ""

    def __init__(self, lib, id):
        """Construct this class. This is normally called by Lib class and
        not by application.

        Keyword arguments:
        lib -- the Lib instance.
        id  -- the pjsua account ID.
        """
        _cb = AccountCallback(self)
        self._id = id
        self._lib = lib
        self._lib._associate_account(self._id, self)
        self._obj_name = "Account " + self.info().uri

    def __del__(self):
        self._lib._disassociate_account(self._id, self)

    def __str__(self):
        return self._obj_name

    def info(self):
        """Retrieve AccountInfo for this account.
        """
        ai = _pjsua.acc_get_info(self._id)
        if ai==None:
            self._lib._err_check("info()", self, -1, "Invalid account")
        return AccountInfo(ai)

    def is_valid(self):
        """
        Check if this account is still valid.

        """
        return _pjsua.acc_is_valid(self._id)

    def set_callback(self, cb):
        """Register callback to receive notifications from this object.

        Keyword argument:
        cb  -- AccountCallback instance.

        """
        if cb:
            self._cb = cb
        else:
            self._cb = AccountCallback(self)

    def set_default(self):
        """ Set this account as default account to send outgoing requests
        and as the account to receive incoming requests when more exact
        matching criteria fails.
        """
        err = _pjsua.acc_set_default(self._id)
        self._lib._err_check("set_default()", self, err)

    def is_default(self):
        """ Check if this account is the default account.

        """
        def_id = _pjsua.acc_get_default()
        return self.is_valid() and def_id==self._id

    def delete(self):
        """ Delete this account.
        
        """
        err = _pjsua.acc_del(self._id)
        self._lib._err_check("delete()", self, err)

    def set_basic_status(self, is_online):
        """ Set basic presence status of this account.

        Keyword argument:
        is_online   -- boolean to indicate basic presence availability.

        """
        err = _pjsua.acc_set_online_status(self._id, is_online)
        self._lib._err_check("set_basic_status()", self, err)

    def set_presence_status(self, is_online, 
                            activity=PresenceActivity.UNKNOWN, 
                            pres_text="", rpid_id=""):
        """ Set presence status of this account. 
        
        Keyword arguments:
        is_online   -- boolean to indicate basic presence availability
        activity    -- value from PresenceActivity
        pres_text   -- optional string to convey additional information about
                       the activity (such as "On the phone")
        rpid_id     -- optional string to be placed as RPID ID. 

        """
        err = _pjsua.acc_set_online_status2(self._id, is_online, activity,
                                            pres_text, rpid_id)
        self._lib._err_check("set_presence_status()", self, err)

    def set_registration(self, renew):
        """Manually renew registration or unregister from the server.

        Keyword argument:
        renew   -- boolean to indicate whether registration is renewed.
                   Setting this value for False will trigger unregistration.

        """
        err = _pjsua.acc_set_registration(self._id, renew)
        self._lib._err_check("set_registration()", self, err)

    def has_registration(self):
        """Returns True if registration is active for this account.

        """
        acc_info = _pjsua.acc_get_info(self._id)
        if not acc_info:
            self._lib._err_check("has_registration()", self, -1, 
                                 "invalid account")
        return acc_info.has_registration

    def set_transport(self, transport):
        """Set this account to only use the specified transport to send
        outgoing requests.

        Keyword argument:
        transport   -- Transport object.

        """
        err = _pjsua.acc_set_transport(self._id, transport._id)
        self._lib._err_check("set_transport()", self, err)

    def make_call(self, dst_uri, hdr_list=None):
        """Make outgoing call to the specified URI.

        Keyword arguments:
        dst_uri  -- Destination SIP URI.
        hdr_list -- Optional list of headers to be sent with outgoing
                    INVITE

        """
        err, cid = _pjsua.call_make_call(self._id, dst_uri, 0, 
                                           0, Lib._create_msg_data(hdr_list))
        self._lib._err_check("make_call()", self, err)
        return Call(self._lib, cid)

    def add_buddy(self, uri):
        """Add new buddy.

        Keyword argument:
        uri         -- SIP URI of the buddy

        Return:
            Buddy object
        """
        buddy_cfg = _pjsua.buddy_config_default()
        buddy_cfg.uri = uri
        buddy_cfg.subscribe = False
        err, buddy_id = _pjsua.buddy_add(buddy_cfg)
        self._lib._err_check("add_buddy()", self, err)
        return Buddy(self._lib, buddy_id, self)


class CallCallback:
    """Class to receive event notification from Call objects. 

    Use Call.set_callback() method to install instance of this callback 
    class to receive event notifications from the call object.

    Member documentation:

    call    -- the Call object.

    """
    call = None

    def __init__(self, call):
        self.call = call

    def on_state(self):
        """Notification that the call's state has changed.

        """
        pass

    def on_media_state(self):
        """Notification that the call's media state has changed.

        """
        pass

    def on_dtmf_digit(self, digits):
        """Notification on incoming DTMF digits.

        Keyword argument:
        digits  -- string containing the received digits.

        """
        pass

    def on_transfer_request(self, dst, code):
        """Notification that call is being transfered by remote party. 

        Application can decide to accept/reject transfer request by returning
        code greater than or equal to 500. The default behavior is to accept 
        the transfer by returning 202.

        Keyword arguments:
        dst     -- string containing the destination URI
        code    -- the suggested status code to return to accept the request.

        Return:
        the callback should return 202 to accept the request, or 300-699 to
        reject the request.

        """
        return code

    def on_transfer_status(self, code, reason, final, cont):
        """
        Notification about the status of previous call transfer request. 

        Keyword arguments:
        code    -- SIP status code to indicate completion status.
        text    -- SIP status reason phrase.
        final   -- if True then this is a final status and no further
                   notifications will be sent for this call transfer
                   status.
        cont    -- suggested return value.

        Return:
        If the callback returns false then no further notification will
        be sent for the transfer request for this call.

        """
        return cont

    def on_replace_request(self, code, reason):
        """Notification when incoming INVITE with Replaces header is received. 

        Application may reject the request by returning value greather than
        or equal to 500. The default behavior is to accept the request.

        Keyword arguments:
        code    -- default status code to return
        reason  -- default reason phrase to return

        Return:
        The callback should return (code, reason) tuple.

        """
        return code, reason

    def on_replaced(self, new_call):
        """
        Notification that this call will be replaced with new_call. 
        After this callback is called, this call will be disconnected.

        Keyword arguments:
        new_call    -- the new call that will replace this call.
        """
        pass

    def on_pager(self, mime_type, body):
        """
        Notification that incoming instant message is received on
        this call.

        Keyword arguments:
        mime_type  -- MIME type of the instant message body.
        body       -- the instant message body.

        """
        pass

    def on_pager_status(self, body, im_id, code, reason):
        """
        Notification about the delivery status of previously sent
        instant message.

        Keyword arguments:
        body    -- message body
        im_id   -- message ID
        code    -- SIP status code
        reason  -- SIP reason phrase

        """
        pass

    def on_typing(self, is_typing):
        """
        Notification that remote is typing or stop typing.

        Keyword arguments:
        is_typing -- boolean to indicate whether remote is currently
                     typing an instant message.

        """
        pass


class CallInfo:
    """This structure contains various information about Call.

    Application may retrieve this information with Call.info().

    Member documentation:

    role            -- CallRole
    account         -- Account object.
    uri             -- SIP URI of local account.
    contact         -- local Contact URI.
    remote_uri      -- remote SIP URI.
    remote_contact  -- remote Contact URI
    sip_call_id     -- call's Call-ID identification
    state           -- CallState
    state_text      -- state text.
    last_code       -- last SIP status code
    last_reason     -- text phrase for last_code
    media_state     -- MediaState
    media_dir       -- MediaDir
    conf_slot       -- conference slot number for this call.
    call_time       -- call's connected duration in seconds.
    total_time      -- total call duration in seconds.
    """
    role = CallRole.CALLER
    account = None
    uri = ""
    contact = ""
    remote_uri = ""
    remote_contact = ""
    sip_call_id = ""
    state = CallState.NULL
    state_text = ""
    last_code = 0
    last_reason = ""
    media_state = MediaState.NONE
    media_dir = MediaDir.NONE
    conf_slot = -1
    call_time = 0
    total_time = 0

    def __init__(self, lib=None, ci=None):
        if lib and ci:
            self._cvt_from_pjsua(lib, ci)

    def _cvt_from_pjsua(self, lib, ci):
        self.role = ci.role
        self.account = lib._lookup_account(ci.acc_id)
        self.uri = ci.local_info
        self.contact = ci.local_contact
        self.remote_uri = ci.remote_info
        self.remote_contact = ci.remote_contact
        self.sip_call_id = ci.call_id
        self.state = ci.state
        self.state_text = ci.state_text
        self.last_code = ci.last_status
        self.last_reason = ci.last_status_text
        self.media_state = ci.media_status
        self.media_dir = ci.media_dir
        self.conf_slot = ci.conf_slot
        self.call_time = ci.connect_duration.sec
        self.total_time = ci.total_duration.sec


class Call:
    """This class represents SIP call.

    Application initiates outgoing call with Account.make_call(), and
    incoming calls are reported in AccountCallback.on_incoming_call().
    """
    _id = -1
    _cb = None
    _lib = None
    _obj_name = ""

    def __init__(self, lib, call_id):
        self._cb = CallCallback(self) 
        self._id = call_id
        self._lib = lib
        self._lib._associate_call(call_id, self)
        self._obj_name = "Call " + self.info().remote_uri

    def __del__(self):
        self._lib._disassociate_call(self._id, self)

    def __str__(self):
        return self._obj_name

    def set_callback(self, cb):
        """
        Set callback object to retrieve event notifications from this call.

        Keyword arguments:
        cb  -- CallCallback instance.
        """
        if cb:
            self._cb = cb
        else:
            self._cb = CallCallback(self)

    def info(self):
        """
        Get the CallInfo.
        """
        ci = _pjsua.call_get_info(self._id)
        if not ci:
            self._lib._err_check("info", self, -1, "Invalid call")
        return CallInfo(self._lib, ci)

    def is_valid(self):
        """
        Check if this call is still valid.
        """
        return _pjsua.call_is_active(self._id)

    def dump_status(self, with_media=True, indent="", max_len=1024):
        """
        Dump the call status.
        """
        return _pjsua.call_dump(self._id, with_media, max_len, indent)

    def answer(self, code=200, reason="", hdr_list=None):
        """
        Send provisional or final response to incoming call.

        Keyword arguments:
        code     -- SIP status code.
        reason   -- Reason phrase. Put empty to send default reason
                    phrase for the status code.
        hdr_list -- Optional list of headers to be sent with the
                    INVITE response.

        """
        err = _pjsua.call_answer(self._id, code, reason, 
                                   Lib._create_msg_data(hdr_list))
        self._lib._err_check("answer()", self, err)

    def hangup(self, code=603, reason="", hdr_list=None):
        """
        Terminate the call.

        Keyword arguments:
        code     -- SIP status code.
        reason   -- Reason phrase. Put empty to send default reason
                    phrase for the status code.
        hdr_list -- Optional list of headers to be sent with the
                    message.

        """
        err = _pjsua.call_hangup(self._id, code, reason, 
                                   Lib._create_msg_data(hdr_list))
        self._lib._err_check("hangup()", self, err)

    def hold(self, hdr_list=None):
        """
        Put the call on hold.

        Keyword arguments:
        hdr_list -- Optional list of headers to be sent with the
                    message.
        """
        err = _pjsua.call_set_hold(self._id, Lib._create_msg_data(hdr_list))
        self._lib._err_check("hold()", self, err)

    def unhold(self, hdr_list=None):
        """
        Release the call from hold.

        Keyword arguments:
        hdr_list -- Optional list of headers to be sent with the
                    message.

        """
        err = _pjsua.call_reinvite(self._id, True, 
                                     Lib._create_msg_data(hdr_list))
        self._lib._err_check("unhold()", self, err)

    def reinvite(self, hdr_list=None):
        """
        Send re-INVITE and optionally offer new codecs to use.

        Keyword arguments:
        hdr_list   -- Optional list of headers to be sent with the
                      message.

        """
        err = _pjsua.call_reinvite(self._id, True, 
                                     Lib._create_msg_data(hdr_list))
        self._lib._err_check("reinvite()", self, err)

    def update(self, hdr_list=None, options=0):
        """
        Send UPDATE and optionally offer new codecs to use.

        Keyword arguments:
        hdr_list   -- Optional list of headers to be sent with the
                      message.
        options    -- Must be zero for now.

        """
        err = _pjsua.call_update(self._id, options, 
                                   Lib._create_msg_data(hdr_list))
        self._lib._err_check("update()", self, err)

    def transfer(self, dest_uri, hdr_list=None):
        """
        Transfer the call to new destination.

        Keyword arguments:
        dest_uri -- Specify the SIP URI to transfer the call to.
        hdr_list -- Optional list of headers to be sent with the
                    message.

        """
        err = _pjsua.call_xfer(self._id, dest_uri, 
                                 Lib._create_msg_data(hdr_list))
        self._lib._err_check("transfer()", self, err)

    def transfer_to_call(self, call, hdr_list=None, options=0):
        """
        Attended call transfer.

        Keyword arguments:
        call     -- The Call object to transfer call to.
        hdr_list -- Optional list of headers to be sent with the
                    message.
        options  -- Must be zero for now.

        """
        err = _pjsua.call_xfer_replaces(self._id, call._id, options,
                                          Lib._create_msg_data(hdr_list))
        self._lib._err_check("transfer_to_call()", self, err)

    def dial_dtmf(self, digits):
        """
        Send DTMF digits with RTP event package.

        Keyword arguments:
        digits  -- DTMF digit string.

        """
        err = _pjsua.call_dial_dtmf(self._id, digits)
        self._lib._err_check("dial_dtmf()", self, err)

    def send_request(self, method, hdr_list=None, content_type=None,
                     body=None):
        """
        Send arbitrary request to remote call. 
        
        This is useful for example to send INFO request. Note that this 
        function should not be used to send request that will change the 
        call state such as CANCEL or BYE.

        Keyword arguments:
        method       -- SIP method name.
        hdr_list     -- Optional header list to be sent with the request.
        content_type -- Content type to describe the body, if the body
                        is present
        body         -- Optional SIP message body.

        """
        if hdr_list and body:
            msg_data = _pjsua.Msg_Data()
            if hdr_list:
                msg_data.hdr_list = hdr_list
            if content_type:
                msg_data.content_type = content_type
            if body:
                msg_data.msg_body = body
        else:
            msg_data = None
                
        err = _pjsua.call_send_request(self._id, method, msg_data)
        self._lib._err_check("send_request()", self, err)


class BuddyInfo:
    """This class contains information about Buddy. Application may 
    retrieve this information by calling Buddy.info().

    Member documentation:

    uri             -- the Buddy URI.
    contact         -- the Buddy Contact URI, if available.
    online_status   -- the presence online status.
    online_text     -- the presence online status text.
    activity        -- the PresenceActivity
    subscribed      -- specify whether buddy's presence status is currently
                       being subscribed.
    """
    uri = ""
    contact = ""
    online_status = 0
    online_text = ""
    activity = PresenceActivity.UNKNOWN
    subscribed = False

    def __init__(self, pjsua_bi=None):
        if pjsua_bi:
            self._cvt_from_pjsua(pjsua_bi)

    def _cvt_from_pjsua(self, inf):
        self.uri = inf.uri
        self.contact = inf.contact
        self.online_status = inf.status
        self.online_text = inf.status_text
        self.activity = inf.activity
        self.subscribed = inf.monitor_pres


class BuddyCallback:
    """This class can be used to receive notifications about Buddy's
    presence status change. Application needs to derive a class from
    this class, and register the instance with Buddy.set_callback().

    Member documentation:

    buddy   -- the Buddy object.
    """
    buddy = None

    def __init__(self, buddy):
        self.buddy = buddy

    def on_state(self):
        """
        Notification that buddy's presence state has changed. Application
        may then retrieve the new status with Buddy.info() function.
        """
        pass
   
    def on_pager(self, mime_type, body):
        """Notification that incoming instant message is received from
        this buddy.

        Keyword arguments:
        mime_type  -- MIME type of the instant message body
        body       -- the instant message body

        """
        pass

    def on_pager_status(self, body, im_id, code, reason):
        """Notification about the delivery status of previously sent
        instant message.

        Keyword arguments:
        body    -- the message body
        im_id   -- message ID
        code    -- SIP status code
        reason  -- SIP reason phrase

        """
        pass

    def on_typing(self, is_typing):
        """Notification that remote is typing or stop typing.

        Keyword arguments:
        is_typing -- boolean to indicate whether remote is currently
                     typing an instant message.

        """
        pass


class Buddy:
    """A Buddy represents person or remote agent.

    This class provides functions to subscribe to buddy's presence and
    to send or receive instant messages from the buddy.
    """
    _id = -1
    _lib = None
    _cb = None
    _obj_name = ""
    _acc = None

    def __init__(self, lib, id, account):
        self._cb = BuddyCallback(self)
        self._lib = lib
        self._id = id
        self._acc = account
        lib._associate_buddy(self._id, self)
        self._obj_name = "Buddy " + self.info().uri

    def __del__(self):
        self._lib._disassociate_buddy(self)

    def __str__(self):
        return self._obj_name

    def info(self):
        """
        Get buddy info as BuddyInfo.
        """
        return BuddyInfo(_pjsua.buddy_get_info(self._id))

    def set_callback(self, cb):
        """Install callback to receive notifications from this object.

        Keyword argument:
        cb  -- BuddyCallback instance.
        """
        if cb:
            self._cb = cb
        else:
            self._cb = BuddyCallback(self)

    def subscribe(self):
        """
        Subscribe to buddy's presence status notification.
        """
        err = _pjsua.buddy_subscribe_pres(self._id, True)
        self._lib._err_check("subscribe()", self, err)

    def unsubscribe(self):
        """
        Unsubscribe from buddy's presence status notification.
        """
        err = _pjsua.buddy_subscribe_pres(self._id, False)
        self._lib._err_check("unsubscribe()", self, err)

    def delete(self):
        """
        Remove this buddy from the buddy list.
        """
        err = _pjsua.buddy_del(self._id)
        self._lib._err_check("delete()", self, err)

    def send_pager(self, text, im_id=0, content_type="text/plain", \
                   hdr_list=None):
        """Send instant message to remote buddy.

        Keyword arguments:
        text         -- Instant message to be sent
        im_id        -- Optional instant message ID to identify this
                        instant message when delivery status callback
                        is called.
        content_type -- MIME type identifying the instant message
        hdr_list     -- Optional list of headers to be sent with the
                        request.

        """
        err = _pjsua.im_send(self._acc._id, self.info().uri, \
                             content_type, text, \
                             Lib._create_msg_data(hdr_list), \
                             im_id)
        self._lib._err_check("send_pager()", self, err)

    def send_typing_ind(self, is_typing=True, hdr_list=None):
        """Send typing indication to remote buddy.

        Keyword argument:
        is_typing -- boolean to indicate wheter user is typing.
        hdr_list  -- Optional list of headers to be sent with the
                     request.

        """
        err = _pjsua.im_typing(self._acc._id, self.info().uri, \
                               is_typing, Lib._create_msg_data(hdr_list))
        self._lib._err_check("send_typing_ind()", self, err)



# Sound device info
class SoundDeviceInfo:
    """This described the sound device info.

    Member documentation:
    name                -- device name.
    input_channels      -- number of capture channels supported.
    output_channels     -- number of playback channels supported.
    default_clock_rate  -- default sampling rate.
    """
    name = ""
    input_channels = 0
    output_channels = 0
    default_clock_rate = 0

    def __init__(self, sdi):
        self.name = sdi.name
        self.input_channels = sdi.input_count
        self.output_channels = sdi.output_count
        self.default_clock_rate = sdi.default_samples_per_sec


# Codec info
class CodecInfo:
    """This describes codec info.

    Member documentation:
    name            -- codec name
    priority        -- codec priority (0-255)
    clock_rate      -- clock rate
    channel_count   -- number of channels
    avg_bps         -- average bandwidth in bits per second
    frm_ptime       -- base frame length in milliseconds
    ptime           -- RTP frame length in milliseconds.
    pt              -- payload type.
    vad_enabled     -- specify if Voice Activity Detection is currently
                       enabled.
    plc_enabled     -- specify if Packet Lost Concealment is currently
                       enabled.
    """
    name = ""
    priority = 0
    clock_rate = 0
    channel_count = 0
    avg_bps = 0
    frm_ptime = 0
    ptime = 0
    pt = 0
    vad_enabled = False
    plc_enabled = False

    def __init__(self, codec_info, codec_param):
        self.name = codec_info.id
        self.priority = codec_info.priority
        self.clock_rate = codec_param.info.clock_rate
        self.channel_count = codec_param.info.channel_count
        self.avg_bps = codec_param.info.avg_bps
        self.frm_ptime = codec_param.info.frm_ptime
        self.ptime = codec_param.info.frm_ptime * \
                        codec_param.setting.frm_per_pkt
        self.ptime = codec_param.info.pt
        self.vad_enabled = codec_param.setting.vad
        self.plc_enabled = codec_param.setting.plc

    def _cvt_to_pjsua(self):
        ci = _pjsua.Codec_Info()
        ci.id = self.name
        ci.priority = self.priority
        return ci


# Codec parameter
class CodecParameter:
    """This specifies various parameters that can be configured for codec.

    Member documentation:

    ptime       -- specify the outgoing RTP packet length in milliseconds.
    vad_enabled -- specify if VAD should be enabled.
    plc_enabled -- specify if PLC should be enabled.
    """
    ptime = 0
    vad_enabled = False
    plc_enabled = False
    _codec_param = None
    
    def __init__(self, codec_param):
        self.ptime = codec_param.info.frm_ptime * \
                        codec_param.setting.frm_per_pkt
        self.vad_enabled = codec_param.setting.vad
        self.plc_enabled = codec_param.setting.plc
        self._codec_param = codec_param

    def _cvt_to_pjsua(self):
        self._codec_param.setting.frm_per_pkt = self.ptime / \
                                                self._codec_param.info.frm_ptime
        self._codec_param.setting.vad = self.vad_enabled
        self._codec_param.setting.plc = self.plc_enabled
        return self._codec_param


# PJSUA Library
_lib = None
class Lib:
    """Library instance.
    
    """
    call = {}
    account = {}
    buddy = {}
    buddy_by_uri = {}
    buddy_by_contact = {}
    _quit = False
    _has_thread = False

    def __init__(self):
        global _lib
        if _lib:
            raise Error("__init()__", None, -1, 
                        "Library instance already exist")
            
        err = _pjsua.create()
        self._err_check("_pjsua.create()", None, err)
        _lib = self

    def __del__(self):
        _pjsua.destroy()

    def __str__(self):
        return "Lib"

    @staticmethod
    def instance():
        """Return singleton instance of Lib.
        """
        return _lib

    def init(self, ua_cfg=None, log_cfg=None, media_cfg=None):
        """
        Initialize pjsua with the specified configurations.

        Keyword arguments:
        ua_cfg      -- optional UAConfig instance
        log_cfg     -- optional LogConfig instance
        media_cfg   -- optional MediaConfig instance

        """
        if not ua_cfg: ua_cfg = UAConfig()
        if not log_cfg: log_cfg = LogConfig()
        if not media_cfg: media_cfg = MediaConfig()

        py_ua_cfg = ua_cfg._cvt_to_pjsua()
        py_ua_cfg.cb.on_call_state = _cb_on_call_state
        py_ua_cfg.cb.on_incoming_call = _cb_on_incoming_call
        py_ua_cfg.cb.on_call_media_state = _cb_on_call_media_state
        py_ua_cfg.cb.on_dtmf_digit = _cb_on_dtmf_digit
        py_ua_cfg.cb.on_call_transfer_request = _cb_on_call_transfer_request
        py_ua_cfg.cb.on_call_transfer_status = _cb_on_call_transfer_status
        py_ua_cfg.cb.on_call_replace_request = _cb_on_call_replace_request
        py_ua_cfg.cb.on_call_replaced = _cb_on_call_replaced
        py_ua_cfg.cb.on_reg_state = _cb_on_reg_state
        py_ua_cfg.cb.on_buddy_state = _cb_on_buddy_state
        py_ua_cfg.cb.on_pager = _cb_on_pager
        py_ua_cfg.cb.on_pager_status = _cb_on_pager_status
        py_ua_cfg.cb.on_typing = _cb_on_typing

        err = _pjsua.init(py_ua_cfg, log_cfg._cvt_to_pjsua(), 
                            media_cfg._cvt_to_pjsua())
        self._err_check("init()", self, err)

    def destroy(self):
        """Destroy the library, and pjsua."""
        global _lib
        if self._has_thread:
            self._quit = 1
            loop = 0
            while self._quit != 2 and loop < 400:
                _pjsua.handle_events(50)
                loop = loop + 1
        _pjsua.destroy()
        _lib = None
        
    def start(self, with_thread=True):
        """Start the library. 

        Keyword argument:
        with_thread -- specify whether the module should create worker
                       thread.

        """
        err = _pjsua.start()
        self._err_check("start()", self, err)
        self._has_thread = with_thread
        if self._has_thread:
            thread.start_new(_worker_thread_main, (0,))

    def handle_events(self, timeout=50):
        """Poll the events from underlying pjsua library.
        
        Application must poll the stack periodically if worker thread
        is disable when starting the library.

        Keyword argument:
        timeout -- in milliseconds.

        """
        return _pjsua.handle_events(timeout)

    def verify_sip_url(self, sip_url):
        """Verify that the specified string is a valid URI. 
        
        Keyword argument:
        sip_url -- the URL string.
        
        Return:
            0 is the the URI is valid, otherwise the appropriate error 
            code is returned.

        """
        return _pjsua.verify_sip_url(sip_url)

    def create_transport(self, type, cfg=None):
        """Create SIP transport instance of the specified type. 
        
        Keyword arguments:
        type    -- transport type from TransportType constant.
        cfg     -- TransportConfig instance

        Return:
            Transport object

        """
        if not cfg: cfg=TransportConfig(type)
        err, tp_id = _pjsua.transport_create(type, cfg._cvt_to_pjsua())
        self._err_check("create_transport()", self, err)
        return Transport(self, tp_id)

    def create_account(self, acc_config, set_default=True):
        """
        Create a new local pjsua account using the specified configuration.

        Keyword arguments:
        acc_config  -- AccountConfig
        set_default -- boolean to specify whether to use this as the
                       default account.

        Return:
            Account instance

        """
        err, acc_id = _pjsua.acc_add(acc_config._cvt_to_pjsua(), set_default)
        self._err_check("create_account()", self, err)
        return Account(self, acc_id)

    def create_account_for_transport(self, transport, set_default=True):
        """Create a new local pjsua transport for the specified transport.

        Keyword arguments:
        transport   -- the Transport instance.
        set_default -- boolean to specify whether to use this as the
                       default account.

        Return:
            Account instance

        """
        err, acc_id = _pjsua.acc_add_local(transport._id, set_default)
        self._err_check("create_account_for_transport()", self, err)
        return Account(self, acc_id)

    def hangup_all(self):
        """Hangup all calls.

        """
        _pjsua.call_hangup_all()

    # Sound device API

    def enum_snd_dev(self):
        """Enumerate sound devices in the system.

        Return:
            array of SoundDeviceInfo. The index of the element specifies
            the device ID for the device.
        """
        sdi_array = _pjsua.enum_snd_devs()
        info = []
        for sdi in sdi_array:
            info.append(SoundDeviceInfo(sdi))
        return info

    def get_snd_dev(self):
        """Get the device IDs of current sound devices used by pjsua.

        Return:
            (capture_dev_id, playback_dev_id) tuple
        """
        return _pjsua.get_snd_dev()

    def set_snd_dev(self, capture_dev, playback_dev):
        """Change the current sound devices.

        Keyword arguments:
        capture_dev  -- the device ID of capture device to be used
        playback_dev -- the device ID of playback device to be used.

        """
        err = _pjsua.set_snd_dev(capture_dev, playback_dev)
        self._err_check("set_current_sound_devices()", self, err)
    
    def set_null_snd_dev(self):
        """Disable the sound devices. This is useful if the system
        does not have sound device installed.

        """
        err = _pjsua.set_null_snd_dev()
        self._err_check("set_null_snd_dev()", self, err)

    
    # Conference bridge

    def conf_get_max_ports(self):
        """Get the conference bridge capacity.

        Return:
            conference bridge capacity.

        """
        return _pjsua.conf_get_max_ports()

    def conf_connect(self, src_slot, dst_slot):
        """Establish unidirectional media flow from souce to sink. 
        
        One source may transmit to multiple destinations/sink. And if 
        multiple sources are transmitting to the same sink, the media 
        will be mixed together. Source and sink may refer to the same ID, 
        effectively looping the media.

        If bidirectional media flow is desired, application needs to call
        this function twice, with the second one having the arguments 
        reversed.

        Keyword arguments:
        src_slot    -- integer to identify the conference slot number of
                       the source/transmitter.
        dst_slot    -- integer to identify the conference slot number of    
                       the destination/receiver.

        """
        err = _pjsua.conf_connect(src_slot, dst_slot)
        self._err_check("conf_connect()", self, err)
    
    def conf_disconnect(self, src_slot, dst_slot):
        """Disconnect media flow from the source to destination port.

        Keyword arguments:
        src_slot    -- integer to identify the conference slot number of
                       the source/transmitter.
        dst_slot    -- integer to identify the conference slot number of    
                       the destination/receiver.

        """
        err = _pjsua.conf_disconnect(src_slot, dst_slot)
        self._err_check("conf_disconnect()", self, err)

    # Codecs API

    def enum_codecs(self):
        """Return list of codecs supported by pjsua.

        Return:
            array of CodecInfo

        """
        ci_array = _pjsua.enum_codecs()
        codec_info = []
        for ci in ci_array:
            cp = _pjsua.codec_get_param(ci.id)
            if cp:
                codec_info.append(CodecInfo(ci, cp))
        return codec_info

    def set_codec_priority(self, name, priority):
        """Change the codec priority.

        Keyword arguments:
        name     -- Codec name
        priority -- Codec priority, which range is 0-255.

        """
        err = _pjsua.codec_set_priority(name, priority)
        self._err_check("set_codec_priority()", self, err)

    def get_codec_parameter(self, name):
        """Get codec parameter for the specified codec.

        Keyword arguments:
        name    -- codec name.

        """
        cp = _pjsua.codec_get_param(name)
        if not cp:
            self._err_check("get_codec_parameter()", self, -1, 
                            "Invalid codec name")
        return CodecParameter(cp)

    def set_codec_parameter(self, name, param):
        """Modify codec parameter for the specified codec.

        Keyword arguments:
        name    -- codec name
        param   -- codec parameter.

        """
        err = _pjsua.codec_set_param(name, param._cvt_to_pjsua())
        self._err_check("set_codec_parameter()", self, err)
    
    # WAV playback and recording

    def create_player(self, filename, loop=False):
        """Create WAV file player.

        Keyword arguments
        filename    -- WAV file name
        loop        -- boolean to specify wheter playback shoudl
                       automatically restart
        Return:
            WAV player ID

        """
        opt = 0
        if not loop:
            opt = opt + 1
        err, player_id = _pjsua.player_create(filename, opt)
        self._err_check("create_player()", self, err)
        return player_id
        
    def player_get_slot(self, player_id):
        """Get the conference port ID for the specified player.

        Keyword arguments:
        player_id  -- the WAV player ID
        
        Return:
            Conference slot number for the player

        """
        slot = _pjsua.player_get_conf_port(player_id)
        self._err_check("player_get_slot()", self, -1, "Invalid player id")
        return slot

    def player_set_pos(self, player_id, pos):
        """Set WAV playback position.

        Keyword arguments:
        player_id   -- WAV player ID
        pos         -- playback position, in samples

        """
        err = _pjsua.player_set_pos(player_id, pos)
        self._err_check("player_set_pos()", self, err)
        
    def player_destroy(self, player_id):
        """Destroy the WAV player.

        Keyword arguments:
        player_id   -- the WAV player ID.

        """
        err = _pjsua.player_destroy(player_id)
        self._err_check("player_destroy()", self, err)

    def create_recorder(self, filename):
        """Create WAV file recorder.

        Keyword arguments
        filename    -- WAV file name

        Return:
            WAV recorder ID

        """
        err, rec_id = _pjsua.recorder_create(filename, 0, None, -1, 0)
        self._err_check("create_recorder()", self, err)
        return rec_id
        
    def recorder_get_slot(self, rec_id):
        """Get the conference port ID for the specified recorder.

        Keyword arguments:
        rec_id  -- the WAV recorder ID
        
        Return:
            Conference slot number for the recorder

        """
        slot = _pjsua.recorder_get_conf_port(rec_id)
        self._err_check("recorder_get_slot()", self, -1, "Invalid recorder id")
        return slot

    def recorder_destroy(self, rec_id):
        """Destroy the WAV recorder.

        Keyword arguments:
        rec_id   -- the WAV recorder ID.

        """
        err = _pjsua.recorder_destroy(rec_id)
        self._err_check("recorder_destroy()", self, err)


    # Internal functions

    @staticmethod
    def strerror(err):
        return _pjsua.strerror(err)
    
    def _err_check(self, op_name, obj, err_code, err_msg=""):
        if err_code != 0:
            raise Error(op_name, obj, err_code, err_msg)

    @staticmethod
    def _create_msg_data(hdr_list):
        if not hdr_list:
            return None
        msg_data = _pjsua.Msg_Data()
        msg_data.hdr_list = hdr_list
        return msg_data
    
    # Internal dictionary manipulation for calls, accounts, and buddies

    def _associate_call(self, call_id, call):
        self.call[call_id] = call

    def _lookup_call(self, call_id):
        return self.call.has_key(call_id) and self.call[call_id] or None

    def _disassociate_call(self, call):
        if self._lookup_call(call._id)==call:
            del self.call[call._id]

    def _associate_account(self, acc_id, account):
        self.account[acc_id] = account

    def _lookup_account(self, acc_id):
        return self.account.has_key(acc_id) and self.account[acc_id] or None

    def _disassociate_account(self, account):
        if self._lookup_account(account._id)==account:
            del self.account[account._id]

    def _associate_buddy(self, buddy_id, buddy):
        self.buddy[buddy_id] = buddy
        uri = SIPUri(buddy.info().uri)
        self.buddy_by_uri[(uri.user, uri.host)] = buddy

    def _lookup_buddy(self, buddy_id, uri=None):
        print "lookup_buddy, id=", buddy_id
        buddy = self.buddy.has_key(buddy_id) and self.buddy[buddy_id] or None
        if uri and not buddy:
            sip_uri = SIPUri(uri)
            print "lookup_buddy, uri=", sip_uri.user, sip_uri.host
            buddy = self.buddy_by_uri.has_key( (sip_uri.user, sip_uri.host) ) \
                    and self.buddy_by_uri[(sip_uri.user, sip_uri.host)] or \
                    None
        return buddy 

    def _disassociate_buddy(self, buddy):
        if self._lookup_buddy(buddy._id)==buddy:
            del self.buddy[buddy._id]
        if self.buddy_by_uri.has_key(buddy.info().uri):
            del self.buddy_by_uri[buddy.info().uri]

    # Account allbacks

    def _cb_on_reg_state(self, acc_id):
        acc = self._lookup_account(acc_id)
        if acc:
            acc._cb.on_reg_state()

    def _cb_on_incoming_call(self, acc_id, call_id, rdata):
        acc = self._lookup_account(acc_id)
        if acc:
            acc._cb.on_incoming_call( Call(self, call_id) )
        else:
            _pjsua.call_hangup(call_id, 603, None, None)

    # Call callbacks 

    def _cb_on_call_state(self, call_id):
        call = self._lookup_call(call_id)
        if call:
            call._cb.on_state()

    def _cb_on_call_media_state(self, call_id):
        call = self._lookup_call(call_id)
        if call:
            call._cb.on_media_state()

    def _cb_on_dtmf_digit(self, call_id, digits):
        call = self._lookup_call(call_id)
        if call:
            call._cb.on_dtmf_digit(digits)

    def _cb_on_call_transfer_request(self, call_id, dst, code):
        call = self._lookup_call(call_id)
        if call:
            return call._cb.on_transfer_request(dst, code)
        else:
            return 603

    def _cb_on_call_transfer_status(self, call_id, code, text, final, cont):
        call = self._lookup_call(call_id)
        if call:
            return call._cb.on_transfer_status(code, text, final, cont)
        else:
            return cont

    def _cb_on_call_replace_request(self, call_id, rdata, code, reason):
        call = self._lookup_call(call_id)
        if call:
            return call._cb.on_replace_request(code, reason)
        else:
            return code, reason

    def _cb_on_call_replaced(self, old_call_id, new_call_id):
        old_call = self._lookup_call(old_call_id)
        new_call = self._lookup_call(new_call_id)
        if old_call and new_call:
            old_call._cb.on_replaced(new_call)

    def _cb_on_pager(self, call_id, from_uri, to_uri, contact, mime_type, 
                     body, acc_id):
        call = None
        if call_id == -1:
            call = self._lookup_call(call_id)
        if call:
            call._cb.on_pager(mime_type, body)
        else:
            acc = self._lookup_account(acc_id)
            buddy = self._lookup_buddy(-1, from_uri)
            if buddy:
                buddy._cb.on_pager(mime_type, body)
            else:
                acc._cb.on_pager(from_uri, contact, mime_type, body)

    def _cb_on_pager_status(self, call_id, to_uri, body, user_data, 
                            code, reason, acc_id):
        call = None
        if call_id == -1:
            call = self._lookup_call(call_id)
        if call:
            call._cb.on_pager_status(body, user_data, code, reason)
        else:
            acc = self._lookup_account(acc_id)
            buddy = self._lookup_buddy(-1, to_uri)
            if buddy:
                buddy._cb.on_pager_status(body, user_data, code, reason)
            else:
                acc._cb.on_pager_status(to_uri, body, user_data, code, reason)

    def _cb_on_typing(self, call_id, from_uri, to_uri, contact, is_typing, 
                      acc_id):
        call = None
        if call_id == -1:
            call = self._lookup_call(call_id)
        if call:
            call._cb.on_typing(is_typing)
        else:
            acc = self._lookup_account(acc_id)
            buddy = self._lookup_buddy(-1, from_uri)
            if buddy:
                buddy._cb.on_typing(is_typing)
            else:
                acc._cb.on_typing(from_uri, contact, is_typing)

    def _cb_on_buddy_state(self, buddy_id):
        buddy = self._lookup_buddy(buddy_id)
        if buddy:
            buddy._cb.on_state()




#
# Internal
#

def _cb_on_call_state(call_id, e):
    _lib._cb_on_call_state(call_id)

def _cb_on_incoming_call(acc_id, call_id, rdata):
    _lib._cb_on_incoming_call(acc_id, call_id, rdata)

def _cb_on_call_media_state(call_id):
    _lib._cb_on_call_media_state(call_id)

def _cb_on_dtmf_digit(call_id, digits):
    _lib._cb_on_dtmf_digit(call_id, digits)

def _cb_on_call_transfer_request(call_id, dst, code):
    return _lib._cb_on_call_transfer_request(call_id, dst, code)

def _cb_on_call_transfer_status(call_id, code, reason, final, cont):
    return _lib._cb_on_call_transfer_status(call_id, code, reason, 
                                             final, cont)
def _cb_on_call_replace_request(call_id, rdata, code, reason):
    return _lib._cb_on_call_replace_request(call_id, rdata, code, reason)

def _cb_on_call_replaced(old_call_id, new_call_id):
    _lib._cb_on_call_replaced(old_call_id, new_call_id)

def _cb_on_reg_state(acc_id):
    _lib._cb_on_reg_state(acc_id)

def _cb_on_buddy_state(buddy_id):
    _lib._cb_on_buddy_state(buddy_id)

def _cb_on_pager(call_id, from_uri, to, contact, mime_type, body, acc_id):
    _lib._cb_on_pager(call_id, from_uri, to, contact, mime_type, body, acc_id)

def _cb_on_pager_status(call_id, to, body, user_data, status, reason, acc_id):
    _lib._cb_on_pager_status(call_id, to, body, user_data, 
                             status, reason, acc_id)

def _cb_on_typing(call_id, from_uri, to, contact, is_typing, acc_id):
    _lib._cb_on_typing(call_id, from_uri, to, contact, is_typing, acc_id)


# Worker thread
def _worker_thread_main(arg):
    global _lib
    thread_desc = 0;
    err = _pjsua.thread_register("python worker", thread_desc)
    _lib._err_check("thread_register()", _lib, err)
    while _lib._quit == 0:
        _pjsua.handle_events(50)
    _lib._quit = 2

