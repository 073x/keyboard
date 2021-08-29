# -*- coding: utf-8 -*-
"""
keyboard
========

Take full control of your keyboard with this small Python library. Hook global events, register hotkeys, simulate key presses and much more.

## Features

- **Global event hook** on all keyboards (captures keys regardless of focus).
- **Listen** and **send** keyboard events.
- Works with **Windows** and **Linux** (requires sudo), with experimental **OS X** support (thanks @glitchassassin!).
- **Pure Python**, no C modules to be compiled.
- **Zero dependencies**. Trivial to install and deploy, just copy the files.
- **Python 2 and 3**.
- Complex hotkey support (e.g. `ctrl+shift+m, ctrl+space`) with controllable timeout.
- Includes **high level API** (e.g. [record](#keyboard.record) and [play](#keyboard.play), [add_abbreviation](#keyboard.add_abbreviation)).
- Maps keys as they actually are in your layout, with **full internationalization support** (e.g. `Ctrl+ç`).
- Events automatically captured in separate thread, doesn't block main program.
- Tested and documented.
- Doesn't break accented dead keys (I'm looking at you, pyHook).
- Mouse support available via project [mouse](https://github.com/boppreh/mouse) (`pip install mouse`).

## Usage

Install the [PyPI package](https://pypi.python.org/pypi/keyboard/):

    pip install keyboard

or clone the repository (no installation required, source files are sufficient):

    git clone https://github.com/boppreh/keyboard

or [download and extract the zip](https://github.com/boppreh/keyboard/archive/master.zip) into your project folder.

Then check the [API docs below](https://github.com/boppreh/keyboard#api) to see what features are available.


## Example

Use as library:

```py
import keyboard

keyboard.press_and_release('shift+s, space')

keyboard.write('The quick brown fox jumps over the lazy dog.')

keyboard.add_hotkey('ctrl+shift+a', print, args=('triggered', 'hotkey'))

# Press PAGE UP then PAGE DOWN to type "foobar".
keyboard.add_hotkey('page up, page down', lambda: keyboard.write('foobar'))

# Blocks until you press esc.
keyboard.wait('esc')

# Record events until 'esc' is pressed.
recorded = keyboard.record(until='esc')
# Then replay back at three times the speed.
keyboard.play(recorded, speed_factor=3)

# Type @@ then press space to replace with abbreviation.
keyboard.add_abbreviation('@@', 'my.long.email@example.com')

# Block forever, like `while True`.
keyboard.wait()
```

Use as standalone module:

```bash
# Save JSON events to a file until interrupted:
python -m keyboard > events.txt

cat events.txt
# {"event_type": "down", "scan_code": 25, "name": "p", "time": 1622447562.2994788, "is_keypad": false}
# {"event_type": "up", "scan_code": 25, "name": "p", "time": 1622447562.431007, "is_keypad": false}
# ...

# Replay events
python -m keyboard < events.txt
```

## Known limitations:

- Events generated under Windows don't report device id (`event.device == None`). [#21](https://github.com/boppreh/keyboard/issues/21)
- Media keys on Linux may appear nameless (scan-code only) or not at all. [#20](https://github.com/boppreh/keyboard/issues/20)
- Key suppression/blocking only available on Windows. [#22](https://github.com/boppreh/keyboard/issues/22)
- To avoid depending on X, the Linux parts reads raw device files (`/dev/input/input*`) but this requires root.
- Other applications, such as some games, may register hooks that swallow all key events. In this case `keyboard` will be unable to report events.
- This program makes no attempt to hide itself, so don't use it for keyloggers or online gaming bots. Be responsible.
- SSH connections forward only the text typed, not keyboard events. Therefore if you connect to a server or Raspberry PI that is running `keyboard` via SSH, the server will not detect your key events.

## Common patterns and mistakes

### Preventing the program from closing

```py
import keyboard
keyboard.add_hotkey('space', lambda: print('space was pressed!'))
# If the program finishes, the hotkey is not in effect anymore.

# Don't do this! This will use 100% of your CPU.
#while True: pass

# Use this instead
keyboard.wait()

# or this
import time
while True:
    time.sleep(1000000)
```

### Waiting for a key press one time

```py
import keyboard

# Don't do this! This will use 100% of your CPU until you press the key.
#
#while not keyboard.is_pressed('space'):
#    continue
#print('space was pressed, continuing...')

# Do this instead
keyboard.wait('space')
print('space was pressed, continuing...')
```

### Repeatedly waiting for a key press

```py
import keyboard

# Don't do this!
#
#while True:
#    if keyboard.is_pressed('space'):
#        print('space was pressed!')
#
# This will use 100% of your CPU and print the message many times.

# Do this instead
while True:
    keyboard.wait('space')
    print('space was pressed! Waiting on it again...')

# or this
keyboard.add_hotkey('space', lambda: print('space was pressed!'))
keyboard.wait()
```

### Invoking code when an event happens

```py
import keyboard

# Don't do this! This will call `print('space')` immediately then fail when the key is actually pressed.
#keyboard.add_hotkey('space', print('space was pressed'))

# Do this instead
keyboard.add_hotkey('space', lambda: print('space was pressed'))

# or this
def on_space():
    print('space was pressed')
keyboard.add_hotkey('space', on_space)
```

### 'Press any key to continue'

```py
# Don't do this! The `keyboard` module is meant for global events, even when your program is not in focus.
#import keyboard
#print('Press any key to continue...')
#keyboard.get_event()

# Do this instead
input('Press enter to continue...')

# Or one of the suggestions from here
# https://stackoverflow.com/questions/983354/how-to-make-a-script-wait-for-a-pressed-key
```
"""
from __future__ import print_function as _print_function

version = '0.13.5'

import re as _re
import itertools as _itertools
import collections as _collections
import threading as _threading
import time as _time
# Python2... Buggy on time changes and leap seconds, but no other good option (https://stackoverflow.com/questions/1205722/how-do-i-get-monotonic-time-durations-in-python).
_time.monotonic = getattr(_time, 'monotonic', None) or _time.time

try:
    # Python2
    long, basestring
    _is_str = lambda x: isinstance(x, basestring)
    _is_number = lambda x: isinstance(x, (int, long))
    import Queue as _queue
    # threading.Event is a function in Python2 wrapping _Event (?!).
    from threading import _Event as _UninterruptibleEvent
except NameError:
    # Python3
    _is_str = lambda x: isinstance(x, str)
    _is_number = lambda x: isinstance(x, int)
    import queue as _queue
    from threading import Event as _UninterruptibleEvent
_is_list = lambda x: isinstance(x, (list, tuple))

# The "Event" class from `threading` ignores signals when waiting and is
# impossible to interrupt with Ctrl+C. So we rewrite `wait` to wait in small,
# interruptible intervals.
class _Event(_UninterruptibleEvent):
    def wait(self):
        while True:
            if _UninterruptibleEvent.wait(self, 0.5):
                break

import platform as _platform
if _platform.system() == 'Windows':
    from. import _winkeyboard as _os_keyboard
elif _platform.system() == 'Linux':
    from. import _nixkeyboard as _os_keyboard
elif _platform.system() == 'Darwin':
    from. import _darwinkeyboard as _os_keyboard
else:
    raise OSError("Unsupported platform '{}'".format(_platform.system()))

from ._keyboard_event import KEY_DOWN, KEY_UP, KeyboardEvent
from ._canonical_names import all_modifiers, sided_modifiers, normalize_name

_modifier_scan_codes = set()
def is_modifier(key):
    """
    Returns True if `key` is a scan code or name of a modifier key.
    """
    if _is_str(key):
        return key in all_modifiers
    else:
        return key in _modifier_scan_codes

class _Enum(object):
    def __init__(self, n, name):
        self.n = n
        self.name = name
    def __lt__(self, other):
        return self.n < other.n
    def __repr__(self):
        return self.name
# Allow the event, if no other hooks SUSPEND'ed or SUPPRESS'ed the event.
ALLOW = _Enum(0, 'ALLOW')
# Temporarily suspend the event if no other hooks SUPPRESS'ed it, to be either
# allowed or suppressed in the future.
SUSPEND = _Enum(1, 'SUSPEND')
# Suppress the event completely, regardless of other hooks decisions.
SUPPRESS = _Enum(2, 'SUPPRESS')

class _KeyboardListener(object): 
    """
    Class for managing hooks and processing keyboard events. Keeps track of which
    keys are pressed (physically and logically), which keys are suspended, etc.
    """
    def __init__(self):
        # Set of scan codes that we've receive KEY_DOWN events but no KEY_UP yet.
        self.physically_pressed_keys = set()
        # Set of scans codes that we've sent or allowed KEY_DOWN events but no KEY_UP yet.
        self.logically_pressed_keys = set()
        # Set of modifiers of currently pressed modifier keys.
        self.active_modifiers = set()
        # Pairs of (event, modifiers).
        self.suspended_event_pairs = []
        # Set when replaying a suspended event, that should not be processed
        # again.
        self.is_replaying = False

        self.suppressing_hooks = []
        self.nonsuppressing_hooks = []
        self.hook_disable_by_id = _collections.defaultdict(set)
        self.async_events_queue = _queue.Queue()

        self.flag_running = _Event()

    def register(self, hook_obj, ids, suppress):
        """
        Registers a hook to process events. Hooks added with suppress=True are
        run in the main blocking thread, and are able to suppress and temporarily
        suspend events.

        The list of ids allows the hook to be removed by id later, such as callback
        or hotkey string.
        """
        hooks_list = self.suppressing_hooks if suppress else self.nonsuppressing_hooks

        # The hook object will be exposed to the user, and it's useful to have
        # `hook_obj.enable()` and `hook_obj.disable()` methods.
        # This could also be done by adding `listener`, `suppress`, and `ids`
        # attributes to the hook, but that's more complicated than just using
        # closures.

        def enable():
            for hook_id in ids:
                self.hook_disable_by_id[hook_id].add(disable)
            hooks_list.append(hook_obj)
        hook_obj.enable = enable

        def disable():
            for hook_id in ids:
                self.hook_disable_by_id[hook_id].discard(disable)
            if hook_obj in hooks_list:
                hooks_list.remove(hook_obj)
        hook_obj.disable = disable

        enable()

        return hook_obj

    def disable_hook_by_id(self, hook_id):
        """
        Removes all the hooks that were added with this id.
        """
        if hasattr(hook_id, 'disable'):
            hook_obj = hook_id
            hook_obj.disable()
        else:
            for hook_disable in list(self.hook_disable_by_id[hook_id]):
                hook_disable()

    def start(self):
        """
        If not yet started, starts the background threads that intercept OS
        events and handles hooks.
        """
        if self.flag_running.is_set():
            return

        self.flag_running.set()

        self.os_listener = _os_keyboard.Listener()
        listening_thread = _threading.Thread(target=lambda: self.os_listener.listen(self.process_sync_event))
        listening_thread.daemon = True
        listening_thread.start()

        # While this thread reads events from the queue and runs hooks
        # asynchronously.
        processing_thread = _threading.Thread(target=self.process_async_queue, args=(self.flag_running,))
        processing_thread.daemon = True
        processing_thread.start()

    def stop(self):
        """
        If currently running, signals the background threads and OS event
        interception to stop. Further events will not be processed, but the
        threads may live a little longer while they wind down.
        """
        if not self.flag_running.is_set():
            return

        self.flag_running.clear()
        self.os_listener.stop()

        # A new flag_running object must be created, otherwise a fast stop/start
        # pair may cause the async thread to never see the flag being cleared.
        # Note that the async thread receives a reference to the flag, so it
        # won't see the new flag_running object.
        self.flag_running = _Event()

    def run_sync_hooks(self, event):
        """
        Passes the given event through all sync hooks registered, deciding to
        allow or suppress the event.
        """
        run_hook = lambda hook: hook.process_event(event, self.physically_pressed_keys, self.logically_pressed_keys, self.active_modifiers)
        hooks_decisions = [run_hook(hook) for hook in self.suppressing_hooks] or [{}]
        temporary_modifiers_state = set(self.active_modifiers)
        _listener.is_replaying = True

        # Check for previously suspended events. Note that decisions for unrelated
        # keys are ignored.
        for suspended_event, suspended_modifiers in list(self.suspended_event_pairs):
            # Use `max` to merge decisions because ALLOW < SUSPEND < SUPPRESS.
            decision = max(decisions.get(suspended_event, ALLOW) for decisions in hooks_decisions)
            if decision is SUSPEND:
                # Suspended event continues suspended. Do nothing.
                pass
            elif decision is SUPPRESS:
                # Suspended event is now suppressed, forget about it.
                self.suspended_event_pairs.remove((suspended_event, suspended_modifiers))
            elif decision is ALLOW:
                # Suspended event is now allowed, replay it.

                # The suspended event may have had a different set of modifiers
                # than what is currently active. We temporarily send fake key
                # presses and releases the match the suspended modifiers,
                # replay the suspended event, then restore the state of the
                # modifiers.
                for modifier in temporary_modifiers_state - suspended_modifiers:
                    _os_keyboard.release(modifier)
                    temporary_modifiers_state.remove(modifier)
                for modifier in suspended_modifiers - temporary_modifiers_state:
                    _os_keyboard.press(modifier)
                    temporary_modifiers_state.add(modifier)

                if suspended_event.event_type == KEY_DOWN:
                    _os_keyboard.press(suspended_event.scan_code)
                else:
                    _os_keyboard.release(suspended_event.scan_code)
                self.suspended_event_pairs.remove((suspended_event, suspended_modifiers))

        # Restore state of modifiers.
        for modifier in self.active_modifiers - temporary_modifiers_state:
            _os_keyboard.press(modifier)
        for modifier in temporary_modifiers_state - self.active_modifiers:
            _os_keyboard.release(modifier)
        _listener.is_replaying = False

        decision = max((decisions.get(event, ALLOW) for decisions in hooks_decisions))
        if decision is SUSPEND:
            self.suspended_event_pairs.append((event, set(self.active_modifiers)))
            return SUPPRESS
        elif decision is SUPPRESS:
            return SUPPRESS
        elif decision is ALLOW:
            return ALLOW

    def process_sync_event(self, event):
        """
        Processes one event, synchronously (blocking the OS from passing the event
        forward). Passes the event through all hooks that could suppress the event,
        and merge their decisions, returning True (the event is allowed) or False
        (the event should be suppressed).

        May replay previously suppressed events that hooks have suspended before
        but marked as allowed now.
        """
        if self.is_replaying:
            decision = ALLOW
        else:
            # Update list of active modifiers and pressed keys.
            if event.event_type == KEY_DOWN:
                self.physically_pressed_keys.add(event.scan_code)
            elif event.event_type == KEY_UP:
                self.physically_pressed_keys.discard(event.scan_code)

            if event.scan_code in _modifier_scan_codes:
                if event.event_type == KEY_DOWN:
                    self.active_modifiers.add(event.scan_code)
                elif event.event_type == KEY_UP:
                    self.active_modifiers.discard(event.scan_code)

            # Send event to be processed by non-blocking hooks.
            self.async_events_queue.put(event)
            decision = self.run_sync_hooks(event)

        if decision is ALLOW:
            if event.event_type == KEY_DOWN:
                self.logically_pressed_keys.add(event.scan_code)
            elif event.event_type == KEY_UP:
                self.logically_pressed_keys.discard(event.scan_code)
            return True
        else:
            return False

    def process_async_queue(self, flag_running):
        """
        Reads events from the queue set up by `process_sync_event`, running the hooks
        that are not capable of suppressing events, asynchronously without blocking
        the OS from passing the event forward.
        """
        while flag_running.is_set():
            try:
                event = self.async_events_queue.get(timeout=3)
            except _queue.Empty:
                continue

            for hook_obj in self.nonsuppressing_hooks:
                # Ignore decisions of non-suppressing hooks.
                _ = hook_obj.process_event(event, self.physically_pressed_keys, self.active_modifiers)

            # Enable tests and others to call `self.async_events_queue.join()`
            # to check when all async events are processed.
            self.async_events_queue.task_done()

def start():
    """
    Starts the global keyboard listener, including background threads, to process
    OS events.
    """
    _listener.start()

def stop():
    """
    Stops the global keyboard listener, and signals the background threads to exit.
    """
    _listener.stop()

def reload():
    """
    Restarts the global keyboard listener, including background threads, and reloads
    the mapping of scan codes to key names.
    """
    stop()
    _os_keyboard.init()
    start()

class _SimpleHook(object):
    """
    A hook that will invoke a user-defined function on every keyboard event,
    passing both a reference to the event and a set of all currently pressed
    scan codes.
    """
    def __init__(self, callback):
        self.callback = callback

    def enable(self):
        # To be overwritten when added to a listener.
        pass

    def disable(self):
        # To be overwritten when added to a listener.
        pass

    def process_event(self, event, physically_pressed_keys, logically_pressed_keys, active_modifiers):
        result = self.callback(event)
        return {event: result if result in (ALLOW, SUSPEND, SUPPRESS) else ALLOW}

def hook(callback, suppress=True):
    hook_obj = _SimpleHook(callback)
    return _listener.register(hook_obj, [callback], suppress)

class _KeyHook(_SimpleHook):
    def __init__(self, scan_codes, callback):
        self.scan_codes = scan_codes
        self.callback = callback

    def process_event(self, event, physically_pressed_keys, logically_pressed_keys, active_modifiers):
        if event.scan_code in self.scan_codes:
            result = self.callback()
            return {event: result if result in (ALLOW, SUPPRESS) else SUPPRESS}
        else:
            return {event: ALLOW}

def hook_key(key, callback, suppress=True):
    hook_obj = _KeyHook(key_to_scan_codes(key), callback)
    return _listener.register(hook_obj, [key, callback], suppress)

class _HotkeyHook(_SimpleHook):
    """
    Hook subclass to detect and trigger callbacks when a hotkey is detected.
    """
    def __init__(self, hotkey, timeout, trigger_on_release, callback):
        self.callback = callback
        self.hotkey = hotkey
        self.timeout = timeout
        self.trigger_on_release = trigger_on_release
        # A set of Finite State Machine transitions based on the current state
        # and input events.
        self.transitions = self.build_hotkey_transition_table(hotkey)

        self.state = 0 
        self.suspended_events = []
        self.scan_code_releases_to_suppress = set()

    def build_hotkey_transition_table(self, hotkey):
            """
            Builds a transition table mapping current hotkey step and received scan code
            to the new step. Technically a Moore-type Finite State Machine.

            transitions[current_state, (1, 2, 3)] -> new_state
            """
            transitions = _collections.defaultdict(lambda: 0)
            get_final_state = lambda sequence, state=0: state if not sequence else get_final_state(sequence[1:], state=transitions[state, sequence[0]])

            history = []
            for i, step in enumerate(hotkey.steps):
                for previous_inputs in set(history):
                    # If a wrong input is given, but which could be the start (or middle)
                    # or a correct sequence, what's the most advanced state it would reach?
                    overlapping_state = max(get_final_state(history[j:] + [previous_inputs]) for j in range(1, len(history)+1))
                    transitions[i, previous_inputs] = overlapping_state

                for input_scan_codes in _itertools.product(*[key.scan_codes for key in step.keys]):
                    transitions[i, tuple(sorted(input_scan_codes))] = i+1

                history.append(input_scan_codes)

            return transitions

    def process_event(self, event, physically_pressed_keys, logically_pressed_keys, active_modifiers):
        """
        Processes receiving events, updating its current state and calling
        `callback` whenever the hotkey is completed.

        Most of this code is to keep track of what events have been suspended
        or suppressed, to return the correct decision to the listener.
        """
        #breakpoint()
        events_to_suppress = []
        step = self.hotkey.steps[min(self.state, len(self.hotkey.steps)-1)] 
        is_main_key = event.scan_code in step.main_key.scan_codes if step.is_standard else any(event.scan_code in key.scan_codes for key in step.keys)

        if event.event_type == KEY_UP:
            if event.scan_code in [suspended_event.scan_code for suspended_event in self.suspended_events]:
                # The KEY_UP for a suspended KEY_DOWN. Suspend it too.
                self.suspended_events.append(event)
            elif event.scan_code in self.scan_code_releases_to_suppress:
                events_to_suppress.append(event)
                self.scan_code_releases_to_suppress.remove(event.scan_code)
        elif event.scan_code in _modifier_scan_codes and step.is_standard:
            pass
        elif self.state < len(self.hotkey.steps):
            if self.suspended_events and event.time - max(e.time for e in self.suspended_events) >= self.timeout:
                self.state = 0
                self.suspended_events.clear()

            if step.is_standard:
                input_scan_codes = tuple(sorted([event.scan_code] + list(active_modifiers)))
            else:
                input_scan_codes = tuple(sorted(list(physically_pressed_keys)))

            self.suspended_events.append(event)

            if step.is_standard or len(physically_pressed_keys) >= len(step.keys) or not is_main_key:
                self.state = self.transitions[self.state, input_scan_codes]

                # How many key presses it took to get to this state.
                n_useful_presses_left = sum(1 if step.is_standard else len(step.keys) for step in self.hotkey.steps[:self.state])
                for suspended_event in sorted(self.suspended_events, key=lambda e: e.time, reverse=True):
                    # Every key press beyond this point is not useful for this hotkey, and should be allowed.
                    if n_useful_presses_left <= 0:
                        self.suspended_events.remove(suspended_event)
                    if suspended_event.event_type == KEY_DOWN:
                        n_useful_presses_left -= 1

        if self.state == len(self.hotkey.steps) and is_main_key and (event.event_type == KEY_UP if self.trigger_on_release else KEY_DOWN):
            if self.callback() is not ALLOW:
                for suspended_event in self.suspended_events:
                    is_logically_pressed = suspended_event.scan_code in logically_pressed_keys

                    if not (suspended_event.event_type == KEY_UP and is_logically_pressed):
                        events_to_suppress.append(suspended_event)

                    if suspended_event.event_type == KEY_DOWN and not is_logically_pressed:
                        self.scan_code_releases_to_suppress.add(suspended_event.scan_code)
                    elif suspended_event.event_type == KEY_UP:
                        self.scan_code_releases_to_suppress.discard(suspended_event.scan_code)
            self.state = 0
            self.suspended_events.clear()

        return {**{suspended_event: SUSPEND for suspended_event in self.suspended_events}, **{e: SUPPRESS for e in events_to_suppress}}

def add_hotkey(hotkey, callback, args=(), suppress=True, timeout=1, trigger_on_release=False):
    if args:
        callback = lambda f=callback: f(*args)

    parsed_hotkey = parse_hotkey(hotkey)
    hook_obj = _HotkeyHook(hotkey=parsed_hotkey, callback=callback, timeout=timeout, trigger_on_release=trigger_on_release)
    return _listener.register(hook_obj, suppress=suppress, ids=[callback, hotkey])

def key_to_scan_codes(key, error_if_missing=True):
    """
    Returns a list of scan codes associated with this key (name or scan code).
    """
    if _is_number(key):
        return (key,)
    elif _is_list(key):
        return sum((key_to_scan_codes(i) for i in key), ())
    elif not _is_str(key):
        raise ValueError('Unexpected key type ' + str(type(key)) + ', value (' + repr(key) + ')')

    normalized = normalize_name(key)
    if normalized in sided_modifiers:
        left_scan_codes = key_to_scan_codes('left ' + normalized, False)
        right_scan_codes = key_to_scan_codes('right ' + normalized, False)
        return left_scan_codes + tuple(c for c in right_scan_codes if c not in left_scan_codes)

    try:
        # Put items in ordered dict to remove duplicates.
        t = tuple(_collections.OrderedDict((scan_code, True) for scan_code, modifier in _os_keyboard.map_name(normalized)))
        e = None
    except (KeyError, ValueError) as exception:
        t = ()
        e = exception

    if not t and error_if_missing:
        raise ValueError('Key {} is not mapped to any known key.'.format(repr(key)), e)
    else:

        return t

class Hotkey(object):
    def __init__(self, steps):
        self.steps = tuple(steps)
    def __repr__(self):
        return ', '.join(map(str, self.steps))
class Step(object):
    def __init__(self, keys):
        self.keys = tuple(keys)
        self.modifiers = [key for key in self.keys if is_modifier(key.scan_codes[0])]
        if len(self.keys) == len(self.modifiers) + 1:
            self.is_standard = True
            self.main_key = next(key for key in self.keys if key not in self.modifiers)
        else:
            self.is_standard = False
            self.main_key = None
    def __repr__(self):
        return '+'.join(map(str, self.keys))
class Key(object):
    def __init__(self, label, scan_codes):
        self.label = label
        self.scan_codes = tuple(scan_codes)
        assert self.scan_codes and all(_is_number(scan_code) for scan_code in self.scan_codes)
    def __repr__(self):
        if self.label:
            return str(self.label)
        elif len(self.scan_codes) == 1:
            return str(self.scan_codes[0])
        else:
            return '({})'.format(','.join(map(str, self.scan_codes)))
def parse_hotkey(hotkey):
    """
    Parses a user-provided hotkey into nested tuples representing the
    parsed structure, with the bottom values being lists of scan codes.
    Also accepts raw scan codes, which are then wrapped in the required
    number of nestings.

    Example:

        parse_hotkey("alt+shift+a, alt+b, c")
        #    Keys:    ^~^ ^~~~^ ^  ^~^ ^  ^
        #    Steps:   ^~~~~~~~~~^  ^~~~^  ^

        # ((alt_codes, shift_codes, a_codes), (alt_codes, b_codes), (c_codes,))
    """
    if isinstance(hotkey, Hotkey):
        return hotkey
    elif _is_number(hotkey) or len(hotkey) == 1:
        key = Key(hotkey, key_to_scan_codes(hotkey))
        step = Step([key])
        return Hotkey([step])
    elif _is_list(hotkey):
        if not any(map(_is_list, hotkey)):
            keys = [Key(k, key_to_scan_codes(k)) for k in hotkey]
            step = Step(keys)
            return Hotkey([step])
        else:
            steps = [Step(Key(None, k) for k in step) for step in hotkey]
            return Hotkey(steps)

    steps = []
    for step in _re.split(r',\s?', hotkey):
        key_names = _re.split(r'\s?\+\s?', step)
        steps.append(Step([Key(name, key_to_scan_codes(name)) for name in key_names]))
    return Hotkey(steps)

def send(hotkey, do_press=True, do_release=True):
    """
    Sends OS events that perform the given *hotkey* hotkey.

    - `hotkey` can be either a scan code (e.g. 57 for space), single key
    (e.g. 'space') or multi-key, multi-step hotkey (e.g. 'alt+F4, enter').
    - `do_press` if true then press events are sent. Defaults to True.
    - `do_release` if true then release events are sent. Defaults to True.

        send(57)
        send('ctrl+alt+del')
        send('alt+F4, enter')
        send('shift+s')

    Note: keys are released in the opposite order they were pressed.
    """
    parsed = parse_hotkey(hotkey)
    for step in parsed.steps:
        if do_press:
            for key in step.keys:
                _os_keyboard.press(key.scan_codes[0])

        if do_release:
            for key in reversed(step.keys):
                _os_keyboard.release(key.scan_codes[0])

# Alias.
press_and_release = send

def press(hotkey):
    """ Presses and holds down a hotkey (see `send`). """
    send(hotkey, True, False)

def release(hotkey):
    """ Releases a hotkey (see `send`). """
    send(hotkey, False, True)

def is_pressed(hotkey):
    """
    Returns True if the key is pressed.

        is_pressed(57) #-> True
        is_pressed('space') #-> True
        is_pressed('ctrl+space') #-> True
    """
    _listener.start_if_necessary()

    if _is_number(hotkey):
        # Shortcut.
        with _pressed_events_lock:
            return hotkey in _pressed_events

    steps = parse_hotkey(hotkey)
    if len(steps) > 1:
        raise ValueError("Impossible to check if multi-step hotkeys are pressed (`a+b` is ok, `a, b` isn't).")

    # Convert _pressed_events into a set 
    with _pressed_events_lock:
        pressed_scan_codes = set(_pressed_events)
    for scan_codes in steps[0]:
        if not any(scan_code in pressed_scan_codes for scan_code in scan_codes):
            return False
    return True

def call_later(fn, args=(), delay=0.001):
    """
    Calls the provided function in a new thread after waiting some time.
    Useful for giving the system some time to process an event, without suppressing
    the current execution flow.
    """
    thread = _threading.Thread(target=lambda: (_time.sleep(delay), fn(*args)))
    thread.start()

_hooks = {}
def old_hook(callback, suppress=False, on_remove=lambda: None):
    """
    Installs a global listener on all available keyboards, invoking `callback`
    each time a key is pressed or released.
    
    The event passed to the callback is of type `keyboard.KeyboardEvent`,
    with the following attributes:

    - `name`: an Unicode representation of the character (e.g. "&") or
    description (e.g.  "space"). The name is always lower-case.
    - `scan_code`: number representing the physical key, e.g. 55.
    - `time`: timestamp of the time the event occurred, with as much precision
    as given by the OS.

    Returns the given callback for easier development.

    Example:

    ```py
    hook(lambda event: print('Got event:', event))
    ```
    """
    if suppress:
        _listener.start_if_necessary()
        append, remove = _listener.suppressing_hooks.append, _listener.suppressing_hooks.remove
    else:
        append, remove = _listener.add_handler, _listener.remove_handler

    append(callback)
    def remove_():
        del _hooks[callback]
        del _hooks[remove_]
        remove(callback)
        on_remove()
    _hooks[callback] = _hooks[remove_] = remove_
    return remove_

def on_press(callback, suppress=False):
    """
    Invokes `callback` for every KEY_DOWN event. For details see `hook`.
    """
    return hook(lambda e: e.event_type == KEY_UP or callback(e), suppress=suppress)

def on_release(callback, suppress=False):
    """
    Invokes `callback` for every KEY_UP event. For details see `hook`.
    """
    return hook(lambda e: e.event_type == KEY_DOWN or callback(e), suppress=suppress)

def old_hook_key(key, callback, suppress=False):
    """
    Hooks key up and key down events for a single key. Returns the event handler
    created. To remove a hooked key use `unhook_key(key)` or
    `unhook_key(handler)`.

    Note: this function shares state with hotkeys, so `clear_all_hotkeys`
    affects it as well.
    """
    _listener.start_if_necessary()
    store = _listener.suppressing_keys if suppress else _listener.nonsuppressing_keys
    scan_codes = key_to_scan_codes(key)
    for scan_code in scan_codes:
        store[scan_code].append(callback)

    def remove_():
        del _hooks[callback]
        del _hooks[key]
        del _hooks[remove_]
        for scan_code in scan_codes:
            store[scan_code].remove(callback)
    _hooks[callback] = _hooks[key] = _hooks[remove_] = remove_
    return remove_

def on_press_key(key, callback, suppress=False):
    """
    Invokes `callback` for KEY_DOWN event related to the given key. For details see `hook`.
    """
    return hook_key(key, lambda e: e.event_type == KEY_UP or callback(e), suppress=suppress)

def on_release_key(key, callback, suppress=False):
    """
    Invokes `callback` for KEY_UP event related to the given key. For details see `hook`.
    """
    return hook_key(key, lambda e: e.event_type == KEY_DOWN or callback(e), suppress=suppress)

def unhook(remove):
    """
    Removes a previously added hook, either by callback or by the return value
    of `hook`.
    """
    _hooks[remove]()
unhook_key = unhook

def unhook_all():
    """
    Removes all keyboard hooks in use, including hotkeys, abbreviations, word
    listeners, `record`ers and `wait`s.
    """
    _listener.start_if_necessary()
    _listener.suppressing_keys.clear()
    _listener.nonsuppressing_keys.clear()
    del _listener.suppressing_hooks[:]
    del _listener.handlers[:]
    unhook_all_hotkeys()

def block_key(key):
    """
    Suppresses all key events of the given key, regardless of modifiers.
    """
    return hook_key(key, lambda e: False, suppress=True)
unblock_key = unhook_key

def remap_key(src, dst):
    """
    Whenever the key `src` is pressed or released, regardless of modifiers,
    press or release the hotkey `dst` instead.
    """
    def handler(event):
        if event.event_type == KEY_DOWN:
            press(dst)
        else:
            release(dst)
        return False
    return hook_key(src, handler, suppress=True)
unremap_key = unhook_key

def parse_hotkey_combinations(hotkey):
    """
    Parses a user-provided hotkey. Differently from `parse_hotkey`,
    instead of each step being a list of the different scan codes for each key,
    each step is a list of all possible combinations of those scan codes.
    """
    def combine_step(step):
        # A single step may be composed of many keys, and each key can have
        # multiple scan codes. To speed up hotkey matching and avoid introducing
        # event delays, we list all possible combinations of scan codes for these
        # keys. Hotkeys are usually small, and there are not many combinations, so
        # this is not as insane as it sounds.
        return (tuple(sorted(scan_codes)) for scan_codes in _itertools.product(*step))

    return tuple(tuple(combine_step(step)) for step in parse_hotkey(hotkey))

def _add_hotkey_step(handler, combinations, suppress):
    """
    Hooks a single-step hotkey (e.g. 'shift+a').
    """
    container = _listener.suppressing_hotkeys if suppress else _listener.nonsuppressing_hotkeys

    # Register the scan codes of every possible combination of
    # modfiier + main key. Modifiers have to be registered in 
    # filtered_modifiers too, so suppression and replaying can work.
    for scan_codes in combinations:
        for scan_code in scan_codes:
            if is_modifier(scan_code):
                _listener.filtered_modifiers[scan_code] += 1
        container[scan_codes].append(handler)

    def remove():
        for scan_codes in combinations:
            for scan_code in scan_codes:
                if is_modifier(scan_code):
                    _listener.filtered_modifiers[scan_code] -= 1
            container[scan_codes].remove(handler)
    return remove

_hotkeys = {}
def old_add_hotkey(hotkey, callback, args=(), suppress=False, timeout=1, trigger_on_release=False):
    """
    Invokes a callback every time a hotkey is pressed. The hotkey must
    be in the format `ctrl+shift+a, s`. This would trigger when the user holds
    ctrl, shift and "a" at once, releases, and then presses "s". To represent
    literal commas, pluses, and spaces, use their names ('comma', 'plus',
    'space').

    - `args` is an optional list of arguments to passed to the callback during
    each invocation.
    - `suppress` defines if successful triggers should block the keys from being
    sent to other programs.
    - `timeout` is the amount of seconds allowed to pass between key presses.
    - `trigger_on_release` if true, the callback is invoked on key release instead
    of key press.

    The event handler function is returned. To remove a hotkey call
    `remove_hotkey(hotkey)` or `remove_hotkey(handler)`.
    before the hotkey state is reset.

    Note: hotkeys are activated when the last key is *pressed*, not released.
    Note: the callback is executed in a separate thread, asynchronously. For an
    example of how to use a callback synchronously, see `wait`.

    Examples:

        # Different but equivalent ways to listen for a spacebar key press.
        add_hotkey(' ', print, args=['space was pressed'])
        add_hotkey('space', print, args=['space was pressed'])
        add_hotkey('Space', print, args=['space was pressed'])
        # Here 57 represents the keyboard code for spacebar; so you will be
        # pressing 'spacebar', not '57' to activate the print function.
        add_hotkey(57, print, args=['space was pressed'])

        add_hotkey('ctrl+q', quit)
        add_hotkey('ctrl+alt+enter, space', some_callback)
    """
    if args:
        callback = lambda callback=callback: callback(*args)

    _listener.start_if_necessary()

    steps = parse_hotkey_combinations(hotkey)

    event_type = KEY_UP if trigger_on_release else KEY_DOWN
    if len(steps) == 1:
        # Deciding when to allow a KEY_UP event is far harder than I thought,
        # and any mistake will make that key "sticky". Therefore just let all
        # KEY_UP events go through as long as that's not what we are listening
        # for.
        handler = lambda e: (event_type == KEY_DOWN and e.event_type == KEY_UP and e.scan_code in _logically_pressed_keys) or (event_type == e.event_type and callback())
        remove_step = _add_hotkey_step(handler, steps[0], suppress)
        def remove_():
            remove_step()
            del _hotkeys[hotkey]
            del _hotkeys[remove_]
            del _hotkeys[callback]
        # TODO: allow multiple callbacks for each hotkey without overwriting the
        # remover.
        _hotkeys[hotkey] = _hotkeys[remove_] = _hotkeys[callback] = remove_
        return remove_

    state = _State()
    state.remove_catch_misses = None
    state.remove_last_step = None
    state.suppressed_events = []
    state.last_update = float('-inf')
    
    def catch_misses(event, force_fail=False):
        if (
                event.event_type == event_type
                and state.index
                and event.scan_code not in allowed_keys_by_step[state.index]
            ) or (
                timeout
                and _time.monotonic() - state.last_update >= timeout
            ) or force_fail: # Weird formatting to ensure short-circuit.

            state.remove_last_step()

            for event in state.suppressed_events:
                if event.event_type == KEY_DOWN:
                    press(event.scan_code)
                else:
                    release(event.scan_code)
            del state.suppressed_events[:]

            index = 0
            set_index(0)
        return True

    def set_index(new_index):
        state.index = new_index

        if new_index == 0:
            # This is done for performance reasons, avoiding a global key hook
            # that is always on.
            state.remove_catch_misses = lambda: None
        elif new_index == 1:
            state.remove_catch_misses()
            # Must be `suppress=True` to ensure `send` has priority.
            state.remove_catch_misses = hook(catch_misses, suppress=True)

        if new_index == len(steps) - 1:
            def handler(event):
                if event.event_type == KEY_UP:
                    remove()
                    set_index(0)
                accept = event.event_type == event_type and callback() 
                if accept:
                    return catch_misses(event, force_fail=True)
                else:
                    state.suppressed_events[:] = [event]
                    return False
            remove = _add_hotkey_step(handler, steps[state.index], suppress)
        else:
            # Fix value of next_index.
            def handler(event, new_index=state.index+1):
                if event.event_type == KEY_UP:
                    remove()
                    set_index(new_index)
                state.suppressed_events.append(event)
                return False
            remove = _add_hotkey_step(handler, steps[state.index], suppress)
        state.remove_last_step = remove
        state.last_update = _time.monotonic()
        return False
    set_index(0)

    allowed_keys_by_step = [
        set().union(*step)
        for step in steps
    ]

    def remove_():
        state.remove_catch_misses()
        state.remove_last_step()
        del _hotkeys[hotkey]
        del _hotkeys[remove_]
        del _hotkeys[callback]
    # TODO: allow multiple callbacks for each hotkey without overwriting the
    # remover.
    _hotkeys[hotkey] = _hotkeys[remove_] = _hotkeys[callback] = remove_
    return remove_
register_hotkey = add_hotkey

def remove_hotkey(hotkey_or_callback):
    """
    Removes a previously hooked hotkey. Must be called with the value returned
    by `add_hotkey`.
    """
    _hotkeys[hotkey_or_callback]()
unregister_hotkey = clear_hotkey = remove_hotkey

def unhook_all_hotkeys():
    """
    Removes all keyboard hotkeys in use, including abbreviations, word listeners,
    `record`ers and `wait`s.
    """
    # Because of "aliases" some hooks may have more than one entry, all of which
    # are removed together.
    _listener.suppressing_hotkeys.clear()
    _listener.nonsuppressing_hotkeys.clear()
unregister_all_hotkeys = remove_all_hotkeys = clear_all_hotkeys = unhook_all_hotkeys

def remap_hotkey(src, dst, suppress=True, trigger_on_release=False):
    """
    Whenever the hotkey `src` is pressed, suppress it and send
    `dst` instead.

    Example:

        remap('alt+w', 'ctrl+up')
    """
    def handler():
        active_modifiers = sorted(modifier for modifier, state in _listener.modifier_states.items() if state == 'allowed')
        for modifier in active_modifiers:
            release(modifier)
        send(dst)
        for modifier in reversed(active_modifiers):
            press(modifier)
        return False
    return add_hotkey(src, handler, suppress=suppress, trigger_on_release=trigger_on_release)
unremap_hotkey = remove_hotkey

def stash_state():
    """
    Builds a list of all currently pressed scan codes, releases them and returns
    the list. Pairs well with `restore_state` and `restore_modifiers`.
    """
    # TODO: stash caps lock / numlock /scrollock state.
    with _pressed_events_lock:
        state = sorted(_pressed_events)
    for scan_code in state:
        _os_keyboard.release(scan_code)
    return state

def restore_state(scan_codes):
    """
    Given a list of scan_codes ensures these keys, and only these keys, are
    pressed. Pairs well with `stash_state`, alternative to `restore_modifiers`.
    """
    _listener.is_replaying = True

    with _pressed_events_lock:
        current = set(_pressed_events)
    target = set(scan_codes)
    for scan_code in current - target:
        _os_keyboard.release(scan_code)
    for scan_code in target - current:
        _os_keyboard.press(scan_code)

    _listener.is_replaying = False

def restore_modifiers(scan_codes):
    """
    Like `restore_state`, but only restores modifier keys.
    """
    restore_state((scan_code for scan_code in scan_codes if is_modifier(scan_code)))

def write(text, delay=0, restore_state_after=True, exact=None):
    """
    Sends artificial keyboard events to the OS, simulating the typing of a given
    text. Characters not available on the keyboard are typed as explicit unicode
    characters using OS-specific functionality, such as alt+codepoint.

    To ensure text integrity, all currently pressed keys are released before
    the text is typed, and modifiers are restored afterwards.

    - `delay` is the number of seconds to wait between keypresses, defaults to
    no delay.
    - `restore_state_after` can be used to restore the state of pressed keys
    after the text is typed, i.e. presses the keys that were released at the
    beginning. Defaults to True.
    - `exact` forces typing all characters as explicit unicode (e.g.
    alt+codepoint or special events). If None, uses platform-specific suggested
    value.
    """
    if exact is None:
        exact = _platform.system() == 'Windows'

    state = stash_state()
    
    # Window's typing of unicode characters is quite efficient and should be preferred.
    if exact:
        for letter in text:
            if letter in '\n\b':
                send(letter)
            else:
                _os_keyboard.type_unicode(letter)
            if delay: _time.sleep(delay)
    else:
        for letter in text:
            try:
                entries = _os_keyboard.map_name(normalize_name(letter))
                scan_code, modifiers = next(iter(entries))
            except (KeyError, ValueError, StopIteration):
                _os_keyboard.type_unicode(letter)
                continue
            
            for modifier in modifiers:
                press(modifier)

            _os_keyboard.press(scan_code)
            _os_keyboard.release(scan_code)

            for modifier in modifiers:
                release(modifier)

            if delay:
                _time.sleep(delay)

    if restore_state_after:
        restore_modifiers(state)

def wait(hotkey=None, suppress=False, trigger_on_release=False):
    """
    Blocks the program execution until the given hotkey is pressed or,
    if given no parameters, blocks forever.
    """
    if hotkey:
        lock = _Event()
        remove = add_hotkey(hotkey, lambda: lock.set(), suppress=suppress, trigger_on_release=trigger_on_release)
        lock.wait()
        remove_hotkey(remove)
    else:
        while True:
            _time.sleep(1e6)

def get_hotkey_name(names=None):
    """
    Returns a string representation of hotkey from the given key names, or
    the currently pressed keys if not given.  This function:

    - normalizes names;
    - removes "left" and "right" prefixes;
    - replaces the "+" key name with "plus" to avoid ambiguity;
    - puts modifier keys first, in a standardized order;
    - sort remaining keys;
    - finally, joins everything with "+".

    Example:

        get_hotkey_name(['+', 'left ctrl', 'shift'])
        # "ctrl+shift+plus"
    """
    if names is None:
        _listener.start_if_necessary()
        with _pressed_events_lock:
            names = [e.name for e in _pressed_events.values()]
    else:
        names = [normalize_name(name) for name in names]
    clean_names = set(e.replace('left ', '').replace('right ', '').replace('+', 'plus') for e in names)
    # https://developer.apple.com/macos/human-interface-guidelines/input-and-output/keyboard/
    # > List modifier keys in the correct order. If you use more than one modifier key in a
    # > hotkey, always list them in this order: Control, Option, Shift, Command.
    modifiers = ['ctrl', 'alt', 'shift', 'windows']
    sorting_key = lambda k: (modifiers.index(k) if k in modifiers else 5, str(k))
    return '+'.join(sorted(clean_names, key=sorting_key))

def read_event(suppress=False):
    """
    Blocks until a keyboard event happens, then returns that event.
    """
    queue = _queue.Queue(maxsize=1)
    hooked = hook(queue.put, suppress=suppress)
    while True:
        event = queue.get()
        unhook(hooked)
        return event

def read_key(suppress=False):
    """
    Blocks until a keyboard event happens, then returns that event's name or,
    if missing, its scan code.
    """
    event = read_event(suppress)
    return event.name or event.scan_code

def read_hotkey(suppress=True):
    """
    Similar to `read_key()`, but blocks until the user presses and releases a
    hotkey (or single key), then returns a string representing the hotkey
    pressed.

    Example:

        read_hotkey()
        # "ctrl+shift+p"
    """
    queue = _queue.Queue()
    fn = lambda e: queue.put(e) or e.event_type == KEY_DOWN
    hooked = hook(fn, suppress=suppress)
    while True:
        event = queue.get()
        if event.event_type == KEY_UP:
            unhook(hooked)
            with _pressed_events_lock:
                names = [e.name for e in _pressed_events.values()] + [event.name]
            return get_hotkey_name(names)

def get_typed_strings(events, allow_backspace=True):
    """
    Given a sequence of events, tries to deduce what strings were typed.
    Strings are separated when a non-textual key is pressed (such as tab or
    enter). Characters are converted to uppercase according to shift and
    capslock status. If `allow_backspace` is True, backspaces remove the last
    character typed.

    This function is a generator, so you can pass an infinite stream of events
    and convert them to strings in real time.

    Note this functions is merely an heuristic. Windows for example keeps per-
    process keyboard state such as keyboard layout, and this information is not
    available for our hooks.

        get_type_strings(record()) #-> ['This is what', 'I recorded', '']
    """
    backspace_name = 'delete' if _platform.system() == 'Darwin' else 'backspace'

    shift_pressed = False
    capslock_pressed = False
    string = ''
    for event in events:
        name = event.name

        # Space is the only key that we _parse_hotkey to the spelled out name
        # because of legibility. Now we have to undo that.
        if event.name == 'space':
            name = ' '

        if 'shift' in event.name:
            shift_pressed = event.event_type == 'down'
        elif event.name == 'caps lock' and event.event_type == 'down':
            capslock_pressed = not capslock_pressed
        elif allow_backspace and event.name == backspace_name and event.event_type == 'down':
            string = string[:-1]
        elif event.event_type == 'down':
            if len(name) == 1:
                if shift_pressed ^ capslock_pressed:
                    name = name.upper()
                string = string + name
            else:
                yield string
                string = ''
    yield string

_recording = None
def start_recording(recorded_events_queue=None):
    """
    Starts recording all keyboard events into a global variable, or the given
    queue if any. Returns the queue of events and the hooked function.

    Use `stop_recording()` or `unhook(hooked_function)` to stop.
    """
    recorded_events_queue = recorded_events_queue or _queue.Queue()
    global _recording
    _recording = (recorded_events_queue, hook(recorded_events_queue.put))
    return _recording

def stop_recording():
    """
    Stops the global recording of events and returns a list of the events
    captured.
    """
    global _recording
    if not _recording:
        raise ValueError('Must call "start_recording" before.')
    recorded_events_queue, hooked = _recording
    unhook(hooked)
    return list(recorded_events_queue.queue)

def record(until='escape', suppress=False, trigger_on_release=False):
    """
    Records all keyboard events from all keyboards until the user presses the
    given hotkey. Then returns the list of events recorded, of type
    `keyboard.KeyboardEvent`. Pairs well with
    `play(events)`.

    Note: this is a suppressing function.
    Note: for more details on the keyboard hook and events see `hook`.
    """
    start_recording()
    wait(until, suppress=suppress, trigger_on_release=trigger_on_release)
    return stop_recording()

def play(events, speed_factor=1.0):
    """
    Plays a sequence of recorded events, maintaining the relative time
    intervals. If speed_factor is <= 0 then the actions are replayed as fast
    as the OS allows. Pairs well with `record()`.

    Note: the current keyboard state is cleared at the beginning and restored at
    the end of the function.
    """
    state = stash_state()

    last_time = None
    for event in events:
        if speed_factor > 0 and last_time is not None:
            _time.sleep((event.time - last_time) / speed_factor)
        last_time = event.time

        key = event.scan_code or event.name
        press(key) if event.event_type == KEY_DOWN else release(key)

    restore_modifiers(state)
replay = play

_word_listeners = {}
def add_word_listener(word, callback, triggers=['space'], match_suffix=False, timeout=2):
    """
    Invokes a callback every time a sequence of characters is typed (e.g. 'pet')
    and followed by a trigger key (e.g. space). Modifiers (e.g. alt, ctrl,
    shift) are ignored.

    - `word` the typed text to be matched. E.g. 'pet'.
    - `callback` is an argument-less function to be invoked each time the word
    is typed.
    - `triggers` is the list of keys that will cause a match to be checked. If
    the user presses some key that is not a character (len>1) and not in
    triggers, the characters so far will be discarded. By default the trigger
    is only `space`.
    - `match_suffix` defines if endings of words should also be checked instead
    of only whole words. E.g. if true, typing 'carpet'+space will trigger the
    listener for 'pet'. Defaults to false, only whole words are checked.
    - `timeout` is the maximum number of seconds between typed characters before
    the current word is discarded. Defaults to 2 seconds.

    Returns the event handler created. To remove a word listener use
    `remove_word_listener(word)` or `remove_word_listener(handler)`.

    Note: all actions are performed on key down. Key up events are ignored.
    Note: word matches are **case sensitive**.
    """
    state = _State()
    state.current = ''
    state.time = -1

    def handler(event):
        name = event.name
        if event.event_type == KEY_UP or name in all_modifiers: return

        if timeout and event.time - state.time > timeout:
            state.current = ''
        state.time = event.time

        matched = state.current == word or (match_suffix and state.current.endswith(word))
        if name in triggers and matched:
            callback()
            state.current = ''
        elif len(name) > 1:
            state.current = ''
        else:
            state.current += name

    hooked = hook(handler)
    def remove():
        hooked()
        del _word_listeners[word]
        del _word_listeners[handler]
        del _word_listeners[remove]
    _word_listeners[word] = _word_listeners[handler] = _word_listeners[remove] = remove
    # TODO: allow multiple word listeners and removing them correctly.
    return remove

def remove_word_listener(word_or_handler):
    """
    Removes a previously registered word listener. Accepts either the word used
    during registration (exact string) or the event handler returned by the
    `add_word_listener` or `add_abbreviation` functions.
    """
    _word_listeners[word_or_handler]()

def add_abbreviation(source_text, replacement_text, match_suffix=False, timeout=2):
    """
    Registers a hotkey that replaces one typed text with another. For example

        add_abbreviation('tm', u'™')

    Replaces every "tm" followed by a space with a ™ symbol (and no space). The
    replacement is done by sending backspace events.

    - `match_suffix` defines if endings of words should also be checked instead
    of only whole words. E.g. if true, typing 'carpet'+space will trigger the
    listener for 'pet'. Defaults to false, only whole words are checked.
    - `timeout` is the maximum number of seconds between typed characters before
    the current word is discarded. Defaults to 2 seconds.
    
    For more details see `add_word_listener`.
    """
    replacement = '\b'*(len(source_text)+1) + replacement_text
    callback = lambda: write(replacement)
    return add_word_listener(source_text, callback, match_suffix=match_suffix, timeout=timeout)

# Aliases.
register_word_listener = add_word_listener
register_abbreviation = add_abbreviation
remove_abbreviation = remove_word_listener

# Start listening threads.
_modifier_scan_codes.update(*(key_to_scan_codes(name, False) for name in all_modifiers) )
_listener = _KeyboardListener()
_listener.start()