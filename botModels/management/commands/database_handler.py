import sqlite3


def get_lang_code(chat_id):
    with sqlite3.connect('db.sqlite3') as c:
        lang_code = c.execute(f'SELECT language_code FROM botModels_profile WHERE chat_id = {chat_id}').fetchone()[0]
    
    return lang_code
    

def change_lang_code(chat_id, lang_code):
    with sqlite3.connect('db.sqlite3') as c:
        c.execute(f'UPDATE botModels_profile SET language_code = ? WHERE chat_id = ?', (lang_code, chat_id))
        c.commit()
        print(f'Язык юзера {chat_id} изменён на {lang_code}')
    