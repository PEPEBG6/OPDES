#Importamos las librerias
import re
import pandas as pd
from deep_translator import GoogleTranslator
import nltk
"""import ssl

try:
    _create_unverified_https_context=ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context=_create_unverified_https_context""" 
#nltk.download()
from nltk.tokenize import word_tokenize
from nltk import pos_tag
#nltk.download('stopwords')
from nltk.corpus import stopwords
#nltk.download('wordnet')
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import sentiwordnet as swn
import matplotlib.pyplot as plt
#Paso 1: Limpiar y traducción del texto
#Cargamos el archivo con los comentarios
data = pd.read_csv('RedNeuronal/review.csv', delimiter=",")
data.head()
#Eliminamos la columna unnamed:1
mydata=data.drop('Unnamed: 1',axis=1)
mydata.head()
print(mydata)

#Traducimos el texto de Español a Ingles
translator=GoogleTranslator(source="es",target="en")
mydata.review=mydata.review.apply(translator.translate)
print(mydata)
#Funcion para limpiar el texto del archivo
def clean(text):
    #Renovemos los caracteres y numeros que no se ocuparan
    text=re.sub('[^A-Za-z]+',' ',text)
    return text
#Limpiamos el texto en la columna comentario
mydata['Cleaned.Reviews']=mydata['review'].apply(clean)
mydata.head()
print(mydata)

#Paso 2:
#2.1 Tokenización: Es el proceso para dividir el texto en diferentes partes llamados tokens
#2.2 Etiquetado POST(Etiquetado gramatical): Es un proceso de conversión de cada token en una tupla que tiene la forma (palabra,etiqueta)
#2.3 Eliminación de palabras irrelevantes

#Generamos el diccionario de etiquetado gramatical
#J=Adjetivo V=Verbo N=Sustantivo y R=Adverbio 
pos_dict={'J':wordnet.ADJ,'V':wordnet.VERB,'N':wordnet.NOUN,'R':wordnet.ADV}

def token_stop_pos(text):
    tags=pos_tag(word_tokenize(text))
    newlist=[]
    for word, tag in tags:
        if word.lower() not in set(stopwords.words('english')):
            newlist.append(tuple([word,pos_dict.get(tag[0])]))
    return newlist

mydata['POS_tagged']=mydata['Cleaned.Reviews'].apply(token_stop_pos)
mydata.head()
print(mydata)

#Paso 3: Obtención de la palabra raíz
#Una palabra raíz e sparte de una palabra responsable de su significado léxico  
wordnet_lemmatizer=WordNetLemmatizer()

def lemmatize(pos_data):
    lemma_rew=" "
    for word, pos in pos_data:
        if not pos:
            lemma=word
            lemma_rew=lemma_rew + " " + lemma
        else:
            lemma=wordnet_lemmatizer.lemmatize(word,pos=pos)
            lemma_rew=lemma_rew + " " + lemma
    return lemma_rew

mydata['Lemma']=mydata['POS_tagged'].apply(lemmatize)
mydata.head()
#Aquí se muestra la oración inicial, contra la oración procesada mostrando las palabras importantes que se procesaran
print(mydata[['review','Lemma']])

#Paso 4: Utilizar los algoritmos de Análisis de Sentimientos(Textblob, VADER, Sentimientos)

#Primer libreria: Textblob

#Estos nos calculara la polaridad, esta varía de -1 a 1(1 más positivo), 0 es neutral, -1 es más negativo
#La subjetividad (efectividad), esta varía de 0 a 1(0 es muy objetivo y 1 muy subjetivo)

#Funcion para calcular la subjetividad
def getSubjectivity(comentarios):
    return TextBlob(comentarios).sentiment.subjectivity
#Funcion para calcular la polaridad
def getPolarity(comentarios):
    return TextBlob(comentarios).sentiment.polarity
#Funcion para analizar los resultados
def analysis(score):
    if score <0:
        return 'Negativo'
    elif score==0:
        return 'Neutro'
    else:
        return 'Positivo'

fin_data=pd.DataFrame(mydata[['review','Lemma']])
fin_data['Subjetividad']=fin_data['Lemma'].apply(getSubjectivity)
fin_data['Polaridad']=fin_data['Lemma'].apply(getPolarity)
fin_data['Resultado']=fin_data['Polaridad'].apply(analysis)
fin_data.head()
print(fin_data)

tb_counts=fin_data.Resultado.value_counts()
print(tb_counts)

#Graficamos los resultados
plt.title("Resultados TextBlob")
plt.figure(figsize=(10,7))
plt.pie(tb_counts.values, labels=tb_counts.index, explode=(0.1,0,0), autopct='%1.1f%%', shadow=False)
plt.show()

