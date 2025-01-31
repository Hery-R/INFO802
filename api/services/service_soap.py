from spyne import Float, Unicode, rpc, Application, ServiceBase, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server


class TimePriceService(ServiceBase):
    @rpc(Float, Float, Float, _returns=Iterable(Unicode))
    def get_time_price(ctx, distance, autonomy, recharge_time):
        try:
            print("LOG - SOAP : Calcul pour", {
                "distance": float(distance),
                "autonomie": float(autonomy),
                "temps_recharge": float(recharge_time)
            })
            
            # Conversion explicite en float pour éviter les erreurs
            distance = float(distance)
            autonomy = float(autonomy)
            recharge_time = float(recharge_time)
            
            nb_recharges = distance / autonomy
            temps_recharge_total = nb_recharges * (recharge_time / 60)  # conversion en heures
            temps_conduite = distance / 90  # vitesse moyenne de 90 km/h
            temps_total = temps_conduite + temps_recharge_total
            prix = temps_total * 2
            
            result = [str(temps_total), str(prix)]
            print("LOG - SOAP : Résultat =", result)
            return result
            
        except Exception as e:
            print(f"Erreur SOAP : {str(e)}")
            return ['0', '0']


application = Application([TimePriceService], 'time_price.soap',
                        in_protocol=Soap11(validator='lxml'),
                        out_protocol=Soap11())

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    server = make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()


