# Object Search

We make use of event checker-handlers:
* button press is managed by VEX event handler
* same with the timer
* lost objects are checked in the main loop

Unfortunately, VEX has no way to cancel a timer, so "turning the timer off" is a little convoluted -- basically, we let the last timer expire and then don't restart it. Same with resetting -- it would be nice to just restart the timer when we detect an object, but the library doesn't work that way. The management has been notified.

<img title="State Transition Diagram" src="docs/State Machine for Object Search Demo.png">
