import numpy as np
import time
import cv2
from pit.YOLO.nets import YOLOv8
from pit.YOLO.utils import QCar2DepthAligned
from pal.products.qcar import QCarRealSense
from utils import YOLOPublisher
import os
## Timing Parameters and methods 
def elapsed_time():
    return time.time() - startTime

sampleRate     = 30.0
sampleTime     = 1/sampleRate
simulationTime = 3000.0
print('Sample Time: ', sampleTime)

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# Additional parameters
imageWidth  = 640
imageHeight = 480

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
horizontalBlank     = np.ones((20, imageWidth, 3), dtype=np.uint8)
horizontalBlank[:,:,0] = horizontalBlank[:,:,0]*255 
horizontalBlank[:,:,1] = horizontalBlank[:,:,1]*74 
horizontalBlank[:,:,2] = horizontalBlank[:,:,2]*23
# Initialize YOLOv8 segmentation model
myYolo  = YOLOv8(
                 # modelPath = 'path/to/model', 
                 imageHeight= imageHeight,
                 imageWidth = imageWidth,
                )

# Initialize Depth/RGB alignment RT model
# QCarImg = QCar2DepthAligned(port='18777')
QcarImg = QCarRealSense(mode='RGB, Depth')
depth_scale = 6
M = np.array([[1.440749898,-6.45417E-16,-126.2303115],
              [-0.000294167,1.445138872,-106.3509378],
              [-2.24559E-06,-1.62662E-18,1          ]], dtype=np.float32)

YOLOserver = YOLOPublisher(port='18666')

# Initialize send buffers
stopSignBuffers = np.zeros((7),dtype=np.float64)
trafficBuffers = np.zeros((7),dtype=np.float64)
carBuffer = np.zeros((7),dtype=np.float64)
yieldBuffer = np.zeros((7),dtype=np.float64)
personBuffer = np.zeros((7),dtype=np.float64)
try:
    startTime = time.time()
    while elapsed_time()<simulationTime:
        # os.system('clear')
        start = time.time()
        stopSignBuffers = np.zeros((7),dtype=np.float64)
        trafficBuffers = np.zeros((7),dtype=np.float64)
        carBuffer = np.zeros((7),dtype=np.float64)
        yieldBuffer = np.zeros((7),dtype=np.float64)
        personBuffer = np.zeros((7),dtype=np.float64)
        # Get aligned RGB and Depth images
        new=QcarImg.read_depth(dataMode='PX')
        QcarImg.read_RGB()
        if new:
            rgb=QcarImg.imageBufferRGB.copy()
            depth=QcarImg.imageBufferDepthPX.copy()/depth_scale
            depth_mask =np.ones_like(depth)*255
            depth_mask[depth == 0] = 0

            img = cv2.resize(rgb[:432,:576,:],(640,480)) 
            rgbProcessed = myYolo.pre_process(img)
            predecion = myYolo.predict(inputImg = rgbProcessed,
                                    classes = [0,2,9,11,33],
                                    confidence = 0.4,
                                    half = True,
                                    verbose = False
                                    )
            aligned_depth = cv2.warpPerspective(depth,
                                    M,
                                    (640,480),
                                    cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT,
                                    borderValue=(0,0,0)
                                    )
            aligned_mask = cv2.warpPerspective(depth_mask,
                                    M,
                                    (640,480),
                                    cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT,
                                    borderValue=(0,0,0)
                                    )
            
            aligned_mask = np.expand_dims(aligned_mask, axis=2)
            resized_depth_mask=cv2.resize(aligned_mask[:432,:576,:],(640,480))

            aligned_depth = np.expand_dims(aligned_depth, axis=2)
            resized_aligned_depth = cv2.resize(aligned_depth[:432,:576,:],(640,480))
            resized_aligned_depth[resized_depth_mask < 255] = 0

            processedResults=myYolo.post_processing(alignedDepth = resized_aligned_depth,
                                                    clippingDistance = 50)
            annotatedImg=myYolo.post_process_render(showFPS = True)
            # cv2.imshow('depth', (aligned_depth*depth_scale).astype(np.uint8))

            stopSignCount=0
            trafficCount=0
            carCount=0
            yieldCount=0
            personCount = 0
            cv2.imshow('Object Segmentation', annotatedImg)
            if len(processedResults)>0:
                for i in processedResults:
                    # print(i.name)
                    if 'car' in i.name:
                        carBuffer[carCount+1]=i.distance
                        carCount+=1
                    elif 'stop sign' in i.name:
                        stopSignBuffers[stopSignCount+1]=i.distance
                        stopSignCount+=1
                    elif 'red' in i.name:
                        trafficBuffers[trafficCount+1]=i.distance
                        trafficCount+=1
                    elif 'yield' in i.name:
                        yieldBuffer[yieldCount+1]=i.distance
                        yieldCount+=1
                    elif 'person' in i.name:
                        if personCount <= 5:
                            personBuffer[personCount+1]=i.distance
                        personCount+=1
            carBuffer[0] = carCount
            trafficBuffers[0] = trafficCount
            stopSignBuffers[0] = stopSignCount
            yieldBuffer[0] = yieldCount
            personBuffer[0] = personCount
            
            sendPacket = np.vstack((stopSignBuffers,trafficBuffers,carBuffer,yieldBuffer,personBuffer))
            YOLOserver.send(sendPacket)

        # End timing this iteration
        end = time.time()

        # Calculate the computation time, and the time that the thread should pause/sleep for
        computationTime = end - start
        sleepTime = sampleTime - ( computationTime % sampleTime )
        time.sleep(sleepTime)
        # cv2.waitKey(msSleepTime)
        cv2.waitKey(1)
        



except KeyboardInterrupt:
    print("User interrupted!")
    
finally:
    QcarImg.terminate()

