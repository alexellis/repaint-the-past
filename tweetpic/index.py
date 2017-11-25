# Copyright (c) Alex Ellis 2017. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import sys
from function import handler

def get_stdin():
    buf = ""
    for line in sys.stdin:
        buf = buf + line
    return buf

if(__name__ == "__main__"):
    st = get_stdin()
    res = handler.handle(st)
    if (res['status_id']):
        print("Replied to "+ str(res['reply_to']))
    else:
        print("Tweetback failed to" + str(res['reply_to']))

