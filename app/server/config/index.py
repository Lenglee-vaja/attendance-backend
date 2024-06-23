from insightface.app import FaceAnalysis


faceApp = FaceAnalysis(name='buffalo_sc',
                      root='insightface_model',
                      providers=['CPUExecutionProvider'])

faceApp.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.5)