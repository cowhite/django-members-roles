Events
======

tabname-opened
---------------

Whenever a tab/url is switched, an event will be fired. If the tab name is "learn", then fired event is "learn-opened"

You can catch the event and then write necessary code::

    $(document).on("tabname-opened", function(){
        // Implement code here
    })