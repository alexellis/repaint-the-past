import cv2
import skvideo.io
import sys

video = skvideo.io.VideoCapture(sys.argv[1])

fn = 1

if video.isOpened():
    fin, frame = video.read()
else:
    print('Failed to open file')
    fin = False

while fin:
    print('Extracting frame %i' % fn)

    fin, frame = video.read()

    filename = 'frames/' + str(fn).zfill(5) + '.jpg'

    cv2.imwrite(filename, frame)

    fn += 1

    cv2.waitKey(1)
video.release()

print('%i frames successfully extracted' % fn)

