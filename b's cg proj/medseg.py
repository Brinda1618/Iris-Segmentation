import cv2 as cv
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

# Left and right eyes indices
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

# Fixed size for displaying iris regions
DISPLAY_SIZE = (400, 300) 

cap = cv.VideoCapture(0)

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv.flip(frame, 1)

        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img_h, img_w = frame.shape[:2]
        results = face_mesh.process(rgb_frame)
        mask = np.zeros((img_h, img_w), dtype=np.uint8)

        if results.multi_face_landmarks:
            mesh_points = np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                                    for p in results.multi_face_landmarks[0].landmark])

            (l_cx, l_cy), l_radius = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), r_radius = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            center_left = np.array([l_cx, l_cy], dtype=np.int32)
            center_right = np.array([r_cx, r_cy], dtype=np.int32)
            cv.circle(frame, center_left, int(l_radius), (200, 255, 0), 1, cv.LINE_AA)
            cv.circle(frame, center_right, int(r_radius), (200, 255, 0), 1, cv.LINE_AA)

            # Drawing on the mask
            cv.circle(mask, center_left, int(l_radius), (255, 255, 255), -1, cv.LINE_AA)
            cv.circle(mask, center_right, int(r_radius), (255, 255, 255), -1, cv.LINE_AA)

            # Extract left iris region
            left_iris_mask = np.zeros_like(frame)
            cv.circle(left_iris_mask, center_left, int(l_radius), (255, 255, 255), -1, cv.LINE_AA)
            left_iris_region = cv.bitwise_and(frame, left_iris_mask)
            left_iris_resized = cv.resize(left_iris_region, DISPLAY_SIZE)

            # Extract right iris region
            right_iris_mask = np.zeros_like(frame)
            cv.circle(right_iris_mask, center_right, int(r_radius), (255, 255, 255), -1, cv.LINE_AA)
            right_iris_region = cv.bitwise_and(frame, right_iris_mask)
            right_iris_resized = cv.resize(right_iris_region, DISPLAY_SIZE)

            combined_frame = np.hstack((left_iris_resized, right_iris_resized))
            cv.imshow('Combined Iris Regions', combined_frame)

        cv.imshow('Mask', mask)
        cv.imshow('Original Frame', frame)
        key = cv.waitKey(1)
        if key == ord('q'):
            break

cap.release()
cv.destroyAllWindows()
