from flask import Flask, render_template, request
import textblob
from autocorrect import Speller
from typing import Tuple, List

app = Flask(__name__)

class SpellCheckerModule:
    def __init__(self) -> None:
        try:
            self.spell_check = Speller()
            self.text_blob = textblob.TextBlob("")
        except ImportError as e:
            raise Exception("The required libraries (autocorrect, textblob) are not installed.")

    def correct_spell(self, text: str) -> str:
        words = text.split()
        corrected_words = []

        for word in words:
            try:
                corrected_word = self.spell_check(word)
                corrected_words.append(corrected_word)
            except Exception as e:
                print(f"Error correcting spelling error: {e}")
                continue

        return " ".join(corrected_words)

    def analyze_text(self, text: str) -> Tuple[str, List[str]]:
        try:
            corrections = [
                ("should be", "could be"),
                ("is not", "is not, but also might be"),
            ]
            corrected_text = self.correct_spell(text)
            grammar_mistakes = []

            for word in text.split():
                if self.spell_check(word) != word:
                    for correction in corrections:
                        if word == correction[0]:
                            corrected_text = corrected_text.replace(correction[0], correction[1])
                            grammar_mistakes.append(f"{word} -> {correction[1]}")
                            break

            return corrected_text, grammar_mistakes
        except Exception as e:
            print(f"Error correcting grammar errors: {e}")
            return "", []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/correct', methods=['POST'])
def correct_text():
    text = request.form['text']
    corrected_result, corrections = SpellCheckerModule().analyze_text(text)
    return render_template('corrected_result.html', result=corrected_result, errors=corrections)

@app.route('/download', methods=['POST'])
def download_file():
    file = request.files['file']
    readable_file = file.read().decode('utf-8')
    corrected_file_text = SpellCheckerModule().correct_spell(readable_file)
    return render_template('corrected_result.html', result=corrected_file_text, errors=[])

if __name__ == "__main__":
    app.run(debug=True)
