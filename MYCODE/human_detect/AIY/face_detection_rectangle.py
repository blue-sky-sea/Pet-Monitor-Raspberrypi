#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Camera inference face detection demo code.

Runs continuous face detection on the VisionBonnet and prints the number of
detected faces.

Example:
face_detection_camera.py --num_frames 10
"""
import argparse

from picamera import PiCamera

from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection
from aiy.vision.annotator import Annotator


def avg_joy_score(faces):
    if faces:
        return sum(face.joy_score for face in faces) / len(faces)
    return 0.0

def main():
    """Face detection camera inference example."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_frames', '-n', type=int, dest='num_frames', default=None,
        help='Sets the number of frames to run for, otherwise runs forever.')
    args = parser.parse_args()

    # Forced sensor mode, 1640x1232, full FoV. See:
    # https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
    # This is the resolution inference run on.
    with PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=30) as camera:
        camera.start_preview()
        
        # Annotator renders in software so use a smaller size and scale results
        # for increased performace.
        annotator = Annotator(camera, dimensions=(320, 240))
        
        scale_x = 320 / 1640
        scale_y = 240 / 1232

        # Incoming boxes are of the form (x, y, width, height). Scale and
        # transform to the form (x1, y1, x2, y2).
        def transform(bounding_box):
            x, y, width, height = bounding_box
            return (scale_x * x, scale_y * y, scale_x * (x + width),
                    scale_y * (y + height))

        with CameraInference(face_detection.model()) as inference:
            for result in inference.run(args.num_frames):
                faces = face_detection.get_faces(result)
                
                from PIL import Image, ImageDraw
                camera.capture('test.jpg')
                img=Image.open('test.jpg')
                img=img.resize((320,240),Image.ANTIALIAS)
                annotator.clear()
                #boxes=[]
                for face in faces:
                    annotator.bounding_box(transform(face.bounding_box), fill=0)
                    print(transform(face.bounding_box))
                    a = ImageDraw.ImageDraw(img)
                    a.rectangle(transform(face.bounding_box))
                annotator.update()
                #img=Image.open('test.jpg')
                #a = ImageDraw.ImageDraw(img)
                #a.rectangle(boxes[0])
                img.save('human.jpg')
                break
                #camera.capture('test3.jpg')
                # print(annotator._buffer.tobytes())
                
                #img=annotator._buffer
                #print(img)
                #img = Image.fromarray(annotator._buffer*255)
                #img.save("faces3.png")
                
                #annotator._camera.capture('test1.jpg')
                import time
                time.sleep(5)
                
                print('#%05d (%5.2f fps): num_faces=%d, avg_joy_score=%.2f' %
                    (inference.count, inference.rate, len(faces), avg_joy_score(faces)))

        camera.stop_preview()


if __name__ == '__main__':
    main()
