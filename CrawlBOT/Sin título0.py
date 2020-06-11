from googletrans import Translator
translator = Translator()
def translate(text, dest):
    while(True):
        try:
            global translator
            target_text = translator.translate(text, src='en', dest=dest)
            return target_text.text.lower()
        except:
            print("Don't worry, take a break")
            translator = Translator()
            
for n in range(10000):
    translate("hello word", "it")