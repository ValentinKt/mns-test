from Observer.observer import Observer


class Crowdfounding:
    """
    Le Sujet (Observable) : Le Crowdfounding.
    Il maintient une liste d'observateurs et les notifie des changements.
    """
    def __init__(self, target: float):
        self._sum = 0
        self._target = target
        # Liste pour stocker les observateurs
        self._observers: list[Observer] = []
        

    def add_observer(self, observer: Observer):
        """Ajoute un observateur à la liste."""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Observer '{observer.__class__.__name__}' added to Crowdfounding.")

    def remove_observer(self, observer: Observer):
        """Retire un observateur de la liste."""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"Observer '{observer.__class__.__name__}' removed from Crowdfounding.")

    def _notify_observers(self):
        """Informe tous les observateurs attachés d'un changement."""
        print("\n--- Notification des observateurs ---")
        for observer in self._observers:
            observer.update(self) # Passe l'instance du panier à l'observateur
        print("--- Fin de la notification ---")

    def add_sum(self, sum: float):
        """Adding new sum to Crowdfounding and notify observers."""
        print(f"\nAdding new sum : '{sum}' to Crowdfounding.")
        self._sum += sum
        self._notify_observers() # Notifie les observateurs après le changement

    def remove_sum(self, sum: float):
        """Removing a sum from crowdfunding and notify observers.."""
        if( self.get_current_sum() >= 0):
            print(f"\nRemoving a sum : '{sum}' from crowdfunding.")
            self._sum -= sum
                 # Notifie les observateurs après le changement
       

    def get_current_sum(self):
        """Returns the current sum of crowdfunding."""
        return self._sum

    def get_target(self):
        """Returns the target of crowdfunding."""
        return self._target
    
    def set_target(self, target: float):
        """Set the target of crowdfunding."""
        self._target = target
        # self._notify_observers() # Notifie les observateurs après le changement

    def is_target_reached(self):
        """Check if the target is reached."""
        return self._sum >= self._target

    def is_target_not_reached(self):
        """Check if the target is not reached."""
        return self._sum < self._target