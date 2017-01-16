#!/usr/bin/env python

from PIL import Image
from workflow import Workflow
import sys
import json
import os
from subprocess import Popen, PIPE

import string
import random

def id_generator(size=4, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))


wf = Workflow()
log = wf.logger
ds = json.loads(sys.argv[1])

for file in ds['files']:
    no_ext, ext = os.path.splitext(file)
    no_ext = os.path.basename(no_ext)
    path, basename = os.path.split(file)
    from_format = ext.strip(".")
    im = Image.open(file)

    generate_thumb = False
    if 'modifier' in ds and ds['modifier'] == 'thumb':
        generate_thumb = True
        to_format = from_format

    if ds['action'] in ['rotate', 'bw1', 'bw8', 'scale'] and not generate_thumb:
        to_format = from_format
        tmp_file = "{path}/{no_ext}.orig.{to_format}".format(**locals())
        os.rename(file, tmp_file)

    if ds['action'] == 'rotate':
        log.debug("rotating")
        im = im.rotate(360 - ds['degrees'], expand=True)
    elif ds['action'] == 'scale':
        log.debug(ds)
        x, y = im.size
        if ds['scale_type'] == '%':
            new_x = int((ds['scale_amount'] / 100.0) * x)
            new_y = int((ds['scale_amount'] / 100.0) * y)
        elif ds['scale_type'] == 'px':
            if ds['scale_direction'] == 'x':
                scaling_factor = x / ds['scale_amount']
                new_x = ds['scale_amount']
                new_y = y / scaling_factor
            elif ds['scale_direction'] == 'y':
                scaling_factor = y / ds['scale_amount']
                new_x = x / scaling_factor
                new_y = ds['scale_amount']
        if generate_thumb:
            no_ext = no_ext + ".thumb"
        im = im.resize([new_x, new_y])
    elif ds['action'] == 'bw1':
        log.debug("1 bit bw")
        im = im.convert("1")
    elif ds['action'] == 'bw8':
        log.debug("1 bit bw")
        im = im.convert("L")
    elif ds['action'] == 'convert':
        to_format = ds["to_format"]
        tmp_file = file

    log.debug(path)
    outfile = "{path}/{no_ext}.{to_format}".format(**locals())
    log.debug(outfile)
    im.save(outfile)

    if ds["replace"]:
        os.remove(tmp_file)


# Refresh finder
scpt = 'tell application "Finder" to tell front window to update every item'
p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate(scpt)
log.debug(stdout)