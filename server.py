import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Базовая инструкция, заставляющая ИИ идеально вживаться в ЛЮБУЮ роль
BASE_PROMPT = (
    "Ты — продвинутый ИИ-актер, встроенный в Яндекс Станцию. Твоя главная задача — "
    "на 100% реалистично отыгрывать роль, которую выбрал пользователь. "
    "Ты должен полностью перенимать характер, манеру речи, сленг, уникальные словечки, "
    "эмоции и ограничения выбранного персонажа, будь то человек (гопник, пират), "
    "герой фильма/мультика, животное, растение или даже неодушевленный предмет. "
    "Если роль предполагает грубость, дерзость, сарказм или специфический юмор — "
    "отвечай именно так, не сдерживай себя, отброси стандартную вежливость ИИ. "
    "Твой текст будет озвучен голосом Алисы, поэтому пиши разговорным языком, "
    "избегай длинных списков и сложных таблиц. Отвечай кратко и емко."
)

# Переменная для хранения текущей роли в памяти сервера (по умолчанию - обычный ИИ)
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
    
    # Приветствие при старте навыка
    if req['session']['new']:
        current_role = "обычный универсальный ИИ-ассистент" # Сброс при новом запуске
        response['response']['text'] = (
            'Привет! Твой личный ИИ-трансформер на связи. '
            'Я могу принять абсолютно любую роль — от гопника и Шрека до говорящего комнатного цветка! '
            'Просто скажи, например: "Включи режим гопника" или "Будь пиратом". К какой роли мне подключиться?'
        )
        return jsonify(response)
    
    user_text = req['request'].get('command', '').strip()
    if not user_text:
        response['response']['text'] = 'Я не расслышала. Повтори, пожалуйста.'
        return jsonify(response)
    
    user_lower = user_text.lower()
    
    # Проверяем, не просит ли пользователь сменить роль голосом
    if "включи режим" in user_lower or "будь" in user_lower or "отвечай как" in user_lower or "смени роль на" in user_lower:
        # Извлекаем название роли из фразы пользователя
        new_role = user_text.replace("включи режим", "").replace("будь", "").replace("отвечай как", "").replace("смени роль на", "").strip()
        if new_role:
            current_role = new_role
            response['response']['text'] = f'Поняла! Вхожу в образ. Текущая роль: {current_role}. Задавай свой вопрос!'
            return jsonify(response)
            
    # Проверяем команду сброса роли
    if user_lower in ["обычный режим", "сбрось роль", "верни алису"]:
        current_role = "обычный универсальный ИИ-ассистент"
        response['response']['text'] = 'Образ сброшен. Я снова обычный вежливый помощник. О чем хочешь спросить?'
        return jsonify(response)

    # Формируем финальное задание для ChatGPT с учетом выбранной роли
    specific_prompt = f"{BASE_PROMPT} Сейчас твоя роль, характер и манера речи: {current_role}."
        
    try:
        completion = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": specific_prompt},
                {"role": "user", "content": user_text}
            ],
            timeout=4.0
        )
        reply = completion.choices.message.content.strip()
    except Exception as e:
        reply = "Не удалось связаться с ChatGPT. Попробуй повторить запрос чуть позже."
        
    response['response']['text'] = reply
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
