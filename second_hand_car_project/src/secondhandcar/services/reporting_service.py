from typing import List, Optional
from datetime import datetime, date as dt_date
from secondhandcar.services.financial_transaction_service import FinancialTransactionService
from secondhandcar.transactions.transaction import Transaction, TransactionType

class ReportingService:
    def __init__(self, financial_service: 'FinancialTransactionService'):
        self._financial_service = financial_service

    def generate_daily_report(self, report_date: Optional[dt_date] = None) -> str:
        if report_date is None:
            report_date = datetime.now().date()

        report_str = f"\n--- Daily Report for {report_date.strftime('%Y-%m-%d')} ---\n"
        
        all_transactions = self._financial_service.get_all_transactions()
        daily_transactions = [
            t for t in all_transactions
            if t.timestamp.date() == report_date
        ]

        if not daily_transactions:
            report_str += "No transactions for this day.\n"
            return report_str

        sales = [t for t in daily_transactions if t.transaction_type == TransactionType.SALE]
        repairs = [t for t in daily_transactions if t.transaction_type == TransactionType.REPAIR]
        vehicle_purchases = [t for t in daily_transactions if t.transaction_type == TransactionType.VEHICLE_PURCHASE]
        part_purchases = [t for t in daily_transactions if t.transaction_type == TransactionType.SPARE_PART_PURCHASE]

        report_str += f"\nSales ({len(sales)}):\n"
        if sales:
            for sale in sales:
                report_str += f"  - {sale}\n"
        else:
            report_str += "  No sales.\n"
        
        report_str += f"\nRepairs ({len(repairs)}):\n"
        if repairs:
            for repair in repairs:
                report_str += f"  - {repair}\n"
        else:
            report_str += "  No repairs.\n"

        report_str += f"\nVehicle Purchases ({len(vehicle_purchases)}):\n"
        if vehicle_purchases:
            for vp in vehicle_purchases:
                report_str += f"  - {vp}\n"
        else:
            report_str += "  No vehicle purchases.\n"

        report_str += f"\nSpare Part Purchases ({len(part_purchases)}):\n"
        if part_purchases:
            for pp in part_purchases:
                report_str += f"  - {pp}\n"
        else:
            report_str += "  No spare part purchases.\n"
            
        total_sales_amount = sum(s.amount for s in sales)
        total_repair_amount = sum(r.amount for r in repairs)
        total_vehicle_purchase_amount = sum(vp.amount for vp in vehicle_purchases)
        total_part_purchase_amount = sum(pp.amount for pp in part_purchases)

        report_str += "\n--- Summary ---\n"
        report_str += f"Total Sales Amount: {total_sales_amount:.2f}\n"
        report_str += f"Total Repair Revenue: {total_repair_amount:.2f}\n"
        report_str += f"Total Vehicle Purchase Cost: {total_vehicle_purchase_amount:.2f}\n"
        report_str += f"Total Spare Part Purchase Cost: {total_part_purchase_amount:.2f}\n"
        
        return report_str
