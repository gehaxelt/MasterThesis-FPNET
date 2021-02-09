### fpmon/master content.js

fp_userAgent = ["navigator.userAgent"];
fp_platform = ["navigator.platform"];
fp_enabled_cookies = ["navigator.cookieEnabled"];
fp_timezone = ["getTimezoneOffset()", "window.Intl"];
fp_content_language = ["navigator.languages", "navigator.userLanguage","navigator.language" ];
fp_canvas = ['getImageData()', 'getLineDash()', 'measureText()', 'isPointInPath()', 
    ];
fp_audio = ["createAnalyser()",'createOscillator()', 'createGain()', 'createScriptProcessor()', 'createDynamicsCompressor()'];
fp_jsfonts = ['fill()', 'fillText()']; 
fp_donottrack = ["navigator.doNotTrack", "navigator.msDoNotTrack", ];
fp_buildID = ["navigator.buildID"];
fp_product = ["navigator.product", ]
fp_product_sub = ["navigator.productSub", ]
fp_vendor = ["navigator.vendor", ];
fp_vendor_sub = ["navigator.vendorSub", ]
fp_hardwareConcurrency = ["navigator.hardwareConcurrency"];
fp_java_enabled = ["navigator.enabled"];
fp_device_memory = ["navigator.deviceMemory"];
fp_list_of_plugins = ["navigator.plugins", ];
fp_permissions = ["navigator.permissions"];

fp_webgl = ['getParameter()', 'getSupportedExtensions()', 'getContextAttributes()',
      'getShaderPrecisionFormat()', 'getExtension()', 'readPixels()', 'getUniformLocation()',
      'getAttribLocation()', 'clearColor()', 'enable()', 'depthFunc()', 'clear()', 'createBuffer()', 'bindBuffer()', 'bufferData()',
      'createProgram()', 'createShader()', 'shaderSource()', 'compileShader()', 'attachShader()', 'linkProgram()', 'useProgram()', 'drawArrays()'
    ];
fp_storage = ["window.sessionStorage", "window.localStorage", "window.indexedDB", "window.openDatabase", "navigator.webkitTemporaryStorage",
      "navigator.webkitPersistentStorage", "navigator.openDatabase", "navigator.localStorage",
    ];
fp_audio_video_formats = ["canPlayType()"];
fp_media_devices = ["navigator.mediaDevices", ];
fp_frequency_analyzer = ['getFloatFrequencyData()', 'getByteFrequencyData()',
      'getFloatTimeDomainData()', 'getByteTimeDomainData()'
    ];
fp_battery = ["navigator.getBattery", ]; 
fp_oscpu = ["navigator.oscpu"];
fp_webdriver = ["window.webdriver", "navigator.webdriver"];
fp_cpuClass = ["navigator.cpuClass"];
fp_geolocation = ["navigator.geolocation"];
fp_appCodeName = ["navigator.appCodeName"];
fp_appName = ["navigator.appName"];
fp_appVersion = ["navigator.appVersion"];
fp_navigator_onLine = ["navigator.onLine"];
fp_browser_language = ["navigator.browserLanguage", ];
fp_system_language = ["navigator.systemLanguage", ];
fp_dragDrop = ["navigator.dragDrop", ];
fp_flash = ["window.swfobject"];
fp_connection = ["navigator.connection"];
fp_mobile = ["window.ondeviceproximity", "window.onuserproximity", "window.DeviceOrientationEvent", "window.DeviceMotionEvent", "navigator.maxTouchPoints", "navigator.msMaxTouchPoints", "navigator.touch"];
fp_screen_window = ["window.devicePixelRatio", "window.innerWidth", "window.innerHeight","window.emit", "window.outerWidth", "window.outerHeight", "screen.colorDepth", "screen.width", "screen.availWidth", "screen.availHeight",
      "screen.pixelDepth", "screen.height", "screen.availTop", "screen.availLeft", "screen.deviceXDPI", "screen.logicalXDPI", "screen.fontSmoothingEnabled", 
      "screen.screenInfo","navigator.orientation"]



CATEGORY_MAPPING = {
# JS / HTML
"Canvas":fp_canvas,
"JS_fonts":fp_jsfonts,
"List_of_plugins":fp_list_of_plugins,
"WebGL":fp_webgl,
"Webdriver":fp_webdriver,
"Flash":fp_flash,
"Cookies_enabled":fp_enabled_cookies,
"Java_enabled":fp_java_enabled,

# media
"Audio_Video_formats":fp_audio_video_formats,
"Audio":fp_audio,
"Media_devices":fp_media_devices,
"Frequency_analyzer":fp_frequency_analyzer,

# language / location / connection
"Geolocation":fp_geolocation,
"Connection":fp_connection,
"Timezone":fp_timezone,
"Content_language":fp_content_language,
"Browser_language":fp_browser_language,
"System_language":fp_system_language,
"Online":fp_navigator_onLine,

# software
"User_agent":fp_userAgent,
"App_version":fp_appVersion,
"Build_ID":fp_buildID,
"Permissions":fp_permissions,
"Product":fp_product,
"Product_sub":fp_product_sub,
"Vendor":fp_vendor,
"Vendor_sub":fp_vendor_sub,
"App_code_name":fp_appCodeName,
"App_name":fp_appName,
"Storage":fp_storage,
"Drag_and_drop":fp_dragDrop,
"DoNotTrack":fp_donottrack,
"Platform":fp_platform,

# system
"Oscpu":fp_oscpu,
"Battery_status":fp_battery,
"Device_memory":fp_device_memory,
"Cpu_Class":fp_cpuClass,
"Hardware_concurrency":fp_hardwareConcurrency,

# mobile
"Mobile":fp_mobile,

# window / screen
"Screen_window":fp_screen_window
}

AGGRO_CATS = [
"Canvas",
"JS_fonts",
"List_of_plugins",
"WebGL",
"Webdriver",
"Audio_Video_formats",
"Audio",
"Media_devices",
"Frequency_analyzer",
"Geolocation",
"Connection",
"Permissions",
"Product_sub",
"Oscpu",
"Battery_status",
"Device_memory",
"Hardware_concurrency",
]