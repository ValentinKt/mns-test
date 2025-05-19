from typing import List
from secondhandcar.models.base_vehicle import BaseVehicle
from secondhandcar.models.customer import Customer
from secondhandcar.models.spare_part import SparePart
from secondhandcar.transactions.sale_transaction import SaleTransaction
from secondhandcar.transactions.repair_transaction import RepairTransaction
from secondhandcar.transactions.purchase_transaction import PurchaseTransaction, PurchaseItemType
from secondhandcar.repositories.interface_vehicle_repository import IVehicleRepository # For updating vehicle status
from secondhandcar.transactions.transaction import Transaction
from secondhandcar.utils.custom_exceptions import InsufficientStockError, VehicleNotFoundError

class FinancialTransactionService:
    def __init__(self, vehicle_repository: IVehicleRepository):
        self._transactions: List[Transaction] = []
        self._vehicle_repository = vehicle_repository
        # In a real app, spare parts would also have a repository
        self._spare_parts_stock: List[SparePart] = [] # Simplified stock

    def record_sale(self, vehicle: BaseVehicle, customer: Customer, sale_price: float) -> SaleTransaction:
        if vehicle.is_sold:
            raise ValueError(f"Vehicle {vehicle.id} is already sold.")
        
        vehicle_in_repo = self._vehicle_repository.get_vehicle_by_id(vehicle.id)
        if not vehicle_in_repo:
            raise VehicleNotFoundError(f"Vehicle {vehicle.id} not found in repository for sale.")

        sale = SaleTransaction(vehicle, customer, sale_price)
        self._transactions.append(sale)
        
        vehicle_in_repo.is_sold = True
        vehicle_in_repo.is_available = False
        self._vehicle_repository.update_vehicle(vehicle_in_repo)
        
        print(f"Sale recorded: {sale}")
        return sale

    def record_repair(self, vehicle: BaseVehicle, customer: Customer, description: str, cost: float, 
                        parts_to_use_references: List[str] = None) -> RepairTransaction:
        
        parts_used_objects: List[SparePart] = []
        actual_parts_cost = 0.0

        if parts_to_use_references:
            for ref in parts_to_use_references:
                part_found = False
                for stock_part in self._spare_parts_stock:
                    if stock_part.reference == ref and stock_part.quantity > 0:
                        parts_used_objects.append(stock_part)
                        stock_part.quantity -= 1 # Decrement stock
                        actual_parts_cost += stock_part.selling_price
                        part_found = True
                        break
                if not part_found:
                    raise InsufficientStockError(f"Spare part with reference {ref} not available or out of stock.")
        
        total_repair_cost = cost + actual_parts_cost # cost is labor, actual_parts_cost is for parts
        repair = RepairTransaction(vehicle, customer, description, total_repair_cost, parts_used_objects)
        self._transactions.append(repair)
        print(f"Repair recorded: {repair}")
        return repair

    def record_vehicle_purchase(self, vehicle: BaseVehicle, purchase_price: float, supplier: str = "Private Seller") -> PurchaseTransaction:
        # Add to repository first
        try:
            self._vehicle_repository.add_vehicle(vehicle) # Assumes vehicle is Car type for now
        except ValueError as e: # Already exists, perhaps update? For now, let it fail if ID clashes.
            print(f"Warning: Could not add vehicle {vehicle.id} to repository: {e}. It might already exist.")

        purchase = PurchaseTransaction(vehicle, purchase_price, supplier)
        self._transactions.append(purchase)
        print(f"Vehicle purchase recorded: {purchase}")
        return purchase

    def record_spare_part_purchase(self, part_name: str, reference: str, purchase_price: float, quantity: int, supplier: str = "Parts Supplier") -> PurchaseTransaction:
        # Update stock
        existing_part = None
        for p in self._spare_parts_stock:
            if p.reference == reference:
                existing_part = p
                break
        
        if existing_part:
            existing_part.quantity += quantity
            # Optionally update purchase price if it changes, e.g., to an average
            # existing_part.purchase_price = ((existing_part.purchase_price * (existing_part.quantity - quantity)) + (purchase_price * quantity)) / existing_part.quantity
            item_for_transaction = existing_part
        else:
            new_part = SparePart(name=part_name, reference=reference, purchase_price=purchase_price, quantity=quantity)
            self._spare_parts_stock.append(new_part)
            item_for_transaction = new_part
            
        total_cost = purchase_price * quantity
        purchase = PurchaseTransaction(item_for_transaction, total_cost, supplier)
        self._transactions.append(purchase)
        print(f"Spare part purchase recorded: {purchase} for {quantity} units.")
        return purchase

    def get_all_transactions(self) -> List[Transaction]:
        return self._transactions.copy()

    def get_spare_parts_stock(self) -> List[SparePart]:
        return self._spare_parts_stock.copy()
