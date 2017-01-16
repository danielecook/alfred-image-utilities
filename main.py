#!/usr/bin/python
# encoding: utf-8

import sys

from workflow import Workflow3
from workflow import ICON_ERROR
from subprocess import Popen, PIPE

import os

import json

scpt = '''
    tell application "Finder"
    set theSelection to selection
    set out to ""
    repeat with oneItem in theSelection
        set file_name to oneItem as string
        set out to file_name & "
" & out
    end repeat
    copy out to stdout
end tell
'''

__version__ = "0.1"

formats = [".bmp", ".tif", ".tiff", ".gif", ".jpg", ".jpeg", ".JPEG", ".png", ".eps", ".ico"]

def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


def main(wf):
    log.debug('Started')

    # Get selected items
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(scpt)
    log.debug(stdout)
    fnames = stdout.strip().splitlines()
    fnames = ["/" + x.split(":", 1)[1].replace(":", "/") for x in fnames]

    fnames_filtered = [x for x in fnames if os.path.splitext(x)[1] in formats]
    log.debug(fnames_filtered)
    # Get args from Workflow, already in normalized Unicode
    args = wf.args

    basenames = [os.path.basename(x) for x in fnames_filtered]

  
    arg = {"files": fnames_filtered,
           "replace": False}

    args = wf.args[0].split(" ")
    log.debug(args)
    if args[0] not in [u'convert', u'rotate', u'color', u'scale']:

        # Add an item to Alfred feedback
        if len(basenames) > 1:
            pl = "s"
        elif len(basenames) == 0:
            wf.add_item(u'Error', subtitle = u'No valid images selected', valid = False, icon = ICON_ERROR)
            wf.send_feedback()
            return
        else:
            pl = ""
        wf.add_item(u'%i valid image%s' % (len(fnames_filtered), pl), uid = 0, subtitle= u', '.join(basenames), icon = "picture.png")
        wf.add_item("convert", autocomplete="convert ", subtitle = "Convert file formats", valid = False, icon = "convert.png")
        wf.add_item("scale", autocomplete="scale ", subtitle = "Scale images", valid = False, icon = "scale.png")
        wf.add_item("rotate ", autocomplete="rotate ", subtitle = "Rotate images", valid = False, icon = "rotate.png")
        wf.add_item("color", autocomplete="color", subtitle = "Convert Color", valid = False, icon = "color.png")

    elif args[0] == u'scale':
        if args[-1]:
            scale = args[-1]
            try:
                scale_amount = int(scale)
            except:
                scale_amount = "..."
        else:
            scale_amount = "..."

        is_valid = type(scale_amount) is int

        arg.update({"action": "scale", "scale_amount": scale_amount, "scale_type": "%",  "replace": False})
        title = u"Scale to %s percent" % scale_amount
        it = wf.add_item(title, valid = is_valid, arg = json.dumps(arg), icon = "scale.png")
        arg["modifier"] = "add_extension"
        it.add_modifier("alt", "Add '.thumb' before extension", arg = json.dumps(arg))
        arg["modifier"] = "replace"
        arg["replace"] = True
        it.add_modifier("cmd", "Replace original", arg = json.dumps(arg))

        title = u'Scale to max width %spx' % (scale_amount)
        arg.update({"action": "scale", "scale_amount": scale_amount, "scale_direction": "x", "scale_type": "px",  "replace": False})
        it = wf.add_item(title, valid = is_valid, arg = json.dumps(arg), icon = "scale.png")
        arg["modifier"] = "add_extension"
        it.add_modifier("alt", "Add '.thumb' before extension", arg = json.dumps(arg))
        arg["modifier"] = "replace"
        arg["replace"] = True
        it.add_modifier("cmd", "Replace original", arg = json.dumps(arg))

        title = u'Scale to max height %spx' % (scale_amount)
        arg.update({"action": "scale", "scale_amount": scale_amount, "scale_direction": "y", "scale_type": "px", "replace": False})
        it = wf.add_item(title, valid = is_valid, arg = json.dumps(arg), icon = "scale.png")
        arg["modifier"] = "add_extension"
        it.add_modifier("alt", "Add '.thumb' before extension", arg = json.dumps(arg))
        arg["modifier"] = "replace"
        arg["replace"] = True
        it.add_modifier("cmd", "Replace original", arg = json.dumps(arg))

        title = u'Generate thumbnail' 
        arg["replace"] = False
        arg.update({"action": "scale", "scale_amount": 200, "scale_type": "px", "modifier": "thumb", "scale_direction": "x", "replace": False})
        it = wf.add_item(title, valid = True, arg = json.dumps(arg), icon = "scale.png")

    elif args[0] == u'convert':
        for format in ['png', 'jpg', 'tif']: 
            arg.update({"action": "convert",
                        "to_format": format,
                        "modifier": None})
            title = u'Convert to %s' % (format)
            it = wf.add_item(title, autocomplete="convert %s" % format, uid = title, valid = True, icon = format + ".png", arg = json.dumps(arg))
            arg["modifier"] = "replace"
            arg["replace"] = True
            it.add_modifier("cmd", "Replace original", arg = json.dumps(arg))

    elif args[0] == u'rotate':
        if args[-1]:
            try:
                degree = int(args[-1])
            except:
                degree = "..."
        else:
            degree = "..."
        is_valid = type(degree) == int
        log.debug(is_valid)
        arg.update({"action": "rotate", "degrees": degree, "replace": False})
        title = u'Rotate %s degrees' % (degree)
        it = wf.add_item(title, valid = is_valid, uid=title, arg = json.dumps(arg), icon = "rotate.png")
        arg["replace"] = True
        it.add_modifier("cmd", "Replace original", arg = json.dumps(arg))

    elif args[0] == u'color':
        arg.update({"action": "bw1", "replace": False})
        title = u'1-bit black and white'
        it = wf.add_item(title, valid = True, uid=u'1bit', arg = json.dumps(arg), icon = "checker.png")
        arg["replace"] = True
        it.add_modifier("cmd", "Replace original", arg = json.dumps(arg))

        arg.update({"action": "bw8", "replace": False})
        title = u'8-bit black and white'
        it = wf.add_item(title, valid = True, uid=u'8bit', arg = json.dumps(arg), icon = "8bit.png")
        arg["replace"] = True
        it.add_modifier("cmd", "Replace original", arg = json.dumps(arg))  

    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow` object
    wf = Workflow3(update_settings = {
        'github_slug': 'danielecook/image-utilities',
        'version': __version__,
        'frequency': 7
        })
    wf.magic_prefix = 'wf:'
    log = wf.logger
    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.

    if wf.update_available:
        # Download new version and tell Alfred to install it
        wf.start_update()

    sys.exit(wf.run(main))