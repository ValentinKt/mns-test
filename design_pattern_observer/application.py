

from Observer.crowdfound_notifier import CrowdfoundingNotifier
from Observer.crowdfunding import Crowdfounding


class Application:

    def __init__(self, name):
        self.name = name

    def run_obserber(self):
       
        crowdfunding = Crowdfounding(600)
        crowdfound_notifier = CrowdfoundingNotifier()
        crowdfunding.add_observer(crowdfound_notifier)
        crowdfunding.add_sum(200)
        crowdfunding.add_sum(500)
    
        
        
        
        
if __name__ == "__main__":
    
    app = Application("Crowdfunding App")
    app.run_obserber()

 
    




    # app1.runExempleSigleton()
    # app1.runExempleFactory()
    # app.runExempleObserver()