from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from api.resources.display import Display
from api.resources.preprocess import Preprocess
from api.resources.filter import Filter
from api.resources.controlFlow import ControlFlow
from api.resources.files import Files
from api.resources.dottedChart import DottedChart
from api.resources.dottedChartDuration import DottedChartDuration
from api.resources.fileExist import FileExist
from api.resources.convertTime import ConvertTime
from api.resources.alias import Alias
from api.resources.join import Join
from api.resources.drop import Drop
from api.resources.statisticStart import StatisticStart
from api.resources.statisticEnd import StatisticEnd
from api.resources.statisticSummary import StatisticSummary
from api.resources.countAttempt import CountAttempt
from api.resources.alphaMiner import RunAlgo
from api.resources.changeCaseid import ChangeCaseID
from api.resources.chooseAlpha import ChooseAlpha

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)

# TODO: graph diganti jadi control flow terus tambahin dotted chart
api.add_resource(Display, '/api/display')
api.add_resource(Preprocess, '/api/prepos')
api.add_resource(Filter, '/api/filter')
api.add_resource(ControlFlow, '/api/controlflow')
api.add_resource(DottedChart, '/api/dottedchart')
api.add_resource(DottedChartDuration, '/api/dottedchartduration')
api.add_resource(Files, '/api/files')
api.add_resource(FileExist, '/api/exist')
api.add_resource(ConvertTime, '/api/convert')
api.add_resource(Alias, '/api/alias')
api.add_resource(Join, '/api/join')
api.add_resource(Drop, '/api/drop')
api.add_resource(StatisticStart, '/api/statisticstart')
api.add_resource(StatisticEnd, '/api/statisticend')
api.add_resource(StatisticSummary, '/api/statisticsummary')
api.add_resource(CountAttempt, '/api/countattempt')
api.add_resource(RunAlgo, '/api/algoritmaalpha')
api.add_resource(ChangeCaseID, '/api/changecaseid')
api.add_resource(ChooseAlpha, '/api/choosealpha')
