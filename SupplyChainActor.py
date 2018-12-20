"""
-------------------------------------------------------
This file contains and defines the SupplyChainActor class.
-------------------------------------------------------
Author:  Tom LaMantia
Email:   tom@lamantia.mail.utoronto.ca
Version: February 7th 2016
-------------------------------------------------------
"""


STORAGE_COST_PER_UNIT = 0.5
BACKORDER_PENALTY_COST_PER_UNIT = 1


class SupplyChainActor:
    
    def __init__(self, policy , nstates , initial_stock , incomingOrdersQueue, outgoingOrdersQueue, incomingDeliveriesQueue, outgoingDeliveriesQueue):
        """
        -------------------------------------------------------
        Constructor for the SupplyChainActor class. All other
        supply chain actors (Retailer, Wholesaler, Distributor, Factory)
        are derived from this class. 
        -------------------------------------------------------
        Preconditions:
            incomingOrdersQueue - queue for incoming orders.
            outgoingOrdersQueue - queue for outgoing orders.
            incomingDeliveriesQueue - queue for incoming deliveries.
            outgoingDeliveriesQueue - queue for outgoing deliveries.
            
        Postconditions:
            Initializes the SupplyChainActor object in its initial state.
        -------------------------------------------------------
        """
        self.currentStock = initial_stock
        self.currentOrders = 0
        self.costsIncurred = 0
        
        self.incomingOrdersQueue = incomingOrdersQueue
        self.outgoingOrdersQueue = outgoingOrdersQueue
        self.incomingDeliveriesQueue = incomingDeliveriesQueue
        self.outgoingDeliveriesQueue = outgoingDeliveriesQueue
        
        self.lastOrderQuantity = 0


        self.policy = policy
        self.nstates = nstates
        self.states = []


        return
    
    def PlaceOutgoingDelivery(self, amountToDeliver):
        """
        -------------------------------------------------------
        Places a delivery to the actor one level higher in the supply
        chain.
        -------------------------------------------------------
        Preconditions: 
            None
        Postconditions:
            Places the delivery. Note: the advancement
            of the queues is handled by the main program.
        -------------------------------------------------------
        """
        self.outgoingDeliveriesQueue.PushEnvelope(amountToDeliver)
        return
    
    def PlaceOutgoingOrder(self, state):
        """
        -------------------------------------------------------
        Calculates the size of the weekly outgoing order.
        -------------------------------------------------------
        Preconditions: weekNum - the current week number.
        Postconditions:
            Calculates the order quantity using an anchor and maintain
            strategy.
        -------------------------------------------------------
        """
        amountToOrder , policy_action = self.policy.calculate_order( state )

        self.outgoingOrdersQueue.PushEnvelope(amountToOrder)
        self.lastOrderQuantity = amountToOrder
        
        return policy_action
    
    def ReceiveIncomingDelivery(self):
        """
        -------------------------------------------------------
        Receives a delivery from the actor one level lower in
        the supply chain.
        -------------------------------------------------------
        Preconditions: 
            None
        Postconditions:
            Updates the current stock based on the incoming
            deliveries queue.
        -------------------------------------------------------
        """
        quantityReceived = self.incomingDeliveriesQueue.PopEnvelope()
        
        if quantityReceived > 0:
            self.currentStock += quantityReceived
                
        return quantityReceived
    
    def ReceiveIncomingOrders(self):
        """
        -------------------------------------------------------
        Receives an incoming order from from the actor one level higher in
        the supply chain.
        -------------------------------------------------------
        Preconditions: 
            None
        Postconditions:
            Updates the current orders based on the incoming
            deliveries queue.
        -------------------------------------------------------
        """
        thisOrder = self.incomingOrdersQueue.PopEnvelope()
        
        if thisOrder > 0:
            self.currentOrders += thisOrder
        return thisOrder
    
    def CalcBeerToDeliver(self):
        """
        -------------------------------------------------------
        Calculates how much beer to deliver to the customer. The
        current stock and number of cases currently on order by the
        customer are updated from within this function.
        -------------------------------------------------------
        Preconditions: 
            None
        Postconditions:
            Returns deliveryQuantitiy - the number of cases to be delivered
            to the customer. currentOrders, currentStock are
            updated to reflect this delivery quantity. 
        -------------------------------------------------------
        """
        deliveryQuantity = 0
        
         #If we can fill the customer's order, we must do it.
        if self.currentStock >= self.currentOrders:
            deliveryQuantity = self.currentOrders
            self.currentStock -= deliveryQuantity
            self.currentOrders -= deliveryQuantity
        #If the current stock cannot cover the order, we must fill as much as we can, and back-order the rest.
        elif self.currentStock >= 0 and self.currentStock < self.currentOrders:
            deliveryQuantity = self.currentStock
            self.currentStock = 0
            self.currentOrders -= deliveryQuantity

        return deliveryQuantity
    
    def CalcCostForTurn(self):
        """
        -------------------------------------------------------
        This function calculates the total costs incurred for the
        current turn. 
        -------------------------------------------------------
        Preconditions: This program must be called LAST in the turn
            sequence to account for orders taken and deliveries.
        Postconditions:
            Returns costsThisTurn - the total cost incurred during
            this turn.
        -------------------------------------------------------
        """
        costsThisTurn = 0
        
        inventoryStorageCost = self.currentStock * STORAGE_COST_PER_UNIT
        backorderPenaltyCost = self.currentOrders * BACKORDER_PENALTY_COST_PER_UNIT
        
        costsThisTurn = inventoryStorageCost + backorderPenaltyCost
        
        return costsThisTurn
    
    def GetCostIncurred(self):
        """
        -------------------------------------------------------
        Returns the total costs incurred. 
        -------------------------------------------------------
        Preconditions: None.
        Postconditions: Returns self.costsIncurred
        -------------------------------------------------------
        """
        return self.costsIncurred
    
    def GetLastOrderQuantity(self):
        """
        -------------------------------------------------------
        Returns the quantity of the last order made. 
        -------------------------------------------------------
        Preconditions: None.
        Postconditions: Returns self.lastOrderQuantity
        -------------------------------------------------------
        """
        return self.lastOrderQuantity
    
    def CalcEffectiveInventory(self):
        """
        -------------------------------------------------------
        Returns the effective inventory of the calling SupplyChainActor
        during the week the method is called.
        -------------------------------------------------------
        Preconditions: None.
        Postconditions: Returns the effective inventory, which
            is defined as self.currentStock - self.currentOrders.
        -------------------------------------------------------
        """
        return (self.currentStock - self.currentOrders)




###########################################################################





class SupplyChainQueue():
    
    def __init__(self, queueLength):
        """
        -------------------------------------------------------
        Constructor for the SupplyChainQueue class.
        -------------------------------------------------------
        Preconditions: queueLength - the length of the queue. This
                argument is used to inplement variable length delays.
        Postconditions: Initializes an empty supply chain queue.
        -------------------------------------------------------
        """
        self.queueLength = queueLength
        self.data = []
        return
    
    def PushEnvelope(self, numberOfCasesToOrder):
        """
        -------------------------------------------------------
        Places an order/delivery into the supply chain queue.
        -------------------------------------------------------
        Preconditions: numberOfCases - an integer which
            indicates the number of cases to order/send out.
        Postconditions: Returns True if the order is successfully
            placed, False otherwise. 
        -------------------------------------------------------
        """
        orderSuccessfullyPlaced = False
        
        if len(self.data) < self.queueLength:
            self.data.append(numberOfCasesToOrder)
            orderSuccessfullyPlaced = True
            
        return orderSuccessfullyPlaced
    
    def AdvanceQueue(self):
        """
        -------------------------------------------------------
        This utility function advances the queue. This mechanism
        drives the delay loop.
        -------------------------------------------------------
        Preconditions: None.
        Postconditions: The item at index [1] (second oldest) is moved
            to index [0], item at index [2] is moved to index [1], etc...
        -------------------------------------------------------
        """
        self.data.pop(0)
        return
    
    def PopEnvelope(self):
        """
        -------------------------------------------------------
        Returns the beer order in the queue.
        -------------------------------------------------------
        Preconditions: None.
        Postconditions: Returns the number of cases of beer ordered.
 
        This method also advances the queue!
        -------------------------------------------------------
        """
        if len(self.data) >= 1:
            quantityDelivered = self.data[0]
            self.AdvanceQueue()
        else:
            quantityDelivered = 0
         
        return quantityDelivered
    
    def PrettyPrint(self):
        """
        -------------------------------------------------------
        Pretty prints the queue.
        -------------------------------------------------------
        Preconditions: None.
        Postconditions: Queue state is printed to the Python console.
        -------------------------------------------------------
        """
        print(self.data)
        return