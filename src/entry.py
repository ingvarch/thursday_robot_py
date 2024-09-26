from js import console, Response, JSON, Object, fetch, Date, Array

def get_nested(obj, *keys):
    current = obj
    for key in keys:
        if not Object.hasOwn(current, key):
            return None
        current = Object.getOwnPropertyDescriptor(current, key).value
    return current

def get_thursday_message():
    now = Date.new()
    day = now.getDay()
    if day == 4:  # Thursday (0 is Sunday, 1 is Monday, ..., 6 is Saturday)
        return "Wow, it's Thursday! 🍺"
    else:
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        return f"It's not Thursday 😢 It's {days[day]}."

async def on_fetch(request, env):

    bot_token = env.BOT_TOKEN

    console.log(f"Received request: {request.method} {request.url}")

    if request.method == "POST":
        try:
            update = await request.json()
            console.log(f"Received update: {JSON.stringify(update)}")

            if Object.hasOwn(update, 'message'):
                chat_id = get_nested(update, 'message', 'chat', 'id')
                text = get_nested(update, 'message', 'text')

                if chat_id is not None and text is not None:
                    console.log(f"Received message: {text} from chat_id: {chat_id}")

                    if text == '/start':
                        message = get_thursday_message()
                        await send_message(chat_id, message, bot_token)
            elif Object.hasOwn(update, 'inline_query'):
                query_id = get_nested(update, 'inline_query', 'id')
                if query_id is not None:
                    await answer_inline_query(query_id, bot_token)
            else:
                console.error("Update does not contain expected structure")
                return Response.new("Invalid update format", {"status": 400})

            return Response.new("OK", {"status": 200})
        except Exception as e:
            console.error(f"Error processing request: {str(e)}")
            console.error(f"Error type: {type(e)}")
            console.error(f"Error args: {e.args}")
            return Response.new("Error", {"status": 500})
    else:
        return Response.new("Please send a POST request", {"status": 200})

async def send_message(chat_id, text, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = Object.fromEntries([
        ["chat_id", str(chat_id)],
        ["text", str(text)]
    ])

    console.log(f"Sending payload: {JSON.stringify(payload)}")

    try:
        response = await fetch(url,
                               method="POST",
                               body=JSON.stringify(payload),
                               headers=Object.fromEntries([["Content-Type", "application/json"]]))

        console.log(f"Response status: {response.status}")

        response_text = await response.text()
        console.log(f"Response text: {response_text}")

        if response.ok:
            response_json = JSON.parse(response_text)
            console.log(f"Telegram API response: {JSON.stringify(response_json)}")

            if get_nested(response_json, 'ok'):
                console.log("Message sent successfully")
            else:
                console.error(f"Failed to send message. Response: {JSON.stringify(response_json)}")
        else:
            console.error(f"Failed to send message. Status: {response.status}, Response: {response_text}")
    except Exception as e:
        console.error(f"Error sending message: {str(e)}")
        console.error(f"Error type: {type(e)}")
        console.error(f"Error args: {e.args}")

async def answer_inline_query(query_id, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/answerInlineQuery"

    message = get_thursday_message()
    results = Array.new(
        Object.fromEntries([
            ("type", "article"),
            ("id", "1"),
            ("title", "What is day today?"),
            ("input_message_content", Object.fromEntries([
                ("message_text", message)
            ])),
            ("description", "Is it Thursday?"),
            ("thumb_url", "https://cdn-icons-png.freepik.com/256/5726/5726532.png"),
            ("thumb_width", 150),
            ("thumb_height", 150)
        ])
    )

    payload = Object.fromEntries([
        ("inline_query_id", query_id),
        ("results", JSON.stringify(results)),
        ("cache_time", 1)
    ])

    console.log(f"Answering inline query with payload: {JSON.stringify(payload)}")

    try:
        response = await fetch(url,
                               method="POST",
                               body=JSON.stringify(payload),
                               headers=Object.fromEntries([("Content-Type", "application/json")]))

        console.log(f"Response status: {response.status}")

        response_text = await response.text()
        console.log(f"Response text: {response_text}")

        if response.ok:
            response_json = JSON.parse(response_text)
            console.log(f"Telegram API response: {JSON.stringify(response_json)}")

            if get_nested(response_json, 'ok'):
                console.log("Inline query answered successfully")
            else:
                console.error(f"Failed to answer inline query. Response: {JSON.stringify(response_json)}")
        else:
            console.error(f"Failed to answer inline query. Status: {response.status}, Response: {response_text}")
    except Exception as e:
        console.error(f"Error answering inline query: {str(e)}")
        console.error(f"Error type: {type(e)}")
        console.error(f"Error args: {e.args}")

export = {'fetch': on_fetch}
