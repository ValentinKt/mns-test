from Observer.observer import Observer
from Observer.crowdfunding import Crowdfounding

class CrowdfoundingNotifier(Observer):
    """
    Un observateur qui réagit aux changements de la somme et si la target du Crowdfounding est atteint, par exemple,
    mettre à jour les niveaux de stock.
    """
    def __init__(self):
        print(f"CrowdfoundingNotifier initialisé")

    def update(self, crowdfunding_observable: Crowdfounding):

        print(f"[CrowdfoundingNotifier] Notification reçue du Crowdfounding.")
        print(f"[CrowdfoundingNotifier] Somme actuelle du Crowdfounding : {crowdfunding_observable.get_current_sum()}")
        print(f"[CrowdfoundingNotifier] Target actuelle du Crowdfounding : {crowdfunding_observable.get_target()}")

        if crowdfunding_observable.is_target_reached():
            print("[CrowdfundingNotifier] Target atteint !")
        
        if crowdfunding_observable.is_target_not_reached():
            print("[CrowdfundingNotifier] Target non atteint.")

    
        
