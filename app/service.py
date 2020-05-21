import json


FILENAME = 'players.json'


class Player:

    def __init__(self, id, filename=FILENAME):
        self.id = id
        self.filename = filename

        with open(self.filename, encoding='utf-8') as f:
            self.data = json.load(f)
        try:
            self.player = [player for player in self.data['players'] if player['id'] == self.id][0]
        except:
            self.player = None

    def get_question_id(self, add=None):
        if add != None:
            self.player['question_id'] += add
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)

        return self.player['question_id']

    def get_answers(self, add=None):
        if add != None:
            self.player['answers'].append(add)
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)

        return self.player['answers']

    def restart_player(self, **kwargs):
        if self.player == None:
            self.player = {'id': self.id}
            self.data['players'].append(self.player)

        for k, v in kwargs.items():
            self.player[k] = v

        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)


def write_client_json(data, filename='answer.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
