class Observer:
    """
    Classe Abstraite (ou Interface) pour les observateurs.
    Toutes les classes d'observateurs concrètes doivent hériter de celle-ci
    et implémenter la méthode 'update'.
    """
    def update(self, subject):
        """
        Cette méthode est appelée par le sujet lorsque son état change.
        'subject' est l'instance du sujet qui a notifié l'observateur.
        """
        raise NotImplementedError("La méthode 'update' doit être implémentée par les sous-classes.")