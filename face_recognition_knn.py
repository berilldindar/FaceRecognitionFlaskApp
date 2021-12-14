import math
from sklearn import neighbors
import os
import os.path
import pickle
from PIL import Image, ImageDraw
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def train(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    X = []
    y = []
    # Eğitim setindeki her bir kişiyi tanımlayın
    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue
        # Mevcut kişi için her bir eğitim görüntüsü arasında tanımlayın
        for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
            image = face_recognition.load_image_file(img_path)
            face_bounding_boxes = face_recognition.face_locations(image)
            if len(face_bounding_boxes) != 1:
                # Bir eğitim görselinde hiç kimse (veya çok fazla kişi) yoksa görseli atlayın.
                if verbose:
                    print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
            else:
                # Eğitim setine mevcut görüntü için yüz kodlaması ekleyin
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                y.append(class_dir)
    # KNN sınıflandırıcısında ağırlıklandırma için kaç tane komşu kullanılacağını belirleyin
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)
    # KNN sınıflandırıcısını oluşturun ve eğitin
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)
    # Eğitilmiş KNN sınıflandırıcısını kaydedin
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)
    return knn_clf
def predict(X_img_path, knn_clf=None, model_path=None, distance_threshold=0.6):
    if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
        raise Exception("Invalid image path: {}".format(X_img_path))

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Eğitilmiş bir KNN modeli yükleyin (geçilmişse)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)
    # Görüntü dosyasını yükleyin ve yüz konumlarını bulun
    X_img = face_recognition.load_image_file(X_img_path)
    X_face_locations = face_recognition.face_locations(X_img)

    # Görüntüde yüz bulunamazsa, boş bir sonuç döndürün.
    if len(X_face_locations) == 0:
        return []
    # Test görüntüsündeki yüzler için kodlamaları bulun
    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)

    # Test yüzü için en iyi eşleşmeleri bulmak için KNN modelini kullanın
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Sınıfları tahmin edin ve eşik dahilinde olmayan sınıflandırmaları kaldırın
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]
def show_prediction_labels_on_image(img_path, predictions):
    pil_image = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    for name, (top, right, bottom, left) in predictions:
        # Yastık modülünü kullanarak yüzün çevresine bir kutu çizin
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
        # Pillow kütüphanesinde UTF-8 olmayan metinle patlayan bir hata oluştuğu için
        # varsayılan bitmap yazı tipini kullanırken UTF-8 kullanmalısın
        name = name.encode("UTF-8")
        # Yüzün altında bir ad olan bir etiket çizin
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Pillow belgelerine göre çizim kitaplığını bellekten kaldırın
    del draw
    # Sonuç görüntüsü
    pil_image.show()
if __name__ == "__main__":
    # ADIM 1: KNN sınıflandırıcısını eğitin ve diske kaydedin
    # Model eğitilip kaydedildikten sonra bir dahaki sefere bu adımı atlayabilirsiniz.
    print("Training KNN classifier...")
    classifier = train("knn_examples/train", model_save_path="trained_knn_model.clf", n_neighbors=2)
    print("Training complete!")

    # ADIM 2: Eğitilmiş sınıflandırıcıyı kullanarak bilinmeyen görüntüler için tahminler yapın
    for image_file in os.listdir("knn_examples/test"):
        full_file_path = os.path.join("knn_examples/test", image_file)

        print("Looking for faces in {}".format(image_file))

        # Eğitimli bir sınıflandırıcı modeli kullanarak görüntüdeki tüm kişileri bulun
        # Not: Sınıflandırıcı dosya adını veya sınıflandırıcı model örneğini iletebilirsiniz.
        predictions = predict(full_file_path, model_path="trained_knn_model.clf")

        # Sonuçları konsolda yazdır
        for name, (top, right, bottom, left) in predictions:
            print("- Found {} at ({}, {})".format(name, left, top))

        # Bir görüntünün üzerine yerleştirilmiş sonuçları göster
        show_prediction_labels_on_image(os.path.join("knn_examples/test", image_file), predictions)