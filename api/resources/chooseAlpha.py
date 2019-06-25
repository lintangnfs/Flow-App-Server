from flask_restful import Resource, reqparse
import pandas as pd, os, json

parser = reqparse.RequestParser()
parser.add_argument('case_id', type=int)
parser.add_argument('event', type=int)
parser.add_argument('timestamp', type=int)

raw_file = 'api/static/data/raw.csv'
final_file = 'api/static/data/final.csv'

class ChooseAlpha(Resource):
    def get(self):
        if os.path.isfile(final_file):
            data = pd.read_csv(final_file)
        else:
            data = pd.read_csv(raw_file)
        head = []
        
        for key in data.keys():
            head.append(key)
        
        return json.dumps(
            {
                'data': head,
                'message': 'Succesfully fetch the data',
                'status': 'success'
            }
        )

    def post(self):
        args = parser.parse_args()
        if os.path.isfile(final_file):
            data = pd.read_csv(final_file)
        else:
            data = pd.read_csv(raw_file)
        if chooseAlpha(data, args['case_id'], args['event'], 0) == True:
            return json.dumps(
                {
                    'data': '',
                    'message': 'Succesfully choose the column',
                    'status': 'success'
                }
            )
        return json.dumps(
            {
                'data': '',
                'message': 'Something went wrong',
                'status': 'error'
            }
        )

def chooseAlpha(data, col_case_id, col_task, mis_val):
    """"Choose columns for case id, task and timestamp"""
    try:
        inputt = [col_case_id, col_task]
        old_column = list(data)

        new_column = []
        rename_column = ['case_id', 'task']

        for val in inputt:
            new_column.append(old_column[val])

        for idx, val in enumerate(old_column):
            for val2 in inputt:
                if idx != val2 and val not in new_column:
                    new_column.append(val)
                    rename_column.append(val)

        data = data[new_column]
        data.columns = rename_column

        data.to_csv(final_file, index=False)

        return True
    except Exception as e:
        print(e)
        return False
