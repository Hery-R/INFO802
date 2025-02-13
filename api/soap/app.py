from flask import Flask, request
from spyne import Float, Unicode, rpc, Application, ServiceBase, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

class TimePriceService(ServiceBase):
    @rpc(Float, Float, Float, _returns=Iterable(Unicode))
    def get_time_price(ctx, distance, autonomy, recharge_time):
        try:
            distance = float(distance)
            autonomy = float(autonomy)
            recharge_time = float(recharge_time)
            
            nb_recharges = distance / autonomy
            temps_recharge_total = nb_recharges * (recharge_time / 60)
            temps_conduite = distance / 90
            temps_total = temps_conduite + temps_recharge_total
            prix = temps_total * 2
            
            return [str(temps_total), str(prix)]
            
        except Exception as e:
            return ['0', '0']

@app.route('/')
def hello():
    return "Service SOAP opérationnel"

# Configuration SOAP
soap_app = Application([TimePriceService], 
    tns='time_price.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11())

# Création de l'application WSGI pour SOAP
soap_wsgi_app = WsgiApplication(soap_app)

# Combinaison des applications Flask et SOAP
application = DispatcherMiddleware(app, {
    '/soap': soap_wsgi_app
})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


