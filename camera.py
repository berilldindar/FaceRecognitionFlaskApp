import cv2
import pickle
from imutils.video import WebcamVideoStream
import face_recognition
class VideoCamera(object):
    def __init__(self):
        self.stream = WebcamVideoStream(src=0).start()
        with open("trained_knn_model.clf", 'rb') as f:
            self.knn_clf = pickle.load(f)

    def __del__(self):
        self.stream.stop()

    def predict(self, frame, knn_clf, distance_threshold=0.4):
        # Yüz lokasyonunu bul
        X_face_locations = face_recognition.face_locations(frame)
        if len(X_face_locations) == 0:
            return []

        # Test görüntüsündeki yüzler için kodlamaları bulun
        faces_encodings = face_recognition.face_encodings(frame, known_face_locations=X_face_locations)

        # Test yüzü için en iyi eşleşmeleri bulmak için KNN modelini kullanın
        closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=2)
        are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]
        for i in range(len(X_face_locations)):
            print("closest_distances")
            print(closest_distances[0][i][0])

        # Sınıfları tahmin edin ve eşik dahilinde olmayan sınıflandırmaları kaldırın
        return [(pred, loc) if rec else ("Unknown", loc) for pred, loc, rec in
                zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

    def get_frame(self):
        image = self.stream.read()
        li = []
        global person_name
        # Motion JPEG kullanıyoruz, ancak OpenCV varsayılan olarak ham görüntüleri yakalamak için
        #bu yüzden doğru şekilde görüntülemek için onu JPEG olarak kodlamalıyız.
        # video akışı.
        f = open("trainStatus.txt")
        for i in f:
            isTrained = int(i)
        if isTrained:  # güncellenmiş model dosyasını değiştir
            # Tekrar yükle
            with open("trained_knn_model.clf", 'rb') as f:
                self.knn_clf = pickle.load(f)
            file = open("trainStatus.txt", "w")
            file.write("0")
            file.close()
        predictions = self.predict(image, self.knn_clf)
        name = ''
        for name, (top, right, bottom, left) in predictions:
            startX = int(left)
            startY = int(top)
            endX = int(right)
            endY = int(bottom)

            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)
            cv2.putText(image, name, (endX - 70, endY - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', image)
        data = []
        data.append(jpeg.tobytes())
        data.append(name)
        return data