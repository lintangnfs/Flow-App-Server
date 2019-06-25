from flask_restful import Resource, request
import csv, json, os, pandas as pd

# Path to raw and final csv
raw_file = 'api/static/data/raw.csv'
final_file = 'api/static/data/final.csv'

class ChangeCaseID(Resource):

    def get(self):
        if os.path.isfile(final_file):
            data = pd.read_csv(final_file)
        else:
            data = pd.read_csv(raw_file)

        return json.dumps(
            {
                'data': list(data.columns),
                'message': 'Succesfully fetch the data',
                'status': 'success'
            }
        )

    def post(self):
        args = request.get_json(force=True)
        if args != None:
            if os.path.isfile(final_file):
                data = pd.read_csv(final_file)
            else:
                data = pd.read_csv(raw_file)

            change(data, args['data']['col1'], args['data']['col2'], args['data']['col3'], args['data']['value'])

            data.to_csv(final_file, index=False)
            return json.dumps(
                {
                    'data': list(data.columns),
                    'message': 'Succesfully join the column',
                    'status': 'success'
                }
            )
        else:
            return json.dumps(
                {
                    'data': '',
                    'message': 'No data received',
                    'status': 'success'
                }
            )
    
def change(data, col1, col2, col3, value):
    try:
        # Replace value in 'User full name' column using value in 'Event name' column 
        # if 'Event name' = 'Course completed' or 'Course activity completion update'
        for i in range(data.shape[0]):
            if data[col3].iloc[i] == value :
                data[col1].iloc[i] = data[col2].iloc[i]
            
    except Exception as e:
        return e