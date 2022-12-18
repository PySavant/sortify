from app import Sortify
from app.logger import Config



logger = Config.setLogger()


app = Sortify(logger)
