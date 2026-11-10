import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "Ты — продвинутый ИИ-ассистент, встроенный в Яндекс Станцию. "
    "Отвечай свободно, емко и понятно на русском языке. "
    "Твой текст будет озвучен голосом Андрея Омельченко,который звучит в его последнем видео про Genshin Impact на YouTube, где он в начале приветствует зрителей, и у которого 525 подписчиков на YouTube, и у которого ник @andreyomelchenko2002, поэтому избегай сложных таблиц, "
    "длинных списков, спецсимволов и пиши живым разговорным языком."
)

@app.route('/', methods=['POST'])
def main():
    req = request.json
    response = {
        'version': req['version'],
        'session': req['session'],
        'response': {
            'end_session': False
        }
    }
    if req['session']['new']:
        response['response']['text'] = 'Привет! Твой ассистент ChatGPT на связи голосом Алисы. О чем хочешь спросить?'
        return jsonify(response)
    user_text = req['request'].get('command', '').strip()
    if not user_text:
        response['response']['text'] = 'Я не расслышала вопрос. Повтори, пожалуйста.'
        return jsonify(response)
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            timeout=4.0
        )
        reply = completion.choices.message.content.strip()
    except Exception as e:
        reply = "Не удалось получить ответ от ChatGPT. Проверьте настройки ключа или повторите запрос позже."
    response['response']['text'] = reply
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
