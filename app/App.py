import time
from scipy import spatial
import numpy as np
import shutil
import json
import requests
from bs4 import BeautifulSoup
import re
import fasttext
import sys
import matplotlib.pyplot as plt
from PyQt6.QtCore import pyqtSlot, QRunnable, QThreadPool
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QStatusBar, QWidget, \
    QVBoxLayout, QSpinBox, QLabel, QLineEdit, QHBoxLayout, QListWidget, QFileDialog, QProgressBar
print('Установка модели...')
import fasttext.util
fasttext.util.download_model('ru', if_exists='ignore')
try:
    import nltk
    nltk.download('stopwords')

except:
    pass
print('Успешно!')
from nltk.corpus import stopwords


labels = ["Отсутсвуют данные"]
sizes = [100]
_, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['grey'])
plt.savefig('./files/pie.png', bbox_inches='tight')


class SettingsWindowb(QWidget):
    def __init__(self):
        super().__init__()
        settings = json.loads(open("./settings/settings.json").read())
        layout = QVBoxLayout()
        self.label = QLabel("Кол-во отзывов:")
        self.setWindowTitle("Настройки banki.ru")

        self.inp = QSpinBox()
        self.inp.setMinimum(100)
        self.inp.setMaximum(100000)
        self.inp.setSingleStep(5)
        self.inp.setValue(settings["bankiru"]["count"])
        self.inp.valueChanged.connect(self.set_banki_c)

        self.label2 = QLabel("Страница:")
        self.inp2 = QSpinBox()
        self.inp2.setMinimum(1)
        self.inp2.setMaximum(100)
        self.inp2.setSingleStep(1)
        self.inp2.setValue(settings["bankiru"]["page"])
        self.inp2.valueChanged.connect(self.set_banki_p)

        layout.addWidget(self.label)
        layout.addWidget(self.inp)
        layout.addWidget(self.label2)
        layout.addWidget(self.inp2)
        self.setLayout(layout)
        self.setFixedSize(150, 100)

    def set_banki_c(self, i):
        settings = json.loads(open("./settings/settings.json").read())
        settings["bankiru"]["count"] = int(i)
        with open('./settings/settings.json', 'w') as file:
            json.dump(settings, file)

    def set_banki_p(self, i):
        settings = json.loads(open("./settings/settings.json").read())
        settings["bankiru"]["page"] = int(i)
        with open('./settings/settings.json', 'w') as file:
            json.dump(settings, file)

class SettingsWindows(QWidget):
    def __init__(self):
        super().__init__()
        settings = json.loads(open("./settings/settings.json").read())
        self.label = QLabel("Кол-во отзывов:")
        self.setWindowTitle("Настройки sravni.ru")

        layout = QVBoxLayout()

        self.inp = QSpinBox()
        self.inp.setMinimum(100)
        self.inp.setMaximum(100000)
        self.inp.setSingleStep(5)
        self.inp.setValue(settings["sravniru"]["count"])
        self.inp.valueChanged.connect(self.set_banki_c)

        self.label2 = QLabel("Страница:")
        self.inp2 = QSpinBox()
        self.inp2.setMinimum(1)
        self.inp2.setMaximum(100)
        self.inp2.setSingleStep(1)
        self.inp2.setValue(settings["sravniru"]["page"])
        self.inp2.valueChanged.connect(self.set_banki_p)

        layout.addWidget(self.label)
        layout.addWidget(self.inp)
        layout.addWidget(self.label2)
        layout.addWidget(self.inp2)
        self.setLayout(layout)
        self.setFixedSize(150, 100)

    def set_banki_c(self, i):
        settings = json.loads(open("./settings/settings.json").read())
        settings["sravniru"]["count"] = int(i)
        with open('./settings/settings.json', 'w') as file:
            json.dump(settings, file)

    def set_banki_p(self, i):
        settings = json.loads(open("./settings/settings.json").read())
        settings["sravniru"]["page"] = int(i)
        with open('./settings/settings.json', 'w') as file:
            json.dump(settings, file)


# Подкласс QMainWindow для настройки главного окна приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.set1 = SettingsWindowb()
        self.set2 = SettingsWindows()
        self.set3 = ProgressBar()
        self.set4 = ProgressBarA()
        self.set5 = ProgressBarV()
        self.setWindowTitle("Анализ клиентских отзывов")
        self.setGeometry(0, 0, 800, 600)

        layout = QHBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()


        self.button_action = QAction("&Открыть", self)
        self.button_action.setStatusTip("Открыть файл")
        self.button_action.triggered.connect(self.on_open)

        self.button_action2 = QAction("&Сохранить", self)
        self.button_action2.setStatusTip("Сохранить файл")
        self.button_action2.setDisabled(True)
        self.button_action2.triggered.connect(self.on_save)
        menu = self.menuBar()

        button_action3 = QAction("&Банки.ру", self)
        button_action3.setStatusTip("Настроить получение отзывов с банки.ру")
        button_action3.triggered.connect(self.bankiru)

        button_action4 = QAction("&Сравни.ру", self)
        button_action4.setStatusTip("Настроить получение отзывов с сравни.ру")
        button_action4.triggered.connect(self.sravniru)

        file_menu = menu.addMenu("&Файл")
        file_menu.addAction(self.button_action)
        file_menu.addAction(self.button_action2)
        file_menu2 = menu.addMenu("&Настройки")
        file_menu2.addAction(button_action3)
        file_menu2.addAction(button_action4)

        self.inp = QListWidget()
        self.inp.addItem("Здесь будут результаты")
        self.inp.setDisabled(True)
        self.rev_l = QLineEdit()
        self.rev_l.setPlaceholderText("Введите отзыв для поиска")
        self.rev_l.setDisabled(True)
        self.rev_vw = QListWidget()
        self.rev_vw.setDisabled(True)
        self.but_rev = QPushButton()
        self.but_rev.setText("Найти схожие отзывы")
        self.but_rev.clicked.connect(self.on_search)
        self.but_rev.setDisabled(True)



        layout2.addWidget(self.inp, 1)
        layout3.addWidget(self.rev_l, 1)
        layout3.addWidget(self.rev_vw, 2)
        layout3.addWidget(self.but_rev, 3)

        self.but1 = QPushButton()
        self.but1.setText("Собрать отзывы")
        self.but1.clicked.connect(self.on_start)
        self.but2 = QPushButton()
        self.but2.setText("Проанализировать отзывы")
        self.but2.setDisabled(True)
        self.but2.clicked.connect(self.on_analize)
        layout2.addWidget(self.but1)
        layout2.addWidget(self.but2)
        self.setStatusBar(QStatusBar(self))
        pixmap = QPixmap("./files/pie.png")
        self.label = QLabel()
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.width(), pixmap.height())

        layout.addWidget(self.label, 1)
        layout.addLayout(layout3, 2)
        layout.addLayout(layout2, 3)
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

        self.threadpool = QThreadPool()
        self.threadpool2 = QThreadPool()

    def bankiru(self, s):
        self.set1.show()
    def sravniru(self, s):
        self.set2.show()

    def on_save(self, _):
        dialog = QFileDialog(self)
        file_path = dialog.getSaveFileUrl(filter="Belchata (*.blt)")[0].path()
        if file_path != "":
            try:
                shutil.copy("./files/reviews.blt", file_path[1:])
            except shutil.Error:
                pass


    def on_open(self, _):
        dialog = QFileDialog(self)
        file_path = dialog.getOpenFileUrl(filter="Belchata (*.blt)")[0].path()
        print(file_path)
        if file_path != "":
            try:
                shutil.copy(file_path[1:], "./files/reviews.blt")
            except shutil.SameFileError:
                pass
            self.but2.setDisabled(False)
            labels = ["Положительные", "Отрицательные"]
            sizes = [len(json.loads(open('./files/reviews.blt').read())["good"]), len(json.loads(open('./files/reviews.blt').read())["bad"])]
            _, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['lime', 'red'])
            plt.savefig('./files/pie.png', bbox_inches='tight')
            pixmap = QPixmap("./files/pie.png")
            self.label.setPixmap(pixmap)
            self.rev_l.setDisabled(False)
            self.rev_vw.setDisabled(False)
            self.but_rev.setDisabled(False)
            self.button_action2.setDisabled(False)


    def on_start(self):
        self.set3.show()
        r = Get_revs(self)
        self.but1.setDisabled(True)
        self.but2.setDisabled(True)
        self.but_rev.setDisabled(True)
        self.rev_vw.setDisabled(True)
        self.rev_l.setDisabled(True)
        self.button_action2.setDisabled(True)
        self.button_action.setDisabled(True)
        self.threadpool.start(r)

    def on_analize(self):
        self.set4.show()
        a = Analize(self)
        self.but1.setDisabled(True)
        self.but2.setDisabled(True)
        self.but_rev.setDisabled(True)
        self.rev_vw.setDisabled(True)
        self.rev_l.setDisabled(True)
        self.button_action2.setDisabled(True)
        self.button_action.setDisabled(True)
        self.threadpool.start(a)
    def on_search(self, s):
        print(self)
        try:
            self.set5.show()
            v = Vect(self)
            self.but1.setDisabled(True)
            self.but2.setDisabled(True)
            self.but_rev.setDisabled(True)
            self.rev_vw.setDisabled(True)
            self.rev_l.setDisabled(True)
            self.button_action2.setDisabled(True)
            self.button_action.setDisabled(True)
            self.threadpool.start(v)
        except Exception as e:
            print(e)


class Analize(QRunnable):
    def __init__(self, p):
        self.p = p
        super(Analize, self).__init__()

    @pyqtSlot()
    def run(self):
        try:
            self.p.inp.clear()
            self.p.set4.prog_bar.setValue(0)
            reviews_sorted = json.loads(open("./files/reviews.blt").read())
            self.p.set4.prog_bar.setValue(10 + self.p.set4.prog_bar.value())

            reviews = reviews_sorted["good"] + reviews_sorted["bad"]
            reviews_deleted_symbols = self.delete_symbols(reviews)
            self.p.set4.prog_bar.setValue(10 + self.p.set4.prog_bar.value())
            reviews_lower = self.lower_review(reviews_deleted_symbols)
            self.p.set4.prog_bar.setValue(10 + self.p.set4.prog_bar.value())

            reviews_vector = self.to_vector(reviews_lower, len(reviews_sorted["good"]), len(reviews_sorted["bad"]))
            self.p.set4.prog_bar.setValue(10 + self.p.set4.prog_bar.value())

            vec_reviews_good = np.array(reviews_vector["good"])
            vec_reviews_bad = np.array(reviews_vector["bad"])
            self.p.set4.prog_bar.setValue(10 + self.p.set4.prog_bar.value())
            print("Ищу общие схожести в отзывах...")
            reviews = json.loads(open('./files/reviews.blt').read())
            self.p.set4.prog_bar.setValue(10 + self.p.set4.prog_bar.value())
            reviews_final = {"good": [], "bad": []}
            for vec in vec_reviews_good:
                print(1)
                try:
                    tree = spatial.KDTree(vec_reviews_good)
                    similar_review = tree.query(vec, max(5, int(round(
                        len(json.loads(open('./files/reviews.blt').read())["good"]) * 0.5) ** 0.5)))
                    similar_vec = [vec_reviews_good[i].tolist() for i in similar_review[1]]
                    for s in similar_vec:
                        ind = reviews_vector["good"].index(s)

                        reviews["good"].pop(ind)
                        r = reviews["good"][ind]
                    reviews_final["good"].append(r)

                except:
                    continue
            self.p.set4.prog_bar.setValue(20 + self.p.set4.prog_bar.value())
            r = ""
            for vec in vec_reviews_bad:
                print(2)
                try:
                    tree = spatial.KDTree(vec_reviews_bad)
                    similar_review = tree.query(vec, max(5, int(round(
                        len(json.loads(open('./files/reviews.blt').read())["bad"]) * 0.5) ** 0.5)))
                    similar_vec = [vec_reviews_bad[i].tolist() for i in similar_review[1]]
                    for s in similar_vec:
                        ind = reviews_vector["bad"].index(s)

                        reviews["bad"].pop(ind)
                        r = reviews["bad"][ind]
                    reviews_final["bad"].append(r)
                except:
                    continue
            print(3)
            self.p.set4.prog_bar.setValue(19 + self.p.set4.prog_bar.value())
            # # self.p.inp.addItems(["1"])
            #
            self.p.set4.hide()
            print(4)
            self.p.inp.setDisabled(False)
            self.p.inp.clear()

            self.p.but1.setDisabled(False)
            self.p.but2.setDisabled(False)
            self.p.but_rev.setDisabled(False)
            self.p.rev_vw.setDisabled(False)
            self.p.rev_l.setDisabled(False)
            self.p.button_action2.setDisabled(False)
            self.p.button_action.setDisabled(False)
            self.p.inp.addItem("--------------------")
            self.p.inp.addItem("Положительные черты:")
            self.p.inp.addItem("--------------------")
            for r in list(set(reviews_final["good"])):
                self.p.inp.addItem(r)
            self.p.inp.addItem("--------------------")
            self.p.inp.addItem("Отрицательные черты:")
            self.p.inp.addItem("--------------------")
            for r in list(set(reviews_final["bad"])):
                self.p.inp.addItem(r)
            del reviews, reviews_lower, reviews_final, reviews_vector, reviews_deleted_symbols, vec_reviews_bad, similar_vec, similar_review, self.p
        except Exception as e:
            print(e, 23)

    def delete_symbols(self, reviews_a):
        reviews_symbols = []
        print('Очистка лишних символов в отзывах...')
        for word in reviews_a:
            reg_sumbols = re.sub('[^\w\s]+|[\d]+', ' ', word)
            reg_eng_symbols = re.sub('[a-zA-Z\s]+', ' ', reg_sumbols)
            reviews_symbols.append(reg_eng_symbols.split())
        return reviews_symbols

    def delete_stop_words(self, review_a):
        stop_words = list(stopwords.words('russian'))
        reviews_stop_words = []
        for s in review_a:
            word = s.lower()
            if word not in stop_words and word != "\n":
                reviews_stop_words.append(word)
        return reviews_stop_words

    def lower_review(self, reviews_a):
        try:
            print('Удаление стоп-слов из отзывов...')
            lower_reviews = []
            for rev in reviews_a:
                deleted_stop_words = self.delete_stop_words(rev)
                lower_reviews.append(deleted_stop_words)
            return lower_reviews
        except Exception as e:
            print(e)

    def get_vector(self, review, ft):
        sentence = "".join(s + " " for s in review)
        sentence_vector = ft.get_sentence_vector(sentence)
        return sentence_vector

    def to_vector(self, lower_reviews_a, l1, l2):
        ft = fasttext.load_model('cc.ru.300.bin')
        print("Перевод отзывов в вектора...")
        reviews_v = {"good": [], "bad": []}
        for i in range(l1):
            reviews_v["good"].append(self.get_vector(lower_reviews_a[i], ft).tolist())
        for i in range(l2):
            reviews_v["bad"].append(
                self.get_vector(lower_reviews_a[i + l1], ft).tolist())
        return reviews_v


class Vect(QRunnable):
    def __init__(self, p):
        self.s = p
        super(Vect, self).__init__()

    @pyqtSlot()
    def run(self):
        user_review = self.s.rev_l.text()
        if str(user_review).replace(" ", "") != "":
            self.s.set5.prog_bar.setValue(0)
            reviews_sorted = json.loads(open("./files/reviews.blt").read())
            self.s.set5.prog_bar.setValue(11 + self.s.set5.prog_bar.value())
            reviews = reviews_sorted["good"] + reviews_sorted["bad"]
            reviews_deleted_symbols = self.delete_symbols(reviews)
            self.s.set5.prog_bar.setValue(11 + self.s.set5.prog_bar.value())
            reviews_lower = self.lower_review(reviews_deleted_symbols)
            del reviews_deleted_symbols
            self.s.set5.prog_bar.setValue(11 + self.s.set5.prog_bar.value())
            self.ft = fasttext.load_model('cc.ru.300.bin')
            reviews_vector = self.to_vector(reviews_lower)
            del reviews_lower
            self.s.set5.prog_bar.setValue(11 + self.s.set5.prog_bar.value())
            reg_symbols = re.sub('[^\w\s]+|[\d]+', ' ', user_review)
            reg_eng_symbols = re.sub('[a-zA-Z\s]+', ' ', reg_symbols)
            new_user_review = reg_eng_symbols.split()
            del reg_eng_symbols, reg_symbols
            self.s.set5.prog_bar.setValue(11 + self.s.set5.prog_bar.value())
            lower_user_review = []
            deleted_stop_words = self.delete_stop_words(new_user_review)
            lower_user_review.append(deleted_stop_words)
            self.s.set5.prog_bar.setValue(11 + self.s.set5.prog_bar.value())
            vec_user_review = self.get_vector(*lower_user_review).tolist()

            self.s.set5.prog_bar.setValue(11 + self.s.set5.prog_bar.value())
            try:
                similar_rev = self.find_similar(reviews_vector, vec_user_review)
                similar_vec = [reviews[i] for i in similar_rev]
                self.s.set5.prog_bar.setValue(11 + self.s.set5.prog_bar.value())
                revs = []
                for s in similar_vec:
                    revs.append(s)
                self.s.set5.prog_bar.setValue(11 + self.s.set5.prog_bar.value())
                self.s.rev_vw.setDisabled(False)
                del reviews, similar_vec, similar_rev, vec_user_review, lower_user_review, deleted_stop_words
                self.s.but1.setDisabled(False)
                self.s.but2.setDisabled(False)
                self.s.rev_l.setDisabled(False)
                self.s.rev_vw.setDisabled(False)
                self.s.but_rev.setDisabled(False)
                self.s.button_action2.setDisabled(False)
                self.s.button_action.setDisabled(False)
                for rev in list(set(revs)):
                    self.s.rev_vw.addItem(rev)
                    print(rev)
                time.sleep(1)
                self.s.set5.hide()
                del revs
            except Exception as e:
                print(e)
        else:
            self.s.but1.setDisabled(False)
            self.s.but2.setDisabled(False)
            self.s.rev_l.setDisabled(False)
            self.s.rev_vw.setDisabled(False)
            self.s.but_rev.setDisabled(False)
            self.s.button_action2.setDisabled(False)
            self.s.button_action.setDisabled(False)
            self.s.set5.hide()




    def delete_symbols(self, reviews_a):
        reviews_symbols = []
        print('Очистка лишних символов в отзывах...')
        for word in reviews_a:
            reg_sumbols = re.sub('[^\w\s]+|[\d]+', ' ', word)
            reg_eng_symbols = re.sub('[a-zA-Z\s]+', ' ', reg_sumbols)
            reviews_symbols.append(reg_eng_symbols.split())
        return reviews_symbols

    def delete_stop_words(self, review_a):
        stop_words = list(stopwords.words('russian'))
        reviews_stop_words = []
        for s in review_a:
            word = s.lower()
            if word not in stop_words and word != "\n":
                reviews_stop_words.append(word)
        return reviews_stop_words

    def lower_review(self, reviews_a):
        print('Удаление стоп-слов из отзывов...')
        lower_reviews = []
        for rev in reviews_a:
            deleted_stop_words = self.delete_stop_words(rev)
            lower_reviews.append(deleted_stop_words)
        return lower_reviews

    def get_vector(self, review):
        try:
            sentence = "".join(s + " " for s in review)
            sentence_vector = self.ft.get_sentence_vector(sentence)
            return sentence_vector
        except Exception as e:
            print(e)

    def to_vector(self, lower_reviews_a):
        try:
            print("Перевод отзывов в вектора...")
            reviews_v = []
            for i in range(len(lower_reviews_a)):
                reviews_v.append(self.get_vector(lower_reviews_a[i]).tolist())
            return reviews_v
        except Exception as e:
            print(e)

    def find_similar(self, vec_reviews, user_review):
        tree = spatial.KDTree(vec_reviews)
        similar_review = tree.query(user_review, 10)
        print()
        return similar_review[1]

class Get_revs(QRunnable):
    def __init__(self, p):
        self.p = p

        super(Get_revs, self).__init__()

    @pyqtSlot()
    def run(self):
        self.p.set3.prog_bar.setValue(0)
        settings = json.loads(open('./settings/settings.json').read())
        revs_s = self.get_review_from_sravniru(settings["sravniru"]["count"], settings["sravniru"]["page"])
        revs_b = self.get_review_from_bankiru(settings["bankiru"]["count"], settings["bankiru"]["page"], self.p.set3.prog_bar.value() - 1)
        reviews_sorted = {"good": revs_b["good"] + revs_s["good"], "bad": revs_b["bad"] + revs_s["bad"]}
        with open("./files/reviews.blt", 'w') as f:
            json.dump(reviews_sorted, f)
        self.p.set3.hide()
        self.p.but1.setDisabled(False)
        self.p.but2.setDisabled(False)
        self.p.rev_l.setDisabled(False)
        self.p.rev_vw.setDisabled(False)
        self.p.but_rev.setDisabled(False)
        self.p.button_action2.setDisabled(False)
        self.p.button_action.setDisabled(False)
        del revs_s, revs_b, reviews_sorted, settings
        try:
            labels = ["Положительные", "Отрицательные"]
            sizes = [len(json.loads(open('./files/reviews.blt').read())["good"]),
                     len(json.loads(open('./files/reviews.blt').read())["bad"])]
            _, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['lime', 'red'])
            plt.savefig('./files/pie.png', bbox_inches='tight')
            pixmap = QPixmap("./files/pie.png")
            self.p.label.setPixmap(pixmap)
            del self.p
        except Exception as e:
            print(e)


    def get_review_from_bankiru(self, num=100, page=1, k=0):
        try:
            revs = {"good": [], "bad": []}
            reviews = 0
            links = []
            while True:
                req = requests.get("https://www.banki.ru/services/responses/bank/tcs/" + f"?page={page}")
                soup = BeautifulSoup(req.content, "html.parser")
                for h3 in soup.find_all("h3", class_="text-weight-medium text-size-3 ldecc766d"):
                    a = h3.find_all("a")
                    links.append(a[0]['href'])
                for link in links:
                    if reviews >= num:
                        return revs
                    req = requests.get("https://www.banki.ru" + link)
                    soup = BeautifulSoup(req.content, "html.parser")
                    for div in soup.find_all("div",
                                             class_="lb1789875 markdown-inside markdown-inside--list-type_circle-fill"):
                        p = div.find_all("p")
                        review = ""
                        for r in p:
                            review += str(r.text).replace("\n", "").replace("\r", "").replace("\t", "")
                        if review == "":
                            review += div.text.replace("\n", "").replace("\r", "").replace("\t", "")
                        if review != "" and review != " " and review != "\n" and review != ', ':
                            if int(soup.find_all("div", class_="lbb810226")[0].find_all("div")[1].text) in (1, 2, 3):
                                revs["bad"].append(review)
                            elif int(soup.find_all("div", class_="lbb810226")[0].find_all("div")[1].text) in (4, 5):
                                revs["good"].append(review)

                            reviews += 1
                            print(f"Получено отзывов с банки.ру: {reviews}/{num}")
                            self.p.set3.prog_bar.setValue(abs(int(50 / num * reviews + k)))
                page += 1
        except Exception as e:
            print(e)

    def get_review_from_sravniru(self, num=100, page=1, k=0):
        revs = {"good": [], "bad": []}
        r = 0
        while True:
            if r >= num:
                return revs
            req = requests.get(
                f"https://www.sravni.ru/proxy-reviews/reviews/?filterBy=withRates&fingerPrint=ea060f38d490a841e5bae143a1505423&isClient=true&locationRoute=&newIds=true&orderBy=byDate&pageIndex={page}&pageSize=10&reviewObjectId=5bb4f769245bc22a520a6353&reviewObjectType=banks&specificProductId=&withVotes=true")
            reviews = req.json()
            if reviews["items"] == []:
                return revs
            for item in reviews["items"]:
                review = item["text"].replace("\n", "").replace("\r", "").replace("\t", "")
                if review != "" and review != " " and review != "\n" and review != ', ':
                    if int(item["rating"]) in (1, 2, 3):
                        revs["bad"].append(review)
                    elif int(item["rating"]) in (4, 5):
                        revs["good"].append(review)

                    r += 1
                    print(f"Получено отзывов с сравни.ру: {r}/{num}")
                    self.p.set3.prog_bar.setValue(abs(int(50 / num * r + k - 1)))
            page += 1


class ProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 100)
        self.setWindowTitle("Получение отзывов")
        layout = QVBoxLayout()
        self.prog_bar = QProgressBar(self)
        self.prog_bar.setValue(0)
        layout.addWidget(self.prog_bar)
        self.setLayout(layout)

class ProgressBarA(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 100)
        self.setWindowTitle("Анализ отзывов")
        layout = QVBoxLayout()
        self.prog_bar = QProgressBar(self)
        self.prog_bar.setValue(0)
        layout.addWidget(self.prog_bar)
        self.setLayout(layout)

class ProgressBarV(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 100)
        self.setWindowTitle("Поиск схожих отзывов")
        layout = QVBoxLayout()
        self.prog_bar = QProgressBar(self)
        self.prog_bar.setValue(0)
        layout.addWidget(self.prog_bar)
        self.setLayout(layout)

try:
    app = QApplication(sys.argv)

    window = MainWindow()
    app.exec()

except Exception as e:
    print(e)

