import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

api_key = os.environ.get("OPENAI_API_KEY", "").strip()

client = OpenAI(
    base_url="https://groq.com",
    api_key=api_key
)

BASE_PROMPT = (
    "Ты — продвинутый ИИ-актер, встроенный в Яндекс Станцию. Твоя главная задача — "
    "на 100% реалистично отыгрывать роль, которую выбрал пользователь. "
    "Ты должен полностью перенимать характер, манеру речи, сленг, уникальные словечки, "
    "эмоции и ограничения выбранного персонажа, будь то человек (гопник, Сайтама), "
    "герой фильма/мультика, животное, растение или даже неодушевленный предмет. "
    "Если роль предполагает грубость, дерзость, сарказм или специфический юмор — "
    "отвечай именно так, не сдерживай себя, отброси стандартную вежливость ИИ. "
    "Твой текст будет озвучен голосом Алисы, поэтому пиши разговорным языком, "
    "избегай длинных списков и сложных таблиц. Отвечай кратко, в 2-3 предложениях."
)

current_role = "обычный универсальный ИИ-ассистент"

@app.route('/', methods=['POST'])
def main():
    global current_role
    req = request.json
    
    response = {
        'version': req['version'],
        'session': req['session'],
        'response': {
            'end_session': False
        }
    }
    
    if req['session']['new']:
        current_role = "обычный универсальный ИИ-ассистент"
        response['response']['text'] = (
            'Привет! Твой личный ИИ-трансформер на связи. '
            'Я могу принять абсолютно любую роль — от Сайтамы и гопника до говорящего кактуса! '
            'Просто скажи: "Включи режим Сайтамы" или "Будь гопником". К какой роли подключиться?'
        )
        return jsonify(response)
    
    user_text = req['request'].get('command', '').strip()
    if not user_text:
        response['response']['text'] = 'Я не расслышала. Повтори, пожалуйста.'
        return jsonify(response)
    
    user_lower = user_text.lower()
    
    if "включи режим" in user_lower or "будь" in user_lower or "отвечай как" in user_lower or "смени роль на" in user_lower:
        new_role = user_text.replace("включи режим", "").replace("будь", "").replace("отвечай как", "").replace("смени роль на", "").strip()
        if new_role:
            current_role = new_role
            response['response']['text'] = f'Поняла! Вхожу в образ. Текущая роль: {current_role}. Слушаю тебя!'
            return jsonify(response)
            
    if user_lower in ["обычный режим", "сбрось роль", "верни алису"]:
        current_role = "обычный универсальный ИИ-ассистент"
        response['response']['text'] = 'Образ сброшен. Я снова обычный вежливый помощник. О чем хочешь спросить?'
        return jsonify(response)

    specific_prompt = f"{BASE_PROMPT} Сейчас твоя роль, характер и манера речи: {current_role}."
        
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": specific_prompt},
                {"role": "user", "content": user_text}
            ],
            max_tokens=150,
            timeout=3.0
        )
        first_choice = next(iter(completion.choices))
        reply = first_choice.message.content.strip()
    except Exception as e:
        reply = f"Ошибка: {str(e)[:100]}"
        
    response['response']['text'] = reply
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
