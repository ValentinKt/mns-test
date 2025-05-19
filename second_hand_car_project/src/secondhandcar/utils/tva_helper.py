class TVAHelper:
    DEFAULT_TVA_RATE = 20.0  # Default VAT rate, e.g., 20%

    @staticmethod
    def calculate_price_ttc(price_ht: float, tva_rate: float = DEFAULT_TVA_RATE) -> float:
        """
        Calculates the price including tax (TTC) from the price excluding tax (HT) and VAT rate.
        :param price_ht: Price excluding tax.
        :param tva_rate: VAT rate in percentage (e.g., 20 for 20%).
        :return: Price including tax.
        """
        if price_ht < 0:
            raise ValueError("Price HT cannot be negative.")
        if tva_rate < 0:
            raise ValueError("TVA rate cannot be negative.")
        return price_ht * (1 + (tva_rate / 100))

    @staticmethod
    def calculate_tva_amount(price_ht: float, tva_rate: float = DEFAULT_TVA_RATE) -> float:
        """
        Calculates the VAT amount from the price excluding tax and VAT rate.
        :param price_ht: Price excluding tax.
        :param tva_rate: VAT rate in percentage.
        :return: VAT amount.
        """
        if price_ht < 0:
            raise ValueError("Price HT cannot be negative.")
        if tva_rate < 0:
            raise ValueError("TVA rate cannot be negative.")
        return price_ht * (tva_rate / 100)
