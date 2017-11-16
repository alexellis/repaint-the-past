# Copyright (c) Alex Ellis 2017. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import sys, json
from function import handler

def get_stdin():
    buf = ""
    for line in sys.stdin:
        buf = buf + line
    return buf

if(__name__ == "__main__"):
    st = get_stdin()
    req = json.loads(st)
    res = handler.handle(req)
    if (res['status_id']):
        print("Replied to %i" % res['status_id'])
    else:
        print("Tweetback to %i failed" % res['reply_to'])
