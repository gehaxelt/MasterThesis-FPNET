    all_elements = document.getElementsByTagName("*");

    // generated using
    /*
      const types = [];
      for (let ev in window) {
        if (/^on/.test(ev)) types[types.length] = ev;
      }
     */

    counts = {"sum": 0, "attr": {}, "handler": {}, "jquery": {}}

    events = [
    "ondevicemotion",
    "ondeviceorientation",
    "onabsolutedeviceorientation",
    "ondeviceproximity",
    "onuserproximity",
    "ondevicelight",
    "onabort",
    "onblur",
    "onfocus",
    "onauxclick",
    "oncanplay",
    "oncanplaythrough",
    "onchange",
    "onclick",
    "onclose",
    "oncontextmenu",
    "oncuechange",
    "ondblclick",
    "ondrag",
    "ondragend",
    "ondragenter",
    "ondragexit",
    "ondragleave",
    "ondragover",
    "ondragstart",
    "ondrop",
    "ondurationchange",
    "onemptied",
    "onended",
    "onformdata",
    "oninput",
    "oninvalid",
    "onkeydown",
    "onkeypress",
    "onkeyup",
    "onload",
    "onloadeddata",
    "onloadedmetadata",
    "onloadend",
    "onloadstart",
    "onmousedown",
    "onmouseenter",
    "onmouseleave",
    "onmousemove",
    "onmouseout",
    "onmouseover",
    "onmouseup",
    "onwheel",
    "onpause",
    "onplay",
    "onplaying",
    "onprogress",
    "onratechange",
    "onreset",
    "onresize",
    "onscroll",
    "onseeked",
    "onseeking",
    "onselect",
    "onshow",
    "onstalled",
    "onsubmit",
    "onsuspend",
    "ontimeupdate",
    "onvolumechange",
    "onwaiting",
    "onselectstart",
    "ontoggle",
    "onpointercancel",
    "onpointerdown",
    "onpointerup",
    "onpointermove",
    "onpointerout",
    "onpointerover",
    "onpointerenter",
    "onpointerleave",
    "ongotpointercapture",
    "onlostpointercapture",
    "onmozfullscreenchange",
    "onmozfullscreenerror",
    "onanimationcancel",
    "onanimationend",
    "onanimationiteration",
    "onanimationstart",
    "ontransitioncancel",
    "ontransitionend",
    "ontransitionrun",
    "ontransitionstart",
    "onwebkitanimationend",
    "onwebkitanimationiteration",
    "onwebkitanimationstart",
    "onwebkittransitionend",
    "onerror",
    "onafterprint",
    "onbeforeprint",
    "onbeforeunload",
    "onhashchange",
    "onlanguagechange",
    "onmessage",
    "onmessageerror",
    "onoffline",
    "ononline",
    "onpagehide",
    "onpageshow",
    "onpopstate",
    "onrejectionhandled",
    "onstorage",
    "onunhandledrejection",
    "onunload"
    ]


    for(i = 0; i < all_elements.length; i++) {
        the_element = all_elements[i]
        attrs = the_element.attributes

        try {
            // Check for events using on-attributes
            for(j = 0; j < attrs.length; j++) {
                attr_name = attrs[j].nodeName
                if(! /^on/.test(attr_name)) {
                    continue
                }

                attr_name in counts["attr"] ? counts["attr"][attr_name] += 1 : counts["attr"][attr_name] = 1
                counts["sum"] +=1
            }
        } catch(e) {}

        try {
            // Check for events using elem.on* = function() deklaration
            for(j = 0; j < events.length; j++) {
                if(the_element[events[j]] != null) {
                    events[j] in counts["handler"] ? counts["handler"][events[j]] += 1 : counts["handler"][events[j]] = 1
                    counts["sum"] +=1
                }
            }
        } catch(e) {}

        try {
            if(window)  {
                if(window.$ && ($._data || $.data)) {
                    $.each(($._data || $.data)($(the_element)[0], "events" ), function(e) {
                        e in counts["jquery"] ? counts["jquery"][e] += 1 : counts["jquery"][e] = 1
                        counts["sum"] +=1
                    });
                } else if(window.jQuery && (jQuery._data || jQuery.data)) {
                    jQuery.each((jQuery._data || jQuery.data)(jQuery(the_element)[0], "events" ), function(e) {
                        e in counts["jquery"] ? counts["jquery"][e] += 1 : counts["jquery"][e] = 1
                        counts["sum"] +=1
                    });
                }
            }
        } catch(e) {}
    }

    return JSON.stringify(counts)