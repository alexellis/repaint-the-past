import cv2
video = cv2.VideoCapture('out.mov')
f_n = 1

if video.isOpened():
    fin, frame = video.read()
else:
    fin = false

while fin:
    fin, frame = video.read()
    cv2.imwrite('frames/' + str(f_n).zfill(5) + '.jpg', frame)
    f_n += 1
    cv2.waitKey(1)
